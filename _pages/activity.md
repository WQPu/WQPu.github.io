---
layout: page
permalink: /activity/
title: Activity
nav: true
nav_order: 3
description: Talks and organization.
---

<div class="activities">
  {% assign activities = site.data.activities.organization | concat: site.data.activities.talks | sort: 'datetime' | reverse %}
  <ol class="activities__list" aria-label="Activities in reverse chronological order">
    {% for activity in activities %}
      <li class="activities__entry">
        <time datetime="{{ activity.datetime }}">{{ activity.date }}</time>
        · <span class="activities__kind">{% if activity.role %}Organization{% else %}Talk{% endif %}</span>
        · <strong>{{ activity.title | escape }}</strong>
        — {% if activity.role %}{{ activity.role | escape }}{% if activity.topic %}: {{ activity.topic | escape }}{% endif %}{% else %}{{ activity.venue | escape }}{% endif %}{% if activity.location %}, {{ activity.location | escape }}{% endif %}
      </li>
    {% endfor %}
  </ol>
</div>
