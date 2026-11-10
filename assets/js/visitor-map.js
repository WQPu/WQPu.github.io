(() => {
  const section = document.querySelector("[data-visitor-map]");
  if (!section) return;

  const { widgetId, siteUrl } = section.dataset;
  const status = section.querySelector("[data-visitor-map-status]");
  const embed = section.querySelector("[data-visitor-map-embed]");
  const statistics = section.querySelector(".visitor-map__statistics");

  // Keep previews out of the real statistics.
  if (!widgetId || !siteUrl || window.location.protocol !== "https:" || window.location.origin !== new URL(siteUrl).origin) {
    status.textContent = "Visitor map preview. Visits here are not counted.";
    return;
  }

  const showUnavailable = () => {
    status.textContent = "Live visitor locations are temporarily unavailable.";
  };

  const observer = new MutationObserver(() => {
    const widget = embed.querySelector("#mapmyvisitors-widget");
    const map = widget?.querySelector(".mapmyvisitors-map");

    // The provider inserts an empty map shell before drawing the visitor map.
    if (!map || (!map.style.backgroundImage && !map.querySelector("svg, canvas"))) return;

    observer.disconnect();
    clearTimeout(timeout);
    if (statistics) widget.href = statistics.href;
    widget.target = "_blank";
    widget.rel = "noopener noreferrer";
    widget.setAttribute("aria-label", "Visitor map and statistics (opens in a new tab)");
    section.dataset.state = "ready";
    status.textContent = "";
  });

  status.textContent = "Loading visitor locations…";
  const timeout = setTimeout(showUnavailable, 10000);
  observer.observe(embed, { childList: true, subtree: true, attributes: true, attributeFilter: ["style"] });

  const script = document.createElement("script");
  script.id = "mapmyvisitors";
  script.async = true;
  const source = new URL("https://mapmyvisitors.com/map.js");
  source.search = new URLSearchParams({ d: widgetId, co: "fcfcfb", cl: "d9e0e3", ct: "61707b", cmo: "bc4242", cmn: "d52b2b", w: "a" });
  script.src = source.href;
  script.addEventListener("error", () => {
    clearTimeout(timeout);
    observer.disconnect();
    showUnavailable();
  });
  embed.append(script);
})();
