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
    formData.append('file', file); // Changed field name from 'audio_file' to 'file' to match server
    
    // Get the instrumental track status
    const isInstrumental = document.getElementById('instrumental-checkbox')?.checked || false;
    formData.append('is_instrumental', isInstrumental ? 'true' : 'false');
    
    // Create the upload request
    const xhr = new XMLHttpRequest();
    
    // Make sure to use the same protocol as the current page to avoid mixed content issues
    // Use relative URLs when possible, full URLs when necessary
    const uploadUrl = (window.location.protocol === 'https:' && window.location.host !== 'localhost:5001') 
        ? `${window.location.protocol}//${window.location.host}/upload` 
        : '/upload';
    
    xhr.open('POST', uploadUrl, true);
    
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
                    // Display analysis results
                    if (response.results && response.results.channel_info) {
                        const channelInfo = response.results.channel_info;
                        const channelDisplay = document.createElement('div');
                        channelDisplay.className = 'analysis-result';
                        channelDisplay.innerHTML = `
                            <h4>Channel Information</h4>
                            <p>Format: ${channelInfo.is_mono ? 'Mono' : 'Stereo'}</p>
                            <p>Channels: ${channelInfo.channel_count}</p>
                        `;
                        document.getElementById('analysis-results').prepend(channelDisplay);
                    }
                    
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