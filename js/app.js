/**
 * Lifedrop - Main Application Controller
 * Handles Multi-Page Routing, Dashboard Operations, AI Assistant, and Emergency Logistics
 */

class LifedropApp {
  constructor() {
    this.activeBloodFilter = 'ALL';
    this.activeCityFilter = '';
    this.quizAnswers = {};
    this.init();
  }

  init() {
    // 1. Theme Setup
    this.initTheme();

    // 2. Setup Active Link Highlighting
    this.highlightActiveNavLink();

    // 3. Setup Onboarding Entrance Gate (non-blocking)
    this.initOnboarding();

    // 4. Initialize Tracker & Compatibility
    this.tracker = new LifedropTracker();

    // 5. Render Core Components (conditional on page)
    this.renderHeroStats();
    this.renderEmergencyFeed();
    this.renderDonorDirectory();
    this.initFaqAccordion();
    this.renderDashboard();
    this.initEligibilityQuiz();

    // 6. Setup Event Listeners
    this.setupEventListeners();

    // 7. Initialize Chat UI
    this.initChatUI();

    // 8. Setup Live Donor Hero Card Preview
    const user = window.lifedropStorage.getCurrentUser();
    const donor = user || window.lifedropStorage.getDonors()[0];
    if (donor) {
      this.tracker.generateHeroCard(donor);
    }
    this.updateNavUserBadge();
  }

  /**
   * --- Active Navigation Link Highlighting ---
   */
  highlightActiveNavLink() {
    const currentPath = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(link => {
      const href = link.getAttribute('href');
      if (href && (href === currentPath || (currentPath === '' && href === 'index.html') || (currentPath === 'index.html' && href === 'index.html'))) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  /**
   * --- 3-Dot Overflow Menu Toggle ---
   */
  toggle3DotMenu(forceState = null) {
    const dropdown = document.getElementById('nav-3dot-dropdown');
    const btn = document.getElementById('btn-3dot-menu');
    if (!dropdown) return;
    const isNowActive = forceState !== null ? forceState : !dropdown.classList.contains('active');
    dropdown.classList.toggle('active', isNowActive);
    if (btn) btn.classList.toggle('active', isNowActive);
  }

  /**
   * --- 1. Onboarding / Registration Entrance Gate ---
   */
  initOnboarding() {
    const overlay = document.getElementById('onboarding-screen-overlay');
    if (!overlay) return;
    overlay.classList.add('dismissed');
  }

  handleOnboardingSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.name.value.trim();
    const bloodGroup = form.bloodGroup.value;
    const city = form.city.value.trim();
    const phone = form.phone.value.trim();

    const newDonor = window.lifedropStorage.addDonor({
      name,
      bloodGroup,
      city,
      area: city,
      phone,
      isEmergencyContact: true
    });

    // Set as active session user
    window.lifedropStorage.setCurrentUser(newDonor);
    this.updateNavUserBadge();

    // Dismiss overlay smoothly
    this.dismissOnboarding();

    // Update Hero Card & Feeds
    this.tracker.generateHeroCard(newDonor);
    this.renderDonorDirectory();
    this.renderHeroStats();
    this.renderDashboard();

    this.showToast(`🎉 Welcome to Lifedrop, ${name}! Your Hero profile is active.`);
  }

  dismissOnboarding(isGuest = false) {
    const overlay = document.getElementById('onboarding-screen-overlay');
    if (overlay) {
      overlay.classList.add('dismissed');
    }
    if (isGuest) {
      this.showToast('🚨 Guest Emergency Mode activated. How can we help you today?');
      window.lifedropStorage.setCurrentUser({
        name: 'Guest Requester',
        bloodGroup: 'All',
        city: 'Current Location',
        isGuest: true
      });
      this.updateNavUserBadge();
    }
  }

  openOnboarding() {
    const overlay = document.getElementById('onboarding-screen-overlay');
    if (overlay) {
      overlay.classList.remove('dismissed');
    }
  }

  updateNavUserBadge() {
    const badgeName = document.getElementById('nav-user-name');
    const badgeAvatar = document.getElementById('nav-user-initials');
    const logoutBtn = document.getElementById('nav-logout-btn');
    const user = window.lifedropStorage.getCurrentUser();

    if (!user || user.isGuest) {
      if (badgeName) badgeName.textContent = 'Guest / Sign In';
      if (badgeAvatar) badgeAvatar.textContent = '👤';
      if (logoutBtn) logoutBtn.classList.add('hidden');
      return;
    }

    if (badgeName) badgeName.textContent = `${user.name.split(' ')[0]} (${user.bloodGroup})`;
    if (badgeAvatar) badgeAvatar.textContent = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    if (logoutBtn) logoutBtn.classList.remove('hidden');
  }

  handleLogout() {
    window.lifedropStorage.clearUserSession();
    this.updateNavUserBadge();
    const defaultDonor = window.lifedropStorage.getDonors()[0];
    if (defaultDonor) {
      this.tracker.generateHeroCard(defaultDonor);
    }
    this.renderDashboard();
    this.showToast('👋 Logged out successfully. You are now browsing as Guest.');
  }

  openProfileModal() {
    const user = window.lifedropStorage.getCurrentUser();
    if (!user || user.isGuest) {
      this.openOnboarding();
    } else {
      this.tracker.generateHeroCard(user);
      const regSection = document.getElementById('donor-registration-section');
      if (regSection) {
        regSection.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.location.href = 'register.html';
      }
      this.showToast(`Active Profile: ${user.name} • Donor ID: ${user.id || 'Verified'}`);
    }
  }

  /**
   * --- 2. Aesthetic Color Theme Management ---
   */
  initTheme() {
    const savedColorTheme = window.lifedropStorage.getColorTheme();
    this.setColorTheme(savedColorTheme, false);
  }

  setColorTheme(themeName, showToast = true) {
    document.documentElement.setAttribute('data-color-theme', themeName);
    window.lifedropStorage.setColorTheme(themeName);

    // Update active swatch
    document.querySelectorAll('.theme-swatch-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-color') === themeName);
    });

