#!/usr/bin/env python3
"""Generate cached text-to-speech audio for Jekyll posts.

The script is intentionally build-system friendly:
- it never requires an API key when cached audio already exists;
- it writes a Jekyll data manifest used by the post layouts;
- it speaks image/diagram alt text and renders TeX into readable narration.
"""

from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


POSTS_DIR = Path("_posts")
OUTPUT_DIR = Path("assets/media/tts")
DATA_FILE = Path("_data/tts.json")
CACHE_FILE = Path(".tts-cache/manifest.json")
CHUNK_CACHE_DIR = Path(".tts-cache/chunks")

DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"

# Bump this to invalidate previously concatenated post audio without
# discarding the per-paragraph ElevenLabs cache. v2 switched from raw
# byte concatenation (broken seeking, wrong duration) to ffmpeg remux.
CONCAT_VERSION = "concat-v2-ffmpeg"


GREEK = {
    "alpha": "alpha",
    "beta": "beta",
    "gamma": "gamma",
    "delta": "delta",
    "epsilon": "epsilon",
    "lambda": "lambda",
    "mu": "mu",
    "nu": "nu",
    "pi": "pi",
    "phi": "phi",
    "psi": "psi",
    "rho": "rho",
    "sigma": "sigma",
    "tau": "tau",
    "theta": "theta",
    "omega": "omega",
    "Delta": "capital delta",
    "Sigma": "capital sigma",
    "Gamma": "capital gamma",
}

COMMANDS = {
    "text": "",
    "mathrm": "",
    "mathbf": "",
    "mathcal": "",
    "left": "",
    "right": "",
    "cdot": " times ",
    "times": " times ",
    "propto": " is proportional to ",
    "sim": " is similar to ",
    "neq": " is not equal to ",
    "infty": " infinity ",
    "rightarrow": " to ",
    "Rightarrow": " implies ",
    "to": " to ",
    "exp": " exp ",
    "sum": " sum ",
    "lim": " limit ",
    "vert": " given ",
    "cap": " intersect ",
}


def split_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---"):
        return {}, markdown
    parts = markdown.split("---", 2)
    if len(parts) < 3:
        return {}, markdown
    raw_front, body = parts[1], parts[2]
    front: dict[str, str] = {}
    for line in raw_front.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        front[key.strip()] = value.strip().strip("'\"")
    return front, body


def post_slug(path: Path) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{1,2}-", "", path.stem)


def strip_code_blocks(text: str) -> str:
    text = re.sub(r"```.*?```", "\nCode block omitted from narration.\n", text, flags=re.S)
    text = re.sub(r"~~~.*?~~~", "\nCode block omitted from narration.\n", text, flags=re.S)
    return text


def fallback_alt(src: str) -> str:
    stem = Path(src.split("?")[0].split("#")[0]).stem
    return stem.replace("-", " ").replace("_", " ").strip()


class ImageNarrator(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        attr = {key.lower(): value or "" for key, value in attrs}
        alt = (attr.get("alt") or attr.get("title") or fallback_alt(attr.get("src", ""))).strip()
        if alt:
            self.parts.append(f"\nDiagram: {alt}.\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.parts.append(html.unescape(f"&#{name};"))


def replace_markdown_images(text: str) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)")

    def repl(match: re.Match[str]) -> str:
        alt = (match.group(1) or match.group(3) or fallback_alt(match.group(2))).strip()
        return f"\nDiagram: {alt}.\n" if alt else "\n"

    return pattern.sub(repl, text)


def replace_html_images(text: str) -> str:
    parser = ImageNarrator()
    parser.feed(text)
    return "".join(parser.parts)


def replace_liquid_figures(text: str) -> str:
    pattern = re.compile(r"{%\s*include\s+figure\.html(?P<attrs>.*?)%}", re.S)

    def repl(match: re.Match[str]) -> str:
        attrs = match.group("attrs")
        alt_match = re.search(r"alt\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s%]+))", attrs)
        path_match = re.search(r"path\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s%]+))", attrs)
        alt = ""
        if alt_match:
            alt = next(group for group in alt_match.groups() if group)
        elif path_match:
            alt = fallback_alt(next(group for group in path_match.groups() if group))
        return f"\nDiagram: {alt}.\n" if alt else "\n"

    return pattern.sub(repl, text)


def balanced_brace_value(text: str, start: int) -> tuple[str, int] | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    value: list[str] = []
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
            if depth > 1:
                value.append(char)
        elif char == "}":
            depth -= 1
            if depth == 0:
                return "".join(value), index + 1
            value.append(char)
        else:
            value.append(char)
    return None


def replace_frac(expr: str) -> str:
    while "\\frac" in expr:
        index = expr.find("\\frac")
        numerator = balanced_brace_value(expr, index + len("\\frac"))
        if not numerator:
            break
        denominator = balanced_brace_value(expr, numerator[1])
        if not denominator:
            break
        spoken = f" the fraction {latex_to_speech(numerator[0])} over {latex_to_speech(denominator[0])} "
        expr = expr[:index] + spoken + expr[denominator[1]:]
    return expr


def latex_to_speech(expr: str) -> str:
    expr = html.unescape(expr)
    expr = replace_frac(expr)
    expr = expr.replace("\\begin{bmatrix}", " matrix ").replace("\\end{bmatrix}", " end matrix ")
    expr = expr.replace("\\\\", " row ")
    expr = expr.replace("&", " column ")
    expr = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), COMMANDS.get(m.group(1), m.group(1))), expr)
    expr = re.sub(r"_\{([^{}]+)\}", r" subscript \1 ", expr)
    expr = re.sub(r"\^\{([^{}]+)\}", r" to the power of \1 ", expr)
    expr = re.sub(r"_([A-Za-z0-9]+)", r" subscript \1 ", expr)
    expr = re.sub(r"\^([A-Za-z0-9]+)", r" to the power of \1 ", expr)
    replacements = {
        "<=": " less than or equal to ",
        ">=": " greater than or equal to ",
        "!=": " is not equal to ",
        "=": " equals ",
        "+": " plus ",
        "-": " minus ",
        "*": " times ",
        "/": " divided by ",
        "(": " open parenthesis ",
        ")": " close parenthesis ",
        "[": " open bracket ",
        "]": " close bracket ",
        "{": " ",
        "}": " ",
    }
    for needle, value in replacements.items():
        expr = expr.replace(needle, value)
    expr = re.sub(r"\s+", " ", expr)
    return expr.strip()


