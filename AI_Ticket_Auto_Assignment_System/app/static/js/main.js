/**
 * HelpDesk AI — Main JavaScript
 * Handles: Sidebar, Dark Mode, Global Search, Toast auto-dismiss, Animations
 */

'use strict';

// ── DOM Ready ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  initSidebar();
  initDarkMode();
  initToasts();
  initGlobalSearch();
  initAnimations();
  updateOpenTicketCount();
});

// ── Sidebar ────────────────────────────────────────────────────────────────
function initSidebar() {
  const sidebar = document.getElementById('sidebar');
  const mainWrapper = document.getElementById('mainWrapper');
  const sidebarToggle = document.getElementById('sidebarToggle');
  const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');

  if (!sidebar) return;

  // Restore state
  const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  if (isCollapsed && window.innerWidth > 992) {
    sidebar.classList.add('collapsed');
    updateToggleIcon(sidebar);
  }

  // Desktop toggle
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('collapsed');
      localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
      updateToggleIcon(sidebar);
    });
  }

  // Mobile toggle
  if (mobileSidebarToggle) {
    mobileSidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('mobile-open');
    });
  }

  // Close sidebar on outside click (mobile)
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 992 &&
        sidebar.classList.contains('mobile-open') &&
        !sidebar.contains(e.target) &&
        e.target !== mobileSidebarToggle) {
      sidebar.classList.remove('mobile-open');
    }
  });
}

function updateToggleIcon(sidebar) {
  const icon = sidebar.querySelector('#sidebarToggle i');
  if (icon) {
    icon.className = sidebar.classList.contains('collapsed')
      ? 'bi bi-chevron-right'
      : 'bi bi-chevron-left';
  }
}

// ── Dark Mode ──────────────────────────────────────────────────────────────
function initDarkMode() {
  const toggle = document.getElementById('darkModeToggle');
  const icon = document.getElementById('themeIcon');
  const html = document.documentElement;

  const currentTheme = localStorage.getItem('theme') || 'light';
  applyTheme(currentTheme);

  if (toggle) {
    toggle.addEventListener('click', function () {
      const newTheme = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem('theme', newTheme);
      applyTheme(newTheme);
    });
  }

  function applyTheme(theme) {
    html.setAttribute('data-bs-theme', theme);
    if (icon) {
      icon.className = theme === 'dark' ? 'bi bi-moon-stars-fill' : 'bi bi-sun-fill';
    }
  }
}

// ── Toast Auto-dismiss ─────────────────────────────────────────────────────
function initToasts() {
  const toasts = document.querySelectorAll('.toast.show');
  toasts.forEach(function (toastEl) {
    // Auto-dismiss after 4 seconds
    setTimeout(function () {
      const bsToast = bootstrap.Toast.getOrCreateInstance(toastEl);
      bsToast.hide();
    }, 4000);
  });
}

// ── Global Search ──────────────────────────────────────────────────────────
function initGlobalSearch() {
  const searchInput = document.getElementById('globalSearch');
  const searchResults = document.getElementById('searchResults');

  if (!searchInput || !searchResults) return;

  let searchTimeout;

  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimeout);
    const q = this.value.trim();

    if (q.length < 2) {
      searchResults.style.display = 'none';
      return;
    }

    searchTimeout = setTimeout(async function () {
      try {
        const resp = await fetch(`/api/v1/tickets?q=${encodeURIComponent(q)}&per_page=5`);
        const data = await resp.json();
        if (data.success && data.data && data.data.tickets.length > 0) {
          renderSearchResults(data.data.tickets, searchResults);
        } else {
          searchResults.style.display = 'none';
        }
      } catch (e) {
        searchResults.style.display = 'none';
      }
    }, 300);
  });

  // Close on outside click
  document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      searchResults.style.display = 'none';
    }
  });

  searchInput.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') searchResults.style.display = 'none';
  });
}

