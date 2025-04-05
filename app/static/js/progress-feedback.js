// Define ProgressManager class first
class ProgressManager {
    constructor() {
        this.logEntries = [];
        this.animationFrame = null;
        this.activityMessages = [
            'Processing audio',
            'Analyzing frequencies',
            'Calculating dynamics',
            'Evaluating stereo field'
        ];
        this.activityInterval = null;
        this.detailedSteps = [
            {
                id: 'file-upload',
                title: 'File Upload',
                description: 'Transferring your audio file to our servers',
                subTasks: ['Verifying format', 'Checking file size', 'Validating metadata']
            },
            {
                id: 'loading-audio', 
                title: 'Audio Decoding',
                description: 'Loading and preparing audio for analysis',
                subTasks: ['Reading headers', 'Decoding samples', 'Normalizing levels']
            },
            {
                id: 'frequency-analysis',
                title: 'Frequency Analysis',
                description: 'Analyzing frequency distribution across 7 bands',
                subTasks: ['Computing FFT', 'Band separation', 'Balance scoring']
            },
            // ... more detailed steps ...
        ];
    }

    // Unified update method
    updateProgress({ type = 'step', id, status, message, active }) {
        const element = document.getElementById(`${type}-${id}`);
        if (!element) return;

        // Handle different update types
        switch(type) {
            case 'step':
                element.classList.remove('waiting', 'in-progress', 'completed');
                element.classList.add(status);
                break;
            case 'subtask':
                element.classList.toggle('active', active);
                break;
            case 'processing':
                element.textContent = message;
                break;
        }

        if (message) this.addToLog(message);
    }

    // Enhanced logging with performance optimization
    addToLog(message) {
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        const logEntry = `[${timestamp}] ${message}`;
        
        this.logEntries.push(logEntry);
        if (this.logEntries.length > 50) {
            this.logEntries.shift(); // Keep log manageable
        }

        this.renderLog();
    }

    addToProgressLog(message) {
        this.addToLog(message);
    }