def replace_math(text: str) -> str:
    text = re.sub(
        r"\$\$(.*?)\$\$",
        lambda m: f"\nEquation: {latex_to_speech(m.group(1))}.\n",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"(?<!\\)\$([^\n$]+?)(?<!\\)\$",
        lambda m: f" equation {latex_to_speech(m.group(1))} ",
        text,
    )
    return text


def clean_markdown(text: str) -> str:
    text = strip_code_blocks(text)
    text = replace_liquid_figures(text)
    text = replace_markdown_images(text)
    text = replace_html_images(text)
    text = replace_math(text)
    text = re.sub(r"{%\s*bibliography.*?%}", "", text)
    text = re.sub(r"{%\s*pdf\s+([^%]+)%}", r"PDF attachment: \1.", text)
    text = re.sub(r"{%.*?%}", "", text, flags=re.S)
    text = re.sub(r"\[\^([^\]]+)\]:", r"Footnote \1:", text)
    text = re.sub(r"\[\^([^\]]+)\]", r" footnote \1 ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("**", "").replace("__", "").replace("*", "").replace("_", " ")
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-+*]\s+", "", text, flags=re.M)
    text = re.sub(r"\s+", " ", html.unescape(text))
    return text.strip()


def body_blocks(body: str) -> list[str]:
    blocks = []
    for block in re.split(r"\n\s*\n+", body):
        cleaned = clean_markdown(block)
        if cleaned:
            blocks.extend(chunk_text(cleaned))
    return blocks


def post_narration_blocks(path: Path) -> tuple[dict[str, str], list[str]]:
    front, body = split_front_matter(path.read_text(encoding="utf-8"))
    title = front.get("title", post_slug(path).replace("-", " ").title())
    description = front.get("description", "")
    parts = [title]
    if description:
        parts.append(description)
    parts.extend(body_blocks(body))
    return front, [part for part in parts if part]


def post_narration(path: Path) -> tuple[dict[str, str], str]:
    front, blocks = post_narration_blocks(path)
    return front, "\n\n".join(blocks)


def chunk_text(text: str, limit: int = 4200) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) + 1 <= limit:
            current = f"{current} {sentence}".strip()
            continue
        if current:
            chunks.append(current)
        while len(sentence) > limit:
            chunks.append(sentence[:limit])
            sentence = sentence[limit:]
        current = sentence
    if current:
        chunks.append(current)
    return chunks


