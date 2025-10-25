// Sync module
const Sync = {
    lastSync: null,
    syncStatus: 'synced',

    init: function() {
        this.bindEvents();
        this.updateSyncStatus();
    },

    bindEvents: function() {
        // Sync now button
        document.getElementById('sync-now-btn').addEventListener('click', () => {
            this.syncNow();
        });

        // Resolve conflicts button
        document.getElementById('resolve-conflicts-btn').addEventListener('click', () => {
            this.resolveConflicts();
        });
    },

    updateSyncStatus: function() {
        const indicator = document.querySelector('.sync-indicator');
        const statusText = document.querySelector('.sync-status span');
        
        indicator.className = 'sync-indicator ' + this.syncStatus;
        
        if (this.syncStatus === 'synced') {
            statusText.textContent = `Last synchronized: ${this.getLastSyncText()}`;
        } else if (this.syncStatus === 'pending') {
            statusText.textContent = 'Sync in progress...';
        } else {
            statusText.textContent = 'Sync error - conflicts detected';
        }
    },

    getLastSyncText: function() {
        if (!this.lastSync) {
            return 'Never';
        }
        
        const now = new Date();
        const lastSync = new Date(this.lastSync);
        const diffMs = now - lastSync;
        const diffMins = Math.floor(diffMs / 60000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minutes ago`;
        
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours} hours ago`;
        
        return lastSync.toLocaleDateString();
    },

    syncNow: function() {
        this.syncStatus = 'pending';
        this.updateSyncStatus();
        
        Utils.showNotification('Syncing bookmarks...', 'info');
        
        // Simulate API call
        setTimeout(() => {
            this.lastSync = new Date().toISOString();
            this.syncStatus = Math.random() > 0.2 ? 'synced' : 'error';
            this.updateSyncStatus();
            
            if (this.syncStatus === 'synced') {
                Utils.showNotification('Sync completed successfully!', 'success');
            } else {
                Utils.showNotification('Sync completed with conflicts', 'warning');
            }
        }, 2000);
    },

    resolveConflicts: function() {
        // In a real app, this would open a conflict resolution interface
        Utils.showNotification('Opening conflict resolution...', 'info');
        
        // Simulate conflict resolution
        setTimeout(() => {
            this.syncStatus = 'synced';
            this.updateSyncStatus();
            Utils.showNotification('Conflicts resolved successfully!', 'success');
        }, 1500);
    }
};