    renderLog() {
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        this.animationFrame = requestAnimationFrame(() => {
            const logContainer = document.getElementById('progress-log');
            if (logContainer) {
                logContainer.innerHTML = this.logEntries
                    .map(entry => `<div class="log-entry">${entry}</div>`)
                    .join('');
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        });
    }

    // Enhanced method to show detailed analysis
    showAnalysisDetails(stepId, details) {
        const step = this.detailedSteps.find(s => s.id === stepId);
        if (step) {
            this.addToLog(`<strong>${step.title}:</strong> ${details}`);
            
            // Visual feedback for current step
            this.updateProgress({
                type: 'step',
                id: stepId,
                status: 'in-progress',
                message: details
            });
        }
    }

    // Enhanced method to complete analysis step
    completeAnalysisStep(stepId, results) {
        const step = this.detailedSteps.find(s => s.id === stepId);
        if (step) {
            const summary = this.generateStepSummary(step, results);
            this.addToLog(summary);
            
            this.updateProgress({
                type: 'step',
                id: stepId,
                status: 'completed',
                message: summary
            });
        }
    }

    generateStepSummary(step, results) {
        // Generate human-readable summary of analysis results
        return `<div class='analysis-summary'>
            <h4>${step.title} Complete</h4>
            <p>${results.summary || 'Analysis completed successfully'}</p>
            ${results.details ? `<pre>${JSON.stringify(results.details, null, 2)}</pre>` : ''}
        </div>`;
    }

    // Processing indicator functions
    showProcessingIndicator(message) {
        const indicator = document.getElementById('processing-indicator');
        if (indicator) {
            indicator.style.display = 'flex';
            this.updateProgress({
                type: 'processing',
                id: 'status-text',
                message: message
            });
            this.startActivityAnimation();
        }
    }

    hideProcessingIndicator() {
        const indicator = document.getElementById('processing-indicator');
        if (indicator) {
            indicator.style.display = 'none';
            this.stopActivityAnimation();
        }
    }

    startActivityAnimation() {
        let counter = 0;
        const activityElement = document.getElementById('progress-activity-counter');
        
        if (activityElement && !this.activityInterval) {
            this.activityInterval = setInterval(() => {
                const msg = this.activityMessages[counter % this.activityMessages.length];
                activityElement.textContent = `${msg}${'.'.repeat(counter % 3 + 1)}`;
                counter++;
            }, 1000);
        }
    }

    stopActivityAnimation() {
        if (this.activityInterval) {
            clearInterval(this.activityInterval);
            this.activityInterval = null;
        }
    }
}

// Then create and initialize the instance
const _progressManager = new ProgressManager();

// Add safe method access with error handling
function getProgressManager() {
    if (!_progressManager) {
        console.error('ProgressManager not initialized!');
        return {
            updateProgress: () => {},
            addToLog: () => {}
        };
    }
    return _progressManager;
}

// Add legacy methods with null checks
_progressManager.updateDetailedProgress = function(stepId, status, message) {
    try {
        this.updateProgress({
            type: 'step',
            id: `progress-step-${stepId}`,
            status: status,
            message: message
        });
    } catch (e) {
        console.error('Error in updateDetailedProgress:', e);
    }
};

_progressManager.updateSubTaskProgress = function(stepId, subTaskId, active, message) {
    try {
        this.updateProgress({
            type: 'subtask',
            id: `${stepId}-${subTaskId.replace(/\s+/g, '-').toLowerCase()}`,
            active: active,
            message: message
        });
    } catch (e) {
        console.error('Error in updateSubTaskProgress:', e);
    }
};

_progressManager.updateProcessingStatus = function(message) {
    try {
        this.updateProgress({
            type: 'processing',
            id: 'status-text',
            message: message
        });
    } catch (e) {
        console.error('Error in updateProcessingStatus:', e);
    }
};

// Export to window with fallback
window.detailedProgress = _progressManager || {
    updateDetailedProgress: () => {},
    updateSubTaskProgress: () => {},
    updateProcessingStatus: () => {},
    addToProgressLog: () => {},
    addToLog: () => {},
    showAnalysisDetails: () => {},
    completeAnalysisStep: () => {}
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize ad banner functionality
    initAdBanners();
    
    // Initialize processing indicator
    initProcessingIndicator();

    // Verify initialization
    if (!window.detailedProgress) {
        console.error('Progress system failed to initialize!');
    }
});

/**
 * Initialize the ad banner functionality
 */
function initAdBanners() {
    // Check if ad banners are already initialized
    if (window.adBannersInitialized) {
        console.log('[Ad Banners] Ad banners already initialized, skipping');
        return;
    }
    
    console.log('[Ad Banners] Initializing ad banner functionality');
    
    // Get the ad banner elements
    const leftAdBanner = document.getElementById('left-ad-banner');
    const rightAdBanner = document.getElementById('right-ad-banner');
    const mobileAdBanner = document.getElementById('mobile-ad-banner');
    
    // Log the initial state of the ad banners
    console.log('[Ad Banners] Initial ad banner state:', {
        'left-ad-banner': leftAdBanner ? {
            exists: true,
            visible: leftAdBanner.classList.contains('visible'),
            classes: Array.from(leftAdBanner.classList)
        } : { exists: false },
        'right-ad-banner': rightAdBanner ? {
            exists: true,
            visible: rightAdBanner.classList.contains('visible'),
            classes: Array.from(rightAdBanner.classList)
        } : { exists: false },
        'mobile-ad-banner': mobileAdBanner ? {
            exists: true,
            visible: mobileAdBanner.classList.contains('visible'),
            classes: Array.from(mobileAdBanner.classList)
        } : { exists: false }
    });
    
    // Initialize ad visibility tracking if function exists
    if (typeof window.setupAdVisibilityTracking === 'function') {
        window.setupAdVisibilityTracking();
        console.log('[Ad Banners] Ad visibility tracking initialized from initAdBanners');
    } else {
        console.warn('[Ad Banners] setupAdVisibilityTracking function not found');
    }
    
    // Set up event listeners for upload and analysis process
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                console.log('[Ad Banners] File selected via input, showing ad banners', {
                    fileName: this.files[0].name,
                    fileSize: this.files[0].size,
                    fileType: this.files[0].type,
                    timestamp: Date.now()
                });
                // Show ad banners when file is selected
                showAdBanners();
            }
        });
    } else {
        console.warn('[Ad Banners] File input element not found');
    }
    
    // Add drag and drop event listeners
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                console.log('[Ad Banners] File dropped, showing ad banners', {
                    fileName: e.dataTransfer.files[0].name,
                    fileSize: e.dataTransfer.files[0].size,
                    fileType: e.dataTransfer.files[0].type,
                    timestamp: Date.now()
                });
                // Show ad banners when file is dropped
                showAdBanners();
            }
        });
    } else {
        console.warn('[Ad Banners] Upload area element not found');
    }
    
    // Add event listener for when analysis is complete
    document.addEventListener('analysisComplete', function() {
        console.log('[Ad Banners] Analysis complete event received, hiding ad banners', {
            timestamp: Date.now(),
            timestampFormatted: new Date().toISOString()
        });
        // Hide ad banners when analysis is complete
        hideAdBanners();
    });
    
    // Mark as initialized
    window.adBannersInitialized = true;
    console.log('[Ad Banners] Ad banner initialization complete');
}

