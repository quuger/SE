// Bookmarks module
const Bookmarks = {
    bookmarks: [],
    filteredBookmarks: [],

    init: function() {
        this.bindEvents();
        this.loadBookmarks();
    },

    bindEvents: function() {
        // Add bookmark form
        document.getElementById('add-bookmark-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddBookmark();
        });

        // Filter and search
        document.getElementById('bookmark-filter').addEventListener('change', () => {
            this.filterBookmarks();
        });

        document.getElementById('bookmark-search').addEventListener('input', () => {
            this.filterBookmarks();
        });
    },

    loadBookmarks: function() {
        token = sessionStorage.getItem('authToken');
        this.bookmarks = Utils.fetchBookmarks(token);

        this.filteredBookmarks = [...this.bookmarks];
        this.renderBookmarks();
    },

    handleAddBookmark: function() {
        const title = document.getElementById('bookmark-title').value;
        const url = document.getElementById('bookmark-url').value;
        const description = document.getElementById('bookmark-description').value;
        const accessLevel = document.getElementById('bookmark-access').value;

        if (!title || !url) {
            Utils.showNotification('Please fill in all required fields', 'warning');
            return;
        }

        if (!Utils.isValidUrl(url)) {
            Utils.showNotification('Please enter a valid URL', 'warning');
            return;
        }

        this.addBookmark(title, url, description, accessLevel);
    },

    addBookmark: function(title, url, description, accessLevel) {
        const newBookmark = {
            url: url,
            title: title,
            description: description,
            access_level: accessLevel,
        };

        token = sessionStorage.getItem('authToken');
        Utils.putBookmark(token, newBookmark);
        // In a real app, this would be an API call
        this.bookmarks.unshift(newBookmark);
        this.filterBookmarks();
        
        // Reset form
        document.getElementById('add-bookmark-form').reset();
        
        Utils.showNotification('Bookmark added successfully!', 'success');
    },

    editBookmark: function(id) {
        const bookmark = this.bookmarks.find(b => b.id === id);
        if (!bookmark) return;

        // In a real app, this would open an edit form/modal
        const newTitle = prompt('Edit title:', bookmark.title);
        if (newTitle && newTitle !== bookmark.title) {
            bookmark.title = newTitle;
            bookmark.updated_at = new Date().toISOString();
            this.filterBookmarks();
            Utils.showNotification('Bookmark updated!', 'success');
        }
    },

    deleteBookmark: function(id) {
        if (!confirm('Are you sure you want to delete this bookmark?')) return;

        // In a real app, this would be an API call
        this.bookmarks = this.bookmarks.filter(bookmark => bookmark.id !== id);
        this.filterBookmarks();
        Utils.showNotification('Bookmark deleted!', 'info');
    },

    filterBookmarks: function() {
        const filterValue = document.getElementById('bookmark-filter').value;
        const searchValue = document.getElementById('bookmark-search').value.toLowerCase();

        this.filteredBookmarks = this.bookmarks.filter(bookmark => {
            // Apply status filter
            if (filterValue !== 'all' && bookmark.status !== filterValue) {
                return false;
            }

            // Apply search filter
            if (searchValue) {
                const searchFields = [bookmark.title, bookmark.url, bookmark.description];
                return searchFields.some(field => 
                    field && field.toLowerCase().includes(searchValue)
                );
            }

            return true;
        });

        this.renderBookmarks();
    },

    renderBookmarks: function() {
        const bookmarkList = document.getElementById('bookmark-list');
        
        if (this.filteredBookmarks.length === 0) {
            bookmarkList.innerHTML = '<p class="text-center" style="grid-column: 1 / -1; padding: 40px;">No bookmarks found. Add your first bookmark above!</p>';
            return;
        }
        
        bookmarkList.innerHTML = this.filteredBookmarks.map(bookmark => `
            <div class="bookmark-item">
                <div class="bookmark-title">${bookmark.title}</div>
                <a href="${bookmark.url}" class="bookmark-url" target="_blank">${bookmark.url}</a>
                <div class="bookmark-description">${bookmark.description || 'No description'}</div>
                <div class="bookmark-meta">
                    <span>Created: ${Utils.formatDate(bookmark.created_at)}</span>
                    <span>Sync v${bookmark.sync_version}</span>
                </div>
                <div class="bookmark-actions">
                    <button class="btn btn-outline btn-sm edit-bookmark" data-id="${bookmark.id}">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger btn-sm delete-bookmark" data-id="${bookmark.id}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
                <div class="bookmark-status status-${bookmark.status}">${bookmark.status}</div>
                <div class="bookmark-status access-${bookmark.access_level}" style="top: 40px;">${bookmark.access_level}</div>
            </div>
        `).join('');
        
        // Add event listeners to action buttons
        document.querySelectorAll('.edit-bookmark').forEach(button => {
            button.addEventListener('click', (e) => {
                const bookmarkId = e.target.closest('.edit-bookmark').getAttribute('data-id');
                this.editBookmark(bookmarkId);
            });
        });
        
        document.querySelectorAll('.delete-bookmark').forEach(button => {
            button.addEventListener('click', (e) => {
                const bookmarkId = e.target.closest('.delete-bookmark').getAttribute('data-id');
                this.deleteBookmark(bookmarkId);
            });
        });
    }
};