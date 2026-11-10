(() => {
  const section = document.querySelector("[data-visitor-map]");
  if (!section) return;

  const { widgetId, siteUrl } = section.dataset;
  const status = section.querySelector("[data-visitor-map-status]");
  const map = section.querySelector("[data-visitor-map-image]");

  // The image request counts a visit. Keep previews out of the real statistics.
  if (!widgetId || !siteUrl || window.location.protocol !== "https:" || window.location.origin !== new URL(siteUrl).origin) {
    status.textContent = "Visitor map preview. Visits here are not counted.";
    return;
  }

  const showUnavailable = () => {
    status.textContent = "Visitor map is temporarily unavailable.";
  };

  status.textContent = "Loading visitor map…";
  const timeout = setTimeout(showUnavailable, 10000);

  map.addEventListener("load", () => {
    clearTimeout(timeout);
    if (map.naturalWidth <= 1 || map.naturalHeight <= 1) {
      showUnavailable();
      return;
    }
    status.textContent = "";
    map.hidden = false;
  });
  map.addEventListener("error", () => {
    clearTimeout(timeout);
    showUnavailable();
  });

  // Use the provider's image embed so rendering does not depend on widget markup.
  const source = new URL("https://mapmyvisitors.com/map.png");
  source.searchParams.set("d", widgetId);
  map.src = source.href;
})();
