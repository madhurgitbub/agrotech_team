// ===== AgroTech Global JavaScript (Role-Based & Bilingual) =====

const PRODUCT_CACHE_KEY = 'agro_products_cache';
const DEFAULT_CATEGORIES = ['All', 'machinery', 'irrigation', 'fertilizer', 'seeds', 'transport'];

const AgroData = {
  products: [],
  categories: [...DEFAULT_CATEGORIES],

  getUser() {
    const raw = localStorage.getItem('agro_user');
    if (raw) {
      try { return JSON.parse(raw); } catch (_) {}
    }
    return {
      id: 'usr-farmer-01',
      name: "Madhur Pratap Singh",
      email: "farmer@agrotech.com",
      phone: "8127059423",
      location: "Indore, MP",
      role: "farmer",
      status: "active"
    };
  },

  saveUser(user) {
    localStorage.setItem('agro_user', JSON.stringify(user));
  },

  getRole() {
    const user = this.getUser();
    return (user.role || 'farmer').toLowerCase();
  },

  isLoggedIn() {
    return !!localStorage.getItem('agro_token');
  },

  isFarmer() {
    return this.getRole() === 'farmer';
  },

  isProvider() {
    const r = this.getRole();
    return r === 'provider' || r === 'seller';
  },

  isAdmin() {
    return this.getRole() === 'admin';
  },

  async loadProducts(forceRefresh = false) {
    try {
      const data = await apiRequest('/services');
      const services = Array.isArray(data.services) ? data.services : [];
      this.products = services;
      this.updateCategories();
      return this.products;
    } catch (error) {
      if (typeof LocalStorageDB !== 'undefined') {
        this.products = LocalStorageDB.getServices();
        this.updateCategories();
        return this.products;
      }
      return [];
    }
  },

  updateCategories() {
    const dynamic = Array.from(new Set(this.products.map(p => p.category).filter(Boolean)));
    this.categories = ['All', ...dynamic];
    if (this.categories.length === 1) this.categories = [...DEFAULT_CATEGORIES];
  },

  findProductById(id) {
    return this.products.find(p => Number(p.id) === Number(id)) || null;
  },

  logout() {
    if (typeof clearSession === 'function') clearSession();
    else {
      localStorage.removeItem('agro_token');
      localStorage.removeItem('agro_user');
      localStorage.removeItem('agro_admin_user');
    }
  }
};

