// Authentication module
const Auth = {
    currentUser: null,

    init: function() {
        this.bindEvents();
        this.checkAuthStatus();
    },

    bindEvents: function() {
        // Login form
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }

        // Register form
        const registerForm = document.getElementById('register-form');
        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleRegister();
            });
        }

        // Logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }
    },

    checkAuthStatus: function() {
        if (Utils.isAuthenticated()) {
            try {
                this.currentUser = JSON.parse(localStorage.getItem('userData'));
                // If on auth pages, redirect to bookmarks
                if (window.location.pathname === '/' || window.location.pathname.includes('index.html') || 
                    window.location.pathname.includes('register.html')) {
                    window.location.href = '/bookmarks.html';
                }
            } catch (e) {
                console.error('Error checking auth status:', e);
                this.handleLogout();
            }
        } else {
            // If on protected pages, redirect to login
            if (window.location.pathname.includes('bookmarks.html') || 
                window.location.pathname.includes('import-export.html') ||
                window.location.pathname.includes('sync.html')) {
                window.location.href = '/';
            }
        }
    },

    handleLogin: async function() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        if (!email || !password) {
            Utils.showNotification('Please fill in all fields', 'warning');
            return;
        }

        try {
            const submitBtn = document.querySelector('#login-form button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Signing in...';
            submitBtn.disabled = true;

            const response = await Utils.loginUser(email, password);

            console.log(response.access_token);
            sessionStorage.setItem('authToken', response.access_token);
            localStorage.setItem('userData', JSON.stringify(response.user));
            this.currentUser = response.user;
            
            Utils.showNotification(`Welcome back, ${response.user.username}!`, 'success');
            setTimeout(() => {
                window.location.href = '/bookmarks.html';
            }, 1500);

        } catch (error) {
            console.error('Login failed:', error);
            // Reset button
            const submitBtn = document.querySelector('#login-form button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Sign In';
                submitBtn.disabled = false;
            }
        }
    },

    handleRegister: async function() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const confirmPassword = document.getElementById('register-confirm-password')?.value;

        if (!username || !email || !password) {
            Utils.showNotification('Please fill in all fields', 'warning');
            return;
        }

        if (confirmPassword && password !== confirmPassword) {
            Utils.showNotification('Passwords do not match', 'warning');
            return;
        }

        if (password.length < 6) {
            Utils.showNotification('Password must be at least 6 characters long', 'warning');
            return;
        }

        try {
            const submitBtn = document.querySelector('#register-form button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Creating account...';
            submitBtn.disabled = true;

            const response = await Utils.registerUser(email, username, password);

            sessionStorage.setItem('authToken', response.access_token);
            localStorage.setItem('userData', JSON.stringify(response.user));
            this.currentUser = response.user;
            
            Utils.showNotification(`Account created successfully! Welcome, ${response.user.username}!`, 'success');
            setTimeout(() => {
                window.location.href = '/bookmarks.html';
            }, 1500);

        } catch (error) {
            console.error('Registration failed:', error);
            // Reset button
            const submitBtn = document.querySelector('#register-form button[type="submit"]');
            if (submitBtn) {
                submitBtn.textContent = 'Sign Up';
                submitBtn.disabled = false;
            }
        }
    },

    handleLogout: function() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        this.currentUser = null;
        Utils.showNotification('Logged out successfully', 'info');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    }
};

// Initialize auth on all pages
document.addEventListener('DOMContentLoaded', function() {
    Auth.init();
});