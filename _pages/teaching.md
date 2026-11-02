---
layout: page
permalink: /teaching/
title: Teaching
nav: true
nav_order: 2
description: Courses, lecture slides, and numerical examples.
---

<div class="teaching-list">
  {% for course in site.data.teaching %}
    <section class="teaching-course">
      <header class="teaching-course__header">
        <p class="teaching-course__code">{{ course.code }}</p>
        <h2>{{ course.title }}</h2>
        <p class="teaching-course__meta">{{ course.institution }} · {{ course.term }}</p>
        <p>{{ course.description }}</p>
      </header>

      <div class="teaching-course__materials">
        <details class="teaching-materials">
          <summary>Slides <span class="teaching-materials__count">{{ course.slides.size }} lectures</span></summary>
          <ul class="teaching-links">
            {% for slide in course.slides %}
              <li><a href="{{ slide.url | relative_url }}" target="_blank" rel="noopener">{{ slide.label }} <span aria-hidden="true">↗</span></a></li>
            {% endfor %}
          </ul>
        </details>

        <details class="teaching-materials">
          <summary>Examples <span class="teaching-materials__count">{{ course.examples.size }} examples</span></summary>
          <ul class="teaching-links">
            {% for example in course.examples %}
              <li><a href="{{ example.url | relative_url }}" target="_blank" rel="noopener">{{ example.title }} <span aria-hidden="true">↗</span></a></li>
            {% endfor %}
          </ul>
        </details>
      </div>
    </section>
  {% endfor %}
</div>