/**
 * Show the ad banners
 */
function showAdBanners() {
    const leftAdBanner = document.getElementById('left-ad-banner');
    const rightAdBanner = document.getElementById('right-ad-banner');
    const mobileAdBanner = document.getElementById('mobile-ad-banner');
    const uploadContainer = document.getElementById('upload-container');
    
    // Check if ads are already visible - if so, don't trigger visibility again
    const leftAlreadyVisible = leftAdBanner && leftAdBanner.classList.contains('visible');
    const rightAlreadyVisible = rightAdBanner && rightAdBanner.classList.contains('visible');
    const mobileAlreadyVisible = mobileAdBanner && mobileAdBanner.classList.contains('visible');
    
    // If all ads are already visible, we'll still update status but won't modify DOM
    const allAdsAlreadyVisible = leftAlreadyVisible && rightAlreadyVisible && mobileAlreadyVisible;
    
    const adStatus = {
        left: leftAdBanner ? { 
            element: 'left-ad-banner', 
            wasVisible: leftAlreadyVisible,
            willBeVisible: true 
        } : null,
        right: rightAdBanner ? { 
            element: 'right-ad-banner', 
            wasVisible: rightAlreadyVisible,
            willBeVisible: true 
        } : null,
        mobile: mobileAdBanner ? { 
            element: 'mobile-ad-banner', 
            wasVisible: mobileAlreadyVisible,
            willBeVisible: true 
        } : null,
        timestamp: Date.now(),
        timestampFormatted: new Date().toISOString(),
        allAdsAlreadyVisible: allAdsAlreadyVisible
    };
    
    console.log('[Ad Banners] Showing ad banners', adStatus);
    
    // Add class to upload container when ads are showing to create space
    if (uploadContainer && !uploadContainer.classList.contains('with-ads')) {
        uploadContainer.classList.add('with-ads');
    }
    
    // Track ad visibility in analytics if the function exists
    if (typeof window.trackAdVisibilityStart === 'function') {
        console.log("[Ad Banners] Calling trackAdVisibilityStart for all banners");
        
        if (leftAdBanner) {
            // Ensure tracking is updated for already visible banners too
            window.trackAdVisibilityStart('left-ad-banner');
            
            // Only add class if not already visible
            if (!leftAlreadyVisible) {
                leftAdBanner.classList.add('visible');
            }
        }
        
        if (rightAdBanner) {
            window.trackAdVisibilityStart('right-ad-banner');
            
            if (!rightAlreadyVisible) {
                rightAdBanner.classList.add('visible');
            }
        }
        
        if (mobileAdBanner) {
            window.trackAdVisibilityStart('mobile-ad-banner');
            
            if (!mobileAlreadyVisible) {
                mobileAdBanner.classList.add('visible');
            }
        }
    } else {
        console.warn("[Ad Banners] trackAdVisibilityStart function not found");
        
        // Still add visible class if tracking isn't available
        if (leftAdBanner && !leftAlreadyVisible) leftAdBanner.classList.add('visible');
        if (rightAdBanner && !rightAlreadyVisible) rightAdBanner.classList.add('visible');
        if (mobileAdBanner && !mobileAlreadyVisible) mobileAdBanner.classList.add('visible');
    }
}

