/**
 * Lifedrop - Storage & Hybrid State Management
 * Combines SQLite REST Backend sync with localStorage offline fallback
 */

class LifedropStorage {
  constructor() {
    this.STORAGE_KEYS = {
      DONORS: 'lifedrop_donors',
      REQUESTS: 'lifedrop_requests',
      CHAT_HISTORY: 'lifedrop_chat_history',
      THEME: 'lifedrop_theme',
      COLOR_THEME: 'lifedrop_color_theme',
      CURRENT_USER: 'lifedrop_current_user',
      ONBOARDING_COMPLETED: 'lifedrop_onboarding_completed'
    };
    this.init();
  }

  // --- Color Themes ---
  getColorTheme() {
    return localStorage.getItem(this.STORAGE_KEYS.COLOR_THEME) || 'luxury-light';
  }

  setColorTheme(themeName) {
    localStorage.setItem(this.STORAGE_KEYS.COLOR_THEME, themeName);
    document.documentElement.setAttribute('data-color-theme', themeName);
    window.dispatchEvent(new CustomEvent('lifedrop:theme-updated', { detail: themeName }));
  }

  // --- Current User & Onboarding ---
  getCurrentUser() {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.CURRENT_USER);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      return null;
    }
  }

  setCurrentUser(user) {
    localStorage.setItem(this.STORAGE_KEYS.CURRENT_USER, JSON.stringify(user));
    localStorage.setItem(this.STORAGE_KEYS.ONBOARDING_COMPLETED, 'true');
    window.dispatchEvent(new CustomEvent('lifedrop:user-updated', { detail: user }));
  }

  isOnboardingCompleted() {
    return localStorage.getItem(this.STORAGE_KEYS.ONBOARDING_COMPLETED) === 'true';
  }

  clearUserSession() {
    localStorage.removeItem(this.STORAGE_KEYS.CURRENT_USER);
    localStorage.removeItem(this.STORAGE_KEYS.ONBOARDING_COMPLETED);
    window.dispatchEvent(new CustomEvent('lifedrop:user-updated', { detail: null }));
  }

  async init() {
    if (localStorage.getItem(this.STORAGE_KEYS.DONORS) === null) {
      localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify([]));
    }
    if (localStorage.getItem(this.STORAGE_KEYS.REQUESTS) === null) {
      localStorage.setItem(this.STORAGE_KEYS.REQUESTS, JSON.stringify([]));
    }

    // Automatically sync initial records from backend database if server is running
    await this.syncWithBackend();
  }

  async syncWithBackend() {
    if (window.lifedropApi) {
      try {
        const isOnline = await window.lifedropApi.checkConnection();
        if (isOnline) {
          const [remoteDonors, remoteRequests] = await Promise.all([
            window.lifedropApi.getDonors(),
            window.lifedropApi.getRequests()
          ]);

          if (remoteDonors && Array.isArray(remoteDonors)) {
            // Normalize backend snake_case fields to frontend camelCase
            const normalizedDonors = remoteDonors.map(d => ({
              id: d.id,
              name: d.name,
              bloodGroup: d.blood_group || d.bloodGroup,
              city: d.city,
              area: d.area || d.city,
              phone: d.phone,
              email: d.email,
              age: d.age,
              weight: d.weight,
              available: d.available === 1 || d.available === true,
              verified: d.verified === 1 || d.verified === true,
              totalDonations: d.total_donations || d.totalDonations || 1,
              lastDonation: d.last_donation || d.lastDonation,
              distanceKm: (1.0 + Math.random() * 4).toFixed(1)
            }));
            localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify(normalizedDonors));
          }

          if (remoteRequests && Array.isArray(remoteRequests)) {
            const normalizedRequests = remoteRequests.map(r => ({
              id: r.id,
              patientName: r.patient_name || r.patientName,
              bloodGroup: r.blood_group || r.bloodGroup,
              units: r.units,
              hospital: r.hospital,
              city: r.city,
              urgency: r.urgency,
              contactName: r.contact_name || r.contactName,
              contactPhone: r.contact_phone || r.contactPhone,
              notes: r.notes,
              status: r.status,
              donorsContacted: r.donors_contacted !== undefined ? r.donors_contacted : r.donorsContacted,
              donorsConfirmed: r.donors_confirmed !== undefined ? r.donors_confirmed : r.donorsConfirmed,
              createdAt: r.created_at || r.createdAt,
              timeline: r.timeline || []
            }));
            localStorage.setItem(this.STORAGE_KEYS.REQUESTS, JSON.stringify(normalizedRequests));
          }

          window.dispatchEvent(new CustomEvent('lifedrop:sync-completed', { detail: { synced: true } }));
        }
      } catch (e) {
        console.warn('[LifedropStorage] Backend initial sync skipped:', e);
      }
    }
  }

  // --- Donors ---
  getDonors() {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.DONORS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error fetching donors:', e);
      return [];
    }
  }

  async getDonorsAsync(filters = {}) {
    if (window.lifedropApi && window.lifedropApi.isBackendAvailable) {
      const remote = await window.lifedropApi.getDonors(filters);
      if (remote) {
        return remote.map(d => ({
          id: d.id,
          name: d.name,
          bloodGroup: d.blood_group || d.bloodGroup,
          city: d.city,
          area: d.area || d.city,
          phone: d.phone,
          available: d.available === 1 || d.available === true,
          verified: d.verified === 1 || d.verified === true,
          totalDonations: d.total_donations || d.totalDonations || 1,
          lastDonation: d.last_donation || d.lastDonation,
          distanceKm: (1.0 + Math.random() * 4).toFixed(1)
        }));
      }
    }
    return this.getDonors();
  }

  addDonor(donor) {
    const donors = this.getDonors();
    const newDonor = {
      id: donor.id || 'DON-' + Math.floor(100 + Math.random() * 900),
      verified: true,
      available: true,
      totalDonations: donor.totalDonations || 1,
      lastDonation: donor.lastDonation || new Date().toISOString().split('T')[0],
      distanceKm: (1.0 + Math.random() * 4).toFixed(1),
      ...donor
    };
    donors.unshift(newDonor);
    localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify(donors));

    // Post to backend database asynchronously
    if (window.lifedropApi) {
      window.lifedropApi.registerDonor(newDonor).catch(err => console.warn('Failed to sync donor to DB:', err));
    }

    window.dispatchEvent(new CustomEvent('lifedrop:donors-updated', { detail: newDonor }));
    return newDonor;
  }

  findDonors({ bloodGroup, city, maxDistance = 50 }) {
    const donors = this.getDonors();
    const normalizedCity = (city || '').trim().toLowerCase();
    const normalizedBg = (bloodGroup || '').trim().toUpperCase();

    // Check compatible donor types if requested
    const compat = window.LIFEDROP_DATA && window.LIFEDROP_DATA.compatibility ? window.LIFEDROP_DATA.compatibility[normalizedBg] : null;
    const compatibleGroups = compat ? compat.canReceiveFrom : [normalizedBg];

    return donors.filter(donor => {
      const matchesBlood = donor.bloodGroup.toUpperCase() === normalizedBg || 
                           compatibleGroups.includes(donor.bloodGroup.toUpperCase());
      const matchesCity = !normalizedCity || 
                          donor.city.toLowerCase().includes(normalizedCity) ||
                          (donor.area && donor.area.toLowerCase().includes(normalizedCity));
      return matchesBlood && matchesCity && donor.available;
    });
  }

  // --- Requests ---
  getRequests() {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.REQUESTS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error fetching requests:', e);
      return [];
    }
  }

  async getRequestsAsync(filters = {}) {
    if (window.lifedropApi && window.lifedropApi.isBackendAvailable) {
      const remote = await window.lifedropApi.getRequests(filters);
      if (remote) {
        return remote.map(r => ({
          id: r.id,
          patientName: r.patient_name || r.patientName,
          bloodGroup: r.blood_group || r.bloodGroup,
          units: r.units,
          hospital: r.hospital,
          city: r.city,
          urgency: r.urgency,
          contactName: r.contact_name || r.contactName,
          contactPhone: r.contact_phone || r.contactPhone,
          notes: r.notes,
          status: r.status,
          donorsContacted: r.donors_contacted !== undefined ? r.donors_contacted : r.donorsContacted,
          donorsConfirmed: r.donors_confirmed !== undefined ? r.donors_confirmed : r.donorsConfirmed,
          createdAt: r.created_at || r.createdAt,
          timeline: r.timeline || []
        }));
      }
    }
    return this.getRequests();
  }

  getRequestById(requestId) {
    if (!requestId) return null;
    const cleanId = requestId.trim().toUpperCase();
    const requests = this.getRequests();
    return requests.find(r => r.id.toUpperCase() === cleanId || (r.contactPhone && r.contactPhone.includes(requestId.trim())));
  }

  async getRequestByIdAsync(requestId) {
    if (window.lifedropApi && window.lifedropApi.isBackendAvailable) {
      const remote = await window.lifedropApi.getRequestById(requestId);
      if (remote) {
        return {
          id: remote.id,
          patientName: remote.patient_name || remote.patientName,
          bloodGroup: remote.blood_group || remote.bloodGroup,
          units: remote.units,
          hospital: remote.hospital,
          city: remote.city,
          urgency: remote.urgency,
          contactName: remote.contact_name || remote.contactName,
          contactPhone: remote.contact_phone || remote.contactPhone,
          notes: remote.notes,
          status: remote.status,
          donorsContacted: remote.donors_contacted !== undefined ? remote.donors_contacted : remote.donorsContacted,
          donorsConfirmed: remote.donors_confirmed !== undefined ? remote.donors_confirmed : remote.donorsConfirmed,
          createdAt: remote.created_at || remote.createdAt,
          timeline: remote.timeline || []
        };
      }
    }
    return this.getRequestById(requestId);
  }

  addRequest(request) {
    const requests = this.getRequests();
    const idNum = Math.floor(1000 + Math.random() * 9000);
    const newRequest = {
      id: request.id || `REQ-${idNum}`,
      status: request.urgency === 'Emergency' ? 'In Progress' : 'Searching',
      donorsContacted: 0,
      donorsConfirmed: 0,
      createdAt: new Date().toISOString(),
      timeline: [
        {
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          event: `Request created for ${request.bloodGroup} at ${request.hospital || request.city}`
        }
      ],
      ...request
    };

    // Calculate initial matching donors for instant preview
    const matchingDonors = this.findDonors({
      bloodGroup: newRequest.bloodGroup,
      city: newRequest.city
    });
    newRequest.donorsContacted = matchingDonors.length;
    if (matchingDonors.length > 0) {
      newRequest.timeline.push({
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        event: `Alert dispatched to ${matchingDonors.length} nearby registered ${newRequest.bloodGroup} donors`
      });
    }

    requests.unshift(newRequest);
    localStorage.setItem(this.STORAGE_KEYS.REQUESTS, JSON.stringify(requests));

    // Post to backend database asynchronously
    if (window.lifedropApi) {
      window.lifedropApi.createRequest(newRequest).then(remoteSaved => {
        if (remoteSaved) {
          // Sync with server assigned values if different
          newRequest.id = remoteSaved.id;
          newRequest.donorsContacted = remoteSaved.donors_contacted;
        }
      }).catch(err => console.warn('Failed to sync request to DB:', err));
    }

    window.dispatchEvent(new CustomEvent('lifedrop:requests-updated', { detail: newRequest }));
    return newRequest;
  }

  // --- Theme ---
  getTheme() {
    return localStorage.getItem(this.STORAGE_KEYS.THEME) || 'dark';
  }

  setTheme(theme) {
    localStorage.setItem(this.STORAGE_KEYS.THEME, theme);
  }
}

// Global instance
window.lifedropStorage = new LifedropStorage();
