let articles = [];

// Chargement des articles (simulés pour test)
async function loadArticles() {
  // Pour le hackathon, on simule quelques articles
  articles = [
    {
      title: "Effet de la microgravité sur les plantes",
      author: "Alice Dupont",
      theme: "Plantes",
      year: "2021",
      summary:
        "Résumé des expériences sur la croissance des plantes en microgravité.",
      impact: "Les plantes poussent 20% moins vite en microgravité.",
      link_data: "https://osdr.nasa.gov/experiment1",
    },
    {
      title: "Sommeil et rythme circadien dans l’espace",
      author: "Bob Martin",
      theme: "Humain",
      year: "2020",
      summary:
        "Étude sur le sommeil des astronautes et les impacts sur leur santé.",
      impact:
        "Les astronautes présentent une perturbation moyenne de 2 heures dans le cycle sommeil-éveil.",
      link_data: "https://osdr.nasa.gov/experiment2",
    },
    {
      title: "Microorganismes et environnement spatial",
      author: "Clara Nguyen",
      theme: "Microbes",
      year: "2019",
      summary: "Analyse de la survie des microorganismes en microgravité.",
      impact:
        "Les bactéries survivent plus longtemps en microgravité et développent certaines résistances.",
      link_data: "https://osdr.nasa.gov/experiment3",
    },
  ];

  populateFilters();
  displayArticles(articles);
}

// Remplissage dynamique des filtres
function populateFilters() {
  const themes = [...new Set(articles.map((a) => a.theme))];
  const authors = [...new Set(articles.map((a) => a.author))];
  const years = [...new Set(articles.map((a) => a.year))];

  const themeSelect = document.getElementById("filterTheme");
  const authorSelect = document.getElementById("filterAuthor");
  const yearSelect = document.getElementById("filterYear");

  themes.forEach((t) => {
    let opt = document.createElement("option");
    opt.value = t;
    opt.textContent = t;
    themeSelect.appendChild(opt);
  });

  authors.forEach((a) => {
    let opt = document.createElement("option");
    opt.value = a;
    opt.textContent = a;
    authorSelect.appendChild(opt);
  });

  years.forEach((y) => {
    let opt = document.createElement("option");
    opt.value = y;
    opt.textContent = y;
    yearSelect.appendChild(opt);
  });
}

// Affichage des articles filtrés
function displayArticles(list) {
  const container = document.getElementById("articles");
  container.innerHTML = "";
  list.forEach((article) => {
    const card = document.createElement("div");
    card.className = "article";
    card.innerHTML = `
      <h2>${article.title}</h2>
      <p><strong>Auteur:</strong> ${article.author} | <strong>Thème:</strong> ${article.theme} | <strong>Année:</strong> ${article.year}</p>
      <p><strong>Résumé:</strong> ${article.summary}</p>
      <p><strong>Impact clé:</strong> ${article.impact}</p>
      <button class="data-link" onclick="window.open('${article.link_data}', '_blank')">Voir données NASA</button>
    `;
    container.appendChild(card);
  });
}

// Application des filtres et tri
function applyFilters() {
  const keyword = document.getElementById("filterKeyword").value.toLowerCase();
  const theme = document.getElementById("filterTheme").value;
  const author = document.getElementById("filterAuthor").value;
  const year = document.getElementById("filterYear").value;
  const sortValue = document.getElementById("sortArticles").value;

  let filtered = articles;

  if (keyword)
    filtered = filtered.filter(
      (a) =>
        a.title.toLowerCase().includes(keyword) ||
        a.summary.toLowerCase().includes(keyword) ||
        a.impact.toLowerCase().includes(keyword)
    );
  if (theme) filtered = filtered.filter((a) => a.theme === theme);
  if (author) filtered = filtered.filter((a) => a.author === author);
  if (year) filtered = filtered.filter((a) => a.year === year);

  // Tri
  if (sortValue === "year_desc") filtered.sort((a, b) => b.year - a.year);
  if (sortValue === "year_asc") filtered.sort((a, b) => a.year - b.year);
  if (sortValue === "title_asc")
    filtered.sort((a, b) => a.title.localeCompare(b.title));
  if (sortValue === "author_asc")
    filtered.sort((a, b) => a.author.localeCompare(b.author));

  displayArticles(filtered);
}

// Écouteurs
document
  .getElementById("filterKeyword")
  .addEventListener("input", applyFilters);
document.getElementById("filterTheme").addEventListener("change", applyFilters);
document
  .getElementById("filterAuthor")
  .addEventListener("change", applyFilters);
document.getElementById("filterYear").addEventListener("change", applyFilters);
document
  .getElementById("sortArticles")
  .addEventListener("change", applyFilters);

// Initialisation
loadArticles();
