---
layout: page
permalink: /papers/
title: papers
description: papers by categories in chronological order.
years: [2022, 2021, 2020, 2018, 2017, 2016]
nav: false
---
<!-- _pages/publications.md -->
<div class="publications">

{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>