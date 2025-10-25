// Utility functions
const Utils = {
    // API configuration for local development
    API_BASE_URL: 'https://localhost:8082',
    
    // Format date
    formatDate: (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Generate unique ID (for client-side temporary IDs)
    generateId: () => {
        return 'temp_' + Date.now().toString() + Math.random().toString(36).substr(2, 9);
    },

    // Validate URL
    isValidUrl: (string) => {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    },

    // Get auth token
    getAuthToken: () => {
        return localStorage.getItem('authToken');
    },

    // Check if user is authenticated
    isAuthenticated: () => {
        return !!localStorage.getItem('authToken');
    },

    // Require authentication - redirect if not logged in
    requireAuth: () => {
        if (!Utils.isAuthenticated()) {
            window.location.href = '/';
            return false;
        }
        return true;
    },

    // Initialize user info
    initUserInfo: () => {
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                const avatar = document.getElementById('user-avatar');
                const username = document.getElementById('username');
                
                if (avatar) {
                    avatar.textContent = user.username?.charAt(0).toUpperCase() || 'U';
                }
                if (username) {
                    username.textContent = user.username || 'User';
                }
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }
    },

    // API request helper with better error handling
    apiRequest: async (endpoint, options = {}) => {
        const token = Utils.getAuthToken();
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            },
            credentials: 'include' // Include cookies for local development
        };

        try {
            console.log(`Making API request to: ${Utils.API_BASE_URL}${endpoint}`);
            
            const response = await fetch(`${Utils.API_BASE_URL}${endpoint}`, {
                ...defaultOptions,
                ...options,
                headers: {
                    ...defaultOptions.headers,
                    ...options.headers
                }
            });

            // Handle unauthorized responses
            if (response.status === 401) {
                localStorage.removeItem('authToken');
                localStorage.removeItem('userData');
                Utils.showNotification('Session expired. Please login again.', 'error');
                setTimeout(() => window.location.href = '/', 2000);
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { error: { message: `HTTP ${response.status}` } };
                }
                throw new Error(errorData.error?.message || `Request failed with status ${response.status}`);
            }

            const data = await response.json();
            return data;

        } catch (error) {
            console.error('API request failed:', error);
            
            // Don't show notification for navigation errors
            if (error.name !== 'TypeError' || error.message !== 'Failed to fetch') {
                Utils.showNotification(error.message || 'Network error. Please try again.', 'error');
            }
            
            throw error;
        }
    },

    registerUser: async (email, username, password) => {
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const raw = JSON.stringify({
            "email": email,
            "username": username,
            "password": password
        });

        const requestOptions = {
            method: "POST",
            headers: myHeaders,
            body: raw,
            redirect: "follow"
        };

        try {
            const response = await fetch("http://localhost:8082/auth/register", requestOptions);
            const result = await response.text();
            return result;
        } catch (error) {
            console.error(error);
            throw error;
        }
    },

    loginUser: async (email, password) => {
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");

        const raw = JSON.stringify({
            "email": email,
            "password": password
        });

        const requestOptions = {
            method: "POST",
            headers: myHeaders,
            body: raw,
            redirect: "follow"
        };

        try {
            const response = await fetch("http://localhost:8082/auth/login", requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    },

    fetchBookmarks: (token) => {
        const myHeaders = new Headers();
        myHeaders.append("Authorization", `Bearer ${token}`);

        const requestOptions = {
            method: "GET",
            headers: myHeaders,
            redirect: "follow"
        };

        try {
            const response = fetch("http://localhost:8082/bookmarks", requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = response.json(); // Use json() for JSON responses
            return result;
        } catch (error) {
            console.error('Failed to fetch bookmarks:', error);
            throw error;
        }
    },

    putBookmark: (token, bookmarkData) => {
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        myHeaders.append("Authorization", `Bearer ${token}`);

        const raw = JSON.stringify(bookmarkData);

        const requestOptions = {
            method: "POST",
            headers: myHeaders,
            body: raw,
            redirect: "follow"
        };

        try {
            const response = fetch("http://localhost:8082/bookmarks", requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = response.json();
            return result;
        } catch (error) {
            console.error('Failed to create bookmark:', error);
            throw error;
        }
    },
    
    // Show notification
    showNotification: (message, type = 'info') => {
        // Remove existing notifications
        document.querySelectorAll('.notification').forEach(n => n.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${Utils.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    },

    getNotificationIcon: (type) => {
        const icons = {
            info: 'fa-info-circle',
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle'
        };
        return icons[type] || icons.info;
    },

    // Escape HTML to prevent XSS
    escapeHtml: (unsafe) => {
        if (!unsafe) return '';
        const div = document.createElement('div');
        div.textContent = unsafe;
        return div.innerHTML;
    },

    // Debounce function for search
    debounce: (func, wait) => {
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
};

// Add CSS for notifications
const notificationStyles = `
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    border-radius: var(--border-radius);
    color: white;
    z-index: 10000;
    animation: slideIn 0.3s ease;
    max-width: 400px;
    box-shadow: var(--box-shadow);
    border-left: 4px solid transparent;
}

.notification-info {
    background-color: var(--primary);
    border-left-color: var(--primary-dark);
}

.notification-success {
    background-color: var(--success);
    border-left-color: #3ab3d4;
}

.notification-warning {
    background-color: var(--warning);
    border-left-color: #e0861b;
}

.notification-error {
    background-color: var(--danger);
    border-left-color: #e11d74;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.notification-content i {
    font-size: 1.2em;
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);