// UI Feedback Toast
function showToast(message, type = 'success', duration = 3000) {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || '💬'}</span> <span>${message}</span>`;
  toast.classList.add('show');
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => toast.classList.remove('show'), duration);
}

function formatPrice(price) {
  return '₹' + Number(price || 0).toLocaleString('en-IN');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function renderStars(rating = 4.5) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(Math.max(0, empty));
}

function getCategoryIcon(cat = '') {
  const icons = {
    machinery: '🚜',
    irrigation: '💧',
    fertilizer: '🌿',
    seeds: '🌱',
    transport: '🚛',
    other: '📦'
  };
  return icons[cat.toLowerCase()] || '📦';
}

function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Role-Based Route Guards
function requireAuth() {
  if (!AgroData.isLoggedIn()) {
    const isPageDir = window.location.pathname.includes('/pages/');
    window.location.href = isPageDir ? 'login.html' : 'pages/login.html';
    return false;
  }
  return true;
}

function requireRole(allowedRoles) {
  if (!requireAuth()) return false;
  const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
  const userRole = AgroData.getRole();
  
  // Normalization for provider/seller
  const effectiveRole = userRole === 'seller' ? 'provider' : userRole;

  if (!roles.includes(effectiveRole) && !roles.includes(userRole)) {
    // Redirect to proper role dashboard
    const isPageDir = window.location.pathname.includes('/pages/');
    const prefix = isPageDir ? '' : 'pages/';
    
    if (effectiveRole === 'provider') {
      window.location.href = prefix + 'provider-dashboard.html';
    } else if (effectiveRole === 'admin') {
      window.location.href = prefix + 'admin-panel.html';
    } else {
      window.location.href = prefix + 'home.html';
    }
    return false;
  }
  return true;
}

// ==================== Hyper-Local Farmer Distance & Location Engine ====================
const AgroLocation = {
  KNOWN_COORDINATES: {
    'indore': { lat: 22.7196, lon: 75.8577, label: 'Indore, MP' },
    'bhopal': { lat: 23.2599, lon: 77.4126, label: 'Bhopal, MP' },
    'ujjain': { lat: 23.1765, lon: 75.7885, label: 'Ujjain, MP' },
    'dewas': { lat: 22.9676, lon: 76.0534, label: 'Dewas, MP' },
    'dhar': { lat: 22.5978, lon: 75.2989, label: 'Dhar, MP' },
    'sehore': { lat: 23.2033, lon: 77.0844, label: 'Sehore, MP' },
    'gwalior': { lat: 26.2183, lon: 78.1828, label: 'Gwalior, MP' },
    'jabalpur': { lat: 23.1815, lon: 79.9864, label: 'Jabalpur, MP' },
    'khargone': { lat: 21.8234, lon: 75.6186, label: 'Khargone, MP' },
    'khandwa': { lat: 21.8314, lon: 76.3498, label: 'Khandwa, MP' },
    'ratlam': { lat: 23.3315, lon: 75.0367, label: 'Ratlam, MP' },
    'sagar': { lat: 23.8388, lon: 78.7378, label: 'Sagar, MP' },
    'vidisha': { lat: 23.5251, lon: 77.8081, label: 'Vidisha, MP' },
    'hoshangabad': { lat: 22.7500, lon: 77.7200, label: 'Hoshangabad, MP' },
    'rewa': { lat: 24.5362, lon: 81.3037, label: 'Rewa, MP' },
    'satna': { lat: 24.6005, lon: 80.8322, label: 'Satna, MP' },
    'jaipur': { lat: 26.9124, lon: 75.7873, label: 'Jaipur, RJ' },
    'kota': { lat: 25.2138, lon: 75.8648, label: 'Kota, RJ' },
    'nagpur': { lat: 21.1458, lon: 79.0882, label: 'Nagpur, MH' },
    'pune': { lat: 18.5204, lon: 73.8567, label: 'Pune, MH' },
    'lucknow': { lat: 26.8467, lon: 80.9462, label: 'Lucknow, UP' }
  },

  getCurrentLocation() {
    const saved = localStorage.getItem('agro_farmer_location');
    if (saved) {
      try { return JSON.parse(saved); } catch (_) {}
    }
    const user = AgroData.getUser();
    const locName = user.location || 'Indore, MP';
    const coords = this.getCoordsForText(locName);
    return { name: locName, lat: coords.lat, lon: coords.lon, isGPS: false };
  },

  setCurrentLocation(name, lat, lon, isGPS = false) {
    const loc = { name, lat, lon, isGPS };
    localStorage.setItem('agro_farmer_location', JSON.stringify(loc));
    window.dispatchEvent(new CustomEvent('agroLocationChanged', { detail: loc }));
    return loc;
  },

  getCoordsForText(text = '') {
    const lower = String(text).toLowerCase();
    for (const [key, val] of Object.entries(this.KNOWN_COORDINATES)) {
      if (lower.includes(key)) return { lat: val.lat, lon: val.lon };
    }
    return { lat: 22.7196, lon: 75.8577 }; // Default Indore
  },

  calculateDistanceKm(lat1, lon1, lat2, lon2) {
    if (!lat1 || !lon1 || !lat2 || !lon2) return 5.0;
    const R = 6371; // km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const dist = R * c;
    return Math.round(dist * 10) / 10;
  },

  getDistanceForService(service) {
    const farmerLoc = this.getCurrentLocation();
    const svcCoords = service.lat && service.lon ? 
      { lat: service.lat, lon: service.lon } : 
      this.getCoordsForText(service.location || 'Indore, MP');
    
    // Hyper-local offset simulation for exact same city to give realistic farm-level distance
    if (Math.abs(farmerLoc.lat - svcCoords.lat) < 0.08 && Math.abs(farmerLoc.lon - svcCoords.lon) < 0.08) {
      const seed = Number(service.id || 1);
      const farmOffset = ((seed * 3.7) % 8.5) + 1.2;
      return Math.round(farmOffset * 10) / 10;
    }

    return this.calculateDistanceKm(farmerLoc.lat, farmerLoc.lon, svcCoords.lat, svcCoords.lon);
  },

  renderDistanceBadge(distanceKm) {
    const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);
    const isNearest = distanceKm <= 10;
    const lang = typeof AgroI18n !== 'undefined' ? AgroI18n.currentLang : 'en';
    const distText = lang === 'hi' ? `${distanceKm} किमी दूर` : `${distanceKm} km away`;
    
    return `
      <span class="location-badge ${isNearest ? 'nearest-glow' : ''}">
        📍 <b>${distText}</b>
        ${isNearest ? `<span class="nearest-tag">${t('location.nearest_badge', '⚡ Nearest')}</span>` : ''}
      </span>
    `;
  },

  async detectGPS() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser.'));
        return;
      }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;
          const loc = this.setCurrentLocation('📍 Live GPS Location', lat, lon, true);
          resolve(loc);
        },
        (err) => {
          reject(err);
        },
        { timeout: 8000, enableHighAccuracy: true }
      );
    });
  }
};

// ==================== AgroWorkDone: Work Completion Workflow for Farmer & Provider ====================
const AgroWorkDone = {
  activeRequestId: null,
  activeRole: null,

  openModal(requestId, serviceName = '', role = 'farmer') {
    this.activeRequestId = requestId;
    this.activeRole = role;

    let modal = document.getElementById('workDoneModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'workDoneModal';
      modal.className = 'agro-modal-backdrop';
      document.body.appendChild(modal);
    }

    const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);
    const isFarmer = role === 'farmer';

    modal.innerHTML = `
      <div class="agro-modal-dialog animate-fade-up" style="max-width:480px">
        <div class="agro-modal-header" style="border-bottom:1.5px solid var(--green-100);padding-bottom:12px;margin-bottom:16px">
          <div style="display:flex;align-items:center;gap:12px">
            <div style="width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,#10b981,#059669);display:flex;align-items:center;justify-content:center;font-size:1.4rem;color:white;box-shadow:0 4px 16px rgba(16,185,129,0.35)">
              🏁
            </div>
            <div>
              <h3 style="color:var(--green-900);font-size:1.15rem;margin:0;font-weight:800">
                ${t('work_done.modal_title', 'Confirm Work Completion')}
              </h3>
              <small style="color:var(--gray-500)">Request #${requestId} · ${serviceName || 'Agri Job'}</small>
            </div>
          </div>
          <button class="agro-modal-close" onclick="AgroWorkDone.closeModal()">✕</button>
        </div>

        <div style="background:var(--green-50);padding:14px;border-radius:14px;margin-bottom:16px;border:1px solid var(--green-200);font-size:0.88rem;color:var(--green-900)">
          <div style="display:flex;align-items:center;gap:8px;font-weight:700;margin-bottom:4px">
            <span>✨</span>
            <span>${isFarmer ? (AgroI18n.currentLang === 'hi' ? 'क्या खेत पर यह कार्य संतोषजनक रूप से पूरा हो चुका है?' : 'Mark this agricultural job as successfully completed on your farm?') : (AgroI18n.currentLang === 'hi' ? 'क्या आपने यह कार्य पूरा कर लिया है? किसान को सूचना भेजी जाएगी।' : 'Confirm that you have completed this machinery/service job?')}</span>
          </div>
          <p style="margin:0;font-size:0.8rem;color:var(--gray-600)">
            ${isFarmer ? (AgroI18n.currentLang === 'hi' ? 'पुष्टि करने पर प्रदाता और आपके दोनों डैशबोर्ड में कार्य पूर्ण (Completed) दिखेगा।' : 'Confirming will mark status as Completed on both your dashboard and the provider\'s.') : (AgroI18n.currentLang === 'hi' ? 'किसान को तत्काल अलर्ट मिलेगा कि कार्य पूरा हो चुका है।' : 'The farmer will be notified immediately that the job is done.')}
          </p>
        </div>

        ${isFarmer ? `
          <div class="form-group" style="margin-bottom:14px">
            <label class="form-label" style="font-weight:700;font-size:0.88rem;color:var(--gray-700)">
              ⭐ ${t('work_done.rating_label', 'Rate the Service (1-5 Stars)')}
            </label>
            <div class="rating-star-selector" id="workDoneStars" style="display:flex;gap:8px;font-size:2rem;cursor:pointer;color:#fbbf24;margin-top:4px">
              <span onclick="AgroWorkDone.setRating(1)" data-star="1">★</span>
              <span onclick="AgroWorkDone.setRating(2)" data-star="2">★</span>
              <span onclick="AgroWorkDone.setRating(3)" data-star="3">★</span>
              <span onclick="AgroWorkDone.setRating(4)" data-star="4">★</span>
              <span onclick="AgroWorkDone.setRating(5)" data-star="5">★</span>
            </div>
            <input type="hidden" id="workDoneRatingVal" value="5">
          </div>

          <div class="form-group" style="margin-bottom:16px">
            <label class="form-label" style="font-weight:700;font-size:0.88rem;color:var(--gray-700)">
              💬 ${t('work_done.feedback_label', 'Your Review / Feedback (Optional)')}
            </label>
            <textarea id="workDoneFeedback" class="form-textarea" rows="2" placeholder="${AgroI18n.currentLang === 'hi' ? 'उदा. समय पर काम हुआ, ट्रैक्टर और ऑपरेटर बहुत बढ़िया थे।' : 'e.g. Completed ploughing right on time. Highly recommended!'}"></textarea>
          </div>
        ` : `
          <div class="form-group" style="margin-bottom:16px">
            <label class="form-label" style="font-weight:700;font-size:0.88rem;color:var(--gray-700)">
              📝 ${AgroI18n.currentLang === 'hi' ? 'कार्य समाप्ति नोट्स / रकबा (वैकल्पिक)' : 'Completion Notes / Total Acreage (Optional)'}
            </label>
            <input type="text" id="workDoneProviderNotes" class="form-input" placeholder="${AgroI18n.currentLang === 'hi' ? 'उदा. कार्य 2.5 एकड़ सफलतापूर्वक पूरा किया गया।' : 'e.g. Successfully completed 2.5 acres.'}">
          </div>
        `}

        <div style="display:flex;gap:10px;justify-content:flex-end">
          <button class="btn btn-secondary" onclick="AgroWorkDone.closeModal()">
            ${t('common.cancel', 'Cancel')}
          </button>
          <button class="btn btn-primary" style="background:linear-gradient(135deg,#10b981,#059669);font-weight:700;box-shadow:0 4px 14px rgba(16,185,129,0.3)" onclick="AgroWorkDone.submit()">
            ${t('work_done.submit_btn', 'Confirm & Complete 🏁')}
          </button>
        </div>
      </div>
    `;

    modal.classList.add('show');
    if (isFarmer) this.setRating(5);
  },

  setRating(val) {
    const input = document.getElementById('workDoneRatingVal');
    if (input) input.value = val;
    const stars = document.querySelectorAll('#workDoneStars span');
    stars.forEach((s, idx) => {
      s.style.color = (idx < val) ? '#f59e0b' : '#cbd5e1';
    });
  },

  closeModal() {
    const modal = document.getElementById('workDoneModal');
    if (modal) modal.classList.remove('show');
  },

  async submit() {
    if (!this.activeRequestId) return;
    const reqId = this.activeRequestId;
    const role = this.activeRole;
    const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);

    try {
      if (typeof apiUpdateRequestStatus === 'function') {
        await apiUpdateRequestStatus(reqId, 'completed');
      } else if (typeof LocalStorageDB !== 'undefined') {
        LocalStorageDB.updateRequestStatus(reqId, 'completed');
      }

      const successMsg = role === 'provider' 
        ? t('work_done.provider_success', 'Work marked as completed! Farmer has been notified.')
        : t('work_done.farmer_success', 'Work marked as completed! Provider has been notified.');
      
      showToast(successMsg, 'success');
      this.closeModal();

      if (typeof loadRequests === 'function') {
        await loadRequests();
      } else if (typeof loadFarmerStats === 'function') {
        loadFarmerStats();
        if (typeof loadRecentAlerts === 'function') loadRecentAlerts();
      } else if (typeof loadIncomingRequests === 'function') {
        loadIncomingRequests();
      } else {
        setTimeout(() => location.reload(), 600);
      }
    } catch (err) {
      showToast(err.message || 'Failed to update status', 'error');
    }
  }
};

// Dynamic Universal Hero-Themed Navbar Renderer
function renderNavbar(activePage = '') {
  const nav = document.getElementById('navbar');
  if (!nav) return;

  const user = AgroData.getUser();
  const role = AgroData.getRole();
  const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);
  const langToggleHtml = typeof AgroI18n !== 'undefined' ? AgroI18n.renderLanguageToggle() : '';
  const firstName = (user.name || 'User').split(' ')[0];

  let linksHtml = '';

  if (role === 'admin') {
    linksHtml = `
      <li><a href="admin-panel.html" class="${activePage === 'admin' ? 'active' : ''}">🛡️ ${t('nav.admin_dashboard', 'Admin Panel')}</a></li>
      <li>${langToggleHtml}</li>
      <li><button class="btn-logout" onclick="handleLogout()">🚪 ${t('nav.logout', 'Logout')}</button></li>
    `;
  } else if (role === 'provider' || role === 'seller') {
    linksHtml = `
      <li><a href="provider-dashboard.html" class="${activePage === 'home' || activePage === 'dashboard' ? 'active' : ''}">📊 ${t('nav.provider_dashboard', 'Dashboard')}</a></li>
      <li><a href="provider-services.html" class="${activePage === 'services' || activePage === 'my_services' ? 'active' : ''}">🚜 ${t('nav.my_services', 'My Services')}</a></li>
      <li><a href="provider-add-service.html" class="${activePage === 'add_service' ? 'active' : ''}">➕ ${t('nav.add_service', 'Add Service')}</a></li>
      <li><a href="provider-requests.html" class="${activePage === 'requests' ? 'active' : ''}">📥 ${t('nav.provider_requests', 'Requests')}</a></li>
      <li><a href="provider-alerts.html" class="${activePage === 'alerts' || activePage === 'notif' ? 'active' : ''}">🔔 ${t('nav.provider_alerts', 'Alerts')}</a></li>
      <li><a href="provider-help.html" class="${activePage === 'help' ? 'active' : ''}">❓ ${t('nav.provider_help', 'Help')}</a></li>
      <li><a href="provider-profile.html" class="${activePage === 'account' || activePage === 'profile' ? 'active' : ''}">👤 ${firstName}</a></li>
      <li>${langToggleHtml}</li>
      <li><button class="btn-logout" onclick="handleLogout()">🚪 ${t('nav.logout', 'Logout')}</button></li>
    `;
  } else {
    // Farmer Navbar (With prominent Hindi/English toggle)
    linksHtml = `
      <li><a href="home.html" class="${activePage === 'home' || activePage === 'dashboard' ? 'active' : ''}">🏠 ${t('nav.home', 'Dashboard')}</a></li>
      <li><a href="search.html" class="${activePage === 'search' ? 'active' : ''}">🔍 ${t('nav.find_services', 'Find Services')}</a></li>
      <li><a href="my_purchase.html" class="${activePage === 'purchases' || activePage === 'requests' ? 'active' : ''}">📋 ${t('nav.my_requests', 'My Requests')}</a></li>
      <li><a href="notifications.html" class="${activePage === 'notif' || activePage === 'alerts' ? 'active' : ''}">🔔 ${t('nav.alerts', 'Alerts')}</a></li>
      <li><a href="help.html" class="${activePage === 'help' ? 'active' : ''}">❓ ${t('nav.help', 'Help')}</a></li>
      <li><a href="myaccount.html" class="${activePage === 'account' || activePage === 'profile' ? 'active' : ''}">👤 ${firstName}</a></li>
      <li>${langToggleHtml}</li>
      <li><button class="btn-logout" onclick="handleLogout()">🚪 ${t('nav.logout', 'Logout')}</button></li>
    `;
  }

  const logoHref = role === 'admin' ? 'admin-panel.html' : (role === 'provider' || role === 'seller') ? 'provider-dashboard.html' : 'home.html';

  nav.innerHTML = `
    <a href="${logoHref}" class="navbar-logo">
      <div class="logo-icon">🌱</div>
      Agro<span>TECH</span>
    </a>
    <ul class="navbar-links" id="navLinks">
      ${linksHtml}
    </ul>
    <div style="display:flex;align-items:center;gap:8px">
      <div class="mobile-lang">${langToggleHtml}</div>
      <button class="mobile-menu-btn" onclick="toggleMobileMenu()">☰</button>
    </div>
  `;
}

function handleLogout() {
  const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);
  if (confirm(t('common.confirm_logout', 'Are you sure you want to logout?'))) {
    AgroData.logout();
    showToast(t('common.logged_out', 'Logged out successfully.'), 'info');
    setTimeout(() => {
      window.location.href = '../index.html';
    }, 600);
  }
}

function toggleMobileMenu() {
  const links = document.querySelector('.navbar-links');
  if (links) links.classList.toggle('open');
}

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('.navbar')) {
    const navLinks = document.querySelector('.navbar-links');
    if (navLinks) navLinks.classList.remove('open');
  }
});

// Listen to language change events and dynamically refresh navbar and DOM
window.addEventListener('agroLanguageChanged', () => {
  const activeNav = document.querySelector('.navbar-links a.active');
  const activePage = activeNav ? activeNav.getAttribute('href') : '';
  renderNavbar(activePage);
});
