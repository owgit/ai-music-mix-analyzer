/**
 * Upload Timeout Extensions
 * Extends the default AJAX timeout for file uploads to handle large files
 * and long processing times.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Increase the default timeout for AJAX requests
    if (typeof $.ajaxSetup === 'function') {
        $.ajaxSetup({
            timeout: 600000, // 10 minutes in milliseconds
            cache: false
        });
    }

    // Add a global AJAX error handler for timeout errors
    $(document).ajaxError(function(event, jqXHR, settings, thrownError) {
        if (jqXHR.status === 0 && thrownError === 'timeout') {
            console.error('Request timed out:', settings.url);
            // Show a user-friendly message
            alert('Your upload is taking longer than expected. The analysis may still be processing in the background. Please check the results page in a few minutes.');
        }
    });

    // For the upload form specifically
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        // Add progress monitoring
        uploadForm.addEventListener('submit', function() {
            const uploadStatus = document.getElementById('upload-status');
            if (uploadStatus) {
                uploadStatus.innerHTML = 'Uploading and analyzing your file. This may take several minutes for larger files...';
                uploadStatus.style.display = 'block';
            }
        });
    }
});

// If using Fetch API for uploads, increase the timeout there too
if (typeof window.fetch === 'function') {
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // For upload endpoints, use extended timeout
        if ((url.includes('/upload') || url.includes('/analyze')) && !options.timeout) {
            options.timeout = 600000; // 10 minutes
        }
        return originalFetch(url, options);
    };
} 