/**
 * Lifedrop - Storage & State Management
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

  init() {
    // Clear legacy mock donors and requests and initialize with clean empty states
    const RESET_KEY = 'lifedrop_clean_state_v3';
    if (!localStorage.getItem(RESET_KEY)) {
      localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify([]));
      localStorage.setItem(this.STORAGE_KEYS.REQUESTS, JSON.stringify([]));
      localStorage.setItem(RESET_KEY, 'true');
    } else {
      if (localStorage.getItem(this.STORAGE_KEYS.DONORS) === null) {
        localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify([]));
      }
      if (localStorage.getItem(this.STORAGE_KEYS.REQUESTS) === null) {
        localStorage.setItem(this.STORAGE_KEYS.REQUESTS, JSON.stringify([]));
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

  addDonor(donor) {
    const donors = this.getDonors();
    const newDonor = {
      id: 'DON-' + Math.floor(100 + Math.random() * 900),
      verified: true,
      available: true,
      totalDonations: 1,
      lastDonation: new Date().toISOString().split('T')[0],
      distanceKm: (1.0 + Math.random() * 4).toFixed(1),
      ...donor
    };
    donors.unshift(newDonor);
    localStorage.setItem(this.STORAGE_KEYS.DONORS, JSON.stringify(donors));
    window.dispatchEvent(new CustomEvent('lifedrop:donors-updated', { detail: newDonor }));
    return newDonor;
  }

  findDonors({ bloodGroup, city, maxDistance = 50 }) {
    const donors = this.getDonors();
    const normalizedCity = (city || '').trim().toLowerCase();
    const normalizedBg = (bloodGroup || '').trim().toUpperCase();

    // Check compatible donor types if requested
    const compat = window.LIFEDROP_DATA.compatibility[normalizedBg];
    const compatibleGroups = compat ? compat.canReceiveFrom : [normalizedBg];

    return donors.filter(donor => {
      // Blood type check (exact or compatible)
      const matchesBlood = donor.bloodGroup.toUpperCase() === normalizedBg || 
                           compatibleGroups.includes(donor.bloodGroup.toUpperCase());
      
      // City check (partial match)
      const matchesCity = !normalizedCity || 
                          donor.city.toLowerCase().includes(normalizedCity) ||
                          donor.area.toLowerCase().includes(normalizedCity);

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

  getRequestById(requestId) {
    if (!requestId) return null;
    const cleanId = requestId.trim().toUpperCase();
    const requests = this.getRequests();
    return requests.find(r => r.id.toUpperCase() === cleanId || r.contactPhone.includes(requestId.trim()));
  }

  addRequest(request) {
    const requests = this.getRequests();
    const idNum = Math.floor(1000 + Math.random() * 9000);
    const newRequest = {
      id: `REQ-${idNum}`,
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

    // Simulate instant broadcast
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