function renderSearchResults(tickets, container) {
  const statusColors = {
    open: '#3b82f6', in_progress: '#f59e0b',
    resolved: '#22c55e', closed: '#6b7280', escalated: '#ef4444'
  };

  const path = window.location.pathname;
  let detailPrefix = '/employee/tickets/';
  if (path.startsWith('/admin')) {
    detailPrefix = '/admin/tickets/';
  } else if (path.startsWith('/agent')) {
    detailPrefix = '/agent/tickets/';
  }

  container.innerHTML = tickets.map(function (t) {
    const color = statusColors[t.status] || '#6b7280';
    return `
      <a href="${detailPrefix}${t.id}" class="search-result-item" style="
        display: flex; gap: 12px; padding: 12px 16px;
        border-bottom: 1px solid var(--border); text-decoration: none;
        transition: background 0.15s;
      " onmouseover="this.style.background='rgba(99,102,241,0.06)'" onmouseout="this.style.background='none'">
        <div style="flex:1">
          <div style="font-size:11px;color:var(--text-muted);margin-bottom:2px">
            <code>${t.ticket_number}</code> ·
            <span style="color:${color}">${t.status.replace('_',' ')}</span>
          </div>
          <div style="font-size:13px;color:var(--text-primary);font-weight:500">
            ${t.title.substring(0, 60)}${t.title.length > 60 ? '...' : ''}
          </div>
        </div>
      </a>`;
  }).join('');

  container.style.display = 'block';
}

// ── Update open ticket count in sidebar ────────────────────────────────────
async function updateOpenTicketCount() {
  const badge = document.getElementById('open-count');
  if (!badge) return;
  try {
    const resp = await fetch('/api/v1/analytics/dashboard');
    const data = await resp.json();
    if (data.success && data.data) {
      badge.textContent = data.data.open || 0;
    }
  } catch (e) {
    // Silently fail
  }
}

// ── Animations ─────────────────────────────────────────────────────────────
function initAnimations() {
  // Intersection Observer for fade-in animations
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card-glass, .kpi-card, .stat-card').forEach(function (el, i) {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transitionDelay = `${i * 0.05}s`;
      observer.observe(el);
    });
  }

  // Animate counter numbers
  document.querySelectorAll('.kpi-value, .stat-value').forEach(function (el) {
    const finalValue = parseInt(el.textContent);
    if (!isNaN(finalValue) && finalValue > 0) {
      animateCounter(el, 0, finalValue, 800);
    }
  });
}

function animateCounter(el, start, end, duration) {
  const startTime = performance.now();
  const originalText = el.textContent;

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
    const current = Math.round(start + (end - start) * eased);
    el.textContent = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(update);
    else el.textContent = originalText;
  }

  requestAnimationFrame(update);
}

// ── Utility Functions ──────────────────────────────────────────────────────
function showToast(message, type = 'info') {
  const container = document.querySelector('.toast-container') ||
    (() => {
      const c = document.createElement('div');
      c.className = 'toast-container position-fixed top-0 end-0 p-3';
      c.style.zIndex = '9999';
      document.body.appendChild(c);
      return c;
    })();

  const icons = { success: 'check-circle', danger: 'x-circle', warning: 'exclamation-triangle', info: 'info-circle' };
  const toastEl = document.createElement('div');
  toastEl.className = `toast show align-items-center text-bg-${type} border-0 mb-2`;
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        <i class="bi bi-${icons[type] || 'info-circle'} me-2"></i>${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;

  container.appendChild(toastEl);
  setTimeout(() => { bootstrap.Toast.getOrCreateInstance(toastEl).hide(); }, 4000);
}

// ── Confirm before dangerous actions ──────────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(function (el) {
  el.addEventListener('click', function (e) {
    if (!confirm(this.dataset.confirm)) e.preventDefault();
  });
});

// ── Copy to clipboard ──────────────────────────────────────────────────────
function copyToClipboard(text, btn) {
  navigator.clipboard.writeText(text).then(function () {
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check2"></i>';
    setTimeout(() => { btn.innerHTML = orig; }, 1500);
    showToast('Copied to clipboard!', 'success');
  });
}
