---
title: ''
date: 2026-04-20
type: landing
design:
  spacing: '5rem'
sections:
  - block: resume-biography-3
    content:
      username: admin
      text: |-
        I am a Postdoctoral Researcher at Wuhan University working with Prof. Jiayi Ma. My research focuses on multi-modal image fusion, video fusion, restoration, and semantics-aware perception for real-world vision systems.
      button:
        text: View Publications
        url: /publication/
      headings:
        about: ''
        education: ''
        interests: ''
    design:
      background:
        gradient_mesh:
          enable: true
      name:
        size: lg
      avatar:
        size: large
        shape: rounded

  - block: markdown
    id: highlights
    content:
      title: Research Highlights
      text: |-
        <div class="hb-highlight-grid">
          <div class="hb-highlight-card">
            <span class="hb-kicker">Focus</span>
            <h3>Controllable Fusion</h3>
            <p>Bridging language-vision priors and multi-modal generation for controllable fusion systems.</p>
          </div>
          <div class="hb-highlight-card">
            <span class="hb-kicker">Impact</span>
            <h3>6,878 Citations</h3>
            <p>Several works recognized as ESI Hot Papers, Highly Cited Papers, and best paper award winners.</p>
          </div>
          <div class="hb-highlight-card">
            <span class="hb-kicker">Direction</span>
            <h3>Task-driven Perception</h3>
            <p>Building fusion models that support detection, understanding, and robust downstream perception.</p>
          </div>
        </div>
    design:
      columns: '1'

  - block: collection
    id: papers
    content:
      title: Featured Publications
      text: Representative papers across TPAMI, IJCV, NeurIPS, CVPR, and Information Fusion.
      filters:
        folders:
          - publication
        featured_only: true
    design:
      view: article-grid
      columns: 2

  - block: collection
    id: news
    content:
      title: Recent News
      page_type: post
      count: 5
      filters:
        author: ''
      order: desc
    design:
      view: card
      spacing:
        padding: [0, 0, 0, 0]
---
