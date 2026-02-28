/* ===== THE AI UPDATE — site.js ===== */

/* --- Particle Background --- */
(function(){
  const c = document.getElementById('particles');
  if (!c) return;
  const ctx = c.getContext('2d');
  let w, h, dots = [];
  function resize(){ w = c.width = window.innerWidth; h = c.height = window.innerHeight; }
  window.addEventListener('resize', resize); resize();
  for (let i = 0; i < 60; i++) {
    dots.push({ x: Math.random()*w, y: Math.random()*h, r: Math.random()*1.5+.3, dx: (Math.random()-.5)*.15, dy: (Math.random()-.5)*.15, o: Math.random()*.4+.1 });
  }
  function draw(){
    ctx.clearRect(0,0,w,h);
    dots.forEach(d => {
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(56,189,248,${d.o})`; ctx.fill();
      d.x += d.dx; d.y += d.dy;
      if(d.x<0||d.x>w) d.dx*=-1;
      if(d.y<0||d.y>h) d.dy*=-1;
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* --- Scroll Reveal --- */
(function(){
  const els = document.querySelectorAll('.anim');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const delay = parseInt(e.target.dataset.delay || 0);
        setTimeout(() => e.target.classList.add('visible'), delay);
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.15 });
  els.forEach(el => io.observe(el));
})();

/* --- Animated Counters --- */
(function(){
  const counters = document.querySelectorAll('[data-count]');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const el = e.target;
        const target = parseInt(el.dataset.count);
        let current = 0;
        const step = Math.ceil(target / 30);
        const timer = setInterval(() => {
          current += step;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = current;
        }, 40);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(el => io.observe(el));
})();

/* --- Nav background on scroll --- */
(function(){
  const nav = document.getElementById('nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.style.background = window.scrollY > 40
      ? 'rgba(6,9,17,.92)' : 'rgba(6,9,17,.75)';
  });
})();

/* --- Local analytics (test mode) --- */
const STORE_KEY = 'aiupdate_test_data';
const SEED = { visits: 0, offerClicks: 0, subscribers: [] };
function db() { return JSON.parse(localStorage.getItem(STORE_KEY) || JSON.stringify(SEED)); }
function save(d) { localStorage.setItem(STORE_KEY, JSON.stringify(d)); }
function track(type) {
  const d = db();
  if (type === 'visit') d.visits++;
  if (type === 'offer_click') d.offerClicks++;
  save(d); renderDashboard();
}
function addSub(name, email) {
  const d = db();
  d.subscribers.unshift({ name, email, at: new Date().toISOString() });
  save(d); renderDashboard();
}
function renderDashboard() {
  const d = db();
  const v = document.getElementById('visits'); if (!v) return;
  const s = d.subscribers.length;
  const c = d.visits ? Math.round((s / d.visits) * 100) : 0;
  document.getElementById('visits').textContent = d.visits;
  document.getElementById('subs').textContent = s;
  document.getElementById('offer').textContent = d.offerClicks;
  document.getElementById('conv').textContent = c + '%';
  const list = document.getElementById('list');
  if (list) {
    list.innerHTML = d.subscribers.slice(0, 20).map(x =>
      `<li>${x.name} — ${x.email} <span style="opacity:.5">${new Date(x.at).toLocaleString()}</span></li>`
    ).join('');
  }
}
function resetData() { localStorage.removeItem(STORE_KEY); renderDashboard(); }
window.resetData = resetData;
window.track = track;
track('visit');

/* --- Lead Form --- */
const form = document.getElementById('leadForm');
if (form) {
  form.addEventListener('submit', e => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    if (!name || !email) return;
    addSub(name, email);
    window.location.href = `thankyou.html?name=${encodeURIComponent(name)}`;
  });
}

renderDashboard();
