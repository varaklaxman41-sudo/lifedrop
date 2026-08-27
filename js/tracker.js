/**
 * Lifedrop - Tracker, Compatibility Matrix & Donor Hero Card Generator
 */

class LifedropTracker {
  constructor() {
    this.selectedBloodGroup = 'O+';
    this.initCompatibilityMatrix();
    this.initEventListeners();
  }

  initEventListeners() {
    // Listen for storage updates
    window.addEventListener('lifedrop:requests-updated', (e) => {
      this.refreshLiveRequestsFeed();
    });
  }

  /**
   * --- 1. Compatibility Matrix Component ---
   */
  initCompatibilityMatrix() {
    const selectorContainer = document.getElementById('compat-selector-buttons');
    if (!selectorContainer) return;

    const bloodTypes = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];
    selectorContainer.innerHTML = bloodTypes
      .map(
        bg => `
        <button type="button" class="compat-btn ${bg === this.selectedBloodGroup ? 'active' : ''}" data-bg="${bg}">
          <span class="compat-btn-drop">🩸</span>
          <span class="compat-btn-text">${bg}</span>
        </button>
      `
      )
      .join('');

    selectorContainer.querySelectorAll('.compat-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const bg = btn.getAttribute('data-bg');
        this.renderCompatibility(bg);
      });
    });

    this.renderCompatibility(this.selectedBloodGroup);
  }

  renderCompatibility(bg) {
    this.selectedBloodGroup = bg;

    // Update active button
    document.querySelectorAll('.compat-btn').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-bg') === bg);
    });

    const info = window.LIFEDROP_DATA.compatibility[bg];
    if (!info) return;

    // Update header info
    const titleEl = document.getElementById('compat-selected-title');
    const badgeEl = document.getElementById('compat-selected-badge');
    const descEl = document.getElementById('compat-selected-desc');
    const giveToContainer = document.getElementById('compat-can-give-to');
    const receiveFromContainer = document.getElementById('compat-can-receive-from');

    if (titleEl) titleEl.textContent = `Blood Group: ${bg}`;
    if (badgeEl) badgeEl.textContent = info.badge;
    if (descEl) descEl.textContent = info.description;

    const allTypes = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];

    // Render "Can Give To" Pills
    if (giveToContainer) {
      giveToContainer.innerHTML = allTypes
        .map(t => {
          const isCompatible = info.canDonateTo.includes(t);
          return `
            <div class="compat-type-pill ${isCompatible ? 'compatible-give' : 'incompatible'}">
              <span class="type-name">${t}</span>
              <span class="type-status">${isCompatible ? '✓ Compatible' : '✕ Not Compatible'}</span>
            </div>
          `;
        })
        .join('');
    }

    // Render "Can Receive From" Pills
    if (receiveFromContainer) {
      receiveFromContainer.innerHTML = allTypes
        .map(t => {
          const isCompatible = info.canReceiveFrom.includes(t);
          return `
            <div class="compat-type-pill ${isCompatible ? 'compatible-receive' : 'incompatible'}">
              <span class="type-name">${t}</span>
              <span class="type-status">${isCompatible ? '✓ Compatible' : '✕ Not Compatible'}</span>
            </div>
          `;
        })
        .join('');
    }
  }

  /**
   * --- 2. Live Request Tracker Component ---
   */
  async trackRequest(reqId) {
    const resultContainer = document.getElementById('tracker-result-card');
    if (!resultContainer) return;

    let req = window.lifedropStorage.getRequestById(reqId);
    if (!req && window.lifedropStorage.getRequestByIdAsync) {
      req = await window.lifedropStorage.getRequestByIdAsync(reqId);
    }

    if (!req) {
      resultContainer.innerHTML = `
        <div class="tracker-empty-state">
          <div class="empty-icon">🔍</div>
          <h3>No Request Found</h3>
          <p>We could not find an active request with ID <strong>"${escapeHTML(reqId)}"</strong>. Please check your tracking number or contact support.</p>
        </div>
      `;
      resultContainer.classList.remove('hidden');
      return;
    }

    const urgencyClass = req.urgency === 'Emergency' ? 'badge-emergency' : 'badge-warning';
    const statusSteps = ['Created', 'Matching', 'Alerted', 'Confirmed', 'Fulfilled'];
    
    let currentStepIndex = 1;
    if (req.status === 'In Progress') currentStepIndex = 2;
    if (req.status === 'Matched') currentStepIndex = 3;
    if (req.status === 'Fulfilled') currentStepIndex = 4;

    resultContainer.innerHTML = `
      <div class="tracker-card glass-panel animate-fade-in">
        <div class="tracker-header">
          <div>
            <span class="badge ${urgencyClass} pulse-badge">● ${req.urgency}</span>
            <h3 class="tracker-id">${req.id}</h3>
            <p class="tracker-meta">Patient: <strong>${escapeHTML(req.patientName)}</strong> • Required at: <strong>${escapeHTML(req.hospital)}, ${escapeHTML(req.city)}</strong></p>
          </div>
          <div class="tracker-blood-badge">
            <span class="bg-label">Required</span>
            <span class="bg-val">${req.bloodGroup}</span>
            <span class="bg-units">${req.units || 1} Unit(s)</span>
          </div>
        </div>

        <div class="tracker-stepper">
          ${statusSteps.map((step, idx) => `
            <div class="stepper-step ${idx <= currentStepIndex ? 'completed' : ''} ${idx === currentStepIndex ? 'active' : ''}">
              <div class="step-circle">${idx < currentStepIndex ? '✓' : idx + 1}</div>
              <div class="step-label">${step}</div>
            </div>
          `).join('')}
        </div>

        <div class="tracker-stats-row">
          <div class="tracker-stat">
            <span class="stat-num">${req.donorsContacted || 0}</span>
            <span class="stat-label">Donors Alerted</span>
          </div>
          <div class="tracker-stat">
            <span class="stat-num text-success">${req.donorsConfirmed || 0}</span>
            <span class="stat-label">Donors Confirmed</span>
          </div>
          <div class="tracker-stat">
            <span class="stat-num text-info">${req.requiredWithin || 'Immediate'}</span>
            <span class="stat-label">Target Window</span>
          </div>
        </div>

        <div class="tracker-timeline-section">
          <h4>Live Dispatch Timeline</h4>
          <ul class="timeline-list">
            ${(req.timeline || []).map(item => `
              <li class="timeline-item">
                <span class="timeline-time">${item.time}</span>
                <span class="timeline-text">${escapeHTML(item.event)}</span>
              </li>
            `).join('')}
          </ul>
        </div>

        <div class="tracker-actions">
          <button type="button" class="btn btn-primary btn-sm" onclick="window.lifedropMap && window.lifedropMap.openNavigationModal(window.lifedropStorage.getRequestById('${req.id}') || {id: '${req.id}', hospital: '${escapeHTML(req.hospital)}', city: '${escapeHTML(req.city)}', bloodGroup: '${req.bloodGroup}', patientName: '${escapeHTML(req.patientName)}', units: ${req.units || 1}})">
            🗺️ Live Route to Hospital
          </button>
          <button type="button" class="btn btn-secondary btn-sm" onclick="window.lifedropApp.openEmergencyChat('${req.id}')">
            💬 Assistant
          </button>
          <a href="tel:${req.contactPhone || '108'}" class="btn btn-outline btn-sm">
            📞 Call Hospital
          </a>
        </div>
      </div>
    `;
    resultContainer.classList.remove('hidden');
  }

  /**
   * --- 3. Donor Hero Card Generator ---
   */
  generateHeroCard(donor) {
    const cardPreview = document.getElementById('donor-card-preview');
    if (!cardPreview) return;

    cardPreview.innerHTML = `
      <div class="hero-id-card glass-panel" id="exportable-hero-card">
        <div class="card-glow-top"></div>
        <div class="card-header">
          <div class="brand">
            <span class="brand-drop">🩸</span>
            <span class="brand-title">LIFEDROP <strong>HERO</strong></span>
          </div>
          <span class="card-status-badge">VERIFIED DONOR</span>
        </div>

        <div class="card-body">
          <div class="donor-avatar">
            <span class="avatar-initials">${donor.name.split(' ').map(n=>n[0]).join('').substring(0,2).toUpperCase()}</span>
          </div>
          <div class="donor-details">
            <h3 class="donor-name">${escapeHTML(donor.name)}</h3>
            <p class="donor-loc">📍 ${escapeHTML(donor.city)}, ${escapeHTML(donor.area || '')}</p>
            <p class="donor-id-tag">ID: <strong>${donor.id}</strong></p>
          </div>
          <div class="donor-blood-tag">
            <span class="blood-label">TYPE</span>
            <span class="blood-value">${donor.bloodGroup}</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="card-stats">
            <div>
              <span class="cs-num">${donor.totalDonations || 1}</span>
              <span class="cs-lbl">Lives Impacted</span>
            </div>
            <div>
              <span class="cs-num">Active</span>
              <span class="cs-lbl">Emergency Ready</span>
            </div>
          </div>
          <div class="card-qr">
            <div class="qr-mock">
              <svg width="42" height="42" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2 2h8v8H2V2zm2 2v4h4V4H4zm10-2h8v8h-8V2zm2 2v4h4V4h-4zM2 14h8v8H2v-8zm2 2v4h4v-4H4zm14 0h4v4h-4v-4zm-4-2h2v2h-2v-2zm2 4h2v4h-2v-4zm2-2h4v2h-4v-2zm-6 4h2v2h-2v-2zm6-6h2v2h-2v-2z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
      <div class="card-export-actions mt-3">
        <button class="btn btn-primary btn-sm" onclick="window.lifedropApp.downloadHeroCard()">
          📥 Download Donor Card
        </button>
        <button class="btn btn-secondary btn-sm" onclick="window.lifedropApp.showToast('Donor profile link copied to clipboard!')">
          🔗 Share Profile
        </button>
      </div>
    `;
  }
}

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

window.LifedropTracker = LifedropTracker;
