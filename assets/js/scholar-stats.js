/* Refresh homepage Scholar statistics from the snapshot written by GitHub Actions. */
(function () {
  "use strict";
  // Always load the shared snapshot from the site root, including nested pages
  // such as /publications/ where a document-relative URL would be incorrect.
  var snapshotUrl = new URL("/assets/json/scholar.json", window.location.origin);
  fetch(snapshotUrl, { cache: "no-store" })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      if (!data || !data.profile) return;
      var profile = data.profile;
      var format = function (value) { return Number(value).toLocaleString("en-US"); };
      var normalizeTitle = function (value) {
        return String(value || "").toLowerCase().replace(/\s+/g, " ").replace(/[\u2010-\u2015]/g, "-").trim();
      };
      var papersByTitle = {};
      Object.keys(data.papers || {}).forEach(function (key) {
        var paper = data.papers[key] || {};
        papersByTitle[normalizeTitle(paper.title)] = paper.citations;
      });
      document.querySelectorAll("[data-scholar-citations]").forEach(function (element) { element.textContent = format(profile.citations); });
      document.querySelectorAll("[data-scholar-summary]").forEach(function (element) { element.textContent = "Google Scholar Citations · h-index " + profile.hindex; });
      document.querySelectorAll("[data-scholar-paper]").forEach(function (element) {
        var citations = papersByTitle[normalizeTitle(element.dataset.scholarPaper)];
        if (Number.isFinite(Number(citations))) {
          element.textContent = "Google Scholar · " + format(citations) + " " + (element.dataset.scholarUnit || "citations");
        }
      });
    })
    .catch(function () { /* Keep the server-rendered fallback when unavailable. */ });
})();
