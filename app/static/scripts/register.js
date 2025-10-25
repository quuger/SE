const API_BASE = 'http://localhost:8082/auth';

let currentToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

// Check if user is already logged in
if (currentToken && currentUser) {
    showProtected();
}

function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

function showLogin() {
    document.getElementById('login-container').classList.add('active');
    document.getElementById('register-container').classList.remove('active');
    document.getElementById('protected-container').classList.remove('active');
    clearMessages();
}

function showRegister() {
    document.getElementById('register-container').classList.add('active');
    document.getElementById('login-container').classList.remove('active');
    document.getElementById('protected-container').classList.remove('active');
    clearMessages();
}

function showProtected() {
    document.getElementById('protected-container').classList.add('active');
    document.getElementById('login-container').classList.remove('active');
    document.getElementById('register-container').classList.remove('active');
    document.getElementById('user-name').textContent = currentUser;
}

function clearMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => {
        msg.style.display = 'none';
    });
}

// Login form handler
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentToken = data.access_token;
            currentUser = data.username;
            
            // Store in localStorage
            localStorage.setItem('authToken', currentToken);
            localStorage.setItem('currentUser', currentUser);
            
            showMessage('login-message', 'Login successful!', 'success');
            setTimeout(() => showProtected(), 1000);
        } else {
            showMessage('login-message', data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('login-message', 'Network error. Please try again.', 'error');
    }
});

// Register form handler
document.getElementById('register-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('register-message', 'Registration successful! Please login.', 'success');
            setTimeout(() => showLogin(), 2000);
            document.getElementById('register-form').reset();
        } else {
            showMessage('register-message', data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('register-message', 'Network error. Please try again.', 'error');
    }
});

// Test protected route
async function testProtectedRoute() {
    if (!currentToken) {
        showMessage('protected-message', 'No token found. Please login again.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/protected?token=${currentToken}`);
        const data = await response.json();
        
        if (response.ok) {
            showMessage('protected-message', data.message, 'success');
        } else {
            showMessage('protected-message', data.detail || 'Access denied', 'error');
        }
    } catch (error) {
        showMessage('protected-message', 'Network error. Please try again.', 'error');
    }
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    currentToken = null;
    currentUser = null;
    showLogin();
    document.getElementById('login-form').reset();
    showMessage('login-message', 'Logged out successfully', 'success');
}