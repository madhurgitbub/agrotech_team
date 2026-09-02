// ===== AgroTech Farmer Dashboard JS =====

let currentServices = [];
let selectedServiceForModal = null;
let isNearestSortActive = true;

document.addEventListener('DOMContentLoaded', async () => {
  if (!requireRole('farmer')) return;
  renderNavbar('home');
  setGreeting();
  loadUserName();
  loadFarmerLocation();

  await Promise.all([
    loadFarmerStats(),
    loadRecentAlerts(),
    loadActiveJobs(),
    loadFarmerServices()
  ]);
});

window.addEventListener('agroLanguageChanged', () => {
  setGreeting();
  loadFarmerLocation();
  loadRecentAlerts();
  loadActiveJobs();
  renderServiceCards(getSortedServices());
});

window.addEventListener('agroLocationChanged', () => {
  loadFarmerLocation();
  renderServiceCards(getSortedServices());
});

function setGreeting() {
  const hour = new Date().getHours();
  const el = document.getElementById('greeting');
  if (!el) return;
  const t = (k, fb) => (typeof AgroI18n !== 'undefined' ? AgroI18n.get(k, fb) : fb);
  if (hour < 12) el.textContent = t('farmer.greeting_morning', 'Good morning! 🌤');
  else if (hour < 17) el.textContent = t('farmer.greeting_afternoon', 'Good afternoon! ☀️');
  else el.textContent = t('farmer.greeting_evening', 'Good evening! 🌙');
}

function loadUserName() {
  const user = AgroData.getUser();
  const el = document.getElementById('userName');
  if (el) el.textContent = (user.name || 'Farmer').split(' ')[0];
}

function loadFarmerLocation() {
  if (typeof AgroLocation === 'undefined') return;
  const loc = AgroLocation.getCurrentLocation();
  const locEl = document.getElementById('farmerCurrentLoc');
  if (locEl) locEl.textContent = loc.name || 'Indore, MP';
  const sel = document.getElementById('districtSelect');
  if (sel && loc.name) sel.value = loc.name;
}

async function loadFarmerStats() {
  try {
    const [servicesRes, requestsRes] = await Promise.all([
      apiGetServices(),
      apiGetMyRequests()
    ]);

    const services = servicesRes.services || [];
    const requests = requestsRes.requests || [];

    document.getElementById('statAvailableServices').textContent = services.length;
    document.getElementById('statPendingRequests').textContent = requests.filter(r => r.status === 'pending').length;
    document.getElementById('statAcceptedRequests').textContent = requests.filter(r => r.status === 'accepted' || r.status === 'confirmed').length;
    document.getElementById('statCompletedRequests').textContent = requests.filter(r => r.status === 'completed').length;
  } catch (err) {
    console.warn('[AgroTech] Stats load fallback:', err);
  }
}

