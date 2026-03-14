---
layout: page
permalink: /repos/
title: repos
description: Open source work and contributions.
nav: false
nav_order: 4
---

<div class="repos-overview">
  <div class="repos-stats">
    <a href="https://github.com/JacobFV">
      <img class="repo-img-light" src="https://github-readme-stats.vercel.app/api?username=JacobFV&show_icons=true&theme=default&hide_border=true&count_private=true" alt="GitHub Stats">
      <img class="repo-img-dark" src="https://github-readme-stats.vercel.app/api?username=JacobFV&show_icons=true&theme=dark&hide_border=true&count_private=true" alt="GitHub Stats">
    </a>
    <a href="https://github.com/JacobFV">
      <img class="repo-img-light" src="https://github-readme-stats.vercel.app/api/top-langs/?username=JacobFV&layout=compact&theme=default&hide_border=true&langs_count=8" alt="Top Languages">
      <img class="repo-img-dark" src="https://github-readme-stats.vercel.app/api/top-langs/?username=JacobFV&layout=compact&theme=dark&hide_border=true&langs_count=8" alt="Top Languages">
    </a>
  </div>

  <div class="repos-graph">
    <a href="https://github.com/JacobFV">
      <img class="repo-img-light" src="https://github-readme-activity-graph.vercel.app/graph?username=JacobFV&theme=github-light&hide_border=true&area=true" alt="Contribution Graph" style="width: 100%; border-radius: 6px;">
      <img class="repo-img-dark" src="https://github-readme-activity-graph.vercel.app/graph?username=JacobFV&theme=github-dark&hide_border=true&area=true" alt="Contribution Graph" style="width: 100%; border-radius: 6px;">
    </a>
  </div>
</div>

## Pinned Repositories

{% if site.data.repositories.github_repos %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.html repository=repo %}
  {% endfor %}
</div>
{% endif %}

---

## Organizations

{% if site.data.repositories.github_users %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for user in site.data.repositories.github_users %}
    {% include repository/repo_user.html username=user %}
  {% endfor %}
</div>
{% endif %}
