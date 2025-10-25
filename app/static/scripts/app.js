// Main application module
const App = {
    init: function() {
        this.bindEvents();
        Auth.init();
        Bookmarks.init();
        ImportExport.init();
        Sync.init();
    },

    bindEvents: function() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                if (Auth.currentUser) {
                    this.showPage(link.getAttribute('data-page'));
                }
            });
        });
    },

    showPage: function(pageId) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show selected page
        document.getElementById(`${pageId}-page`).classList.add('active');
        
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageId) {
                link.classList.add('active');
            }
        });
    },

    showAuthPages: function() {
        // Hide app pages, show auth pages
        document.querySelectorAll('.page:not(#login-page):not(#register-page)').forEach(page => {
            page.style.display = 'none';
        });
        document.getElementById('login-page').classList.add('active');
        document.getElementById('register-page').classList.remove('active');
        document.querySelector('header').style.display = 'none';
        document.querySelector('footer').style.display = 'none';
    },

    showAppPages: function() {
        // Show all pages and navigation
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'block';
        });
        document.querySelector('header').style.display = 'block';
        document.querySelector('footer').style.display = 'block';
        
        this.showAuthPages();
        this.showPage('bookmarks');
        
        // Update user info in header
        if (Auth.currentUser) {
            const avatar = document.querySelector('.avatar');
            const username = document.querySelector('.user-info span');
            
            avatar.textContent = Auth.currentUser.username.charAt(0).toUpperCase();
            username.textContent = Auth.currentUser.username;
        }
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    App.init();
});