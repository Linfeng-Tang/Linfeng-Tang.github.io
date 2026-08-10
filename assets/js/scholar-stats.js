/* Refresh homepage Scholar statistics from the snapshot written by GitHub Actions. */
(function () {
  "use strict";
  var snapshotUrl = new URL("assets/json/scholar.json", document.baseURI);
  fetch(snapshotUrl, { cache: "no-store" })
    .then(function (response) { return response.ok ? response.json() : null; })
    .then(function (data) {
      if (!data || !data.profile) return;
      var profile = data.profile;
      var format = function (value) { return Number(value).toLocaleString("en-US"); };
      document.querySelectorAll("[data-scholar-citations]").forEach(function (element) { element.textContent = format(profile.citations); });
      document.querySelectorAll("[data-scholar-summary]").forEach(function (element) { element.textContent = "Google Scholar citations · h-index " + profile.hindex; });
    })
    .catch(function () { /* Keep the server-rendered fallback when unavailable. */ });
})();
