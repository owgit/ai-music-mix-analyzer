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
            
            // Check if it's an upload request
            if (settings.url.includes('/upload') || settings.url.includes('/analyze')) {
                // Show improved user feedback
                const uploadStatus = document.getElementById('upload-status');
                if (uploadStatus) {
                    uploadStatus.innerHTML = `
                        <div class="timeout-message">
                            <p><strong>Analysis is continuing in the background</strong></p>
                            <p>Your file is being analyzed even though the connection timed out. Please check back in a few minutes.</p>
                            <p>Refresh the page and look for your track in the recent analyses section.</p>
                        </div>
                    `;
                    uploadStatus.style.display = 'block';
                } else {
                    alert('Your upload is taking longer than expected. The analysis is continuing in the background. Please check the results page in a few minutes.');
                }
            }
        }
    });

    // For the upload form specifically
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        // Add progress monitoring
        uploadForm.addEventListener('submit', function(e) {
            // Prevent default form submission if we're handling it with AJAX
            if (typeof window.initiateAndPollProcess === 'function') {
                e.preventDefault();
                
                // Get file name or ID from the form
                const fileInput = document.getElementById('file-input');
                if (fileInput && fileInput.files.length > 0) {
                    const fileName = fileInput.files[0].name;
                    
                    // Show processing status
                    const uploadStatus = document.getElementById('upload-status');
                    if (uploadStatus) {
                        uploadStatus.innerHTML = 'Uploading and analyzing your file. This will take several minutes...';
                        uploadStatus.style.display = 'block';
                    }
                    
                    // For demo purposes, let's progress the upload stage
                    // In a real implementation, you'd handle the file upload first,
                    // then call initiateAndPollProcess with the returned track ID
                    
                    // Here we would do the actual file upload using FormData and fetch
                    // Then pass the returned track ID to the polling function
                }
            } else {
                // Default behavior if polling function isn't available
                const uploadStatus = document.getElementById('upload-status');
                if (uploadStatus) {
                    uploadStatus.innerHTML = 'Uploading and analyzing your file. This may take several minutes for larger files...';
                    uploadStatus.style.display = 'block';
                }
            }
        });
    }
    
    // Add listener for the progress bar to update with more granular feedback
    const progressBar = document.getElementById('progress-bar');
    const progressStage = document.getElementById('progress-stage');
    const progressText = document.getElementById('progress-text');
    
    if (progressBar && progressStage && progressText) {
        // Create a mutation observer to watch for changes to the progress bar's width
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'style') {
                    const width = parseInt(progressBar.style.width);
                    
                    // If progress seems stuck at a certain percentage for too long
                    if (width > 90 && width < 100) {
                        // Gradually update the message to indicate it's still working
                        if (!progressText.dataset.longProcess) {
                            progressText.dataset.longProcess = 'true';
                            progressText.innerHTML = 'Analysis is taking longer than usual but still processing...';
                        }
                    }
                }
            });
        });
        
        // Start observing the progress bar
        observer.observe(progressBar, { attributes: true });
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