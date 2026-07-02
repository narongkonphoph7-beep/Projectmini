// Vercel ใช้ /api (relative) ส่วน local dev ใช้ localhost:8000
const API = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:8000/api'
  : '/api';

async function apiFetch(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'เกิดข้อผิดพลาด');
  }
  return res.json();
}

function showToast(msg, type = 'success') {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = `show ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 2800);
}

function formatThb(n) {
  return '฿' + Number(n).toLocaleString('th-TH', { minimumFractionDigits: 0, maximumFractionDigits: 2 });
}

function formatDate(d) {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: '2-digit' });
}

function stockDot(stock, threshold) {
  if (stock <= 0)           return 'dot-gray';
  if (stock <= threshold)   return 'dot-amber';
  return 'dot-green';
}

function stockBadge(stock, threshold) {
  if (stock <= 0)         return '<span class="badge badge-red">หมดสต็อก</span>';
  if (stock <= threshold) return '<span class="badge badge-pink">ใกล้หมด</span>';
  return '<span class="badge badge-green">ปกติ</span>';
}

// Sidebar active state
document.addEventListener('DOMContentLoaded', () => {
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.getAttribute('href') === path) el.classList.add('active');
  });
});
