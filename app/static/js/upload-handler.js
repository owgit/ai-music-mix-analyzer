/**
 * Handle the file upload process
 * @param {File} file - The audio file to upload
 */
function handleFileUpload(file) {
    if (!file) return;
    
    // Check if the file is an audio file
    if (!file.type.startsWith('audio/')) {
        showError('Please select an audio file (MP3, WAV, FLAC, etc.)');
        return;
    }
    
    // Check if the file size is within limits (100MB)
    const maxSize = 100 * 1024 * 1024; // 100MB in bytes
    if (file.size > maxSize) {
        showError('File size exceeds the 100MB limit. Please select a smaller file.');
        return;
    }
    
    // Hide the upload area and show the processing indicator
    if (window.detailedProgress && window.detailedProgress.showProcessingIndicator) {
        window.detailedProgress.showProcessingIndicator('Preparing your audio file...');
    } else {
        // Fallback if the detailed progress module isn't available
        document.getElementById('upload-area').style.display = 'none';
        document.getElementById('progress-container').style.display = 'block';
    }
    
    // Create FormData for the file upload
    const formData = new FormData();
    formData.append('audio_file', file);
    
    // Get the instrumental track status
    const isInstrumental = document.getElementById('is-instrumental')?.checked || false;
    formData.append('is_instrumental', isInstrumental ? 'true' : 'false');
    
    // Create the upload request
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);
    
    // Set up progress tracking
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);
            updateUploadProgress(percentComplete);
            
            // Update the processing message based on upload progress
            if (window.detailedProgress && window.detailedProgress.updateProcessingStatus) {
                if (percentComplete < 30) {
                    window.detailedProgress.updateProcessingStatus('Uploading your audio file...');
                } else if (percentComplete < 70) {
                    window.detailedProgress.updateProcessingStatus('Upload in progress...');
                } else {
                    window.detailedProgress.updateProcessingStatus('Almost there, finalizing upload...');
                }
            }
        }
    };
    
    // Handle the response
    xhr.onload = function() {
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Redirect to the results page
                    window.location.href = response.redirect_url;
                } else {
                    showError(response.error || 'Upload failed. Please try again.');
                    resetUploadUI();
                }
            } catch (e) {
                showError('Error processing response. Please try again.');
                resetUploadUI();
            }
        } else {
            showError('Upload failed with status: ' + xhr.status);
            resetUploadUI();
        }
    };
    
    // Handle errors
    xhr.onerror = function() {
        showError('Network error occurred. Please check your connection and try again.');
        resetUploadUI();
    };
    
    // Start the upload
    xhr.send(formData);
} 