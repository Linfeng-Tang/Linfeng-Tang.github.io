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
        我现为武汉大学博士后研究人员，合作导师为马佳义教授。研究方向主要包括多模态图像融合、视频融合、图像恢复，以及面向真实任务的语义感知建模。
      button:
        text: 查看论文
        url: /zh/publication/
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
      title: 研究亮点
      text: |-
        <div class="hb-highlight-grid">
          <div class="hb-highlight-card">
            <span class="hb-kicker">方向</span>
            <h3>可控图像融合</h3>
            <p>探索语言视觉先验与多模态生成结合的可控融合框架。</p>
          </div>
          <div class="hb-highlight-card">
            <span class="hb-kicker">影响力</span>
            <h3>6,878 次引用</h3>
            <p>多篇论文入选 ESI 热点论文、高被引论文，并获得最佳论文奖。</p>
          </div>
          <div class="hb-highlight-card">
            <span class="hb-kicker">目标</span>
            <h3>任务驱动感知</h3>
            <p>让图像融合真正服务于检测、理解与复杂场景下的稳健感知。</p>
          </div>
        </div>
    design:
      columns: '1'

  - block: collection
    id: papers
    content:
      title: 代表论文
      text: 聚焦 TPAMI、IJCV、NeurIPS、CVPR 与 Information Fusion 的代表性工作。
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
      title: 最新动态
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
