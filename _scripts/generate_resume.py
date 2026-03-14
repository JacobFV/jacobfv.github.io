#!/usr/bin/env python3
"""
Generate a PDF resume from _data/cv.yml and _config.yml.

Uses weasyprint to convert an HTML template to PDF.
Run: python3 _scripts/generate_resume.py
Output: assets/pdf/Resume.pdf
"""

import yaml
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def escape_html(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_markdown_links(text):
    """Convert simple markdown links [text](url) to HTML anchors."""
    import re
    text = str(text)
    text = re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2">\1</a>',
        text
    )
    return text


def render_time_table(entry, max_items=None):
    """Render a time_table CV section to HTML."""
    html = ""
    contents = entry.get("contents", [])
    if max_items:
        contents = contents[:max_items]

    for item in contents:
        html += '<div class="cv-item">\n'
        html += '  <div class="cv-item-header">\n'
        if item.get("year"):
            html += f'    <span class="cv-date">{escape_html(item["year"])}</span>\n'
        html += '    <div class="cv-item-title">\n'
        if item.get("title"):
            html += f'      <strong>{render_markdown_links(item["title"])}</strong>\n'
        if item.get("institution"):
            html += f'      <span class="cv-institution">{render_markdown_links(item["institution"])}</span>\n'
        html += '    </div>\n'
        html += '  </div>\n'

        if item.get("description"):
            html += '  <ul class="cv-description">\n'
            for desc in item["description"]:
                html += f'    <li>{render_markdown_links(desc)}</li>\n'
            html += '  </ul>\n'

        html += '</div>\n'

    return html


def render_nested_list(entry):
    """Render a nested_list CV section to HTML."""
    html = ""
    for item in entry.get("contents", []):
        html += f'<div class="cv-skill-group">\n'
        html += f'  <strong>{escape_html(item.get("title", ""))}</strong>: '
        items = item.get("items", [])
        html += ", ".join(escape_html(i) for i in items)
        html += '\n</div>\n'
    return html


def render_list(entry):
    """Render a list CV section to HTML."""
    html = '<ul class="cv-list">\n'
    for item in entry.get("contents", []):
        html += f'  <li>{render_markdown_links(item)}</li>\n'
    html += '</ul>\n'
    return html


def generate_resume_html(cv_data, config):
    """Generate the full resume HTML document."""
    name = f'{config.get("first_name", "")} {config.get("middle_name", "")} {config.get("last_name", "")}'.strip()
    email = config.get("email", "")
    url = config.get("url", "")
    github = config.get("github_username", "")
    linkedin = config.get("linkedin_username", "")
    twitter = config.get("twitter_username", "")

    # Build sections
    sections_html = ""
    for entry in cv_data:
        title = entry.get("title", "")
        entry_type = entry.get("type", "")

        sections_html += f'<section class="cv-section">\n'
        sections_html += f'  <h2>{escape_html(title)}</h2>\n'

        if entry_type == "time_table":
            sections_html += render_time_table(entry)
        elif entry_type == "nested_list":
            sections_html += render_nested_list(entry)
        elif entry_type == "list":
            sections_html += render_list(entry)
        else:
            for item in entry.get("contents", []):
                sections_html += f'<p>{render_markdown_links(item)}</p>\n'

        sections_html += '</section>\n'

    contact_parts = []
    if email:
        contact_parts.append(f'<a href="mailto:{email}">{email}</a>')
    if url:
        contact_parts.append(f'<a href="{url}">{url}</a>')
    if github:
        contact_parts.append(f'<a href="https://github.com/{github}">github.com/{github}</a>')
    if linkedin:
        contact_parts.append(f'<a href="https://linkedin.com/in/{linkedin}">linkedin.com/in/{linkedin}</a>')
    contact_line = " &middot; ".join(contact_parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape_html(name)} - Resume</title>
  <style>
    @page {{
      size: letter;
      margin: 0.6in 0.7in;
    }}
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    body {{
      font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
      font-size: 9.5pt;
      line-height: 1.4;
      color: #1a1a1a;
    }}
    a {{
      color: #1a1a1a;
      text-decoration: none;
    }}
    header {{
      text-align: center;
      margin-bottom: 12pt;
      padding-bottom: 8pt;
      border-bottom: 1px solid #ccc;
    }}
    header h1 {{
      font-size: 18pt;
      font-weight: 700;
      margin-bottom: 4pt;
      letter-spacing: 0.5pt;
    }}
    header .contact {{
      font-size: 8.5pt;
      color: #555;
    }}
    .cv-section {{
      margin-bottom: 10pt;
    }}
    .cv-section h2 {{
      font-size: 11pt;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5pt;
      border-bottom: 1px solid #ddd;
      padding-bottom: 2pt;
      margin-bottom: 6pt;
      color: #333;
    }}
    .cv-item {{
      margin-bottom: 6pt;
    }}
    .cv-item-header {{
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}
    .cv-date {{
      font-size: 8.5pt;
      color: #666;
      white-space: nowrap;
      min-width: 130pt;
    }}
    .cv-item-title {{
      flex: 1;
    }}
    .cv-institution {{
      color: #555;
      margin-left: 4pt;
    }}
    .cv-description {{
      margin-left: 140pt;
      margin-top: 2pt;
      padding-left: 12pt;
      font-size: 9pt;
      color: #333;
    }}
    .cv-description li {{
      margin-bottom: 1pt;
    }}
    .cv-skill-group {{
      margin-bottom: 3pt;
      font-size: 9pt;
    }}
    .cv-list {{
      padding-left: 16pt;
      font-size: 9pt;
    }}
    .cv-list li {{
      margin-bottom: 2pt;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{escape_html(name)}</h1>
    <div class="contact">{contact_line}</div>
  </header>
  {sections_html}
</body>
</html>"""

    return html


def main():
    cv_path = PROJECT_ROOT / "_data" / "cv.yml"
    config_path = PROJECT_ROOT / "_config.yml"
    output_path = PROJECT_ROOT / "assets" / "pdf" / "Resume.pdf"

    if not cv_path.exists():
        print(f"Error: {cv_path} not found", file=sys.stderr)
        sys.exit(1)
    if not config_path.exists():
        print(f"Error: {config_path} not found", file=sys.stderr)
        sys.exit(1)

    cv_data = load_yaml(cv_path)
    config = load_yaml(config_path)

    html = generate_resume_html(cv_data, config)

    # Write HTML for debugging
    html_output = PROJECT_ROOT / "_scripts" / "resume_output.html"
    with open(html_output, "w") as f:
        f.write(html)
    print(f"HTML written to {html_output}")

    # Try to generate PDF with weasyprint
    try:
        from weasyprint import HTML
        HTML(string=html).write_pdf(str(output_path))
        print(f"PDF written to {output_path}")
    except ImportError:
        print("weasyprint not installed. Install with: pip install weasyprint")
        print("HTML resume generated — convert manually or install weasyprint for PDF.")
        # Fallback: try wkhtmltopdf
        import subprocess
        try:
            subprocess.run(
                ["wkhtmltopdf", "--page-size", "Letter", "--margin-top", "15mm",
                 "--margin-bottom", "15mm", "--margin-left", "18mm", "--margin-right", "18mm",
                 str(html_output), str(output_path)],
                check=True, capture_output=True
            )
            print(f"PDF written to {output_path} (via wkhtmltopdf)")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("wkhtmltopdf also not available. PDF not generated.")
            sys.exit(1)


if __name__ == "__main__":
    main()
