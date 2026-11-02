/* The full chronological list remains available without JavaScript. */
(function () {
  "use strict";
  const browser = document.querySelector("[data-publication-browser]");
  if (!browser) return;

  const yearPanel = document.getElementById("publications-by-year");
  const topicPanel = document.getElementById("publications-by-topic");
  const controls = browser.querySelector("[data-publication-controls]");
  const topicLinks = browser.querySelector("[data-publication-topic-links]");
  const topicSelectGroup = browser.querySelector("[data-publication-topic-select]");
  const topicSelect = topicSelectGroup.querySelector("select");
  const topicNote = browser.querySelector("[data-publication-topic-note]");
  const count = browser.querySelector("[data-publication-result-count]");
  const sections = Array.from(browser.querySelectorAll("[data-publication-topic]"));
  const total = browser.dataset.publicationCount;
  const previousTopicIds = {
    learning: "optimization",
    sensing: "signal-processing",
    arrays: "signal-processing",
    radar: "tracking",
  };
  const topicFragmentIds = Array.from(new Set(Object.keys(previousTopicIds).concat(
    sections.map((section) => section.dataset.publicationTopic)
  ))).sort((a, b) => b.length - a.length);

  function render(view, topic, updateUrl) {
    const selected = sections.find((section) => section.dataset.publicationTopic === topic);
    topic = selected ? topic : "";
    const byTopic = view === "topic";
    yearPanel.hidden = byTopic;
    topicPanel.hidden = !byTopic;
    topicLinks.hidden = !byTopic;
    topicSelectGroup.hidden = !byTopic;
    topicSelect.value = topic;
    topicNote.hidden = !byTopic;
    sections.forEach((section) => {
      section.hidden = byTopic && !!topic && section !== selected;
    });
    browser.querySelectorAll("[data-publication-view]").forEach((link) => {
      if (link.dataset.publicationView === (byTopic ? "topic" : "year")) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    topicLinks.querySelectorAll("[data-publication-filter]").forEach((link) => {
      if (link.dataset.publicationFilter === topic) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    count.textContent = `${byTopic && selected ? selected.dataset.topicCount : total} publications`;
    controls.hidden = false;

    if (updateUrl) {
      const url = new URL(window.location.href);
      if (byTopic) url.searchParams.set("view", "topic");
      else url.searchParams.delete("view");
      if (byTopic && topic) url.searchParams.set("topic", topic);
      else url.searchParams.delete("topic");
      url.hash = "";
      if (url.href !== window.location.href) window.history.pushState({}, "", url);
    }
  }

  function fromUrl() {
    const params = new URLSearchParams(window.location.search);
    let target = null;
    try {
      const fragment = decodeURIComponent(window.location.hash.slice(1));
      target = document.getElementById(fragment);
      if (!target) {
        const previousTopic = topicFragmentIds.find((id) => fragment === `topic-${id}` || fragment.startsWith(`topic-${id}-`));
        if (previousTopic) {
          const suffix = fragment.slice(`topic-${previousTopic}`.length);
          target = document.getElementById(`topic-${previousTopicIds[previousTopic] || previousTopic}${suffix}`);
          if (!target && suffix) {
            target = Array.from(topicPanel.querySelectorAll(".publication-item[id]")).find((item) => item.id.endsWith(suffix)) || null;
          }
        }
      }
    } catch (_) {
      // A malformed fragment must not prevent the publication list from loading.
    }
    const targetTopic = target && target.closest("[data-publication-topic]");
    if (targetTopic) render("topic", targetTopic.dataset.publicationTopic, false);
    else if (target && yearPanel.contains(target)) render("year", "", false);
    else {
      const topic = params.get("topic") || "";
      render(params.get("view"), previousTopicIds[topic] || topic, false);
    }
    if (target) target.scrollIntoView();
  }

  controls.addEventListener("click", (event) => {
    const link = event.target.closest("[data-publication-view]");
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    render(link.dataset.publicationView, "", true);
  });
  topicLinks.addEventListener("click", (event) => {
    const link = event.target.closest("[data-publication-filter]");
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    render("topic", link.dataset.publicationFilter, true);
  });
  topicSelect.addEventListener("change", () => render("topic", topicSelect.value, true));
  window.addEventListener("popstate", fromUrl);
  window.addEventListener("hashchange", fromUrl);
  fromUrl();
})();