    const themeLabels = {
      'luxury-light': '☀️ Clean White Theme',
      'royal-aurora': '🌌 Royal Aurora (Midnight & Ruby)',
      'neon-crimson': '🔴 Cyber Crimson (Obsidian & Laser Red)',
      'vitality-emerald': '🌿 Bio-Tech Mint (Teal & Neon Mint)'
    };

    if (showToast) {
      this.showToast(`Applied ${themeLabels[themeName] || themeName} ✨`);
    }
  }

  /**
   * --- 3. Stats & Counter Animation ---
   */
  /**
   * --- 3. Stats & Counter Animation ---
   */
  renderHeroStats() {
    const donors = window.lifedropStorage.getDonors();
    const requests = window.lifedropStorage.getRequests();

    const elDonors = document.getElementById('stat-active-donors');
    const elSaved = document.getElementById('stat-lives-saved');
    const elUrgent = document.getElementById('stat-urgent-cases');
    const elTime = document.getElementById('stat-response-time');

    const totalDonations = donors.reduce((acc, d) => acc + (d.totalDonations || 1), 0);
    const urgentCount = requests.filter(r => r.urgency === 'Emergency' && r.status !== 'Fulfilled').length;

    if (elDonors) elDonors.textContent = donors.length.toLocaleString();
    if (elSaved) elSaved.textContent = totalDonations > 0 ? (totalDonations * 3).toLocaleString() : '0';
    if (elUrgent) elUrgent.textContent = urgentCount.toString();
    if (elTime) elTime.textContent = '< 8 Mins';
  }

  /**
   * --- 4. Live Emergency Request Feed ---
   */
  renderEmergencyFeed() {
    const container = document.getElementById('emergency-feed-container');
    if (!container) return;

    const requests = window.lifedropStorage.getRequests();
    const activeReqs = requests;

    if (activeReqs.length === 0) {
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px 24px;" class="glass-panel">
          <div style="font-size: 2.8rem; margin-bottom: 12px;">🕊️</div>
          <h3 style="font-size: 1.25rem; margin-bottom: 8px;">No Active Emergency Requests</h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; max-width: 480px; margin: 0 auto 20px; line-height: 1.5;">
            All clear! No urgent patient requirements currently reported across regional hospitals.
          </p>
          <button class="btn btn-emergency" onclick="window.lifedropApp.openRequestModal()">
            🚨 Submit Emergency Request
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = activeReqs.map(req => {
      const isUrgent = req.urgency === 'Emergency';
      const badgeClass = isUrgent ? 'badge-emergency' : 'badge-warning';
      const progressPercent = req.status === 'Fulfilled' ? 100 : (req.status === 'Matched' ? 75 : (req.status === 'In Progress' ? 45 : 20));

      return `
        <div class="req-feed-card glass-panel ${isUrgent ? 'urgent-case' : ''}">
          <div class="req-card-top">
            <div class="req-bg-badge">
              <div class="req-blood-type">${req.bloodGroup}</div>
              <div>
                <h4 class="req-patient-title">${this.escapeHTML(req.patientName)}</h4>
                <p class="req-hospital">📍 ${this.escapeHTML(req.hospital)}, ${this.escapeHTML(req.city)}</p>
              </div>
            </div>
            <span class="badge ${badgeClass}">${req.urgency}</span>
          </div>

          <div class="req-meta-details">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted);">
              <span>Units Needed: <strong>${req.units || 1} Unit(s)</strong></span>
              <span>Status: <strong class="text-info">${req.status}</strong></span>
            </div>
            <div class="req-progress-bar">
              <div class="req-progress-fill" style="width: ${progressPercent}%;"></div>
            </div>
          </div>

          <div class="req-card-footer">
            <span style="font-size: 0.75rem; color: var(--text-dim);">ID: <strong>${req.id}</strong></span>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-secondary btn-sm" onclick="window.lifedropApp.trackRequestId('${req.id}')">
                🔍 Track
              </button>
              <button class="btn btn-primary btn-sm" onclick="window.lifedropApp.respondToRequest('${req.id}', '${req.bloodGroup}')">
                ❤️ I Can Donate
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  /**
   * --- 5. Donor Directory & Filters ---
   */
  renderDonorDirectory() {
    const container = document.getElementById('donors-grid-container');
    if (!container) return;

    let donors = window.lifedropStorage.getDonors();

    if (this.activeBloodFilter !== 'ALL') {
      donors = donors.filter(d => d.bloodGroup.toUpperCase() === this.activeBloodFilter.toUpperCase());
    }

    if (this.activeCityFilter.trim()) {
      const q = this.activeCityFilter.toLowerCase().trim();
      donors = donors.filter(d => 
        d.city.toLowerCase().includes(q) || 
        (d.area && d.area.toLowerCase().includes(q))
      );
    }

    if (donors.length === 0) {
      const isFiltered = this.activeBloodFilter !== 'ALL' || this.activeCityFilter.trim() !== '';
      container.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px 24px;" class="glass-panel">
          <div style="font-size: 2.8rem; margin-bottom: 12px;">❤️</div>
          <h3 style="font-size: 1.25rem; margin-bottom: 8px;">
            ${isFiltered ? `No Donors Found Matching Filter` : `No Donors Registered Yet`}
          </h3>
          <p style="color: var(--text-muted); font-size: 0.9rem; max-width: 480px; margin: 0 auto 20px; line-height: 1.5;">
            ${isFiltered ? `Try clearing your search query or selecting "All Blood Groups".` : `Be the first lifesaver in your community! Register your blood group and generate your official Hero Pass.`}
          </p>
          <a href="register.html" class="btn btn-primary">
            ❤️ Register as a Donor
          </a>
        </div>
      `;
      return;
    }

    container.innerHTML = donors.map(donor => `
      <div class="donor-card glass-panel">
        <div>
          <div class="donor-top">
            <div class="donor-avatar-circle">
              ${donor.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase()}
            </div>
            <div class="donor-blood-badge">${donor.bloodGroup}</div>
          </div>

          <h4 class="donor-name-text">${this.escapeHTML(donor.name)}</h4>
          <p class="donor-location-text">📍 ${this.escapeHTML(donor.city)}, ${this.escapeHTML(donor.area || '')}</p>
        </div>

        <div>
          <div class="donor-stats-row">
            <span>Last Donated: <strong>${donor.lastDonation || 'Available'}</strong></span>
            <span>Impact: <strong>${donor.totalDonations || 1} Saved</strong></span>
          </div>

          <div style="margin-top: 12px; display: flex; gap: 8px;">
            <button class="btn btn-secondary btn-sm" style="flex: 1;" onclick="window.lifedropApp.openDonorCardModal('${donor.id}')">
              🪪 Hero Card
            </button>
            <button class="btn btn-primary btn-sm" style="flex: 1;" onclick="window.lifedropApp.contactDonorDirect('${donor.name}', '${donor.bloodGroup}', '${donor.phone}')">
              📞 Contact
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  setBloodFilter(bloodGroup, btnElement) {
    this.activeBloodFilter = bloodGroup;
    if (btnElement) {
      document.querySelectorAll('.filter-chip').forEach(btn => btn.classList.remove('active'));
      btnElement.classList.add('active');
    }
    this.renderDonorDirectory();
  }

  handleCityFilter(cityValue) {
    this.activeCityFilter = cityValue;
    this.renderDonorDirectory();
  }

  handleHeroSearch(e) {
    e.preventDefault();
    const bg = document.getElementById('hero-search-blood-group').value;
    const city = document.getElementById('hero-search-city').value;

    const directorySection = document.getElementById('donor-directory-section');
    if (directorySection) {
      this.activeBloodFilter = bg;
      this.activeCityFilter = city;
      this.renderDonorDirectory();
      directorySection.scrollIntoView({ behavior: 'smooth' });
      this.showToast(`Filtered donors for ${bg} in ${city || 'all areas'}`);
    } else {
      window.location.href = `donors.html?bg=${encodeURIComponent(bg)}&city=${encodeURIComponent(city)}`;
    }
  }

  contactDonorDirect(donorName, bloodGroup, phone) {
    this.showToast(`Connecting with ${donorName} (${bloodGroup}): ${phone}`);
    this.openEmergencyChat(`Connect me with donor ${donorName} (${bloodGroup})`);
  }

  /**
   * --- 6. Dashboard & Operations Management ---
   */
  renderDashboard() {
    this.renderDashboardMetrics();
    this.renderInventoryStock();
    this.renderOpsTable();
    this.renderUserHub();
  }

  renderDashboardMetrics() {
    const donors = window.lifedropStorage.getDonors();
    const requests = window.lifedropStorage.getRequests();

    const mDonors = document.getElementById('dash-metric-donors');
    const mRequests = document.getElementById('dash-metric-requests');
    const mLives = document.getElementById('dash-metric-lives');
    const mUnits = document.getElementById('dash-metric-units');

    const totalDonations = donors.reduce((acc, d) => acc + (d.totalDonations || 1), 0);
    const activeReqCount = requests.filter(r => r.status !== 'Fulfilled').length;

    if (mDonors) mDonors.textContent = donors.length.toLocaleString();
    if (mRequests) mRequests.textContent = activeReqCount.toString();
    if (mLives) mLives.textContent = totalDonations > 0 ? (totalDonations * 3).toLocaleString() : '0';
    if (mUnits) mUnits.textContent = totalDonations > 0 ? totalDonations.toLocaleString() : '0';
  }

  renderInventoryStock() {
    const container = document.getElementById('dash-inventory-container');
    if (!container) return;

    const inventory = window.LIFEDROP_DATA.inventory || [];
    container.innerHTML = inventory.map(item => {
      let badgeClass = 'badge-success';
      let barClass = 'bar-stable';
      if (item.status === 'Critical') {
        badgeClass = 'badge-emergency';
        barClass = 'bar-critical';
      } else if (item.status === 'Low') {
        badgeClass = 'badge-warning';
        barClass = 'bar-low';
      } else if (item.status === 'Good') {
        badgeClass = 'badge-info';
        barClass = 'bar-good';
      }

      return `
        <div class="inventory-item-card">
          <div class="inventory-item-header">
            <span class="inventory-blood-badge">${item.bloodGroup}</span>
            <span class="badge ${badgeClass}">${item.status}</span>
          </div>
          <div class="inventory-bar-track">
            <div class="inventory-bar-fill ${barClass}" style="width: ${item.capacityPct}%;"></div>
          </div>
          <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--text-muted);">
            <span>Stock: <strong>${item.unitsAvailable} Units</strong></span>
            <span>Demand: ${item.dailyDemand}/day</span>
          </div>
        </div>
      `;
    }).join('');
  }

  renderOpsTable() {
    const tbody = document.getElementById('dash-ops-tbody');
    if (!tbody) return;

    const requests = window.lifedropStorage.getRequests();
    if (requests.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 36px 20px; color: var(--text-muted); font-size: 0.9rem;">🕊️ No active hospital emergency dispatches. All quiet across regional centers.</td></tr>`;
      return;
    }

    tbody.innerHTML = requests.map(req => {
      const urgencyClass = req.urgency === 'Emergency' ? 'badge-emergency' : 'badge-warning';
      const statusClass = req.status === 'Fulfilled' ? 'badge-success' : (req.status === 'Matched' ? 'badge-info' : 'badge-warning');

      return `
        <tr>
          <td><strong>${req.id}</strong></td>
          <td><span class="donor-blood-badge">${req.bloodGroup}</span></td>
          <td><strong>${this.escapeHTML(req.patientName)}</strong></td>
          <td>${this.escapeHTML(req.hospital)}, ${this.escapeHTML(req.city)}</td>
          <td><span class="badge ${urgencyClass}">${req.urgency}</span></td>
          <td><span class="badge ${statusClass}">${req.status}</span></td>
          <td>
            <div style="display: flex; gap: 6px;">
              <button class="btn btn-secondary btn-sm" onclick="window.lifedropApp.trackRequestId('${req.id}')">Track</button>
              ${req.status !== 'Fulfilled' ? `<button class="btn btn-primary btn-sm" onclick="window.lifedropApp.fulfillRequest('${req.id}')">Fulfill</button>` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  renderUserHub() {
    const hubName = document.getElementById('dash-user-name');
    const hubBlood = document.getElementById('dash-user-blood');
    const hubAvatar = document.getElementById('dash-user-avatar');
    const user = window.lifedropStorage.getCurrentUser();

    if (!user || user.isGuest) {
      if (hubName) hubName.textContent = 'Guest Volunteer';
      if (hubBlood) hubBlood.textContent = 'Sign In to Sync Pass';
      if (hubAvatar) hubAvatar.textContent = '👤';
    } else {
      if (hubName) hubName.textContent = user.name;
      if (hubBlood) hubBlood.textContent = `Blood Group: ${user.bloodGroup} • ${user.city || 'Verified'}`;
      if (hubAvatar) hubAvatar.textContent = user.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase();
    }
  }

  toggleAvailability(checkbox) {
    const isAvail = checkbox.checked;
    this.showToast(isAvail ? '🟢 You are marked AVAILABLE for emergency donor dispatch.' : '⚪ You are marked UNAVAILABLE.');
  }

  fulfillRequest(reqId) {
    const req = window.lifedropStorage.getRequestById(reqId);
    if (req) {
      req.status = 'Fulfilled';
      window.lifedropStorage.updateRequest(req);
      this.renderDashboard();
      this.renderEmergencyFeed();
      this.showToast(`Request ${reqId} successfully marked as FULFILLED!`);
    }
  }

  /**
   * --- 7. Eligibility Quiz ---
   */
  initEligibilityQuiz() {
    // Quiz state listener
  }

  handleQuizAnswer(questionId, isYes, btnElement) {
    this.quizAnswers[questionId] = isYes;
    const parent = btnElement.parentElement;
    parent.querySelectorAll('.quiz-btn').forEach(b => b.classList.remove('selected-yes', 'selected-no'));
    btnElement.classList.add(isYes ? 'selected-yes' : 'selected-no');

    // If 4 questions answered, calculate result
    const keys = Object.keys(this.quizAnswers);
    if (keys.length >= 4) {
      const eligibleBox = document.getElementById('quiz-result-eligible');
      const ineligibleBox = document.getElementById('quiz-result-ineligible');
      
      const isEligible = this.quizAnswers['age'] === true &&
                         this.quizAnswers['weight'] === true &&
                         this.quizAnswers['health'] === true &&
                         this.quizAnswers['interval'] === true;

      if (eligibleBox && ineligibleBox) {
        if (isEligible) {
          eligibleBox.style.display = 'block';
          ineligibleBox.style.display = 'none';
        } else {
          eligibleBox.style.display = 'none';
          ineligibleBox.style.display = 'block';
        }
      }
    }
  }

  /**
   * --- 8. Quick Modals & Actions ---
   */
  openRequestModal() {
    const modal = document.getElementById('modal-new-request');
    if (modal) modal.classList.add('active');
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  }

  handleQuickRequestForm(e) {
    e.preventDefault();
    const form = e.target;
    const bloodGroup = form.bloodGroup.value;
    const units = parseInt(form.units.value) || 1;
    const patientName = form.patientName.value.trim();
    const city = form.city.value.trim();
    const hospital = form.hospital.value.trim();
    const urgency = form.urgency.value;
    const contactPhone = form.contactPhone.value.trim();

    const newReq = window.lifedropStorage.addRequest({
      bloodGroup,
      units,
      patientName,
      city,
      hospital,
      urgency,
      contactPhone
    });

    this.closeModal('modal-new-request');
    form.reset();

    this.showToast(`🚨 Emergency Blood Request created! Tracking ID: ${newReq.id}`);
    this.renderEmergencyFeed();
    this.renderHeroStats();
    this.renderDashboard();
    this.trackRequestId(newReq.id);
  }

  handleDonorRegisterForm(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.donorName.value.trim();
    const bloodGroup = form.donorBloodGroup.value;
    const city = form.donorCity.value.trim();
    const area = form.donorArea.value.trim();
    const phone = form.donorPhone.value.trim();

    const newDonor = window.lifedropStorage.addDonor({
      name,
      bloodGroup,
      city,
      area: area || city,
      phone,
      isEmergencyContact: true
    });

    window.lifedropStorage.setCurrentUser(newDonor);
    this.updateNavUserBadge();

    form.reset();
    this.showToast(`Profile updated! Donor ID ${newDonor.id} active.`);
    this.tracker.generateHeroCard(newDonor);
    this.renderDonorDirectory();
    this.renderHeroStats();
    this.renderDashboard();

    const heroCardSection = document.getElementById('donor-registration-section');
    if (heroCardSection) {
      heroCardSection.scrollIntoView({ behavior: 'smooth' });
    }
  }

  trackRequestId(reqId) {
    const input = document.getElementById('tracker-query-input');
    if (input) input.value = reqId;
    this.tracker.trackRequest(reqId);
    
    const trackerSection = document.getElementById('request-tracker-section');
    if (trackerSection) {
      trackerSection.scrollIntoView({ behavior: 'smooth' });
    } else {
      const isTrackerPage = window.location.pathname.includes('tracker.html');
      if (!isTrackerPage) {
        window.location.href = `tracker.html?req=${encodeURIComponent(reqId)}`;
      }
    }
  }

  respondToRequest(reqId, bloodGroup) {
    this.showToast(`Directing you to coordinate donation for ${reqId} (${bloodGroup}).`);
    this.openEmergencyChat(`I am ready to donate ${bloodGroup} for request ${reqId}`);
  }

  openDonorCardModal(donorId) {
    const donor = window.lifedropStorage.getDonors().find(d => d.id === donorId);
    if (donor) {
      this.tracker.generateHeroCard(donor);
      const regSection = document.getElementById('donor-registration-section');
      if (regSection) {
        regSection.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.location.href = 'register.html';
      }
    }
  }

  downloadHeroCard() {
    this.showToast('Preparing digital Hero Donor Card for download...');
    setTimeout(() => {
      this.showToast('✓ Donor ID badge saved to your device!');
    }, 600);
  }

  showToast(message) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  /**
   * --- 9. Chatbot UI Logic ---
   */
  initChatUI() {
    this.chatOverlay = document.getElementById('chat-window-overlay');
    this.chatLauncher = document.getElementById('chat-launcher-btn');
    this.chatBody = document.getElementById('chat-messages-body');
    this.chatInput = document.getElementById('chat-user-input');
    this.chatSendBtn = document.getElementById('chat-send-trigger');

    if (this.chatBody && this.chatBody.children.length === 0) {
      this.appendMessage(
        'assistant',
        'Hello! I am the Lifedrop Assistant. How can I assist you right now?',
        ['🚨 Urgent Blood Request', '❤️ Register as Donor', '🔍 Track Request REQ-1042', '❓ Eligibility Criteria']
      );
    }
  }

  toggleChat(forceState = null) {
    if (!this.chatOverlay) return;
    const shouldOpen = forceState !== null ? forceState : !this.chatOverlay.classList.contains('active');
    this.chatOverlay.classList.toggle('active', shouldOpen);
    if (shouldOpen && this.chatInput) {
      setTimeout(() => this.chatInput.focus(), 150);
    }
  }

  openEmergencyChat(initialPrompt = null) {
    this.toggleChat(true);
    if (initialPrompt) {
      setTimeout(() => {
        this.sendChatMessage(initialPrompt);
      }, 200);
    }
  }

  appendMessage(sender, text, quickReplies = []) {
    if (!this.chatBody) return;

    const msgEl = document.createElement('div');
    msgEl.className = `chat-message ${sender}`;

    const avatarHtml = sender === 'assistant' ? `
      <div class="message-avatar">
        <img src="assets/logo.svg" alt="AI" style="width: 18px; height: 18px;">
      </div>
    ` : `
      <div class="message-avatar">👤</div>
    `;

    let quickRepliesHtml = '';
    if (quickReplies && quickReplies.length > 0) {
      quickRepliesHtml = `
        <div class="chat-action-chips-wrap">
          ${quickReplies.map(qr => `<button type="button" class="chat-action-chip" onclick="window.lifedropApp.sendChatMessage('${this.escapeHTML(qr)}')">${this.escapeHTML(qr)}</button>`).join('')}
        </div>
      `;
    }

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    msgEl.innerHTML = `
      ${avatarHtml}
      <div>
        <div class="message-bubble">${this.escapeHTML(text)}</div>
        ${quickRepliesHtml}
        <span class="message-timestamp">${timeStr}</span>
      </div>
    `;

    this.chatBody.appendChild(msgEl);
    this.chatBody.scrollTop = this.chatBody.scrollHeight;
  }

  sendChatMessage(customText = null) {
    const text = customText || (this.chatInput ? this.chatInput.value.trim() : '');
    if (!text) return;

    if (!customText && this.chatInput) {
      this.chatInput.value = '';
    }

    this.appendMessage('user', text);

    setTimeout(() => {
      if (window.lifedropAssistant) {
        const response = window.lifedropAssistant.processUserInput(text);
        this.appendMessage('assistant', response.message, response.quickReplies);
      } else {
        this.appendMessage('assistant', "I'm routing your request to nearby blood banks and emergency donors immediately.");
      }
    }, 400);
  }

  initFaqAccordion() {
    const container = document.getElementById('faq-accordion-container');
    if (!container) return;

    const faqs = window.LIFEDROP_DATA.faqs || [];
    container.innerHTML = faqs.map((faq, idx) => `
      <div class="faq-item ${idx === 0 ? 'active' : ''}">
        <div class="faq-question" onclick="this.parentElement.classList.toggle('active')">
          <span>${this.escapeHTML(faq.q)}</span>
          <span class="faq-icon">▼</span>
        </div>
        <div class="faq-answer">
          ${this.escapeHTML(faq.a)}
        </div>
      </div>
    `).join('');
  }

  setupEventListeners() {
    window.addEventListener('lifedrop:donors-updated', () => {
      this.renderDonorDirectory();
      this.renderHeroStats();
      this.renderDashboard();
    });

    window.addEventListener('lifedrop:requests-updated', () => {
      this.renderEmergencyFeed();
      this.renderHeroStats();
      this.renderDashboard();
    });

    window.addEventListener('lifedrop:user-updated', () => {
      this.updateNavUserBadge();
      this.renderUserHub();
    });

    if (this.chatInput) {
      this.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          this.sendChatMessage();
        }
      });
    }

    if (this.chatSendBtn) {
      this.chatSendBtn.addEventListener('click', () => {
        this.sendChatMessage();
      });
    }

    // 3-Dot Menu Outside Click & Escape Listener
    document.addEventListener('click', (e) => {
      const wrap = document.querySelector('.nav-3dot-wrap');
      if (wrap && !wrap.contains(e.target)) {
        this.toggle3DotMenu(false);
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.toggle3DotMenu(false);
      }
    });
  }

  escapeHTML(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  window.lifedropApp = new LifedropApp();
});