def request_elevenlabs(api_key: str, voice_id: str, model_id: str, text: str) -> bytes:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    payload = json.dumps(
        {
            "text": text,
            "model_id": model_id,
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
            "xi-api-key": api_key,
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate_audio(api_key: str, voice_id: str, model_id: str, text: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(".tmp")
    with tmp.open("wb") as handle:
        for index, chunk in enumerate(chunk_text(text), start=1):
            sys.stderr.write(f"  chunk {index}\n")
            handle.write(request_elevenlabs(api_key, voice_id, model_id, chunk))
            time.sleep(0.2)
    tmp.replace(output)


def chunk_digest(voice_id: str, model_id: str, text: str) -> str:
    return hashlib.sha256(f"{voice_id}\0{model_id}\0{text}".encode("utf-8")).hexdigest()


def paragraph_audio_path(digest: str) -> Path:
    return CHUNK_CACHE_DIR / f"{digest}.mp3"


def concat_mp3s(chunk_paths: list[Path], output: Path) -> None:
    """Remux a list of MP3 chunks into a single MP3 with correct duration.

    ElevenLabs returns mp3_44100_128 (CBR 128 kbps), so ``-c copy`` writes a
    single clean container without re-encoding. Naive byte concatenation
    leaves multiple MP3 headers in the file: the browser reads only the
    first one, reports the wrong duration, and seeking jumps to the start.
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as listing:
        for chunk in chunk_paths:
            listing.write(f"file '{chunk.resolve().as_posix()}'\n")
        list_path = Path(listing.name)
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-f", "concat", "-safe", "0",
                "-i", str(list_path),
                "-c", "copy",
                str(output),
            ],
            check=True,
        )
    finally:
        list_path.unlink(missing_ok=True)


def write_post_audio_from_paragraphs(
    api_key: str,
    voice_id: str,
    model_id: str,
    paragraphs: list[str],
    output: Path,
) -> list[str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    CHUNK_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    paragraph_hashes = []
    chunk_paths: list[Path] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        digest = chunk_digest(voice_id, model_id, paragraph)
        paragraph_hashes.append(digest)
        cached = paragraph_audio_path(digest)
        if not cached.exists():
            sys.stderr.write(f"  paragraph {index}\n")
            cached.write_bytes(request_elevenlabs(api_key, voice_id, model_id, paragraph))
            time.sleep(0.2)
        chunk_paths.append(cached)
    concat_mp3s(chunk_paths, output)
    return paragraph_hashes


def http_error_body(exc: urllib.error.HTTPError) -> str:
    return exc.read().decode("utf-8", "ignore")


def is_quota_error(body: str) -> bool:
    return "quota_exceeded" in body or "credits remaining" in body


def skip_reason(args: argparse.Namespace, quota_exhausted: bool) -> str:
    if quota_exhausted:
        return "ElevenLabs quota is exhausted"
    if args.skip_api:
        return "API use is disabled"
    return "no ElevenLabs API key"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", default=os.getenv("ELEVENLABS_API_KEY"))
    parser.add_argument("--voice-id", default=os.getenv("ELEVENLABS_VOICE_ID") or DEFAULT_VOICE_ID)
    parser.add_argument("--model-id", default=os.getenv("ELEVENLABS_MODEL_ID") or DEFAULT_MODEL_ID)
    parser.add_argument("--skip-api", action="store_true")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.stderr.write("ffmpeg is required to concatenate post audio; install it and retry.\n")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = load_json(CACHE_FILE)
    data: dict[str, dict[str, str]] = {}
    changed = False
    quota_exhausted = False

    for path in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        _front, paragraphs = post_narration_blocks(path)
        paragraph_hashes = [chunk_digest(args.voice_id, args.model_id, paragraph) for paragraph in paragraphs]
        digest = hashlib.sha256(
            ("\0".join(paragraph_hashes) + "\0" + CONCAT_VERSION).encode("utf-8")
        ).hexdigest()
        slug = post_slug(path)
        audio_path = OUTPUT_DIR / f"{slug}.mp3"
        cached_post = cache.get(path.as_posix(), {})
        chunk_files_exist = all(paragraph_audio_path(paragraph_hash).exists() for paragraph_hash in paragraph_hashes)
        if cached_post.get("hash") == digest and audio_path.exists():
            data[path.as_posix()] = {
                "audio": "/" + audio_path.as_posix(),
                "hash": digest,
            }
            continue
        if chunk_files_exist:
            sys.stderr.write(f"Rebuilding {audio_path} from paragraph cache.\n")
            concat_mp3s(
                [paragraph_audio_path(paragraph_hash) for paragraph_hash in paragraph_hashes],
                audio_path,
            )
            cache[path.as_posix()] = {
                "hash": digest,
                "audio": "/" + audio_path.as_posix(),
                "paragraph_hashes": paragraph_hashes,
            }
            changed = True
            data[path.as_posix()] = {
                "audio": "/" + audio_path.as_posix(),
                "hash": digest,
            }
            continue
        if args.skip_api or not args.api_key or quota_exhausted:
            sys.stderr.write(f"Skipping {path}: {skip_reason(args, quota_exhausted)} and cached audio is missing/stale.\n")
            if audio_path.exists():
                data[path.as_posix()] = {
                    "audio": "/" + audio_path.as_posix(),
                    "hash": digest,
                }
            continue
        sys.stderr.write(f"Generating {audio_path}\n")
        try:
            paragraph_hashes = write_post_audio_from_paragraphs(
                args.api_key,
                args.voice_id,
                args.model_id,
                paragraphs,
                audio_path,
            )
        except urllib.error.HTTPError as exc:
            body = http_error_body(exc)
            sys.stderr.write(f"ElevenLabs failed for {path}: HTTP {exc.code} {body}\n")
            if is_quota_error(body):
                sys.stderr.write("ElevenLabs quota exhausted; continuing deploy with cached/generated audio only.\n")
                quota_exhausted = True
                audio_path.with_suffix(".tmp").unlink(missing_ok=True)
                continue
            return 1
        cache[path.as_posix()] = {
            "hash": digest,
            "audio": "/" + audio_path.as_posix(),
            "paragraph_hashes": paragraph_hashes,
        }
        changed = True
        data[path.as_posix()] = {
            "audio": "/" + audio_path.as_posix(),
            "hash": digest,
        }

    write_json(DATA_FILE, data)
    if changed:
        write_json(CACHE_FILE, cache)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
