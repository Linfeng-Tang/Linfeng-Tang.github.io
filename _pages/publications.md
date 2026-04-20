---
layout: page
permalink: /publications/
title: Publications
description: Selected papers, representative projects, and a full reverse-chronological publication archive.
nav: true
nav_order: 2
page_class: publication-page
---
<section class="page-hero-band">
  <div class="page-hero-copy">
    <span class="eyebrow">Research Output</span>
    <p>
      My research centers on multi-modal image fusion, restoration, and perception-oriented visual understanding. This page highlights representative work while keeping the full publication list easy to scan and filter.
    </p>
  </div>
  <div class="page-metrics">
    <div class="page-metric">
      <span class="page-metric-value">15+</span>
      <span class="page-metric-label">high-impact papers</span>
    </div>
    <div class="page-metric">
      <span class="page-metric-value">6,878</span>
      <span class="page-metric-label">Google Scholar citations</span>
    </div>
    <div class="page-metric">
      <span class="page-metric-value">2</span>
      <span class="page-metric-label">best paper awards</span>
    </div>
  </div>
</section>

<section class="page-panel publication-intro">
  <div class="panel-head">
    <div>
      <span class="eyebrow">Archive</span>
      <h2>Browse by topic, venue, or title</h2>
    </div>
    <p>
      The full list below is ordered in reverse chronological order. Citation counts shown in highlighted notes were refreshed from my personal Google Scholar profile on April 20, 2026. The live profile remains available on
      <a href="https://scholar.google.com/citations?user=PyRqpAsAAAAJ&hl=en">Google Scholar</a>.
    </p>
  </div>

  <div class="publication-toolbar">
    {% include bib_search.liquid %}
  </div>

  <div class="publications publication-collection">
    {% bibliography %}
  </div>
</section>
