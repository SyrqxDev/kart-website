// ===== HERO SLIDESHOW =====
// Add or remove images here — just edit this list. Use URLs or local paths
// like "images/race1.jpg". They rotate automatically behind the title.
const heroImages = [
    "images/IMG_0276.jpg",
    "images/IMG_0292.jpg",
    "images/IMG_0303.jpg",
    "images/IMG_0382.jpg",
    "images/IMG_0626.jpg",
    "images/IMG_0660.jpg",
    "images/IMG_0674.jpg",
];
const SLIDE_INTERVAL = 5000; // ms between slides

// ===== ABOUT — edit your bio, stats and details here =====
const about = {
  // Each string is its own paragraph.
  bio: [
    "I'm a competitive karting driver with a relentless focus on race craft, consistency and continual improvement. Since first stepping into a kart I've been hooked on the pursuit of the perfect lap.",
    "Racing across regional and national championships, I bring dedication on track and professionalism off it — working closely with partners to deliver real value both at the circuit and online.",
  ],
  // Headline numbers shown as cards.
  stats: [
    { value: "12+", label: "Races" },
    { value: "22/100", label: "Top Finish" },
    { value: "5+", label: "Seasons" },
  ],
  // The detail card on the right. Add/remove rows freely.
  spec: [
    { label: "Class", value: "Senior Rotax" },
    { label: "Number", value: "95" },
    { label: "Home Circuit", value: "Paul Fletcher International" },
    { label: "Team", value: "George Whitbread Racing" },
    { label: "Best Result", value: "P22/100 Drivers" },
  ],
};

// ===== DATA — edit these to update the site =====
const results = [
  { date: "2025-07", event: "NKC 2025", circuit: "Warden Law", cls: "Senior Rotax", pos: 11 },
  { date: "2024-09", event: "NKC 2024", circuit: "Three Sisters", cls: "Senior Rotax", pos: 13 },
  { date: "2025-10", event: "NKC 2024", circuit: "Warden Law", cls: "Senior Rotax", pos: 20 },
];

// ===== INSTAGRAM (live feed via Behold) =====
// 1. Go to https://behold.so, sign up (free) and connect @tristansharpe193
// 2. Create a feed, copy its Feed ID, and paste it below.
// The section then auto-updates with your real latest posts. Leave blank to
// use the manual fallback list (`instaPosts`) further down.
const BEHOLD_FEED_ID = "sImfTIJHxMLa47PchyoN";
const INSTA_COUNT = 4;     // how many posts to show

// Manual fallback — used only if BEHOLD_FEED_ID is empty or the feed fails.
const instaPosts = [
  { img: "", cap: "", url: "https://instagram.com" },
  { img: "", cap: "", url: "https://instagram.com" },
  { img: "", cap: "", url: "https://instagram.com" },
  { img: "", cap: "", url: "https://instagram.com" },
];

// ===== RENDER SLIDESHOW =====
const slideshow = document.getElementById("heroSlideshow");
if (heroImages.length) {
  slideshow.innerHTML = heroImages.map((src, i) =>
    `<div class="hero__slide${i === 0 ? " active" : ""}" style="background-image:url('${src}')"></div>`
  ).join("");
  const slides = slideshow.querySelectorAll(".hero__slide");
  if (slides.length > 1) {
    let current = 0;
    setInterval(() => {
      slides[current].classList.remove("active");
      current = (current + 1) % slides.length;
      slides[current].classList.add("active");
    }, SLIDE_INTERVAL);
  }
}

// ===== RENDER ABOUT =====
document.getElementById("aboutBio").innerHTML = about.bio.map(p => `<p>${p}</p>`).join("");
document.getElementById("aboutStats").innerHTML = about.stats.map(s =>
  `<div class="stat"><strong>${s.value}</strong><span>${s.label}</span></div>`).join("");
document.getElementById("aboutSpec").innerHTML = about.spec.map(s =>
  `<li><span>${s.label}</span><strong>${s.value}</strong></li>`).join("");

// ===== RENDER RESULTS =====
function posClass(p) { return p <= 3 ? `pos pos--p${p}` : "pos"; }
function fmtDate(d) {
  const [y, m] = d.split("-");
  return new Date(y, m - 1).toLocaleDateString("en-US", { month: "short", year: "numeric" });
}
const resultsBody = document.getElementById("resultsBody");
resultsBody.innerHTML = results.map(r => `
  <div class="results__row">
    <span>${fmtDate(r.date)}</span>
    <span>${r.event}</span>
    <span>${r.circuit}</span>
    <span>${r.cls}</span>
    <span class="${posClass(r.pos)}">P${r.pos}</span>
  </div>`).join("");

// ===== RENDER INSTAGRAM =====
const instaGrid = document.getElementById("instaGrid");

function renderInsta(posts) {
  instaGrid.innerHTML = posts.slice(0, INSTA_COUNT).map(p => `
    <a class="insta__post" href="${p.url}" target="_blank" rel="noopener" data-cap="${p.cap}">
      <img src="${p.img}" alt="${p.cap}" loading="lazy" />
    </a>`).join("");
}

async function loadInstagram() {
  // Show fallback immediately so the grid is never empty.
  renderInsta(instaPosts);
  if (!BEHOLD_FEED_ID) return;
  try {
    const res = await fetch(`https://feeds.behold.so/${BEHOLD_FEED_ID}`);
    if (!res.ok) throw new Error(res.status);
    const data = await res.json();
    const posts = (data.posts || data).map(p => ({
      img: p.sizes?.medium?.mediaUrl || p.mediaUrl || p.thumbnailUrl,
      cap: (p.caption || p.prunedCaption || "").split("\n")[0].slice(0, 80) || "View on Instagram",
      url: p.permalink,
    })).filter(p => p.img);
    if (posts.length) renderInsta(posts);
  } catch (err) {
    console.warn("Instagram feed unavailable, using fallback.", err);
  }
}
loadInstagram();

// ===== NAV =====
const nav = document.getElementById("nav");
const navLinks = document.getElementById("navLinks");
const navToggle = document.getElementById("navToggle");

window.addEventListener("scroll", () => {
  nav.classList.toggle("scrolled", window.scrollY > 30);
});
navToggle.addEventListener("click", () => navLinks.classList.toggle("open"));
navLinks.querySelectorAll("a").forEach(a =>
  a.addEventListener("click", () => navLinks.classList.remove("open"))
);

// ===== SCROLL REVEAL =====
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("visible"); io.unobserve(e.target); } });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach(el => io.observe(el));

// ===== YEAR =====
document.getElementById("year").textContent = new Date().getFullYear();
