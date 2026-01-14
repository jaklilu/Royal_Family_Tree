// API configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://your-render-backend.onrender.com';  // Update with your Render URL

// Debounce helper
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// API helper functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: { message: 'Request failed' } }));
            throw new Error(error.error?.message || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// API endpoints
const api = {
    async getHealth() {
        return apiRequest('/health');
    },

    async getRoot() {
        return apiRequest('/api/root');
    },

    async search(query) {
        if (!query || query.trim().length === 0) {
            return { results: [] };
        }
        return apiRequest(`/api/search?q=${encodeURIComponent(query)}`);
    },

    async getNeighborhood(personId) {
        return apiRequest(`/api/neighborhood/${personId}`);
    },

    async getPerson(personId) {
        return apiRequest(`/api/person/${personId}`);
    },

    async getRelationship(person1Id, person2Id) {
        return apiRequest(`/api/relationship?person1_id=${person1Id}&person2_id=${person2Id}`);
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { api, debounce };
}