async function loadActiveJobs() {
  const card = document.getElementById('activeJobsCard');
  const listEl = document.getElementById('activeJobsList');
  if (!card || !listEl) return;

  try {
    const res = await apiGetMyRequests();
    const requests = res.requests || [];
    const active = requests.filter(r => r.status === 'accepted' || r.status === 'confirmed');

    if (active.length === 0) {
      card.style.display = 'none';
      return;
    }

    card.style.display = 'block';
    const isHi = typeof AgroI18n !== 'undefined' && AgroI18n.currentLang === 'hi';

    listEl.innerHTML = active.map(r => `
      <div style="background:white;border:1px solid #bbf7d0;border-radius:14px;padding:14px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        <div>
          <div style="font-family:'Sora',sans-serif;font-weight:700;color:#065f46;font-size:1rem;display:flex;align-items:center;gap:8px">
            <span>🚜 ${r.service_name}</span>
            <span class="status-pill status-accepted">✅ ${isHi ? 'स्वीकृत' : 'ACCEPTED'}</span>
          </div>
          <div style="font-size:0.82rem;color:#64748b;margin-top:4px">
            <span>🔖 #${r.request_id || r.id}</span> · 
            <span>👤 ${isHi ? 'प्रदाता' : 'Provider'}: <b>${r.provider?.name || 'Verified Partner'}</b></span> · 
            <span>📞 ${r.provider?.phone || '—'}</span>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px">
          <div style="font-family:'Sora',sans-serif;font-weight:800;font-size:1.15rem;color:#047857">${formatPrice(r.price)}</div>
          <button class="btn-work-done" onclick="AgroWorkDone.openModal('${r.request_id || r.id}', '${r.service_name}', 'farmer')">
            <span>🏁</span> <span>${isHi ? 'काम पूरा हुआ (पुष्टि करें)' : 'Confirm Work Done'}</span>
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    card.style.display = 'none';
  }
}

async function loadRecentAlerts() {
  const alertsContainer = document.getElementById('recentAlertsList');
  if (!alertsContainer) return;

  try {
    const data = await apiGetAlerts();
    const alerts = data.alerts || [];
    if (alerts.length === 0) {
      alertsContainer.innerHTML = `<div style="color:var(--gray-500);font-size:0.875rem">${AgroI18n.get('farmer.no_alerts', 'No new alerts at the moment.')}</div>`;
      return;
    }

    const recent = alerts.slice(0, 3);
    alertsContainer.innerHTML = recent.map(a => `
      <div class="alert-chip-item">
        <div style="display:flex;align-items:center;gap:8px">
          <span>${a.type === 'request' ? '📦' : a.type === 'status' ? '🔔' : '📢'}</span>
          <div>
            <strong style="color:var(--gray-800);display:block;font-size:0.85rem">${a.title}</strong>
            <span style="color:var(--gray-600);font-size:0.8rem">${a.message}</span>
          </div>
        </div>
        <span style="font-size:0.75rem;color:var(--gray-400);white-space:nowrap">${formatDate(a.created_at)}</span>
      </div>
    `).join('');
  } catch (err) {
    alertsContainer.innerHTML = `<div style="color:var(--gray-500);font-size:0.875rem">No recent alerts.</div>`;
  }
}

async function loadFarmerServices() {
  const grid = document.getElementById('productGrid');
  if (!grid) return;
  grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--gray-500)">Loading nearest available services...</div>';

  try {
    const res = await apiGetServices();
    currentServices = res.services || [];
    renderServiceCards(getSortedServices());
  } catch (err) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--gray-500)">Failed to load services.</div>';
  }
}

function getSortedServices() {
  if (!currentServices || currentServices.length === 0) return [];
  const list = [...currentServices];
  
  if (isNearestSortActive && typeof AgroLocation !== 'undefined') {
    list.sort((a, b) => {
      const distA = AgroLocation.getDistanceForService(a);
      const distB = AgroLocation.getDistanceForService(b);
      return distA - distB;
    });
  }
  return list.slice(0, 8);
}

function toggleNearestSort() {
  isNearestSortActive = !isNearestSortActive;
  const btn = document.getElementById('nearestSortToggle');
  const badge = document.getElementById('nearestSortedBadge');
  
  if (btn) {
    if (isNearestSortActive) {
      btn.style.background = 'rgba(16,185,129,0.3)';
      btn.style.borderColor = '#34d399';
    } else {
      btn.style.background = 'rgba(255,255,255,0.15)';
      btn.style.borderColor = 'rgba(255,255,255,0.3)';
    }
  }
  if (badge) badge.style.display = isNearestSortActive ? 'inline-block' : 'none';
  renderServiceCards(getSortedServices());
}

function renderServiceCards(list) {
  const grid = document.getElementById('productGrid');
  if (!grid) return;

  if (list.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">🚜</div>
        <h3>No services available</h3>
        <p>Check back later or browse all categories.</p>
      </div>`;
    return;
  }

  grid.innerHTML = list.map((s, i) => {
    const distKm = typeof AgroLocation !== 'undefined' ? AgroLocation.getDistanceForService(s) : null;
    const distBadge = distKm !== null ? AgroLocation.renderDistanceBadge(distKm) : '';

    return `
      <div class="product-card animate-fade-up" style="animation-delay:${i * 0.05}s">
        <img class="product-card-img" src="${s.image}" alt="${s.name}"
             onerror="this.src='https://via.placeholder.com/300x180/e8f5e9/2e7d32?text=${encodeURIComponent(s.name)}'"
             onclick="openRequestModalById(${s.id})" style="cursor:pointer">
        <div class="product-card-body">
          <div class="product-card-cat">${getCategoryIcon(s.category)} ${s.category}</div>
          <div class="product-card-name" onclick="openRequestModalById(${s.id})" style="cursor:pointer">${s.name}</div>
          <div class="product-card-desc">${s.description}</div>
          
          <div class="product-card-meta">
            <div class="product-card-price">${formatPrice(s.price)} <span>/ ${s.unit}</span></div>
            <div class="product-card-rating">★ ${s.rating || 4.5} <span style="color:#94a3b8">(${s.reviews || 10})</span></div>
          </div>

          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:4px">
            <div class="product-card-location" style="margin-bottom:0">📍 ${s.location || 'Local Hub'}</div>
            ${distBadge}
          </div>

          <button class="btn btn-primary btn-sm btn-full" style="border-radius:12px;font-weight:700;margin-top:4px" onclick="openRequestModalById(${s.id})">
            📝 ${AgroI18n.get('farmer.request_service', 'Request Service')}
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function openRequestModalById(serviceId) {
  const s = currentServices.find(x => x.id === Number(serviceId));
  if (!s) return;
  selectedServiceForModal = s;

  document.getElementById('reqServiceId').value = s.id;
  document.getElementById('reqProviderId').value = s.posted_by || (s.provider?.id || '');
  document.getElementById('reqUnitPrice').value = s.price;
  document.getElementById('reqModalServiceName').textContent = s.name;
  document.getElementById('reqModalProvider').textContent = `Provider: ${s.provider?.name || 'Verified Partner'}`;
  document.getElementById('reqModalPrice').textContent = `${formatPrice(s.price)} / ${s.unit}`;
  document.getElementById('reqQuantity').value = 1;

  const loc = typeof AgroLocation !== 'undefined' ? AgroLocation.getCurrentLocation() : { name: '' };
  document.getElementById('reqAddress').value = loc.name || '';
  document.getElementById('reqDate').value = 'Tomorrow 9:00 AM';
  document.getElementById('reqNotes').value = '';

  calculateEstimatedPrice();
  document.getElementById('requestModal').classList.add('show');
}

function closeRequestModal() {
  document.getElementById('requestModal').classList.remove('show');
  selectedServiceForModal = null;
}

function calculateEstimatedPrice() {
  const qty = Math.max(1, parseInt(document.getElementById('reqQuantity').value) || 1);
  const unitPrice = parseFloat(document.getElementById('reqUnitPrice').value) || 0;
  const total = qty * unitPrice;
  document.getElementById('reqTotalEstimate').textContent = formatPrice(total);
}

async function submitServiceRequest() {
  const serviceId = parseInt(document.getElementById('reqServiceId').value);
  const providerId = document.getElementById('reqProviderId').value;
  const quantity = parseInt(document.getElementById('reqQuantity').value) || 1;
  const preferredDate = document.getElementById('reqDate').value.trim();
  const address = document.getElementById('reqAddress').value.trim();
  const notes = document.getElementById('reqNotes').value.trim();
  const btn = document.getElementById('submitReqBtn');

  if (!selectedServiceForModal) return;
  if (!address || !preferredDate) {
    showToast(AgroI18n.get('common.fill_required', 'Please fill in address and preferred date.'), 'error');
    return;
  }

  const payload = {
    service_id: serviceId,
    service_name: selectedServiceForModal.name,
    provider_id: providerId || null,
    quantity,
    price: quantity * (selectedServiceForModal.price || 0),
    payment_method: 'cod',
    address,
    notes,
    preferred_date: preferredDate
  };

  try {
    btn.disabled = true;
    btn.textContent = AgroI18n.get('common.loading', 'Submitting...');
    await apiCreateServiceRequest(payload);
    closeRequestModal();
    showToast(AgroI18n.get('services.confirm_success', 'Your service request has been sent to the provider!'), 'success');
    await loadFarmerStats();
    await loadActiveJobs();
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = `<span data-i18n="services.submit_request">${AgroI18n.get('services.submit_request', 'Send Request to Provider →')}</span>`;
    showToast(err.message, 'error');
  }
}

function openLocationPickerModal() {
  const modal = document.getElementById('locationModal');
  if (modal) modal.classList.add('show');
}

function closeLocationPickerModal() {
  const modal = document.getElementById('locationModal');
  if (modal) modal.classList.remove('show');
}

function saveSelectedLocation() {
  const sel = document.getElementById('districtSelect');
  if (!sel) return;
  const locName = sel.value;
  const coords = AgroLocation.getCoordsForText(locName);
  AgroLocation.setCurrentLocation(locName, coords.lat, coords.lon, false);
  closeLocationPickerModal();
  showToast(`Location set to ${locName}`, 'success');
}

async function triggerGPSDetect() {
  const btn = document.getElementById('gpsDetectBtn');
  if (btn) btn.innerHTML = `<span>🛰️</span> <span>${AgroI18n.get('location.detecting', 'Detecting...')}</span>`;
  try {
    const loc = await AgroLocation.detectGPS();
    showToast(AgroI18n.get('location.gps_success', 'GPS location detected!'), 'success');
  } catch (err) {
    showToast(AgroI18n.get('location.gps_error', 'Could not detect GPS. Using default location.'), 'warning');
  } finally {
    if (btn) btn.innerHTML = `<span>🛰️</span> <span data-i18n="location.detect_gps">Detect Live GPS</span>`;
  }
}

function performSearch() {
  const q = document.getElementById('homeSearch').value.trim();
  if (q) window.location.href = `search.html?q=${encodeURIComponent(q)}`;
  else window.location.href = 'search.html';
}

document.getElementById('homeSearch')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') performSearch();
});
