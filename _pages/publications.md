---
layout: page
permalink: /publications/
title: Publications
description: Browse publications by year or research topic.
nav: true
nav_order: 1
---

<p class="publication-note">For the most up-to-date record, see <a href="https://scholar.google.com.hk/citations?user=JpRVZaIAAAAJ&amp;sortby=pubdate" target="_blank" rel="noopener">Google Scholar</a>.</p>
<p class="publication-legend"><sup class="publication-item__corresponding">*</sup> Corresponding author, where information is available.</p>

{% assign publication_count = 0 %}
{% for year in site.data.publications %}
  {% for group in year.groups %}
    {% assign publication_count = publication_count | plus: group.items.size %}
  {% endfor %}
{% endfor %}

<div class="publication-browser" data-publication-browser data-publication-count="{{ publication_count }}">
  <div class="publication-controls" data-publication-controls hidden>
    <nav class="publication-view-switch" aria-label="Publication view">
      <a href="{{ '/publications/' | relative_url }}" data-publication-view="year" aria-current="page">By Year</a>
      <a href="{{ '/publications/' | relative_url }}?view=topic" data-publication-view="topic">By Topic</a>
    </nav>
    <p class="publication-result-count" aria-live="polite" data-publication-result-count>{{ publication_count }} publications</p>
  </div>

  <nav class="publication-topic-links" aria-label="Research topics" data-publication-topic-links hidden>
    <a href="{{ '/publications/' | relative_url }}?view=topic" data-publication-filter="" aria-current="page">All topics</a>
    {% for topic in site.data.publication_topics %}
      <a href="{{ '/publications/' | relative_url }}?view=topic&amp;topic={{ topic.id }}" data-publication-filter="{{ topic.id }}">{{ topic.name | escape }} <span>{{ topic.count }}</span></a>
    {% endfor %}
  </nav>
  <div class="publication-topic-select" data-publication-topic-select hidden>
    <label for="publication-topic-select">Research topic</label>
    <select id="publication-topic-select">
      <option value="">All topics</option>
      {% for topic in site.data.publication_topics %}
        <option value="{{ topic.id }}">{{ topic.name | escape }} ({{ topic.count }})</option>
      {% endfor %}
    </select>
  </div>
  <p class="publication-topic-note" data-publication-topic-note hidden>Each publication is listed under one main topic.</p>

  <div class="publication-index" id="publications-by-year">
  {% for year in site.data.publications %}
    <section class="publication-year">
      <h2>{{ year.year }}</h2>
      {% for group in year.groups %}
        <div class="publication-group">
          <h3>{{ group.name }}</h3>
          <ol class="publication-list">
            {% for paper in group.items %}
              {% include publication_item.liquid paper=paper %}
            {% endfor %}
          </ol>
        </div>
      {% endfor %}
    </section>
  {% endfor %}
  </div>

  <div class="publication-index" id="publications-by-topic" hidden>
    {% for topic in site.data.publication_topics %}
      <section class="publication-topic" id="topic-{{ topic.id }}" data-publication-topic="{{ topic.id }}" data-topic-count="{{ topic.count }}">
        <h2>{{ topic.name | escape }} <span>{{ topic.count }}</span></h2>
        <p class="publication-topic__description">{{ topic.description | escape }}</p>
        {% assign topic_prefix = 'topic-' | append: topic.id | append: '-' %}
        {% for year in topic.years %}
          <div class="publication-topic__year">
            <h3>{{ year.year }}</h3>
            <ol class="publication-list">
              {% for group in year.groups %}
                {% for paper in group.items %}
                  {% include publication_item.liquid paper=paper id_prefix=topic_prefix %}
                {% endfor %}
              {% endfor %}
            </ol>
          </div>
        {% endfor %}
      </section>
    {% endfor %}
  </div>
</div>

<script src="{{ '/assets/js/publications.js' | relative_url }}" defer></script>
