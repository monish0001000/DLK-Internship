// OdinCrypto Main JS

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Auto-dismiss alerts after 5s
document.querySelectorAll('.alert-odin').forEach(el => {
  setTimeout(() => el.style.opacity = '0', 4500);
  setTimeout(() => el.remove(), 5000);
});

// Copy to clipboard
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check-lg"></i>';
    btn.style.color = 'var(--green)';
    setTimeout(() => { btn.innerHTML = orig; btn.style.color = ''; }, 1800);
  });
}

// Password strength checker
function checkStrength(pw) {
  let score = 0;
  if (pw.length >= 8)  score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[a-z]/.test(pw)) score++;
  if (/\d/.test(pw))    score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  return score; // 0-6
}

function updateStrengthBar(inputId, barId, labelId) {
  const pw = document.getElementById(inputId)?.value || '';
  const score = checkStrength(pw);
  const fill = document.getElementById(barId);
  const label = document.getElementById(labelId);
  if (!fill) return;
  const pct = Math.round((score / 6) * 100);
  fill.style.width = pct + '%';
  const levels = ['', 'Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Excellent'];
  const colors = ['', '#ef4444', '#f59e0b', '#f59e0b', '#22c55e', '#22c55e', '#22d3ee'];
  fill.style.background = colors[score] || '#ef4444';
  if (label) label.textContent = levels[score] || '';
}

// Algorithm selector
document.querySelectorAll('.algo-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const group = btn.closest('.algo-grid');
    group.querySelectorAll('.algo-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    const input = group.nextElementSibling;
    if (input && input.type === 'hidden') input.value = btn.dataset.value;
    const target = btn.dataset.target;
    if (target) {
      document.querySelectorAll('[data-algo-section]').forEach(s => s.style.display = 'none');
      const el = document.querySelector(`[data-algo-section="${target}"]`);
      if (el) el.style.display = '';
    }
  });
});

// Score ring animation
function animateScoreRing(id, score) {
  const circle = document.getElementById(id);
  if (!circle) return;
  const r = parseFloat(circle.getAttribute('r'));
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  circle.style.strokeDasharray = circ;
  circle.style.strokeDashoffset = circ;
  setTimeout(() => {
    circle.style.transition = 'stroke-dashoffset 1.2s ease';
    circle.style.strokeDashoffset = offset;
  }, 200);
}
