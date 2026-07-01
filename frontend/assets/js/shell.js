// Renders sidebar + topbar into #app-shell
function renderShell(pageTitle = '') {
  const shell = document.getElementById('app-shell');
  if (!shell) return;
  shell.innerHTML = `
  <aside class="sidebar">
    <div class="logo-wrap">
      <a class="logo" href="index.html">
        <div class="logo-icon">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M8 2C5 2 3 4 3 6.5c0 3 5 7.5 5 7.5s5-4.5 5-7.5C13 4 11 2 8 2z" fill="#c084fc"/>
          </svg>
        </div>
        <span class="logo-text">Douceur</span>
      </a>
    </div>
    <nav class="nav-section">
      <div class="nav-label">Navigation</div>
      <a class="nav-item" href="index.html">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <rect x="1.5" y="1.5" width="5.5" height="5.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <rect x="9"   y="1.5" width="5.5" height="5.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <rect x="1.5" y="9"   width="5.5" height="5.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <rect x="9"   y="9"   width="5.5" height="5.5" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
        </svg>
        Dashboard
      </a>
      <a class="nav-item" href="products.html">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <rect x="2" y="4" width="12" height="9" rx="1.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M5 4V3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1" stroke="currentColor" stroke-width="1.2"/>
          <path d="M5 8h6M5 11h4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        สินค้า
      </a>
      <a class="nav-item" href="inventory.html">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M3 4h10M3 8h10M3 12h6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        สต็อก
      </a>
      <a class="nav-item" href="sales.html">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M3 11.5L6.5 8l2.5 2 4-5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        รายรับ-รายจ่าย
      </a>
      <a class="nav-item" href="settings.html">
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="5.5" stroke="currentColor" stroke-width="1.2"/>
          <path d="M8 5.5v3h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        ตั้งค่า
      </a>
    </nav>
    <div class="sidebar-bottom">
      <div class="user-row">
        <div class="avatar">K</div>
        <span class="user-name">Kamon</span>
      </div>
    </div>
  </aside>

  <div class="main">
    <header class="topbar">
      <div class="topbar-left">
        <span class="topbar-title">Douceur</span>
      </div>
    </header>
    <div class="content" id="page-content"></div>
  </div>`;

  // mark active
  const page = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-item').forEach(el => {
    if (el.getAttribute('href') === page) el.classList.add('active');
  });
}