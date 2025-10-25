// Import/Export module
const ImportExport = {
    init: function() {
        this.bindEvents();
    },

    bindEvents: function() {
        // Format options
        document.querySelectorAll('.format-option').forEach(option => {
            option.addEventListener('click', () => {
                this.selectFormat(option);
            });
        });

        // Export button
        document.getElementById('export-btn').addEventListener('click', () => {
            this.handleExport();
        });

        // Import button
        document.getElementById('import-btn').addEventListener('click', () => {
            this.handleImport();
        });
    },

    selectFormat: function(selectedOption) {
        // Remove active class from all options
        document.querySelectorAll('.format-option').forEach(option => {
            option.classList.remove('active');
        });
        
        // Add active class to selected option
        selectedOption.classList.add('active');
    },

    getSelectedFormat: function() {
        const activeOption = document.querySelector('.format-option.active');
        return activeOption ? activeOption.getAttribute('data-format') : 'json';
    },

    handleExport: function() {
        const format = this.getSelectedFormat();
        
        // In a real app, this would be an API call
        this.exportBookmarks(format);
    },

    handleImport: function() {
        const fileInput = document.getElementById('import-file');
        const file = fileInput.files[0];
        
        if (!file) {
            Utils.showNotification('Please select a file to import', 'warning');
            return;
        }

        const format = this.getSelectedFormat();
        this.importBookmarks(format, file);
    },

    exportBookmarks: function(format) {
        // In a real app, this would be an API call
        const data = JSON.stringify(Bookmarks.bookmarks, null, 2);
        
        // Create download link
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bookmarks.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        Utils.showNotification(`Bookmarks exported as ${format.toUpperCase()}!`, 'success');
    },

    importBookmarks: function(format, file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            try {
                const content = e.target.result;
                
                // In a real app, this would parse the file and send to API
                // For now, we'll just show a success message
                Utils.showNotification(`Successfully imported ${format.toUpperCase()} file!`, 'success');
                
                // Clear file input
                document.getElementById('import-file').value = '';
                
            } catch (error) {
                Utils.showNotification('Error importing file. Please check the format.', 'error');
                console.error('Import error:', error);
            }
        };
        
        reader.onerror = () => {
            Utils.showNotification('Error reading file', 'error');
        };
        
        reader.readAsText(file);
    }
};