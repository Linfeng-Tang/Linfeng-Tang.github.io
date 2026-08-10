const list = document.querySelector("#publication-list");
const status = document.querySelector("#sync-status");
const search = document.querySelector("#pub-search");
const clear = document.querySelector("#clear-search");
const empty = document.querySelector("#publication-empty");

const escapeHTML = (value) => value.replace(/[&<>"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[character]));

function paperTitle(citation) {
  const match = citation.match(/"(.+?)"/);
  return match ? match[1] : citation;
}

function cleanCitation(citation) {
  return citation.replace(/\s*\(Code\)/gi, "").replace(/\s+\./g, ".").trim();
}

function formatTime(iso) {
  if (!iso) return "Source connected";
  return `Updated ${new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(iso))}`;
}

function linksFor(paper) {
  const sourceLinks = (paper.links || []).map((link) => ({ label: link.label, url: link.url }));
  const links = [
    paper.paper && { label: "Paper", url: paper.paper },
    paper.code && { label: "Code", url: paper.code },
    ...sourceLinks,
  ].filter(Boolean);
  const unique = links.filter((link, index, all) => link.url && all.findIndex((item) => item.url === link.url) === index);
  if (paper.citations > 100) unique.push({ label: `${paper.citations.toLocaleString()} citations`, url: "https://scholar.google.com/citations?user=73trMQkAAAAJ&hl=en", citation: true });
  return unique.map((link) => `<a class="badge${link.citation ? " citations" : ""}" href="${escapeHTML(link.url)}" target="_blank" rel="noreferrer">${escapeHTML(link.label)}</a>`).join("");
}

function render(publications, query = "") {
  const needle = query.trim().toLowerCase();
  const filtered = publications.filter((paper) => `${paper.year} ${paper.citation}`.toLowerCase().includes(needle));
  const groups = filtered.reduce((result, paper) => {
    (result[paper.year] ||= []).push(paper);
    return result;
  }, {});
  let serial = 0;
  list.innerHTML = Object.entries(groups).sort(([a], [b]) => Number(b) - Number(a)).map(([year, papers]) => `
    <section class="year-group" aria-label="Publications in ${year}">
      <h3 class="year-heading">Year ${year}<span class="year-count">${papers.length} publication${papers.length === 1 ? "" : "s"}</span></h3>
      <ol class="paper-list">
        ${papers.map((paper) => `<li class="paper" value="${++serial}"><p class="paper-citation">${escapeHTML(cleanCitation(paper.citation))}</p><div class="paper-links">${linksFor(paper)}</div></li>`).join("")}
      </ol>
    </section>`).join("");
  empty.hidden = filtered.length > 0;
}

async function loadPublications() {
  try {
    const response = await fetch("data/publications.json", { cache: "no-store" });
    if (!response.ok) throw new Error("Publication data is unavailable");
    const data = await response.json();
    render(data.publications);
    status.textContent = `${formatTime(data.syncedAt)} · ${data.publications.length} entries`;
    search.addEventListener("input", () => render(data.publications, search.value));
    clear.addEventListener("click", () => { search.value = ""; search.focus(); render(data.publications); });
  } catch (error) {
    status.textContent = "Publication data is temporarily unavailable";
    list.innerHTML = "<p class=\"empty-state\">Please visit the original publication page while this list refreshes.</p>";
  }
}

document.querySelector("#current-year").textContent = new Date().getFullYear();
loadPublications();
