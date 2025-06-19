// Import functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log("Import.js loaded");
    
    // Get the form and button elements
    var importForm = document.getElementById('importForm');
    var importBtn = document.getElementById('importBtn');
    var loadingBtn = document.getElementById('loadingBtn');
    
    // Add submit event listener to the form
    if (importForm) {
        console.log("Import form found");
        importForm.addEventListener('submit', function(e) {
            console.log("Form submitted");
            
            // Check if file is selected
            var fileInput = document.getElementById('importFile');
            if (fileInput && fileInput.files.length === 0) {
                e.preventDefault();
                alert('يرجى اختيار ملف للاستيراد');
                return false;
            }
            
            // Validate file type
            var fileName = fileInput.value;
            var fileExt = fileName.split('.').pop().toLowerCase();
            if (fileExt !== 'xlsx' && fileExt !== 'xls' && fileExt !== 'csv') {
                e.preventDefault();
                alert('يرجى اختيار ملف بتنسيق Excel (.xlsx, .xls) أو CSV (.csv)');
                return false;
            }
            
            // Show loading button and hide submit button
            if (importBtn) importBtn.classList.add('d-none');
            if (loadingBtn) loadingBtn.classList.remove('d-none');
        });
    }
    
    // Function to show the import modal
    window.showImportModal = function() {
        console.log("Showing import modal");
        var importModal = document.getElementById('importModal');
        if (importModal && typeof bootstrap !== 'undefined') {
            try {
                var modal = new bootstrap.Modal(importModal);
                modal.show();
            } catch (error) {
                console.error("Error showing modal:", error);
                // Fallback method if the bootstrap Modal constructor fails
                importModal.style.display = 'block';
                importModal.classList.add('show');
                document.body.classList.add('modal-open');
                
                // Create backdrop if it doesn't exist
                var backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        } else {
            console.error("Import modal or bootstrap not found");
        }
    };
    
    // Check if we need to show the modal on page load
    var importResults = document.querySelector('[data-import-results="true"]');
    if (importResults) {
        console.log("Import results found, showing modal");
        window.showImportModal();
    }
}); 