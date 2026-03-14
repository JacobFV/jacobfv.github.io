---
layout: page
permalink: /papers/
title: papers
description: Papers and writings in reverse chronological order.
years: [2022, 2021, 2020, 2018, 2017]
nav: false
---

<div class="publications">

{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
