// Authentication module
const Auth = {
    currentUser: null,

    init: function() {
        this.bindEvents();
        this.checkAuthStatus();
    },

    bindEvents: function() {
        // Login form
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Register form
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        // Auth page switches
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterPage();
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginPage();
        });

        // Logout
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.handleLogout();
        });
    },

    checkAuthStatus: function() {
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('userData');

        if (token && userData) {
            this.currentUser = JSON.parse(userData);
            App.showAppPages();
        } else {
            App.showAuthPages();
        }
    },

    handleLogin: async function() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            // Simulate API call - replace with actual API
            const response = await this.mockLogin(email, password);
            
            this.currentUser = response.user;
            localStorage.setItem('authToken', response.access_token);
            localStorage.setItem('userData', JSON.stringify(response.user));
            
            Utils.showNotification('Login successful!', 'success');
            App.showAppPages();
        } catch (error) {
            Utils.showNotification('Login failed. Please check your credentials.', 'error');
        }
    },

    handleRegister: async function() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        try {
            // Simulate API call - replace with actual API
            const response = await this.mockRegister(username, email, password);
            
            this.currentUser = response.user;
            localStorage.setItem('authToken', response.access_token);
            localStorage.setItem('userData', JSON.stringify(response.user));
            
            Utils.showNotification('Registration successful!', 'success');
            App.showAppPages();
        } catch (error) {
            Utils.showNotification('Registration failed. Please try again.', 'error');
        }
    },

    handleLogout: function() {
        this.currentUser = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        App.showAuthPages();
        Utils.showNotification('Logged out successfully', 'info');
    },

    showLoginPage: function() {
        document.getElementById('login-page').classList.add('active');
        document.getElementById('register-page').classList.remove('active');
    },

    showRegisterPage: function() {
        document.getElementById('register-page').classList.add('active');
        document.getElementById('login-page').classList.remove('active');
    },

    // Mock API calls - replace with actual API implementation
    mockLogin: function(email, password) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (email && password) {
                    resolve({
                        user: {
                            id: "123e4567-e89b-12d3-a456-426614174000",
                            email: email,
                            username: "bookmark_lover",
                            account_type: "premium",
                            created_at: "2023-01-15T10:30:00Z",
                            updated_at: "2023-05-20T14:45:00Z"
                        },
                        access_token: "mock_jwt_token_here",
                        refresh_token: "mock_refresh_token_here"
                    });
                } else {
                    reject(new Error('Invalid credentials'));
                }
            }, 1000);
        });
    },

    mockRegister: function(username, email, password) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (username && email && password) {
                    resolve({
                        user: {
                            id: Utils.generateId(),
                            email: email,
                            username: username,
                            account_type: "free",
                            created_at: new Date().toISOString(),
                            updated_at: new Date().toISOString()
                        },
                        access_token: "mock_jwt_token_here",
                        refresh_token: "mock_refresh_token_here"
                    });
                } else {
                    reject(new Error('Invalid registration data'));
                }
            }, 1000);
        });
    }
};