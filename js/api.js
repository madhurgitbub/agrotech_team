/**
 * AgroTech API Client & Offline-Resilient Role-Based Backend Bridge
 * Connects frontend smoothly to FastAPI backend with zero-setup offline fallback.
 * Supports Farmer, Provider, and Admin roles.
 */

const DEFAULT_API_BASE = 'http://127.0.0.1:8000/api';

function getApiBase() {
  const saved = localStorage.getItem('agro_api_base');
  return saved && saved.trim() ? saved.trim().replace(/\/+$/, '') : DEFAULT_API_BASE;
}

function setApiBase(baseUrl) {
  const normalized = String(baseUrl || '').trim().replace(/\/+$/, '');
  if (!normalized) throw new Error('API base URL cannot be empty.');
  localStorage.setItem('agro_api_base', normalized);
  return normalized;
}

// Check backend connectivity status
async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${getApiBase()}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    return res.ok;
  } catch (_) {
    return false;
  }
}

// Local mock database storage for fallback mode
const LocalStorageDB = {
  getUsers() {
    const defaultUsers = [
      {
        id: 'usr-admin-01',
        name: 'System Administrator',
        email: 'admin@agrotech.com',
        phone: '9876543210',
        password: 'admin123',
        location: 'National Head Office',
        role: 'admin',
        status: 'active',
        created_at: new Date(Date.now() - 30 * 86400000).toISOString()
      },
      {
        id: 'usr-farmer-01',
        name: 'Madhur Pratap Singh',
        email: 'farmer@agrotech.com',
        phone: '8127059423',
        password: 'farmer123',
        location: 'Indore, MP',
        role: 'farmer',
        status: 'active',
        created_at: new Date(Date.now() - 20 * 86400000).toISOString()
      },
      {
        id: 'usr-provider-01',
        name: 'Rajesh Patel (Kisan Agro Services)',
        email: 'provider@agrotech.com',
        phone: '9893012345',
        password: 'provider123',
        location: 'Indore, MP',
        role: 'provider',
        status: 'active',
        created_at: new Date(Date.now() - 15 * 86400000).toISOString()
      }
    ];
    const stored = localStorage.getItem('agro_local_users');
    if (!stored) {
      localStorage.setItem('agro_local_users', JSON.stringify(defaultUsers));
      return defaultUsers;
    }
    try {
      const parsed = JSON.parse(stored);
      // Ensure default accounts exist
      defaultUsers.forEach(du => {
        if (!parsed.some(u => u.email === du.email)) {
          parsed.push(du);
        }
      });
      localStorage.setItem('agro_local_users', JSON.stringify(parsed));
      return parsed;
    } catch (_) {
      return defaultUsers;
    }
  },

  saveUsers(users) {
    localStorage.setItem('agro_local_users', JSON.stringify(users));
  },

  getServices() {
    const defaultServices = [
      { id: 1, name: "Mahindra 575 DI Tractor Rental", category: "machinery", price: 800, unit: "per acre", description: "Powerful 45HP tractor suitable for ploughing, tilling, and heavy-duty farming tasks.", image: "https://5.imimg.com/data5/SELLER/Default/2021/6/CX/WL/RI/30912792/mahindra-tractor-yuvraj-bumper-1000x1000.jpg", rating: 4.8, reviews: 128, available: true, status: "approved", location: "Indore, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 2, name: "John Deere 5050 D Tractor", category: "machinery", price: 1000, unit: "per acre", description: "High-efficiency tractor with advanced hydraulics and rotary tiller attachment.", image: "https://cpimg.tistatic.com/10029058/b/4/John-deere-Tractors..jpg", rating: 4.9, reviews: 95, available: true, status: "approved", location: "Bhopal, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 3, name: "Modern Combine Harvester", category: "machinery", price: 1200, unit: "per acre", description: "Fast harvesting for wheat, soybean, and paddy. Reduces harvest loss significantly.", image: "https://5.imimg.com/data5/WC/IE/YH/ANDROID-86040604/prod-20200810-2031297210080910753376724-jpg-1000x1000.jpg", rating: 4.7, reviews: 72, available: true, status: "approved", location: "Ujjain, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 4, name: "Fieldking Heavy Rotavator", category: "machinery", price: 500, unit: "per acre", description: "Heavy-duty 7-feet rotavator for complete soil preparation and fine seedbed.", image: "https://www.fieldking.com/blogs/wp-content/uploads/2024/09/Ploughing.jpg", rating: 4.6, reviews: 64, available: true, status: "approved", location: "Gwalior, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 5, name: "Automatic Drip Irrigation Kit", category: "irrigation", price: 3500, unit: "per kit", description: "Complete drip system for 1 acre land. Saves up to 60% water and boosts yield.", image: "https://5.imimg.com/data5/SELLER/Default/2022/10/BC/MY/LI/21395960/drip-irrigation-system-1000x1000.jpg", rating: 4.8, reviews: 89, available: true, status: "approved", location: "Indore, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 6, name: "IFFCO DAP Fertilizer (50kg Bag)", category: "fertilizer", price: 1350, unit: "per bag", description: "Original certified DAP fertilizer for strong root growth and early crop establishment.", image: "https://5.imimg.com/data5/SELLER/Default/2022/5/NJ/VT/MB/26553143/dap-fertilizer-500x500.jpg", rating: 4.7, reviews: 201, available: true, status: "approved", location: "Bhopal, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 7, name: "HYV Premium Wheat Seeds (GW-322)", category: "seeds", price: 450, unit: "per kg", description: "Certified disease-resistant high yield wheat seeds with high germination rate.", image: "https://5.imimg.com/data5/SELLER/Default/2021/9/ZG/OS/PB/3131427/wheat-seeds-500x500.jpg", rating: 4.9, reviews: 156, available: true, status: "approved", location: "Sehore, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() },
      { id: 8, name: "5-Ton Crop Transport Mini Truck", category: "transport", price: 2500, unit: "per trip", description: "Reliable door-to-mandi farm transport service with GPS tracking available 24/7.", image: "https://5.imimg.com/data5/SELLER/Default/2022/3/QF/XN/XJ/149399990/mini-truck-500x500.jpg", rating: 4.5, reviews: 43, available: true, status: "approved", location: "Indore, MP", posted_by: "usr-provider-01", created_at: new Date().toISOString() }
    ];
    const stored = localStorage.getItem('agro_services');
    if (!stored) {
      localStorage.setItem('agro_services', JSON.stringify(defaultServices));
      return defaultServices;
    }
    try {
      const parsed = JSON.parse(stored);
      if (parsed.length === 0) {
        localStorage.setItem('agro_services', JSON.stringify(defaultServices));
        return defaultServices;
      }
      return parsed;
    } catch (_) {
      return defaultServices;
    }
  },

  saveServices(services) {
    localStorage.setItem('agro_services', JSON.stringify(services));
  },

  getRequests() {
    const defaultReqs = [
      {
        id: 1,
        request_id: 'REQ-1001',
        farmer_id: 'usr-farmer-01',
        farmer_name: 'Madhur Pratap Singh',
        farmer_phone: '8127059423',
        provider_id: 'usr-provider-01',
        service_id: 1,
        service_name: 'Mahindra 575 DI Tractor Rental',
        quantity: 2,
        price: 1600,
        payment_method: 'cod',
        payment_status: 'pending',
        status: 'accepted',
        address: 'Indore Farm Sector 4',
        notes: 'Need for ploughing 2 acres land.',
        preferred_date: 'Tomorrow 8:00 AM',
        created_at: new Date(Date.now() - 2 * 3600000).toISOString()
      },
      {
        id: 2,
        request_id: 'REQ-1002',
        farmer_id: 'usr-farmer-01',
        farmer_name: 'Madhur Pratap Singh',
        farmer_phone: '8127059423',
        provider_id: 'usr-provider-01',
        service_id: 5,
        service_name: 'Automatic Drip Irrigation Kit',
        quantity: 1,
        price: 3500,
        payment_method: 'upi',
        payment_status: 'paid',
        status: 'pending',
        address: 'Indore Farm Sector 4',
        notes: 'Installation assistance required.',
        preferred_date: 'This weekend',
        created_at: new Date(Date.now() - 24 * 3600000).toISOString()
      }
    ];
    const stored = localStorage.getItem('agro_service_requests');
    if (!stored) {
      localStorage.setItem('agro_service_requests', JSON.stringify(defaultReqs));
      return defaultReqs;
    }
    try {
      return JSON.parse(stored);
    } catch (_) {
      return defaultReqs;
    }
  },

  saveRequests(reqs) {
    localStorage.setItem('agro_service_requests', JSON.stringify(reqs));
  },

  getAlerts(userId = null, role = null) {
    const defaultAlerts = [
      { id: 1, user_id: 'usr-farmer-01', audience: 'farmer', type: 'request', title: 'Service Request Accepted ✅', message: 'Your booking for Mahindra 575 DI Tractor has been accepted by the provider.', is_read: false, created_at: new Date(Date.now() - 2 * 3600000).toISOString() },
      { id: 2, user_id: 'usr-farmer-01', audience: 'farmer', type: 'system', title: '🌾 Welcome to AgroTech!', message: 'Explore available farm machinery, rental equipment and farm supplies in your region.', is_read: true, created_at: new Date(Date.now() - 48 * 3600000).toISOString() },
      { id: 3, user_id: 'usr-provider-01', audience: 'provider', type: 'request', title: 'New Booking Received 🚜', message: 'Farmer Madhur Pratap Singh requested Mahindra 575 DI Tractor Rental.', is_read: false, created_at: new Date(Date.now() - 3 * 3600000).toISOString() },
      { id: 4, user_id: null, audience: 'all', type: 'promo', title: '🎉 Seasonal Harvesting Discounts', message: 'Special 15% discount on combine harvesters and transport services this season.', is_read: false, created_at: new Date(Date.now() - 72 * 3600000).toISOString() }
    ];
    const stored = localStorage.getItem('agro_alerts');
    let list = defaultAlerts;
    if (stored) {
      try { list = JSON.parse(stored); } catch (_) {}
    } else {
      localStorage.setItem('agro_alerts', JSON.stringify(defaultAlerts));
    }
    if (userId) {
      return list.filter(a => a.user_id === userId || a.audience === 'all' || (role && a.audience === role));
    }
    return list;
  },

  saveAlerts(alerts) {
    localStorage.setItem('agro_alerts', JSON.stringify(alerts));
  },

  addAlert(alert) {
    const list = this.getAlerts();
    alert.id = Date.now();
    alert.is_read = false;
    alert.created_at = new Date().toISOString();
    list.unshift(alert);
    this.saveAlerts(list);
  },

  handleLocalRequest(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const body = options.body ? JSON.parse(options.body) : {};
    const currentUser = JSON.parse(localStorage.getItem('agro_user') || 'null');

    // 1. Health
    if (path === '/health') {
      return { status: 'ok', database: 'local_storage', mode: 'offline_ready' };
    }

    // 2. Auth Login
    if (path === '/auth/login' && method === 'POST') {
      const users = this.getUsers();
      const u = (body.username || '').toLowerCase().trim();
      const p = body.password || '';

      const matched = users.find(
        x => (x.email.toLowerCase() === u || x.name.toLowerCase() === u || x.phone === u) && x.password === p
      );

      if (!matched) {
        throw new Error('Invalid username/email or password.');
      }
      if (matched.status === 'blocked') {
        throw new Error('This account is blocked. Please contact admin.');
      }

      const dummyToken = 'agt_local_tok_' + btoa(JSON.stringify({ id: matched.id, email: matched.email, role: matched.role }));
      const userPublic = {
        id: matched.id,
        name: matched.name,
        email: matched.email,
        phone: matched.phone,
        location: matched.location || '',
        role: matched.role || 'farmer',
        status: matched.status || 'active',
        created_at: matched.created_at || new Date().toISOString()
      };
      return { message: 'Login successful (Offline Local Mode)', token: dummyToken, user: userPublic };
    }

    // 3. Auth Register
    if (path === '/auth/register' && method === 'POST') {
      const users = this.getUsers();
      const email = (body.email || '').toLowerCase().trim();
      if (users.some(x => x.email.toLowerCase() === email)) {
        throw new Error('This email is already registered. Please login.');
      }

      const otp = '123456';
      const otps = JSON.parse(localStorage.getItem('agro_pending_otps') || '{}');
      otps[email] = { payload: { ...body, email }, otp, created: Date.now() };
      localStorage.setItem('agro_pending_otps', JSON.stringify(otps));

      return {
        message: `OTP sent successfully! (Dev Code: ${otp})`,
        debug_otp: otp,
        email
      };
    }

    // 4. Verify OTP
    if (path === '/auth/register/verify-otp' && method === 'POST') {
      const email = (body.email || '').toLowerCase().trim();
      const otp = (body.otp || '').trim();
      const otps = JSON.parse(localStorage.getItem('agro_pending_otps') || '{}');
      const pending = otps[email];

      if (pending && pending.otp !== otp && otp !== '123456') {
        throw new Error('Invalid OTP code. Please enter 123456 or the code provided.');
      }

      const pData = pending ? pending.payload : { name: 'User', email, phone: '9876543210', password: 'password', location: '', role: 'farmer' };
      const users = this.getUsers();
      const newUser = {
        id: 'usr_' + Date.now(),
        name: pData.name,
        email: pData.email,
        phone: pData.phone,
        password: pData.password,
        location: pData.location || '',
        role: pData.role || 'farmer',
        status: 'active',
        created_at: new Date().toISOString()
      };
      users.push(newUser);
      this.saveUsers(users);

      delete otps[email];
      localStorage.setItem('agro_pending_otps', JSON.stringify(otps));

      const dummyToken = 'agt_local_tok_' + btoa(JSON.stringify({ id: newUser.id, email: newUser.email, role: newUser.role }));
      const userPublic = {
        id: newUser.id,
        name: newUser.name,
        email: newUser.email,
        phone: newUser.phone,
        location: newUser.location,
        role: newUser.role,
        status: newUser.status,
        created_at: newUser.created_at
      };
      return { message: 'Account verified and created successfully! 🌱', token: dummyToken, user: userPublic };
    }

    // 5. Auth /me
    if (path === '/auth/me') {
      if (!currentUser) throw new Error('Not authenticated.');
      return { user: currentUser };
    }

    // 6. Admin Login
    if (path === '/admin/login' && method === 'POST') {
      const res = this.handleLocalRequest('/auth/login', options);
      if (res.user.role !== 'admin') {
        throw new Error('Admin access required.');
      }
      return res;
    }

    // 7. Admin Register
    if (path === '/admin/register' && method === 'POST') {
      const users = this.getUsers();
      const email = (body.email || '').toLowerCase().trim();
      if (users.some(x => x.email.toLowerCase() === email)) {
        throw new Error('Admin with this email already exists.');
      }
      const newAdmin = {
        id: 'usr_adm_' + Date.now(),
        name: body.name,
        email,
        phone: body.phone || '9876543210',
        password: body.password,
        location: body.location || 'Headquarters',
        role: 'admin',
        status: 'active',
        created_at: new Date().toISOString()
      };
      users.push(newAdmin);
      this.saveUsers(users);
      return { message: 'Admin account created successfully', user: newAdmin };
    }

    // 8. Services GET (public/farmer)
    if (path.startsWith('/services') && method === 'GET' && !path.includes('/my')) {
      const services = this.getServices();
      return { services: services.filter(s => s.available !== false) };
    }

    // 9. Services /my (Provider)
    if (path === '/services/my' && method === 'GET') {
      const services = this.getServices();
      const myId = currentUser?.id || 'usr-provider-01';
      return { services: services.filter(s => s.posted_by === myId || !s.posted_by) };
    }

    // 10. Service Create (POST)
    if (path === '/services' && method === 'POST') {
      const services = this.getServices();
      const newSvc = {
        id: Date.now(),
        name: body.name,
        category: body.category,
        price: Number(body.price),
        unit: body.unit || 'per day',
        description: body.description,
        location: body.location || '',
        image: body.image || '',
        available: body.available !== false,
        status: 'approved',
        posted_by: currentUser?.id || 'usr-provider-01',
        rating: 4.8,
        reviews: 1,
        created_at: new Date().toISOString()
      };
      services.unshift(newSvc);
      this.saveServices(services);
      return newSvc;
    }

    // 11. Service Update (PUT)
    if (path.startsWith('/services/') && method === 'PUT') {
      const id = parseInt(path.split('/')[2]);
      const services = this.getServices();
      const idx = services.findIndex(s => s.id === id);
      if (idx === -1) throw new Error('Service not found.');
      services[idx] = { ...services[idx], ...body };
      this.saveServices(services);
      return services[idx];
    }

    // 12. Service Delete (DELETE)
    if (path.startsWith('/services/') && method === 'DELETE') {
      const id = parseInt(path.split('/')[2]);
      let services = this.getServices();
      services = services.filter(s => s.id !== id);
      this.saveServices(services);
      return { message: 'Service deleted.' };
    }

    // 13. Requests POST (Farmer creates request)
    if (path === '/requests' && method === 'POST') {
      const reqs = this.getRequests();
      const newReq = {
        id: Date.now(),
        request_id: 'REQ-' + String(Date.now()).slice(-7),
        farmer_id: currentUser?.id || 'usr-farmer-01',
        farmer_name: currentUser?.name || 'Farmer',
        farmer_phone: currentUser?.phone || '8127059423',
        provider_id: body.provider_id || 'usr-provider-01',
        service_id: body.service_id,
        service_name: body.service_name,
        quantity: body.quantity || 1,
        price: Number(body.price),
        payment_method: body.payment_method || 'cod',
        payment_status: 'pending',
        status: 'pending',
        address: body.address || '',
        notes: body.notes || '',
        preferred_date: body.preferred_date || 'ASAP',
        created_at: new Date().toISOString()
      };
      reqs.unshift(newReq);
      this.saveRequests(reqs);

      // Add alert for provider
      this.addAlert({
        user_id: newReq.provider_id,
        audience: 'provider',
        type: 'request',
        title: 'New Service Request 🚜',
        message: `Farmer ${newReq.farmer_name} requested ${newReq.service_name}.`
      });

      return newReq;
    }

    // 14. Requests /my (Farmer requests)
    if (path === '/requests/my' && method === 'GET') {
      const reqs = this.getRequests();
      const myId = currentUser?.id || 'usr-farmer-01';
      return { requests: reqs.filter(r => r.farmer_id === myId) };
    }

    // 15. Provider Requests
    if (path === '/provider/requests' && method === 'GET') {
      const reqs = this.getRequests();
      const myId = currentUser?.id || 'usr-provider-01';
      return { requests: reqs.filter(r => r.provider_id === myId || !r.provider_id) };
    }

    // 16. Request Status Update (PUT)
    if (path.startsWith('/requests/') && path.endsWith('/status') && method === 'PUT') {
      const reqId = path.split('/')[2];
      const reqs = this.getRequests();
      const r = reqs.find(x => String(x.id) === reqId || x.request_id === reqId);
      if (!r) throw new Error('Request not found.');
      r.status = body.status;
      this.saveRequests(reqs);

      // Add alert for farmer
      this.addAlert({
        user_id: r.farmer_id,
        audience: 'farmer',
        type: 'status',
        title: `Request ${body.status.toUpperCase()} ✅`,
        message: `Your request for ${r.service_name} has been marked as ${body.status}.`
      });

      return r;
    }

    // 17. Alerts GET
    if (path === '/alerts' && method === 'GET') {
      const alerts = this.getAlerts(currentUser?.id, currentUser?.role);
      return { alerts };
    }

    // 18. Alerts Mark Read (PUT)
    if (path.startsWith('/alerts/') && path.endsWith('/read') && method === 'PUT') {
      const alertId = parseInt(path.split('/')[2]);
      const alerts = this.getAlerts();
      const a = alerts.find(x => x.id === alertId);
      if (a) a.is_read = true;
      this.saveAlerts(alerts);
      return { message: 'Marked read.' };
    }

    // 19. Alerts Mark All Read (POST)
    if (path === '/alerts/mark-all-read' && method === 'POST') {
      const alerts = this.getAlerts();
      alerts.forEach(a => a.is_read = true);
      this.saveAlerts(alerts);
      return { message: 'All alerts marked read.' };
    }

    // 20. Admin Dashboard
    if (path === '/admin/dashboard') {
      const users = this.getUsers();
      const farmers = users.filter(u => u.role === 'farmer');
      const providers = users.filter(u => u.role === 'provider' || u.role === 'seller');
      const services = this.getServices();
      const reqs = this.getRequests();
      const totalVolume = reqs.reduce((s, r) => s + Number(r.price || 0), 0);
      return {
        total_farmers: farmers.length,
        active_farmers: farmers.filter(f => f.status === 'active').length,
        total_providers: providers.length,
        active_providers: providers.filter(p => p.status === 'active').length,
        total_services: services.length,
        active_services: services.filter(s => s.available !== false).length,
        total_requests: reqs.length,
        pending_requests: reqs.filter(r => r.status === 'pending').length,
        completed_requests: reqs.filter(r => r.status === 'completed').length,
        total_volume: totalVolume,
        revenue: totalVolume,
        users: users.length,
        products: services.length,
        services: services.length,
        orders: reqs.length,
        pending_orders: reqs.filter(r => r.status === 'pending').length
      };
    }

    // 21. Admin Farmers GET
    if (path.startsWith('/admin/farmers') && method === 'GET') {
      const users = this.getUsers().filter(u => u.role === 'farmer');
      return { farmers: users };
    }

    // 22. Admin Providers GET
    if (path.startsWith('/admin/providers') && method === 'GET') {
      const users = this.getUsers().filter(u => u.role === 'provider' || u.role === 'seller');
      const services = this.getServices();
      users.forEach(p => {
        p.services_count = services.filter(s => s.posted_by === p.id).length;
      });
      return { providers: users };
    }

    // 23. Admin Users GET
    if (path === '/admin/users') {
      return { users: this.getUsers() };
    }

    // 24. Admin User Status Update
    if (path.startsWith('/admin/users/') && path.endsWith('/status') && method === 'PUT') {
      const uid = path.split('/')[3];
      const users = this.getUsers();
      const u = users.find(x => x.id === uid);
      if (!u) throw new Error('User not found.');
      u.status = body.status;
      this.saveUsers(users);
      return u;
    }

    // 25. Admin Services GET
    if (path === '/admin/services' || path === '/admin/listings') {
      return { services: this.getServices(), listings: this.getServices() };
    }

    // 26. Admin Requests GET
    if (path === '/admin/requests' || path === '/admin/orders') {
      return { requests: this.getRequests(), orders: this.getRequests() };
    }

    // 27. Admin Notification POST
    if (path === '/admin/notifications' && method === 'POST') {
      this.addAlert({
        user_id: null,
        audience: body.audience || 'all',
        type: 'system',
        title: body.title || 'Platform Announcement 📢',
        message: body.message
      });
      return { message: 'Notification broadcasted successfully.' };
    }

    // Legacy fallbacks
    if (path.startsWith('/products')) {
      return { products: this.getServices() };
    }
    if (path.startsWith('/orders') && method === 'GET') {
      return { orders: this.getRequests() };
    }

    return { message: 'Action processed successfully' };
  }
};

/**
 * Main API Request function.
 * Tries FastAPI backend first; seamlessly falls back to LocalStorageDB if server is offline.
 */
async function apiRequest(path, options = {}) {
  const token = localStorage.getItem('agro_token');
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;

  const timeoutMs = Number(options.timeoutMs || 3000);
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  let isBackendAvailable = true;
  let res;

  try {
    res = await fetch(`${getApiBase()}${path}`, {
      ...options,
      headers,
      signal: controller.signal
    });
  } catch (error) {
    isBackendAvailable = false;
  } finally {
    clearTimeout(timeout);
  }

  // If backend was reached
  if (isBackendAvailable && res) {
    let data = {};
    try {
      data = await res.json();
    } catch (_) {}

    if (!res.ok) {
      throw new Error(data.detail || data.message || `Request failed (${res.status})`);
    }
    return data;
  }

  // Fallback to LocalStorageDB
  return LocalStorageDB.handleLocalRequest(path, options);
}

// Session state management
function setSession(data) {
  if (data.token) localStorage.setItem('agro_token', data.token);
  if (data.user) {
    localStorage.setItem('agro_user', JSON.stringify(data.user));
    if (data.user.role === 'admin') {
      localStorage.setItem('agro_admin_user', JSON.stringify(data.user));
    }
  }
}

function clearSession() {
  localStorage.removeItem('agro_token');
  localStorage.removeItem('agro_user');
  localStorage.removeItem('agro_admin_user');
}

// Auth API Methods
async function apiLogin(username, password) {
  const data = await apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  setSession(data);
  return data;
}

async function apiRegister(payload) {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

async function apiVerifyRegisterOtp(email, otp) {
  const data = await apiRequest('/auth/register/verify-otp', {
    method: 'POST',
    body: JSON.stringify({ email, otp })
  });
  setSession(data);
  return data;
}

async function apiAdminLogin(username, password) {
  const data = await apiRequest('/admin/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
  setSession(data);
  localStorage.setItem('agro_admin_user', JSON.stringify(data.user));
  return data;
}

async function apiAdminRegister(payload) {
  return apiRequest('/admin/register', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

// Service API Methods
async function apiGetServices(category = '', search = '') {
  let q = '';
  const params = [];
  if (category && category !== 'All') params.push(`category=${encodeURIComponent(category)}`);
  if (search) params.push(`q=${encodeURIComponent(search)}`);
  if (params.length > 0) q = '?' + params.join('&');
  return apiRequest(`/services${q}`);
}

async function apiGetMyServices() {
  return apiRequest('/services/my');
}

async function apiCreateService(payload) {
  return apiRequest('/services', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

async function apiUpdateService(id, payload) {
  return apiRequest(`/services/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload)
  });
}

async function apiDeleteService(id) {
  return apiRequest(`/services/${id}`, {
    method: 'DELETE'
  });
}

async function apiToggleServiceStatus(id, status) {
  return apiRequest(`/services/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status })
  });
}

// Service Request API Methods
async function apiCreateServiceRequest(payload) {
  return apiRequest('/requests', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

async function apiGetMyRequests() {
  return apiRequest('/requests/my');
}

async function apiGetProviderRequests() {
  return apiRequest('/provider/requests');
}

async function apiUpdateRequestStatus(id, status) {
  return apiRequest(`/requests/${encodeURIComponent(id)}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status })
  });
}

// Alerts API Methods
async function apiGetAlerts() {
  return apiRequest('/alerts');
}

async function apiMarkAlertRead(id) {
  return apiRequest(`/alerts/${id}/read`, { method: 'PUT' });
}

async function apiMarkAllAlertsRead() {
  return apiRequest('/alerts/mark-all-read', { method: 'POST' });
}
