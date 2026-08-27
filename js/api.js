/**
 * Lifedrop - REST API Client & Synchronization Layer
 * Seamlessly interfaces with Python + SQLite backend, with fallback for offline mode
 */

class LifedropApiClient {
  constructor() {
    // If frontend is served directly by backend or port 5000, use relative /api, else fallback to http://127.0.0.1:5000/api
    const isHostedOnBackend = window.location.port === '5000' || window.location.pathname.startsWith('/api');
    this.baseUrl = isHostedOnBackend ? '/api' : 'http://127.0.0.1:5000/api';
    this.isBackendAvailable = false;
    this.checkConnection();
  }

  /**
   * Health check to detect whether the Python backend is live
   */
  async checkConnection() {
    try {
      const res = await fetch(`${this.baseUrl}/health`, { method: 'GET', cache: 'no-cache' });
      if (res.ok) {
        const data = await res.json();
        this.isBackendAvailable = data.status === 'online';
        window.dispatchEvent(new CustomEvent('lifedrop:backend-status', { detail: { online: true, service: data.service } }));
        return true;
      }
    } catch (e) {
      this.isBackendAvailable = false;
      window.dispatchEvent(new CustomEvent('lifedrop:backend-status', { detail: { online: false } }));
    }
    return false;
  }

  // --- Donors ---

  async getDonors(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.bloodGroup && filters.bloodGroup !== 'ALL') params.append('bloodGroup', filters.bloodGroup);
      if (filters.city) params.append('city', filters.city);
      if (filters.available !== undefined) params.append('available', filters.available);

      const res = await fetch(`${this.baseUrl}/donors?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data || [];
    } catch (e) {
      console.warn('[LifedropApi] Failed to fetch donors from backend, using local fallback:', e);
      return null;
    }
  }

  async registerDonor(donorData) {
    try {
      const res = await fetch(`${this.baseUrl}/donors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(donorData)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to register donor to backend:', e);
      return null;
    }
  }

  async matchDonors(bloodGroup, city = '') {
    try {
      const params = new URLSearchParams({ bloodGroup, city });
      const res = await fetch(`${this.baseUrl}/donors/match?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data || [];
    } catch (e) {
      console.warn('[LifedropApi] Failed to query donor matches:', e);
      return null;
    }
  }

  async updateDonorStatus(donorId, updates = {}) {
    try {
      const res = await fetch(`${this.baseUrl}/donors/${donorId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to update donor status:', e);
      return null;
    }
  }

  // --- Emergency Requests ---

  async getRequests(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.urgency && filters.urgency !== 'ALL') params.append('urgency', filters.urgency);
      if (filters.status && filters.status !== 'ALL') params.append('status', filters.status);
      if (filters.city) params.append('city', filters.city);

      const res = await fetch(`${this.baseUrl}/requests?${params.toString()}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data || [];
    } catch (e) {
      console.warn('[LifedropApi] Failed to fetch requests from backend:', e);
      return null;
    }
  }

  async getRequestById(requestId) {
    try {
      const res = await fetch(`${this.baseUrl}/requests/${encodeURIComponent(requestId)}`);
      if (!res.ok) return null;
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to fetch request by ID:', e);
      return null;
    }
  }

  async createRequest(reqData) {
    try {
      const res = await fetch(`${this.baseUrl}/requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reqData)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to create emergency request on backend:', e);
      return null;
    }
  }

  async updateRequestStatus(reqId, status, confirmedCount) {
    try {
      const body = {};
      if (status) body.status = status;
      if (confirmedCount !== undefined) body.donorsConfirmed = confirmedCount;

      const res = await fetch(`${this.baseUrl}/requests/${encodeURIComponent(reqId)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to update request status:', e);
      return null;
    }
  }

  async addTimelineEvent(reqId, eventText) {
    try {
      const res = await fetch(`${this.baseUrl}/requests/${encodeURIComponent(reqId)}/timeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event: eventText })
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to append timeline event:', e);
      return null;
    }
  }

  // --- Inventory & Stats ---

  async getInventory() {
    try {
      const res = await fetch(`${this.baseUrl}/inventory`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data || [];
    } catch (e) {
      console.warn('[LifedropApi] Failed to fetch inventory:', e);
      return null;
    }
  }

  async getStats() {
    try {
      const res = await fetch(`${this.baseUrl}/stats`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data;
    } catch (e) {
      console.warn('[LifedropApi] Failed to fetch stats:', e);
      return null;
    }
  }

  // --- Assistant / AI Chat ---

  async chatWithAssistant(message, sessionId = 'default') {
    try {
      const res = await fetch(`${this.baseUrl}/assistant/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId })
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('[LifedropApi] Assistant API offline:', e);
      return null;
    }
  }

  async resetAssistantSession(sessionId = 'default') {
    try {
      const res = await fetch(`${this.baseUrl}/assistant/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('[LifedropApi] Assistant reset failed:', e);
      return null;
    }
  }

  async getAssistantHistory(sessionId = 'default') {
    try {
      const res = await fetch(`${this.baseUrl}/assistant/history/${encodeURIComponent(sessionId)}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const json = await res.json();
      return json.data || [];
    } catch (e) {
      console.warn('[LifedropApi] Assistant history fetch failed:', e);
      return [];
    }
  }
}

// Instantiate global client
window.lifedropApi = new LifedropApiClient();
