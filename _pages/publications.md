---
layout: page
permalink: /publications/
title: Publications
description: Publications in reverse chronological order.
nav: true
nav_order: 2
---
<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->

{% include bib_search.liquid %}

<p class="publication-note">
  This list is kept in reverse chronological order. Citation counts are synchronized daily from my personal Google Scholar profile, while the live profile total remains available on
  <a href="https://scholar.google.com/citations?user=PyRqpAsAAAAJ&hl=zh-CN">Google Scholar</a>.
</p>

<div class="publications">

{% bibliography %}

</div>

<script src="{{ '/assets/js/scholar-stats.js' | relative_url }}"></script>
