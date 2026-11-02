(() => {
  const section = document.querySelector("[data-visitor-map]");
  if (!section) return;

  const widgetId = section.dataset.widgetId;
  const status = section.querySelector("[data-visitor-map-status]");
  const embed = section.querySelector("[data-visitor-map-embed]");
  const hostname = window.location.hostname.toLowerCase();
  const siteHostname = new URL(section.dataset.siteUrl).hostname.toLowerCase();

  // Never send local previews or test visits to the real analytics project.
  if (!widgetId || /^(localhost|127\.0\.0\.1|\[::1\])$/.test(hostname) || hostname !== siteHostname) {
    status.textContent = "Visitor map preview";
    return;
  }

  status.textContent = "Loading visitor map…";
  section.dataset.state = "loading";

  const observer = new MutationObserver(() => {
    const widget = embed.querySelector("#mapmyvisitors-widget");
    if (!widget) return;

    // The provider defaults to navigating the current page when its map is clicked.
    widget.target = "_blank";
    widget.rel = "noopener noreferrer";
    widget.setAttribute("aria-label", "View visitor map and statistics on MapMyVisitors (opens in a new tab)");

    const statisticsUrl = new URL(widget.href, window.location.href);
    const hasStatistics = statisticsUrl.hostname === "mapmyvisitors.com" && statisticsUrl.pathname.startsWith("/web/");
    const pageviews = widget.querySelector(".mapmyvisitors-visitors")?.textContent || "";
    // The map element exists while the provider is still showing "Loading data…".
    if (!hasStatistics || !/\d/.test(pageviews) || !widget.querySelector(".mapmyvisitors-map")) return;

    statisticsUrl.protocol = "https:";
    widget.href = statisticsUrl.href;
    section.dataset.state = "ready";
    clearTimeout(timeout);
    observer.disconnect();
  });
  observer.observe(embed, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["href"] });

  const showUnavailable = () => {
    if (section.dataset.state === "ready") return;
    section.dataset.state = "unavailable";
    status.textContent = "Visitor map is temporarily unavailable.";
  };
  const timeout = setTimeout(showUnavailable, 15000);

  const script = document.createElement("script");
  script.id = "mapmyvisitors";
  script.async = true;
  const source = new URL("https://mapmyvisitors.com/map.js");
  source.search = new URLSearchParams({ d: widgetId, co: "fcfcfb", cl: "d9e0e3", ct: "61707b", w: "a" });
  script.src = source.href;
  script.addEventListener("error", () => {
    clearTimeout(timeout);
    observer.disconnect();
    showUnavailable();
  });
  embed.append(script);
})();