/**
 * Hide the ad banners
 */
function hideAdBanners() {
    const leftAdBanner = document.getElementById('left-ad-banner');
    const rightAdBanner = document.getElementById('right-ad-banner');
    const mobileAdBanner = document.getElementById('mobile-ad-banner');
    const uploadContainer = document.getElementById('upload-container');
    
    // Check if ads are already hidden - if so, don't trigger visibility tracking again
    const leftAlreadyHidden = leftAdBanner && !leftAdBanner.classList.contains('visible');
    const rightAlreadyHidden = rightAdBanner && !rightAdBanner.classList.contains('visible');
    const mobileAlreadyHidden = mobileAdBanner && !mobileAdBanner.classList.contains('visible');
    
    // If all ads are already hidden, we'll still log the event but won't modify DOM
    const allAdsAlreadyHidden = leftAlreadyHidden && rightAlreadyHidden && mobileAlreadyHidden;
    
    const adStatus = {
        left: leftAdBanner ? { 
            element: 'left-ad-banner', 
            wasVisible: !leftAlreadyHidden,
            willBeVisible: false 
        } : null,
        right: rightAdBanner ? { 
            element: 'right-ad-banner', 
            wasVisible: !rightAlreadyHidden,
            willBeVisible: false 
        } : null,
        mobile: mobileAdBanner ? { 
            element: 'mobile-ad-banner', 
            wasVisible: !mobileAlreadyHidden,
            willBeVisible: false 
        } : null,
        timestamp: Date.now(),
        timestampFormatted: new Date().toISOString(),
        allAdsAlreadyHidden: allAdsAlreadyHidden
    };
    
    console.log('[Ad Banners] Hiding ad banners', adStatus);
    
    // Track ad visibility end in analytics if the function exists
    if (typeof window.trackAdVisibilityEnd === 'function') {
        console.log("[Ad Banners] Calling trackAdVisibilityEnd for all banners");
        
        // Call tracking function for any banners that were visible
        if (leftAdBanner && !leftAlreadyHidden) {
            window.trackAdVisibilityEnd('left-ad-banner');
        }
        
        if (rightAdBanner && !rightAlreadyHidden) {
            window.trackAdVisibilityEnd('right-ad-banner');
        }
        
        if (mobileAdBanner && !mobileAlreadyHidden) {
            window.trackAdVisibilityEnd('mobile-ad-banner');
        }
    } else {
        console.warn("[Ad Banners] trackAdVisibilityEnd function not found");
    }
    
    // Remove visible class for all banners to ensure consistent state
    if (leftAdBanner) leftAdBanner.classList.remove('visible');
    if (rightAdBanner) rightAdBanner.classList.remove('visible');
    if (mobileAdBanner) mobileAdBanner.classList.remove('visible');
    
    // Remove class from upload container when ads are hidden
    if (uploadContainer) {
        uploadContainer.classList.remove('with-ads');
    }
}

// Initialize processing indicator DOM elements
function initProcessingIndicator() {
    const container = document.getElementById('progress-container');
    if (!container || document.getElementById('processing-indicator')) return;
    
    const indicator = document.createElement('div');
    indicator.id = 'processing-indicator';
    indicator.className = 'processing-indicator';
    
    const spinner = document.createElement('div');
    spinner.className = 'processing-spinner';
    
    const status = document.createElement('div');
    status.id = 'status-text';
    status.className = 'processing-status';
    
    indicator.appendChild(spinner);
    indicator.appendChild(status);
    container.appendChild(indicator);
}