const projects = [
  { name: "Dev Journal CLI", desc: "Track tasks quickly from terminal with SQLite-backed persistence." },
  { name: "FastAPI Task API", desc: "Simple REST API with validated payloads and endpoint tests." },
  { name: "Node File Organizer", desc: "CLI utility to group files by extension with dry-run support." },
  { name: "Algorithms Toolkit", desc: "Interview-ready Python implementations with unit tests." }
];

const mount = document.querySelector("#projects");
projects.forEach((project, idx) => {
  const card = document.createElement("article");
  card.className = "card";
  card.style.animationDelay = `${idx * 80}ms`;
  card.innerHTML = `<h3>${project.name}</h3><p>${project.desc}</p>`;
  mount.appendChild(card);
});