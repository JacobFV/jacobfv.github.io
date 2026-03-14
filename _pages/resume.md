---
layout: page
permalink: /resume/
title: resume
nav: false
order: 10
---

<p style="margin-bottom: 1rem;">
  <a href="{{ '/assets/pdf/Resume.pdf' | relative_url }}" target="_blank" class="btn btn-sm btn-outline-primary">
    <i class="fas fa-download"></i> Download PDF
  </a>
  <span style="font-size: 0.85rem; color: var(--global-text-color-light); margin-left: 0.5rem;">
    Auto-generated from site data
  </span>
</p>

{% pdf /assets/pdf/Resume.pdf %}
