/**
 * AgroTech Bilingual Translation Engine (English + Hindi / हिंदी)
 * Provides centralized dictionary, persistent language selection, and reactive DOM translation.
 */

const AgroI18n = {
  currentLang: localStorage.getItem('agro_lang') || 'en',

  translations: {
    en: {
      // General & Brand
      'app.name': 'AgroTECH',
      'app.tagline': 'Smart Agricultural Platform',
      'app.hero_badge': '🌱 Smart Agricultural Mechanization Platform',
      'lang.switch': 'Language',
      'lang.en': 'English',
      'lang.hi': 'हिंदी (Hindi)',

      // Roles
      'role.farmer': 'Farmer',
      'role.provider': 'Service Provider',
      'role.admin': 'Administrator',
      'role.all': 'All Users',
      'role.badge_farmer': '🌾 Farmer',
      'role.badge_provider': '🚜 Service Provider',
      'role.badge_admin': '🛡️ Administrator',

      // Navigation - Header
      'nav.about': 'About',
      'nav.crop_calendar': 'Crop Calendar',
      'nav.faq': 'F&Q',
      'nav.admin_login': 'Admin Login',
      'nav.farmer_login': 'Farmer Login',
      'nav.provider_login': 'Provider Login',

      // Navigation - Farmer
      'nav.home': 'Dashboard',
      'nav.find_services': 'Find Services',
      'nav.my_requests': 'My Requests',
      'nav.alerts': 'Alerts',
      'nav.help': 'Help & Support',
      'nav.profile': 'Profile',
      'nav.wishlist': 'Wishlist',
      'nav.logout': 'Logout',
      'nav.login': 'Login',
      'nav.register': 'Register',

      // Navigation - Provider
      'nav.provider_dashboard': 'Dashboard',
      'nav.my_services': 'My Services',
      'nav.add_service': 'Add Service',
      'nav.provider_requests': 'Requests',
      'nav.provider_alerts': 'Alerts',
      'nav.provider_help': 'Help & Guides',
      'nav.provider_profile': 'Provider Profile',

      // Navigation - Admin
      'nav.admin_dashboard': 'Dashboard',
      'nav.admin_farmers': 'Farmers',
      'nav.admin_providers': 'Providers',
      'nav.admin_services': 'Services',
      'nav.admin_requests': 'Requests',
      'nav.admin_alerts': 'Alerts & Broadcasts',
      'nav.admin_reports': 'Reports & Analytics',
      'nav.admin_complaints': 'Complaints & Support',
      'nav.admin_settings': 'Settings',

      // Farmer Dashboard
      'farmer.greeting_morning': 'Good morning! 🌤',
      'farmer.greeting_afternoon': 'Good afternoon! ☀️',
      'farmer.greeting_evening': 'Good evening! 🌙',
      'farmer.what_needed': 'What do you need today?',
      'farmer.search_placeholder': 'Search machinery, seeds, fertilizers, irrigation...',
      'farmer.search_btn': 'Search',
      'farmer.stat_services': 'Available Services',
      'farmer.stat_pending': 'Pending Requests',
      'farmer.stat_accepted': 'Accepted Requests',
      'farmer.stat_completed': 'Completed Services',
      'farmer.stat_spent': 'Total Spent',
      'farmer.featured_services': '🚜 Available Services & Equipment',
      'farmer.view_all': 'View All Services →',
      'farmer.quick_actions': 'Quick Actions',
      'farmer.recent_alerts': 'Recent Alerts',
      'farmer.no_alerts': 'No new alerts at the moment.',
      'farmer.request_service': 'Request Service',
      'farmer.send_request': 'Send Service Request',
      'farmer.book_now': 'Book Now',

      // Service Categories
      'cat.all': 'All Categories',
      'cat.machinery': 'Machinery',
      'cat.irrigation': 'Irrigation',
      'cat.fertilizer': 'Fertilizers',
      'cat.seeds': 'Seeds',
      'cat.transport': 'Transport',
      'cat.other': 'Other Services',

      // Find Services / Product Search
      'services.find_title': '🔍 Find Agricultural Services & Machinery',
      'services.find_subtitle': 'Browse verified providers, tractors, harvesters, and farm supplies',
      'services.results_count': 'Showing {count} available services',
      'services.provider_label': 'Provider',
      'services.location_label': 'Location',
      'services.price_label': 'Price',
      'services.availability': 'Availability',
      'services.available': 'Available',
      'services.unavailable': 'Unavailable',
      'services.sort_default': 'Sort: Default',
      'services.sort_low_high': 'Price: Low to High',
      'services.sort_high_low': 'Price: High to Low',
      'services.sort_rating': 'Top Rated',
      'services.request_modal_title': 'Send Service Request',
      'services.required_acres_qty': 'Quantity / Acres / Duration *',
      'services.request_date': 'Preferred Date *',
      'services.service_address': 'Farm / Delivery Address *',
      'services.request_notes': 'Additional Notes or Requirements',
      'services.submit_request': 'Submit Request to Provider →',
      'services.confirm_success': 'Your service request has been sent to the provider!',

      // Farmer Requests Page
      'requests.title': '📋 My Service Requests',
      'requests.subtitle': 'Track the real-time status of your service requests and bookings',
      'requests.tab_all': 'All Requests',
      'requests.tab_pending': '⏳ Pending',
      'requests.tab_accepted': '✅ Accepted',
      'requests.tab_rejected': '❌ Rejected',
      'requests.tab_completed': '🏁 Completed',
      'requests.tab_cancelled': '🚫 Cancelled',
      'requests.empty_title': 'No Requests Found',
      'requests.empty_desc': 'You haven\'t made any service requests yet. Browse available services to get started!',
      'requests.browse_btn': 'Find Services →',
      'requests.provider_contact': 'Provider Contact',
      'requests.requested_on': 'Requested On',
      'requests.status': 'Status',
      'requests.est_cost': 'Total Price',

      // Provider Dashboard
      'provider.dash_title': 'Provider Dashboard',
      'provider.dash_subtitle': 'Manage your equipment, listings, and customer bookings',
      'provider.stat_total_services': 'Total Services',
      'provider.stat_active_services': 'Active Listings',
      'provider.stat_pending_requests': 'Pending Requests',
      'provider.stat_accepted_requests': 'Accepted Requests',
      'provider.stat_completed_requests': 'Completed Jobs',
      'provider.stat_earnings': 'Total Earnings',
      'provider.recent_requests': '📥 Recent Service Requests',
      'provider.no_requests': 'No incoming requests yet.',
      'provider.manage_services': 'Manage My Services →',
      'provider.add_new_service': '➕ Add New Service',

      // Provider My Services
      'my_services.title': '🚜 My Services & Equipment',
      'my_services.subtitle': 'Create, edit, toggle availability, or remove your listings',
      'my_services.add_btn': '➕ Add New Service',
      'my_services.empty_title': 'No Services Listed Yet',
      'my_services.empty_desc': 'Start earning by offering your machinery, tools, or farm services.',
      'my_services.active': 'Active',
      'my_services.inactive': 'Inactive',
      'my_services.edit': 'Edit',
      'my_services.delete': 'Delete',
      'my_services.delete_confirm_title': 'Delete this service?',
      'my_services.delete_confirm_desc': 'This action cannot be undone. The listing will be removed permanently.',
      'my_services.yes_delete': 'Yes, Delete',
      'my_services.cancel': 'Cancel',
      'my_services.save_changes': 'Save Changes',
      'my_services.edit_modal_title': 'Edit Service Details',

      // Provider Add Service
      'add_service.title': '➕ List a New Service',
      'add_service.subtitle': 'Help fellow farmers and earn by sharing your agricultural resources',
      'add_service.form_title': 'Service Details',
      'add_service.name_label': 'Service / Equipment Name *',
      'add_service.name_placeholder': 'e.g. Mahindra 575 DI Tractor Rental',
      'add_service.category_label': 'Category *',
      'add_service.category_select': '-- Select Category --',
      'add_service.price_label': 'Price (₹) *',
      'add_service.price_placeholder': 'e.g. 800',
      'add_service.unit_label': 'Price Unit *',
      'add_service.unit_per_day': 'Per Day',
      'add_service.unit_per_acre': 'Per Acre',
      'add_service.unit_per_kg': 'Per KG',
      'add_service.unit_per_bag': 'Per Bag',
      'add_service.unit_per_trip': 'Per Trip',
      'add_service.unit_per_kit': 'Per Kit',
      'add_service.unit_per_hour': 'Per Hour',
      'add_service.location_label': 'Service Location / Base *',
      'add_service.location_placeholder': 'e.g. Indore, Madhya Pradesh',
      'add_service.contact_label': 'Provider Contact Number',
      'add_service.contact_placeholder': 'e.g. 9876543210',
      'add_service.description_label': 'Detailed Description *',
      'add_service.description_placeholder': 'Describe condition, HP/capacity, operator included, terms...',
      'add_service.image_label': 'Service / Equipment Photo',
      'add_service.upload_text': 'Click or drag image to upload',
      'add_service.upload_hint': 'JPG, PNG, WEBP — Max 5MB',
      'add_service.publish_btn': '🚀 Publish Service Listing',
      'add_service.tips_title': '💡 Tips for higher bookings',
      'add_service.tip1': 'Use specific equipment models and clear specifications.',
      'add_service.tip2': 'Mention if fuel, driver, or operator is included.',
      'add_service.tip3': 'Upload authentic, bright photos of your actual machinery.',
      'add_service.tip4': 'Keep pricing competitive with local market rates.',

      // Provider Requests Page
      'prov_req.title': '📥 Customer Service Requests',
      'prov_req.subtitle': 'Review requests from farmers, accept or reject, and mark jobs completed',
      'prov_req.farmer_name': 'Farmer Name',
      'prov_req.farmer_contact': 'Contact',
      'prov_req.service_name': 'Requested Service',
      'prov_req.request_date': 'Date Requested',
      'prov_req.location': 'Farm Location',
      'prov_req.notes': 'Customer Notes',
      'prov_req.status': 'Current Status',
      'prov_req.action_accept': '✅ Accept Request',
      'prov_req.action_reject': '❌ Reject Request',
      'prov_req.action_complete': '🏁 Mark Completed',
      'prov_req.accepted_msg': 'Request accepted! Farmer has been notified.',
      'prov_req.rejected_msg': 'Request rejected. Farmer has been notified.',
      'prov_req.completed_msg': 'Job marked as completed! Thank you.',
      'prov_req.empty_title': 'No Requests Received',
      'prov_req.empty_desc': 'When farmers book your services, their requests will appear here.',

      // Location & Nearest Options
      'location.title': 'Location & Distance',
      'location.my_location': 'My Location',
      'location.detect_gps': 'Detect Live GPS',
      'location.detecting': 'Detecting GPS...',
      'location.gps_success': 'Location detected via GPS!',
      'location.gps_error': 'GPS unavailable. Selected default location.',
      'location.nearest_first': '📍 Nearest First',
      'location.km_away': '{km} km away',
      'location.nearest_badge': '⚡ Nearest',
      'location.filter_distance': 'Distance Filter',
      'location.within_10km': 'Within 10 km',
      'location.within_25km': 'Within 25 km',
      'location.within_50km': 'Within 50 km',
      'location.all_distances': 'All Distances',
      'location.change_location': 'Change Location',
      'location.select_city': 'Select District / City',
      'location.showing_near': 'Showing equipment & services near',

      // Work Done & Work Completion Workflow
      'work_done.mark_done': '✅ Mark Work Done',
      'work_done.confirm_done': '✅ Confirm Work Done',
      'work_done.completed_badge': '🏁 Work Completed',
      'work_done.modal_title': 'Confirm Work Completion',
      'work_done.rating_label': 'Rate the Service (1-5 Stars)',
      'work_done.feedback_label': 'Your Review / Feedback (Optional)',
      'work_done.submit_btn': 'Confirm & Mark Completed',
      'work_done.provider_success': 'Work marked as completed! Farmer has been notified.',
      'work_done.farmer_success': 'Work marked as completed! Provider has been notified.',
      'work_done.confirm_prompt': 'Are you sure this agricultural job is completed?',
      'work_done.already_done': '✨ Work has been marked as Completed',

      // Provider Help
      'prov_help.title': '❓ Provider Guide & Help',
      'prov_help.subtitle': 'Learn how to optimize listings, handle customer requests, and grow your revenue',
      'prov_help.faq1_q': 'How do I add and manage my farm equipment?',
      'prov_help.faq1_a': 'Go to "Add Service" in your navigation bar, fill in the details (equipment name, pricing, unit, high quality photo, location) and click Publish. You can manage, update or deactivate listings anytime from "My Services".',
      'prov_help.faq2_q': 'How do I get notified of new customer requests?',
      'prov_help.faq2_a': 'Whenever a farmer books your service, it immediately appears in your "Requests" tab and an alert is added to your "Alerts" center.',
      'prov_help.faq3_q': 'What happens when I accept a request?',
      'prov_help.faq3_a': 'Accepting a request sends an instant confirmation alert to the farmer with your contact details so you both can coordinate delivery or service execution.',
      'prov_help.faq4_q': 'How do I contact platform support?',
      'prov_help.faq4_a': 'You can submit the support inquiry form below or call the AgroTech helpline at +91 11 1234 5678.',

      // Admin Panel
      'admin.portal_title': 'Admin Control Panel',
      'admin.portal_subtitle': 'Comprehensive management for Farmers, Providers, Services, Requests & Analytics',
      'admin.stat_total_farmers': 'Total Farmers',
      'admin.stat_active_farmers': 'Active Farmers',
      'admin.stat_total_providers': 'Total Providers',
      'admin.stat_active_providers': 'Active Providers',
      'admin.stat_total_services': 'Total Services',
      'admin.stat_pending_requests': 'Pending Requests',
      'admin.stat_completed_requests': 'Completed Requests',
      'admin.stat_revenue': 'Total Volume',
      'admin.farmers_tab_all': 'All Farmers',
      'admin.farmers_tab_active': 'Active Farmers',
      'admin.farmers_tab_inactive': 'Blocked / Inactive Farmers',
      'admin.providers_tab_all': 'All Providers',
      'admin.providers_tab_active': 'Active Providers',
      'admin.providers_tab_inactive': 'Blocked / Inactive Providers',
      'admin.search_farmers': 'Search farmers by name, email, phone, location...',
      'admin.search_providers': 'Search providers by name, email, phone, location...',
      'admin.search_services': 'Search services by name, category, provider...',
      'admin.table_name': 'Name',
      'admin.table_email': 'Email',
      'admin.table_phone': 'Phone',
      'admin.table_location': 'Location',
      'admin.table_status': 'Status',
      'admin.table_joined': 'Joined Date',
      'admin.table_services_count': 'Services Count',
      'admin.table_actions': 'Actions',
      'admin.btn_activate': 'Activate',
      'admin.btn_block': 'Block User',
      'admin.btn_delete': 'Delete',
      'admin.btn_view_details': 'View Details',
      'admin.send_broadcast_title': 'Send System Notification',
      'admin.broadcast_audience': 'Target Audience',
      'admin.broadcast_message': 'Message Content',
      'admin.broadcast_btn': '📣 Send Announcement',
      'admin.confirm_user_status': 'Are you sure you want to change this user\'s status?',

      // Alerts & Notifications
      'alerts.title': '🔔 Notifications & Alerts',
      'alerts.subtitle': 'Stay informed on order updates, booking responses, and announcements',
      'alerts.mark_all_read': '✓ Mark All Read',
      'alerts.tab_all': 'All Alerts',
      'alerts.tab_requests': '📦 Requests',
      'alerts.tab_system': '📢 System',
      'alerts.empty': 'You have no alerts at this time.',

      // Profile & Account
      'profile.title': '👤 My Account Profile',
      'profile.subtitle': 'Manage your personal details, contact information, and preferences',
      'profile.edit_btn': '✏️ Edit Profile',
      'profile.save_btn': '💾 Save Profile',
      'profile.cancel_btn': '✕ Cancel',
      'profile.full_name': 'Full Name',
      'profile.email': 'Email Address',
      'profile.phone': 'Phone Number',
      'profile.location': 'Address / Location',
      'profile.farming_details': 'Farming / Business Information',
      'profile.role_label': 'Account Role',
      'profile.status_label': 'Account Status',
      'profile.updated_success': 'Profile updated successfully! ✅',

      // Authentication (Login / Register)
      'auth.login_title': 'Login to AgroTECH',
      'auth.login_subtitle': 'Sign in to access your role-based dashboard',
      'auth.username_label': 'Email / Username / Phone',
      'auth.password_label': 'Password',
      'auth.login_btn': 'Login →',
      'auth.no_account': 'Don\'t have an account?',
      'auth.register_now': 'Register here',
      'auth.register_title': 'Create Your AgroTECH Account',
      'auth.register_subtitle': 'Choose your role to get started with smart farming',
      'auth.select_role': 'Select Your Role *',
      'auth.role_farmer_desc': 'I want to find & rent machinery, buy seeds, and book services.',
      'auth.role_provider_desc': 'I have equipment, machinery, transport, or supplies to offer.',
      'auth.full_name_label': 'Full Name *',
      'auth.contact_label': 'Contact Phone Number (10 digits) *',
      'auth.email_label': 'Email Address *',
      'auth.confirm_pw_label': 'Confirm Password *',
      'auth.state_label': 'State *',
      'auth.address_label': 'Village / Town / District',
      'auth.pincode_label': 'Pincode',
      'auth.otp_label': 'Email Verification OTP *',
      'auth.send_otp_btn': 'Send Verification OTP →',
      'auth.verify_create_btn': 'Verify OTP & Create Account →',
      'auth.have_account': 'Already registered?',
      'auth.admin_portal_link': '🛡️ Admin Login Portal',

      // Common Actions & Form Validation
      'common.loading': 'Loading...',
      'common.save': 'Save',
      'common.cancel': 'Cancel',
      'common.submit': 'Submit',
      'common.delete': 'Delete',
      'common.close': 'Close',
      'common.success': 'Success',
      'common.error': 'Error',
      'common.confirm': 'Confirm',
      'common.yes': 'Yes',
      'common.no': 'No',
      'common.back': '← Back',
      'common.view': 'View',
      'common.fill_required': 'Please fill in all required fields.',
      'common.unauthorized': 'You do not have permission to access this page.',
      'common.logged_out': 'Logged out successfully.',

      // Landing Page & Hero Section
      'landing.headline_1': 'Smart Machinery.',
      'landing.headline_2': 'Smarter Farming.',
      'landing.hero_desc': 'AgroTech connects farmers with verified agricultural machinery owners and rural service providers — enabling faster ploughing, harvesting, drip irrigation, and crop transport with transparent per-acre pricing.',
      'landing.find_machinery_btn': '🚜 Find Machinery Near You →',
      'landing.how_it_works_btn': '⚡ Explore How It Works',
      'landing.farmer_portal_btn': '🌾 Farmer Portal',
      'landing.provider_portal_btn': '🚜 Sahyogi Portal',
      'landing.admin_portal_btn': '🛡️ Admin Portal',
      'landing.stat_verified_machines': 'On-Demand Machinery',
      'landing.stat_farmers': 'Fair Acre Pricing',
      'landing.stat_hubs': 'Direct Sahyogi Connect',
      'landing.stat_value': 'Pay After Work Guarantee',
      'landing.pillar_machines_title': 'On-Demand Machinery',
      'landing.pillar_machines_desc': 'Instant access to tractors, harvesters & implements within your village radius.',
      'landing.pillar_pricing_title': 'Transparent Acre Rates',
      'landing.pillar_pricing_desc': 'Standardized per-acre and per-day pricing with zero middlemen commission.',
      'landing.pillar_dispatch_title': 'Instant Sahyogi Dispatch',
      'landing.pillar_dispatch_desc': 'Real-time job confirmation and direct farmer-to-operator communication.',
      'landing.pillar_security_title': 'Pay After Inspection',
      'landing.pillar_security_desc': 'Pay securely via UPI or Cash only after work is verified on your field.',
      'landing.prob_title': 'From Machinery Scarcity to Smart Digital Booking',
      'landing.prob_subtitle': 'Solving real, daily challenges of Indian farmers through on-demand machinery access',
      'landing.traditional_way': 'Traditional Farming Challenges',
      'landing.agrotech_way': 'The AgroTech Smart Solution',
      'landing.how_title': 'How AgroTech Works',
      'landing.how_subtitle': '5 simple steps from machinery discovery to completed farm operations',
      'landing.step1_title': '01 — Discover',
      'landing.step1_desc': 'Search tractors, harvesters, rotavators, and farm inputs available in your local radius.',
      'landing.step2_title': '02 — Compare',
      'landing.step2_desc': 'Review verified provider ratings, equipment HP, transparent per-acre rates, and specs.',
      'landing.step3_title': '03 — Request',
      'landing.step3_desc': 'Submit your land acreage and preferred schedule with one click and zero hassle.',
      'landing.step4_title': '04 — Connect',
      'landing.step4_desc': 'Verified Sahyogi confirms, dispatches equipment, and updates you via instant SMS & app alert.',
      'landing.step5_title': '05 — Farm Smarter',
      'landing.step5_desc': 'Precision farm operations completed on time. Pay securely with Cash or UPI upon completion.',
      'landing.calc_title': 'Smart Acre & Machinery Cost Estimator',
      'landing.calc_subtitle': 'Calculate instant rental estimates, time saved, and farm efficiency for your land',
      'landing.calc_select_machine': 'Select Machinery Type',
      'landing.calc_land_acres': 'Land Area (Acres):',
      'landing.calc_est_total': 'Estimated Rental Cost:',
      'landing.calc_time_saved': 'Estimated Time Saved:',
      'landing.calc_book_cta': 'Book This Machine Now →',
      'landing.farmer_first_title': 'Technology Built for the Reality of Indian Agriculture',
      'landing.sahyogi_title': 'Empowering Rural Machinery Owners & Agri-Entrepreneurs',
      'landing.sahyogi_desc': 'Turn idle tractors and implements into steady seasonal income while serving your community.',
      'landing.cta_title': 'Ready to Make Farming Smarter?',
      'landing.cta_subtitle': 'Join thousands of farmers and verified machinery partners growing together on AgroTech.',
      'landing.cta_farmer': '🌾 Start Farming Smarter (Farmer)',
      'landing.cta_sahyogi': '🚜 List Your Machinery (Sahyogi)'
    },

    hi: {
      // General & Brand
      'app.name': 'एग्रोटेक (AgroTECH)',
      'app.tagline': 'स्मार्ट कृषि मंच',
      'app.hero_badge': '🌱 आधुनिक कृषि यंत्रीकरण मंच',
      'lang.switch': 'भाषा (Language)',
      'lang.en': 'English (अंग्रेजी)',
      'lang.hi': 'हिंदी (Hindi)',

      // Roles
      'role.farmer': 'किसान (Farmer)',
      'role.provider': 'सेवा प्रदाता (Provider)',
      'role.admin': 'प्रशासक (Admin)',
      'role.all': 'सभी उपयोगकर्ता',
      'role.badge_farmer': '🌾 किसान (Farmer)',
      'role.badge_provider': '🚜 सेवा प्रदाता (Provider)',
      'role.badge_admin': '🛡️ प्रशासक (Admin)',

      // Navigation - Header
      'nav.about': 'परिचय (About)',
      'nav.crop_calendar': 'फसल कैलेंडर',
      'nav.faq': 'सामान्य प्रश्न (F&Q)',
      'nav.admin_login': 'प्रशासक लॉगिन',
      'nav.farmer_login': 'किसान लॉगिन',
      'nav.provider_login': 'प्रदाता लॉगिन',

      // Navigation - Farmer
      'nav.home': 'डैशबोर्ड',
      'nav.find_services': 'सेवाएं खोजें',
      'nav.my_requests': 'मेरे अनुरोध',
      'nav.alerts': 'अलर्ट / सूचनाएं',
      'nav.help': 'सहायता एवं संपर्क',
      'nav.profile': 'मेरी प्रोफाइल',
      'nav.wishlist': 'विशलिस्ट',
      'nav.logout': 'लॉगआउट',
      'nav.login': 'लॉगिन',
      'nav.register': 'पंजीकरण',

      // Navigation - Provider
      'nav.provider_dashboard': 'डैशबोर्ड',
      'nav.my_services': 'मेरी सेवाएं',
      'nav.add_service': 'सेवा जोड़ें',
      'nav.provider_requests': 'प्राप्त अनुरोध',
      'nav.provider_alerts': 'अलर्ट / सूचनाएं',
      'nav.provider_help': 'मार्गदर्शिका एवं सहायता',
      'nav.provider_profile': 'प्रदाता प्रोफाइल',

      // Navigation - Admin
      'nav.admin_dashboard': 'डैशबोर्ड',
      'nav.admin_farmers': 'किसान प्रबंधन',
      'nav.admin_providers': 'प्रदाता प्रबंधन',
      'nav.admin_services': 'सेवाएं प्रबंधन',
      'nav.admin_requests': 'अनुरोध प्रबंधन',
      'nav.admin_alerts': 'अलर्ट एवं घोषणाएं',
      'nav.admin_reports': 'रिपोर्ट एवं एनालिटिक्स',
      'nav.admin_complaints': 'शिकायतें एवं सहायता',
      'nav.admin_settings': 'सेटिंग्स',

      // Farmer Dashboard
      'farmer.greeting_morning': 'शुभ प्रभात! 🌤',
      'farmer.greeting_afternoon': 'शुभ दोपहर! ☀️',
      'farmer.greeting_evening': 'शुभ संध्या! 🌙',
      'farmer.what_needed': 'आज आपको क्या चाहिए?',
      'farmer.search_placeholder': 'मशीनरी, बीज, खाद, सिंचाई खोजें...',
      'farmer.search_btn': 'खोजें',
      'farmer.stat_services': 'उपलब्ध सेवाएं',
      'farmer.stat_pending': 'लंबित अनुरोध',
      'farmer.stat_accepted': 'स्वीकृत अनुरोध',
      'farmer.stat_completed': 'पूर्ण सेवाएं',
      'farmer.stat_spent': 'कुल खर्च',
      'farmer.featured_services': '🚜 उपलब्ध सेवाएं एवं कृषि उपकरण',
      'farmer.view_all': 'सभी सेवाएं देखें →',
      'farmer.quick_actions': 'त्वरित कार्य',
      'farmer.recent_alerts': 'हालिया अलर्ट',
      'farmer.no_alerts': 'वर्तमान में कोई नया अलर्ट नहीं है।',
      'farmer.request_service': 'सेवा का अनुरोध करें',
      'farmer.send_request': 'सेवा अनुरोध भेजें',
      'farmer.book_now': 'अभी बुक करें',

      // Service Categories
      'cat.all': 'सभी श्रेणियां',
      'cat.machinery': 'कृषि मशीनरी',
      'cat.irrigation': 'सिंचाई उपकरण',
      'cat.fertilizer': 'उर्वरक / खाद',
      'cat.seeds': 'उन्नत बीज',
      'cat.transport': 'फसल परिवहन',
      'cat.other': 'अन्य सेवाएं',

      // Find Services / Product Search
      'services.find_title': '🔍 कृषि सेवाएं एवं उपकरण खोजें',
      'services.find_subtitle': 'सत्यापित प्रदाताओं से ट्रैक्टर, हार्वेस्टर एवं सामग्री किराए पर लें',
      'services.results_count': '{count} उपलब्ध सेवाएं दिखाई जा रही हैं',
      'services.provider_label': 'प्रदाता',
      'services.location_label': 'स्थान',
      'services.price_label': 'मूल्य',
      'services.availability': 'उपलब्धता',
      'services.available': 'उपलब्ध',
      'services.unavailable': 'अनुपलब्ध',
      'services.sort_default': 'क्रम: डिफ़ॉल्ट',
      'services.sort_low_high': 'मूल्य: कम से अधिक',
      'services.sort_high_low': 'मूल्य: अधिक से कम',
      'services.sort_rating': 'सर्वोच्च रेटिंग',
      'services.request_modal_title': 'सेवा अनुरोध फॉर्म',
      'services.required_acres_qty': 'मात्रा / एकड़ / अवधि *',
      'services.request_date': 'वांछित तिथि *',
      'services.service_address': 'खेत / डिलीवरी का पता *',
      'services.request_notes': 'अतिरिक्त विवरण या आवश्यकताएं',
      'services.submit_request': 'प्रदाता को अनुरोध भेजें →',
      'services.confirm_success': 'आपका सेवा अनुरोध प्रदाता को भेज दिया गया है!',

      // Farmer Requests Page
      'requests.title': '📋 मेरे सेवा अनुरोध',
      'requests.subtitle': 'अपने सभी सेवा अनुरोधों और बुकिंग की स्थिति देखें',
      'requests.tab_all': 'सभी अनुरोध',
      'requests.tab_pending': '⏳ लंबित (Pending)',
      'requests.tab_accepted': '✅ स्वीकृत (Accepted)',
      'requests.tab_rejected': '❌ अस्वीकृत (Rejected)',
      'requests.tab_completed': '🏁 पूर्ण (Completed)',
      'requests.tab_cancelled': '🚫 रद्द (Cancelled)',
      'requests.empty_title': 'कोई अनुरोध नहीं मिला',
      'requests.empty_desc': 'आपने अभी तक कोई सेवा अनुरोध नहीं किया है। सेवाएं खोजने के लिए ब्राउज़ करें!',
      'requests.browse_btn': 'सेवाएं खोजें →',
      'requests.provider_contact': 'प्रदाता संपर्क',
      'requests.requested_on': 'अनुरोध तिथि',
      'requests.status': 'स्थिति',
      'requests.est_cost': 'कुल मूल्य',

      // Provider Dashboard
      'provider.dash_title': 'सेवा प्रदाता डैशबोर्ड',
      'provider.dash_subtitle': 'अपने कृषि उपकरण, लिस्टिंग और ग्राहक बुकिंग का प्रबंधन करें',
      'provider.stat_total_services': 'कुल सेवाएं',
      'provider.stat_active_services': 'सक्रिय लिस्टिंग',
      'provider.stat_pending_requests': 'लंबित अनुरोध',
      'provider.stat_accepted_requests': 'स्वीकृत अनुरोध',
      'provider.stat_completed_requests': 'पूर्ण कार्य',
      'provider.stat_earnings': 'कुल कमाई',
      'provider.recent_requests': '📥 हालिया सेवा अनुरोध',
      'provider.no_requests': 'अभी तक कोई नया अनुरोध नहीं आया है।',
      'provider.manage_services': 'मेरी सेवाएं प्रबंधित करें →',
      'provider.add_new_service': '➕ नई सेवा जोड़ें',

      // Provider My Services
      'my_services.title': '🚜 मेरी सेवाएं एवं उपकरण',
      'my_services.subtitle': 'अपनी लिस्टिंग जोड़ें, संपादित करें, उपलब्धता बदलें या हटाएं',
      'my_services.add_btn': '➕ नई सेवा जोड़ें',
      'my_services.empty_title': 'कोई सेवा सूचीबद्ध नहीं है',
      'my_services.empty_desc': 'अपने कृषि उपकरण या सेवाएं साझा करके कमाई शुरू करें।',
      'my_services.active': 'सक्रिय (Active)',
      'my_services.inactive': 'निष्क्रिय (Inactive)',
      'my_services.edit': 'संपादित करें',
      'my_services.delete': 'हटाएं',
      'my_services.delete_confirm_title': 'क्या आप इस सेवा को हटाना चाहते हैं?',
      'my_services.delete_confirm_desc': 'यह क्रिया पूर्ववत नहीं की जा सकती। सेवा हमेशा के लिए हट जाएगी।',
      'my_services.yes_delete': 'हाँ, हटाएं',
      'my_services.cancel': 'रद्द करें',
      'my_services.save_changes': 'बदलाव सहेजें',
      'my_services.edit_modal_title': 'सेवा विवरण संपादित करें',

      // Provider Add Service
      'add_service.title': '➕ नई सेवा जोड़ें',
      'add_service.subtitle': 'साथी किसानों की मदद करें और अपने कृषि संसाधन साझा करके कमाएं',
      'add_service.form_title': 'सेवा का विवरण',
      'add_service.name_label': 'सेवा / उपकरण का नाम *',
      'add_service.name_placeholder': 'उदा. महिंद्रा 575 DI ट्रैक्टर किराया',
      'add_service.category_label': 'श्रेणी *',
      'add_service.category_select': '-- श्रेणी चुनें --',
      'add_service.price_label': 'मूल्य (₹) *',
      'add_service.price_placeholder': 'उदा. 800',
      'add_service.unit_label': 'मूल्य इकाई *',
      'add_service.unit_per_day': 'प्रति दिन (Per Day)',
      'add_service.unit_per_acre': 'प्रति एकड़ (Per Acre)',
      'add_service.unit_per_kg': 'प्रति किग्रा (Per KG)',
      'add_service.unit_per_bag': 'प्रति बोरी (Per Bag)',
      'add_service.unit_per_trip': 'प्रति ट्रिप (Per Trip)',
      'add_service.unit_per_kit': 'प्रति किट (Per Kit)',
      'add_service.unit_per_hour': 'प्रति घंटा (Per Hour)',
      'add_service.location_label': 'सेवा स्थान / केंद्र *',
      'add_service.location_placeholder': 'उदा. इंदौर, मध्य प्रदेश',
      'add_service.contact_label': 'प्रदाता संपर्क नंबर',
      'add_service.contact_placeholder': 'उदा. 9876543210',
      'add_service.description_label': 'विस्तृत विवरण *',
      'add_service.description_placeholder': 'उपकरण की स्थिति, क्षमता, ऑपरेटर शामिल है या नहीं, शर्तें लिखें...',
      'add_service.image_label': 'उपकरण / सेवा की तस्वीर',
      'add_service.upload_text': 'तस्वीर अपलोड करने के लिए क्लिक करें',
      'add_service.upload_hint': 'JPG, PNG, WEBP — अधिकतम 5MB',
      'add_service.publish_btn': '🚀 सेवा प्रकाशित करें',
      'add_service.tips_title': '💡 अधिक बुकिंग पाने के लिए सुझाव',
      'add_service.tip1': 'उपकरण का सही मॉडल और विशेषताएं स्पष्ट लिखें।',
      'add_service.tip2': 'बताएं कि ड्राइवर या ऑपरेटर साथ में उपलब्ध है या नहीं।',
      'add_service.tip3': 'अपने असली उपकरण की साफ और स्पष्ट फोटो लगाएं।',
      'add_service.tip4': 'स्थानीय बाजार के अनुसार उचित मूल्य निर्धारित करें।',

      // Provider Requests Page
      'prov_req.title': '📥 किसान सेवा अनुरोध',
      'prov_req.subtitle': 'किसानों से प्राप्त अनुरोध देखें, स्वीकार या अस्वीकार करें और कार्य पूर्ण करें',
      'prov_req.farmer_name': 'किसान का नाम',
      'prov_req.farmer_contact': 'संपर्क नंबर',
      'prov_req.service_name': 'अनुरोधित सेवा',
      'prov_req.request_date': 'अनुरोध तिथि',
      'prov_req.location': 'खेत का स्थान',
      'prov_req.notes': 'विशेष निर्देश / नोट्स',
      'prov_req.status': 'वर्तमान स्थिति',
      'prov_req.action_accept': '✅ अनुरोध स्वीकार करें',
      'prov_req.action_reject': '❌ अनुरोध अस्वीकार करें',
      'prov_req.action_complete': '🏁 कार्य पूर्ण चिन्हित करें',
      'prov_req.accepted_msg': 'अनुरोध स्वीकार कर लिया गया! किसान को सूचित कर दिया गया है।',
      'prov_req.rejected_msg': 'अनुरोध अस्वीकार कर दिया गया। किसान को सूचित कर दिया गया है।',
      'prov_req.completed_msg': 'कार्य पूर्ण चिन्हित हो गया! धन्यवाद।',
      'prov_req.empty_title': 'कोई अनुरोध प्राप्त नहीं हुआ',
      'prov_req.empty_desc': 'जब किसान आपकी सेवाओं को बुक करेंगे, तो उनके अनुरोध यहाँ दिखाई देंगे।',

      // Location & Nearest Options
      'location.title': 'स्थान एवं दूरी (Location & Distance)',
      'location.my_location': 'मेरी लोकेशन',
      'location.detect_gps': '📍 लाइव जीपीएस पहचानें',
      'location.detecting': 'जीपीएस से लोकेशन खोजी जा रही है...',
      'location.gps_success': 'जीपीएस द्वारा लोकेशन सफलतापूर्वक प्राप्त हुई!',
      'location.gps_error': 'जीपीएस उपलब्ध नहीं है। डिफ़ॉल्ट स्थान चुना गया।',
      'location.nearest_first': '📍 निकटतम सेवाएं पहले',
      'location.km_away': '{km} किमी दूर',
      'location.nearest_badge': '⚡ निकटतम',
      'location.filter_distance': 'दूरी फ़िल्टर',
      'location.within_10km': '10 किमी के भीतर',
      'location.within_25km': '25 किमी के भीतर',
      'location.within_50km': '50 किमी के भीतर',
      'location.all_distances': 'सभी दूरियां',
      'location.change_location': 'स्थान बदलें',
      'location.select_city': 'जिला / शहर चुनें',
      'location.showing_near': 'इसके निकटतम कृषि उपकरण और सेवाएं दिखाई जा रही हैं',

      // Work Done & Work Completion Workflow
      'work_done.mark_done': '✅ काम पूरा हुआ चिह्नित करें',
      'work_done.confirm_done': '✅ काम पूरा हुआ (पुष्टि करें)',
      'work_done.completed_badge': '🏁 काम संपन्न (Completed)',
      'work_done.modal_title': 'कार्य पूर्णता पुष्टि एवं समीक्षा',
      'work_done.rating_label': 'सेवा को रेटिंग दें (1-5 स्टार्स)',
      'work_done.feedback_label': 'आपकी समीक्षा / अनुभव (वैकल्पिक)',
      'work_done.submit_btn': 'पुष्टि करें और काम पूरा करें',
      'work_done.provider_success': 'काम पूरा चिह्नित किया गया! किसान को सूचित कर दिया गया है।',
      'work_done.farmer_success': 'काम सफलतापूर्वक पूरा हुआ! प्रदाता को सूचित कर दिया गया है।',
      'work_done.confirm_prompt': 'क्या आप पुष्टि करते हैं कि यह कृषि कार्य सफलतापूर्वक पूरा हो चुका है?',
      'work_done.already_done': '✨ कार्य संपन्न चिह्नित किया जा चुका है',

      // Provider Help
      'prov_help.title': '❓ प्रदाता मार्गदर्शिका एवं सहायता',
      'prov_help.subtitle': 'जानें कि अपनी लिस्टिंग कैसे बेहतर बनाएं, अनुरोध कैसे संभालें और आय कैसे बढ़ाएं',
      'prov_help.faq1_q': 'मैं अपने कृषि उपकरण कैसे जोड़ और प्रबंधित कर सकता हूँ?',
      'prov_help.faq1_a': 'नेविगेशन बार में "सेवा जोड़ें" पर जाएं, विवरण (उपकरण का नाम, मूल्य, फोटो, स्थान) भरें और प्रकाशित करें। आप "मेरी सेवाएं" से कभी भी बदलाव कर सकते हैं।',
      'prov_help.faq2_q': 'नए ग्राहक अनुरोध की सूचना मुझे कैसे मिलेगी?',
      'prov_help.faq2_a': 'जब भी कोई किसान आपकी सेवा बुक करेगा, वह तुरंत आपके "अनुरोध" टैब में दिखेगा और अलर्ट सूचना भी मिलेगी।',
      'prov_help.faq3_q': 'अनुरोध स्वीकार करने पर क्या होता है?',
      'prov_help.faq3_a': 'अनुरोध स्वीकार करने पर किसान को आपके संपर्क नंबर के साथ तत्काल सूचना भेजी जाती है ताकि आप दोनों समय और डिलीवरी तय कर सकें।',
      'prov_help.faq4_q': 'सपोर्ट टीम से कैसे संपर्क करें?',
      'prov_help.faq4_a': 'आप नीचे दिए गए फॉर्म द्वारा सहायता मांग सकते हैं या हेल्पलाइन +91 11 1234 5678 पर कॉल कर सकते हैं।',

      // Admin Panel
      'admin.portal_title': 'प्रशासक नियंत्रण कक्ष (Admin Panel)',
      'admin.portal_subtitle': 'किसानों, प्रदाताओं, सेवाओं, अनुरोधों और एनालिटिक्स का केंद्रीय प्रबंधन',
      'admin.stat_total_farmers': 'कुल किसान',
      'admin.stat_active_farmers': 'सक्रिय किसान',
      'admin.stat_total_providers': 'कुल प्रदाता',
      'admin.stat_active_providers': 'सक्रिय प्रदाता',
      'admin.stat_total_services': 'कुल सेवाएं',
      'admin.stat_pending_requests': 'लंबित अनुरोध',
      'admin.stat_completed_requests': 'पूर्ण अनुरोध',
      'admin.stat_revenue': 'कुल कारोबार',
      'admin.farmers_tab_all': 'सभी किसान',
      'admin.farmers_tab_active': 'सक्रिय किसान',
      'admin.farmers_tab_inactive': 'अवरुद्ध / निष्क्रिय किसान',
      'admin.providers_tab_all': 'सभी प्रदाता',
      'admin.providers_tab_active': 'सक्रिय प्रदाता',
      'admin.providers_tab_inactive': 'अवरुद्ध / निष्क्रिय प्रदाता',
      'admin.search_farmers': 'नाम, ईमेल, फोन, स्थान से किसान खोजें...',
      'admin.search_providers': 'नाम, ईमेल, फोन, स्थान से प्रदाता खोजें...',
      'admin.search_services': 'नाम, श्रेणी या प्रदाता से सेवाएं खोजें...',
      'admin.table_name': 'नाम',
      'admin.table_email': 'ईमेल',
      'admin.table_phone': 'फोन',
      'admin.table_location': 'स्थान',
      'admin.table_status': 'स्थिति',
      'admin.table_joined': 'शामिल होने की तिथि',
      'admin.table_services_count': 'सेवाओं की संख्या',
      'admin.table_actions': 'कार्यवाई',
      'admin.btn_activate': 'सक्रिय करें',
      'admin.btn_block': 'अवरुद्ध करें (Block)',
      'admin.btn_delete': 'हटाएं',
      'admin.btn_view_details': 'विवरण देखें',
      'admin.send_broadcast_title': 'सिस्टम घोषणा / नोटिफिकेशन भेजें',
      'admin.broadcast_audience': 'लक्षित दर्शक',
      'admin.broadcast_message': 'संदेश सामग्री',
      'admin.broadcast_btn': '📣 घोषणा भेजें',
      'admin.confirm_user_status': 'क्या आप इस उपयोगकर्ता की स्थिति बदलना चाहते हैं?',

      // Alerts & Notifications
      'alerts.title': '🔔 सूचनाएं एवं अलर्ट',
      'alerts.subtitle': 'ऑर्डर अपडेट, बुकिंग प्रतिक्रिया और महत्वपूर्ण घोषणाओं से अवगत रहें',
      'alerts.mark_all_read': '✓ सभी पढ़े गए चिन्हित करें',
      'alerts.tab_all': 'सभी अलर्ट',
      'alerts.tab_requests': '📦 अनुरोध',
      'alerts.tab_system': '📢 सिस्टम',
      'alerts.empty': 'वर्तमान में कोई अलर्ट नहीं है।',

      // Profile & Account
      'profile.title': '👤 मेरा खाता प्रोफाइल',
      'profile.subtitle': 'अपनी व्यक्तिगत जानकारी, संपर्क नंबर और प्राथमिकताएं प्रबंधित करें',
      'profile.edit_btn': '✏️ प्रोफाइल संपादित करें',
      'profile.save_btn': '💾 प्रोफाइल सहेजें',
      'profile.cancel_btn': '✕ रद्द करें',
      'profile.full_name': 'पूरा नाम',
      'profile.email': 'ईमेल पता',
      'profile.phone': 'फोन नंबर',
      'profile.location': 'पता / स्थान',
      'profile.farming_details': 'कृषि / व्यवसाय की जानकारी',
      'profile.role_label': 'खाता भूमिका (Role)',
      'profile.status_label': 'खाता स्थिति',
      'profile.updated_success': 'प्रोफाइल सफलतापूर्वक अपडेट हो गई! ✅',

      // Authentication (Login / Register)
      'auth.login_title': 'एग्रोटेक में लॉगिन करें',
      'auth.login_subtitle': 'अपने भूमिका-आधारित डैशबोर्ड तक पहुंचने के लिए साइन इन करें',
      'auth.username_label': 'ईमेल / यूजरनेम / फोन',
      'auth.password_label': 'पासवर्ड',
      'auth.login_btn': 'लॉगिन करें →',
      'auth.no_account': 'खाता नहीं है?',
      'auth.register_now': 'यहाँ पंजीकरण करें',
      'auth.register_title': 'एग्रोटेक खाता बनाएं',
      'auth.register_subtitle': 'स्मार्ट खेती शुरू करने के लिए अपनी भूमिका चुनें',
      'auth.select_role': 'अपनी भूमिका चुनें (Role) *',
      'auth.role_farmer_desc': 'मैं मशीनरी किराए पर लेना, बीज खरीदना और सेवाएं बुक करना चाहता हूँ।',
      'auth.role_provider_desc': 'मेरे पास किराए या बिक्री के लिए कृषि उपकरण, मशीनरी या सेवाएं हैं।',
      'auth.full_name_label': 'पूरा नाम *',
      'auth.contact_label': 'संपर्क फोन नंबर (10 अंक) *',
      'auth.email_label': 'ईमेल पता *',
      'auth.confirm_pw_label': 'पासवर्ड की पुष्टि करें *',
      'auth.state_label': 'राज्य *',
      'auth.address_label': 'गांव / कस्बा / जिला',
      'auth.pincode_label': 'पिनकोड',
      'auth.otp_label': 'ईमेल सत्यापन ओटीपी *',
      'auth.send_otp_btn': 'सत्यापन ओटीपी भेजें →',
      'auth.verify_create_btn': 'ओटीपी सत्यापित करें और खाता बनाएं →',
      'auth.have_account': 'पहले से पंजीकृत हैं?',
      'auth.admin_portal_link': '🛡️ प्रशासक (Admin) पोर्टल',

      // Common Actions & Form Validation
      'common.loading': 'लोड हो रहा है...',
      'common.save': 'सहेजें',
      'common.cancel': 'रद्द करें',
      'common.submit': 'जमा करें',
      'common.delete': 'हटाएं',
      'common.close': 'बंद करें',
      'common.success': 'सफल',
      'common.error': 'त्रुटि',
      'common.confirm': 'पुष्टि करें',
      'common.yes': 'हाँ',
      'common.no': 'नहीं',
      'common.back': '← वापस जाएं',
      'common.view': 'देखें',
      'common.fill_required': 'कृपया सभी आवश्यक फ़ील्ड भरें।',
      'common.unauthorized': 'आपको इस पृष्ठ तक पहुँचने की अनुमति नहीं है।',
      'common.logged_out': 'सफलतापूर्वक लॉगआउट हो गया।',

      // Landing Page & Hero Section (Hindi)
      'landing.headline_1': 'स्मार्ट मशीनरी।',
      'landing.headline_2': 'आधुनिक और समृद्ध खेती।',
      'landing.hero_desc': 'एग्रोटेक किसानों को सत्यापित कृषि मशीनरी मालिकों और ग्रामीण सेवा प्रदाताओं से जोड़ता है — पारदर्शी प्रति एकड़ दरों पर जुताई, कटाई, ड्रिप सिंचाई और फसल परिवहन की आसान सुविधा।',
      'landing.find_machinery_btn': '🚜 मशीनरी खोजें →',
      'landing.how_it_works_btn': '⚡ जाने कैसे काम करता है',
      'landing.farmer_portal_btn': '🌾 किसान पोर्टल',
      'landing.provider_portal_btn': '🚜 सहयोगी पोर्टल',
      'landing.stat_verified_machines': 'मांग पर उपलब्ध मशीनरी',
      'landing.stat_farmers': 'पारदर्शी प्रति एकड़ दरें',
      'landing.stat_hubs': 'सीधा सहयोगी संपर्क',
      'landing.stat_value': 'संतुष्टि उपरांत भुगतान',
      'landing.pillar_machines_title': 'मांग पर उपलब्ध मशीनरी',
      'landing.pillar_machines_desc': 'अपने गांव के दायरे में ट्रैक्टर, हार्वेस्टर और आधुनिक उपकरणों की त्वरित उपलब्धता।',
      'landing.pillar_pricing_title': 'पारदर्शी प्रति एकड़ दरें',
      'landing.pillar_pricing_desc': 'बिना किसी बिचौलिये या अतिरिक्त कमीशन के स्पष्ट एवं निश्चित प्रति एकड़ दरें।',
      'landing.pillar_dispatch_title': 'त्वरित सहयोगी सेवा',
      'landing.pillar_dispatch_desc': 'सीधा किसान-ऑपरेटर संपर्क और तय समय पर खेत तक मशीन की रवानगी।',
      'landing.pillar_security_title': 'संतुष्टि के बाद भुगतान',
      'landing.pillar_security_desc': 'खेत में काम का निरीक्षण करने के बाद यूपीआई अथवा नकद द्वारा सुरक्षित भुगतान।',
      'landing.prob_title': 'मशीनरी की किल्लत से लेकर स्मार्ट डिजिटल बुकिंग तक',
      'landing.prob_subtitle': 'मांग पर आधारित मशीनरी पहुंच द्वारा भारतीय किसानों की दैनिक चुनौतियों का वास्तविक समाधान',
      'landing.traditional_way': 'पारंपरिक खेती की चुनौतियाँ',
      'landing.agrotech_way': 'एग्रोटेक का स्मार्ट समाधान',
      'landing.how_title': 'एग्रोटेक कैसे काम करता है',
      'landing.how_subtitle': 'मशीनरी की खोज से लेकर खेत के काम पूरा होने तक 5 सरल चरण',
      'landing.step1_title': '01 — खोजें',
      'landing.step1_desc': 'अपने गांव या ब्लॉक में उपलब्ध ट्रैक्टर, हार्वेस्टर, रोटावेटर और कृषि सामग्री खोजें।',
      'landing.step2_title': '02 — तुलना करें',
      'landing.step2_desc': 'सत्यापित प्रदाता की रेटिंग, मशीन की क्षमता, पारदर्शी प्रति एकड़ दर और विशेषताओं की तुलना करें।',
      'landing.step3_title': '03 — अनुरोध भेजें',
      'landing.step3_desc': 'अपनी जमीन का रकबा (एकड़) और पसंदीदा तारीख एक क्लिक में दर्ज करें।',
      'landing.step4_title': '04 — पुष्टि व कार्य',
      'landing.step4_desc': 'सत्यापित सहयोगी तुरंत पुष्टि करता है, मशीन समय पर पहुंचती है और एसएमएस/ऐप पर अपडेट मिलता है।',
      'landing.step5_title': '05 — समृद्ध खेती',
      'landing.step5_desc': 'समय पर गुणवत्तापूर्ण काम पूरा, काम से संतुष्ट होकर नकद या यूपीआई द्वारा सुरक्षित भुगतान करें।',
      'landing.calc_title': 'स्मार्ट एकड़ व मशीनरी लागत कैलकुलेटर',
      'landing.calc_subtitle': 'अपनी जमीन के लिए तुरंत अनुमानित किराया, समय की बचत और दक्षता की गणना करें',
      'landing.calc_select_machine': 'मशीनरी का प्रकार चुनें',
      'landing.calc_land_acres': 'जमीन का क्षेत्रफल (एकड़):',
      'landing.calc_est_total': 'अनुमानित किराया लागत:',
      'landing.calc_time_saved': 'समय की बचत:',
      'landing.calc_book_cta': 'यह मशीन अभी बुक करें →',
      'landing.farmer_first_title': 'भारतीय कृषि की वास्तविकताओं के लिए निर्मित तकनीक',
      'landing.sahyogi_title': 'ग्रामीण मशीनरी मालिकों और कृषि उद्यमियों का सशक्तिकरण',
      'landing.sahyogi_desc': 'अपने ट्रैक्टर और उपकरणों को किराए पर देकर सीजन में ₹40,000–₹80,000 की अतिरिक्त आय कमाएं।',
      'landing.cta_title': 'क्या आप अपनी खेती को स्मार्ट बनाने के लिए तैयार हैं?',
      'landing.cta_subtitle': 'एग्रोटेक पर हजारों किसानों और सत्यापित मशीनरी पार्टनर्स से जुड़ें और आगे बढ़ें।',
      'landing.cta_farmer': '🌾 स्मार्ट खेती शुरू करें (किसान)',
      'landing.cta_sahyogi': '🚜 अपनी मशीनरी जोड़ें (सहयोगी)'
    }
  },

  get(key, fallback = '') {
    const langDict = this.translations[this.currentLang] || this.translations.en;
    if (langDict && langDict[key] !== undefined) {
      return langDict[key];
    }
    const enDict = this.translations.en;
    if (enDict && enDict[key] !== undefined) {
      return enDict[key];
    }
    return fallback || key;
  },

  t(key, params = {}, fallback = '') {
    let text = this.get(key, fallback);
    if (params && typeof params === 'object') {
      Object.keys(params).forEach(p => {
        text = text.replace(new RegExp(`\\{${p}\\}`, 'g'), params[p]);
      });
    }
    return text;
  },

  setLanguage(lang) {
    if (lang !== 'en' && lang !== 'hi') lang = 'en';
    this.currentLang = lang;
    localStorage.setItem('agro_lang', lang);
    document.documentElement.lang = lang;
    this.translateDOM();
    window.dispatchEvent(new CustomEvent('agroLanguageChanged', { detail: { lang } }));
  },

  toggleLanguage() {
    const next = this.currentLang === 'en' ? 'hi' : 'en';
    this.setLanguage(next);
  },

  translateDOM(root = document) {
    // 1. Text elements
    root.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (key) {
        el.textContent = this.get(key, el.textContent);
      }
    });

    // 2. HTML elements
    root.querySelectorAll('[data-i18n-html]').forEach(el => {
      const key = el.getAttribute('data-i18n-html');
      if (key) {
        el.innerHTML = this.get(key, el.innerHTML);
      }
    });

    // 3. Placeholders
    root.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (key) {
        el.setAttribute('placeholder', this.get(key, el.getAttribute('placeholder') || ''));
      }
    });

    // 4. Titles / tooltips
    root.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (key) {
        el.setAttribute('title', this.get(key, el.getAttribute('title') || ''));
      }
    });

    // 5. Update language switchers in DOM
    document.querySelectorAll('.lang-toggle-btn').forEach(btn => {
      const isHi = this.currentLang === 'hi';
      btn.innerHTML = isHi ? '🇮🇳 <b>हिंदी</b>' : '🇬🇧 <b>EN</b>';
      btn.setAttribute('title', isHi ? 'Switch to English' : 'हिंदी में बदलें');
    });

    document.querySelectorAll('.lang-dual-toggle').forEach(el => {
      const isHi = this.currentLang === 'hi';
      const enBtn = el.querySelector('.lang-dual-en');
      const hiBtn = el.querySelector('.lang-dual-hi');
      if (enBtn) enBtn.classList.toggle('active', !isHi);
      if (hiBtn) hiBtn.classList.toggle('active', isHi);
    });
  },

  renderLanguageToggle() {
    const isHi = this.currentLang === 'hi';
    return `
      <div class="lang-switcher" style="display:inline-flex;align-items:center;margin:0 4px">
        <button type="button" class="lang-toggle-btn" onclick="AgroI18n.toggleLanguage()" 
          style="background:rgba(255,255,255,0.14);border:1.5px solid rgba(255,255,255,0.28);color:white;padding:6px 14px;border-radius:20px;cursor:pointer;font-size:0.82rem;font-weight:700;display:flex;align-items:center;gap:6px;transition:all 0.25s ease;backdrop-filter:blur(8px);"
          title="${isHi ? 'Switch to English' : 'हिंदी में बदलें'}">
          ${isHi ? '🇮🇳 <b>हिंदी</b>' : '🇬🇧 <b>English</b>'}
        </button>
      </div>
    `;
  },

  renderDualLanguageToggle(className = '') {
    const isHi = this.currentLang === 'hi';
    return `
      <div class="lang-dual-toggle ${className}">
        <button type="button" class="lang-dual-btn lang-dual-en ${!isHi ? 'active' : ''}" onclick="AgroI18n.setLanguage('en')">
          🇬🇧 English
        </button>
        <button type="button" class="lang-dual-btn lang-dual-hi ${isHi ? 'active' : ''}" onclick="AgroI18n.setLanguage('hi')">
          🇮🇳 हिंदी
        </button>
      </div>
    `;
  }
};

// Auto-initialize when document loads
if (typeof document !== 'undefined') {
  document.addEventListener('DOMContentLoaded', () => {
    document.documentElement.lang = AgroI18n.currentLang;
    AgroI18n.translateDOM();
  });
}
