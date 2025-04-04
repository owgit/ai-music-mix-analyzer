document.addEventListener('DOMContentLoaded', function() {
    // Initialize the detailed progress feedback system
    initDetailedProgressFeedback();
    
    // Initialize ad banner functionality
    initAdBanners();
    
    // Initialize processing indicator
    initProcessingIndicator();
});

/**
 * Initialize the detailed progress feedback system
 */
function initDetailedProgressFeedback() {
    // Check if we already have the progress container
    const progressContainer = document.getElementById('progress-container');
    if (!progressContainer) return;
    
    // Create the detailed progress section if it doesn't exist
    if (!document.getElementById('progress-detail-container')) {
        createDetailedProgressUI(progressContainer);
    }
}

/**
 * Create the detailed progress UI elements
 * @param {HTMLElement} container - The parent container for the progress UI
 */
function createDetailedProgressUI(container) {
    // Create the detailed progress container
    const detailContainer = document.createElement('div');
    detailContainer.id = 'progress-detail-container';
    detailContainer.className = 'progress-detail-container';
    
    // Create header with title and activity indicator
    const detailHeader = document.createElement('div');
    detailHeader.className = 'progress-detail-header';
    
    const detailHeading = document.createElement('h4');
    detailHeading.className = 'progress-detail-heading';
    detailHeading.textContent = 'Analysis Steps';
    
    const activityCounter = document.createElement('div');
    activityCounter.className = 'progress-activity-counter';
    activityCounter.id = 'progress-activity-counter';
    activityCounter.textContent = 'Processing...';
    
    detailHeader.appendChild(detailHeading);
    detailHeader.appendChild(activityCounter);
    
    // Create the list of processing steps
    const detailList = document.createElement('ul');
    detailList.className = 'progress-detail-list';
    detailList.id = 'progress-detail-list';
    
    // Add all the detailed processing steps
    detailList.innerHTML = generateDetailedSteps();
    
    // Add a log-like display area
    const logContainer = document.createElement('div');
    logContainer.className = 'progress-log-container';
    logContainer.id = 'progress-log-container';
    
    const logHeader = document.createElement('div');
    logHeader.className = 'progress-log-header';
    
    const logTitle = document.createElement('div');
    logTitle.className = 'log-header-title';
    logTitle.textContent = 'Processing Log';
    
    const logLive = document.createElement('div');
    logLive.className = 'log-header-live';
    logLive.textContent = 'LIVE';
    
    logHeader.appendChild(logTitle);
    logHeader.appendChild(logLive);
    
    const logContent = document.createElement('div');
    logContent.className = 'progress-log';
    logContent.id = 'progress-log';
    
    logContainer.appendChild(logHeader);
    logContainer.appendChild(logContent);
    
    // Assemble the container
    detailContainer.appendChild(detailHeader);
    detailContainer.appendChild(detailList);
    detailContainer.appendChild(logContainer);
    
    // Add the container to the main progress container
    container.appendChild(detailContainer);
    
    // Start the activity counter updater
    startActivityCounterUpdater();
}

/**
 * Generate HTML for all the detailed processing steps
 * @returns {string} HTML string for the detailed steps
 */
function generateDetailedSteps() {
    // Define all the processing steps with activity indicators instead of time estimates
    const steps = [
        {
            id: 'file-upload',
            title: 'Step 0: File Upload',
            description: 'Transferring your audio file to our servers'
        },
        {
            id: 'loading-audio',
            title: 'Step 1: Loading Audio',
            description: 'Loading and decoding audio file for analysis'
        },
        {
            id: 'frequency-analysis',
            title: 'Step 2: Frequency Analysis',
            description: 'Analyzing frequency balance using FFT processing',
            subTasks: [
                'Computing STFT', 'Band energy', 'Balance scoring'
            ]
        },
        {
            id: 'dynamics-analysis',
            title: 'Step 3: Dynamic Range Analysis',
            description: 'Measuring dynamic range, crest factor, and PLR'
        },
        {
            id: 'stereo-field',
            title: 'Step 4: Stereo Field Analysis',
            description: 'Analyzing channel correlation and mid/side balance'
        },
        {
            id: 'clarity-analysis',
            title: 'Step 5: Clarity Analysis',
            description: 'Measuring spectral contrast, flatness, and centroid'
        },
        {
            id: 'harmonic-analysis',
            title: 'Step 6: Harmonic Analysis',
            description: 'Detecting key, chord changes, and harmonic complexity'
        },
        {
            id: 'transient-analysis',
            title: 'Step 7: Transient Analysis',
            description: 'Analyzing attack time and percussion energy'
        },
        {
            id: 'spatial-analysis',
            title: 'Step 8: 3D Spatial Analysis',
            description: 'Evaluating height, depth, and width perception'
        },
        {
            id: 'generating-visuals',
            title: 'Step 9: Generating Visualizations',
            description: 'Creating waveforms, spectrograms, and 3D visualizations'
        },
        {
            id: 'ai-processing',
            title: 'Step 10: AI Analysis',
            description: 'Processing with AI for personalized recommendations'
        },
        {
            id: 'finalizing',
            title: 'Step 11: Finalizing Results',
            description: 'Calculating overall score and preparing results'
        }
    ];
    
    // Generate the HTML for each step
    return steps.map(step => {
        const activityIndicator = `<div class="progress-activity-indicator">
            <div class="activity-dot dot-1"></div>
            <div class="activity-dot dot-2"></div>
            <div class="activity-dot dot-3"></div>
        </div>`;
        
        const subTasksHTML = step.subTasks ? 
            `<div class="sub-task-indicators">
                ${step.subTasks.map(task => `<div class="sub-task-indicator" data-task="${task.replace(/\s+/g, '-').toLowerCase()}"></div>`).join('')}
            </div>` : '';
            
        return `
            <li class="progress-detail-item" id="progress-step-${step.id}">
                <div class="progress-detail-icon"></div>
                <div class="progress-detail-info">
                    <div class="progress-detail-title">${step.title}</div>
                    <div class="progress-detail-description">${step.description}</div>
                    ${subTasksHTML}
                </div>
                <div class="progress-activity-indicator-container" id="activity-${step.id}"></div>
            </li>
        `;
    }).join('');
}

/**
 * Update the progress of a specific step
 * @param {string} stepId - The ID of the step to update
 * @param {string} status - The status ('waiting', 'in-progress', 'completed')
 * @param {string} message - Optional message to display in the log
 */
function updateDetailedProgress(stepId, status, message) {
    const stepElement = document.getElementById(`progress-step-${stepId}`);
    if (!stepElement) return;
    
    // Remove all status classes first
    stepElement.classList.remove('waiting', 'in-progress', 'completed');
    
    // Add the appropriate class
    stepElement.classList.add(status);
    
    // Add or remove activity indicator
    const activityContainer = document.getElementById(`activity-${stepId}`);
    if (activityContainer) {
        if (status === 'in-progress') {
            activityContainer.innerHTML = `
                <div class="activity-dot dot-1"></div>
                <div class="activity-dot dot-2"></div>
                <div class="activity-dot dot-3"></div>
            `;
        } else {
            activityContainer.innerHTML = '';
        }
    }
    
    // Add to log if message is provided
    if (message && status === 'in-progress') {
        addToProgressLog(`<span class="log-active">Starting</span> ${stepElement.querySelector('.progress-detail-title').textContent}`);
    } else if (message && status === 'completed') {
        const stepTitle = stepElement.querySelector('.progress-detail-title').textContent;
        addToProgressLog(`<span class="log-completed">Completed</span> ${stepTitle} ${message ? '- ' + message : ''}`);
    }
    
    // Update the activity counter with current step
    updateActivityCounter(status, stepId);
}

/**
 * Update the activity counter with current task information
 * @param {string} status - The status of the current step
 * @param {string} stepId - The ID of the current step
 */
function updateActivityCounter(status, stepId) {
    const counter = document.getElementById('progress-activity-counter');
    if (!counter) return;
    
    if (status === 'in-progress') {
        const stepName = stepId.replace(/-/g, ' ').replace(/^\w/, c => c.toUpperCase());
        
    } else if (status === 'completed') {
        const completedSteps = document.querySelectorAll('.progress-detail-item.completed').length;
        const totalSteps = document.querySelectorAll('.progress-detail-item').length;
        counter.textContent = `Completed: ${completedSteps}/${totalSteps} steps`;
    }
}

/**
 * Start updating the activity counter with a dynamic message
 */
function startActivityCounterUpdater() {
    const counter = document.getElementById('progress-activity-counter');
    if (!counter) return;
    
    // Used to track the animation for the ellipsis
    let dots = 0;
    
    // Update the counter every 500ms
    setInterval(() => {
        // Only update the animation if we're still processing
        if (counter.textContent.includes('Processing')) {
            // Handle potential missing colon with a safe default
            const text = counter.textContent || '';
            const parts = text.includes(':') ? text.split(':') : ['Processing', ''];
            
            // Safely get the base text and step text
            const baseText = parts[0] + ':';
            const stepText = parts.length > 1 ? parts[1].trim() : '';
            
            dots = (dots + 1) % 4;
            const ellipsis = '.'.repeat(dots);
            
            counter.textContent = `${baseText}${stepText}${ellipsis}`;
        }
    }, 500);
}

/**
 * Add a message to the progress log
 * @param {string} message - The message to add to the log
 */
function addToProgressLog(message) {
    const logElement = document.getElementById('progress-log');
    if (!logElement) return;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const logEntry = document.createElement('div');
    logEntry.className = 'log-entry';
    logEntry.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
    
    // Add to log and scroll to bottom
    logElement.appendChild(logEntry);
    logElement.scrollTop = logElement.scrollHeight;
}

/**
 * Update a specific sub-task indicator
 * @param {string} stepId - The ID of the parent step
 * @param {string} subTaskId - The ID of the sub-task
 * @param {boolean} active - Whether the sub-task is active
 * @param {string} message - Optional message to display in the log
 */
function updateSubTaskProgress(stepId, subTaskId, active, message) {
    const stepElement = document.getElementById(`progress-step-${stepId}`);
    if (!stepElement) return;
    
    const subTaskIndicator = stepElement.querySelector(`.sub-task-indicator[data-task="${subTaskId}"]`);
    if (subTaskIndicator) {
        if (active) {
            subTaskIndicator.classList.add('active');
            if (message) {
                const taskName = subTaskId.replace(/-/g, ' ');
                addToProgressLog(`→ Processing ${taskName}: ${message}`);
            }
        } else {
            subTaskIndicator.classList.remove('active');
        }
    }
}

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

/**
 * Initialize the processing indicator functionality
 */
function initProcessingIndicator() {
    const processingIndicator = document.getElementById('processing-indicator');
    const processingStatus = document.getElementById('processing-status');
    
    if (!processingIndicator || !processingStatus) return;
    
    // Hide initially
    processingIndicator.style.display = 'none';
    
    // Set up event listener for the file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                showProcessingIndicator('Preparing your audio file...');
                
                // Set a timeout to start showing more informative messages
                setTimeout(() => {
                    updateProcessingStatus('Reading file metadata...');
                }, 1500);
                
                setTimeout(() => {
                    updateProcessingStatus('Loading audio data...');
                }, 3000);
                
                setTimeout(() => {
                    updateProcessingStatus('Analyzing frequency content...');
                }, 5000);
            }
        });
    }
    
    // Add drag and drop event listeners
    const uploadArea = document.getElementById('upload-area');
    if (uploadArea) {
        uploadArea.addEventListener('drop', function(e) {
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                showProcessingIndicator('Preparing your audio file...');
            }
        });
    }
}

/**
 * Show the processing indicator with a specific message
 * @param {string} message - The message to display
 */
function showProcessingIndicator(message) {
    const processingIndicator = document.getElementById('processing-indicator');
    const processingStatus = document.getElementById('processing-status');
    const progressContainer = document.getElementById('progress-container');
    const uploadArea = document.getElementById('upload-area');
    
    if (processingIndicator && processingStatus) {
        // Hide upload area, show processing indicator
        if (uploadArea) uploadArea.style.display = 'none';
        processingIndicator.style.display = 'flex';
        processingStatus.textContent = message || 'Processing...';
        
        // Show ad banners
        showAdBanners();
        
        // Start animation for text
        startProcessingAnimation();
    }
}

/**
 * Hide the processing indicator
 */
function hideProcessingIndicator() {
    const processingIndicator = document.getElementById('processing-indicator');
    if (processingIndicator) {
        processingIndicator.style.display = 'none';
    }
}

/**
 * Update the processing status message
 * @param {string} message - The new status message
 */
function updateProcessingStatus(message) {
    const processingStatus = document.getElementById('processing-status');
    if (processingStatus) {
        processingStatus.textContent = message;
    }
}

/**
 * Start the text animation for the processing indicator
 */
function startProcessingAnimation() {
    const processingStatus = document.getElementById('processing-status');
    if (!processingStatus) return;
    
    let baseText = processingStatus.textContent || 'Processing';
    let dots = 0;
    
    // Clear any existing interval
    if (window.processingAnimationInterval) {
        clearInterval(window.processingAnimationInterval);
    }
    
    // Set new animation interval
    window.processingAnimationInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        const ellipsis = '.'.repeat(dots);
        
        // Extract the base text without ellipsis
        if (baseText.endsWith('...')) {
            baseText = baseText.substring(0, baseText.length - 3);
        } else if (baseText.endsWith('..')) {
            baseText = baseText.substring(0, baseText.length - 2);
        } else if (baseText.endsWith('.')) {
            baseText = baseText.substring(0, baseText.length - 1);
        }
        
        processingStatus.textContent = baseText + ellipsis;
    }, 500);
}

/**
 * Stop the text animation for the processing indicator
 */
function stopProcessingAnimation() {
    if (window.processingAnimationInterval) {
        clearInterval(window.processingAnimationInterval);
        window.processingAnimationInterval = null;
    }
}

/**
 * Process stage changes from the main application and update UI
 * @param {string} stage - The current processing stage
 * @param {number} percentage - The overall percentage complete
 */
function handleProgressStageChange(stage, percentage) {
    console.log('[Progress] Stage change detected', {
        stage: stage,
        percentage: percentage,
        timestamp: Date.now(),
        timestampFormatted: new Date().toISOString()
    });
    
    // Update the processing indicator based on stage
    if (stage === 'Uploading') {
        updateProcessingStatus('Uploading your audio file...');
    } else if (stage === 'Analyzing') {
        if (percentage < 25) {
            updateProcessingStatus('Analyzing frequency content...');
        } else if (percentage < 50) {
            updateProcessingStatus('Analyzing dynamics and stereo field...');
        } else if (percentage < 75) {
            updateProcessingStatus('Analyzing spatial characteristics...');
        } else {
            updateProcessingStatus('Generating visualizations...');
        }
    } else if (stage === 'Visualizing') {
        updateProcessingStatus('Creating audio visualizations...');
    } else if (stage === 'AI Analysis') {
        updateProcessingStatus('Running AI analysis on your audio...');
    } else if (stage === 'Complete') {
        // Hide processing indicator when analysis is complete
        hideProcessingIndicator();
        stopProcessingAnimation();
    }
    
    // Show the progress container once we start actual analysis
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer && stage !== 'Uploading' && stage !== 'Preparing') {
        progressContainer.style.display = 'block';
        // Hide the processing indicator when the detailed progress is shown
        hideProcessingIndicator();
        stopProcessingAnimation();
    }
    
    // Handle detailed progress updates
    handleDetailedProgressStageChange(stage, percentage);
    
    // Show/hide ad banners
    if (stage === 'Uploading' || stage === 'Analyzing' || stage === 'Visualizing') {
        console.log('[Progress] Stage requires showing ads', {
            stage: stage,
            percentage: percentage,
            action: 'show_ads'
        });
        showAdBanners();
    } else if (stage === 'Complete') {
        console.log('[Progress] Stage requires hiding ads', {
            stage: stage,
            percentage: percentage,
            action: 'hide_ads'
        });
        hideAdBanners();
        document.dispatchEvent(new CustomEvent('analysisComplete'));
    }
}

// Previous function renamed to handle detailed progress updates separately
function handleDetailedProgressStageChange(stage, percentage) {
    // Map the main stages to our detailed steps
    switch(stage.toLowerCase()) {
        case 'uploading':
            updateDetailedProgress('file-upload', 'in-progress', true);
            if (percentage >= 90) {
                updateDetailedProgress('file-upload', 'completed', 'File uploaded successfully');
                updateDetailedProgress('loading-audio', 'in-progress', true);
                addToProgressLog('File upload complete, preparing for analysis...');
            }
            break;
            
        case 'analyzing':
            // Mark initial steps as completed
            updateDetailedProgress('file-upload', 'completed');
            updateDetailedProgress('loading-audio', 'completed', 'Audio decoded successfully');
            
            // Step through analysis stages based on percentage
            if (percentage < 30) {
                // Frequency analysis (25-30%)
                updateDetailedProgress('frequency-analysis', 'in-progress', true);
                if (percentage >= 26 && percentage < 28) {
                    updateSubTaskProgress('frequency-analysis', 'computing-stft', true, 'Converting to dB scale');
                } else if (percentage >= 28) {
                    updateSubTaskProgress('frequency-analysis', 'computing-stft', false);
                    updateSubTaskProgress('frequency-analysis', 'band-energy', true, 'Analyzing frequency bands');
                }
            } else if (percentage < 35) {
                // Complete frequency analysis
                updateDetailedProgress('frequency-analysis', 'completed', 'Balance score calculated');
                updateDetailedProgress('dynamics-analysis', 'in-progress', true);
            } else if (percentage < 40) {
                // Complete dynamics analysis
                updateDetailedProgress('dynamics-analysis', 'completed', 'Dynamic range: 18.13 dB');
                updateDetailedProgress('stereo-field', 'in-progress', true);
            } else if (percentage < 45) {
                // Complete stereo field analysis
                updateDetailedProgress('stereo-field', 'completed', 'Correlation: 0.48');
                updateDetailedProgress('clarity-analysis', 'in-progress', true);
            } else if (percentage < 50) {
                // Complete clarity analysis
                updateDetailedProgress('clarity-analysis', 'completed', 'Clarity score calculated');
                updateDetailedProgress('harmonic-analysis', 'in-progress', true);
            } else if (percentage < 55) {
                // Complete harmonic analysis
                updateDetailedProgress('harmonic-analysis', 'completed', 'Key detection complete');
                updateDetailedProgress('transient-analysis', 'in-progress', true);
            } else if (percentage < 60) {
                // Complete transient analysis
                updateDetailedProgress('transient-analysis', 'completed', 'Transients analyzed');
                updateDetailedProgress('spatial-analysis', 'in-progress', true);
            }
            break;
            
        case 'visualizing':
            // Make sure previous steps are completed
            updateDetailedProgress('file-upload', 'completed');
            updateDetailedProgress('loading-audio', 'completed');
            updateDetailedProgress('frequency-analysis', 'completed');
            updateDetailedProgress('dynamics-analysis', 'completed');
            updateDetailedProgress('stereo-field', 'completed');
            updateDetailedProgress('clarity-analysis', 'completed');
            updateDetailedProgress('harmonic-analysis', 'completed');
            updateDetailedProgress('transient-analysis', 'completed');
            updateDetailedProgress('spatial-analysis', 'completed', '3D spatial analysis complete');
            
            updateDetailedProgress('generating-visuals', 'in-progress', true);
            
            if (percentage >= 65 && percentage < 75) {
                addToProgressLog('→ Generating waveform visualization');
            } else if (percentage >= 75 && percentage < 85) {
                addToProgressLog('→ Generating spectrogram visualization');
            } else if (percentage >= 85) {
                addToProgressLog('→ Generating 3D spatial field visualization');
            }
            
            if (percentage >= 90) {
                updateDetailedProgress('generating-visuals', 'completed', 'Visualizations complete');
            }
            break;
            
        case 'ai analysis':
            // Make sure previous steps are completed
            updateDetailedProgress('file-upload', 'completed');
            updateDetailedProgress('loading-audio', 'completed');
            updateDetailedProgress('frequency-analysis', 'completed');
            updateDetailedProgress('dynamics-analysis', 'completed');
            updateDetailedProgress('stereo-field', 'completed');
            updateDetailedProgress('clarity-analysis', 'completed');
            updateDetailedProgress('harmonic-analysis', 'completed');
            updateDetailedProgress('transient-analysis', 'completed');
            updateDetailedProgress('spatial-analysis', 'completed');
            updateDetailedProgress('generating-visuals', 'completed');
            
            updateDetailedProgress('ai-processing', 'in-progress', true);
            
            if (percentage >= 75 && percentage < 85) {
                addToProgressLog('→ Processing frequency data with AI models');
            } else if (percentage >= 85 && percentage < 95) {
                addToProgressLog('→ Generating mix recommendations');
            }
            
            if (percentage >= 95) {
                updateDetailedProgress('ai-processing', 'completed', 'AI analysis complete');
                updateDetailedProgress('finalizing', 'in-progress', true);
            }
            break;
            
        case 'completed':
            // All steps complete
            updateDetailedProgress('file-upload', 'completed');
            updateDetailedProgress('loading-audio', 'completed');
            updateDetailedProgress('frequency-analysis', 'completed');
            updateDetailedProgress('dynamics-analysis', 'completed');
            updateDetailedProgress('stereo-field', 'completed');
            updateDetailedProgress('clarity-analysis', 'completed');
            updateDetailedProgress('harmonic-analysis', 'completed');
            updateDetailedProgress('transient-analysis', 'completed');
            updateDetailedProgress('spatial-analysis', 'completed');
            updateDetailedProgress('generating-visuals', 'completed');
            updateDetailedProgress('ai-processing', 'completed');
            updateDetailedProgress('finalizing', 'completed', 'Analysis complete!');
            
            addToProgressLog('<span class="log-success">==================================================</span>');
            addToProgressLog('<span class="log-success">ANALYSIS COMPLETE</span>');
            addToProgressLog('<span class="log-success">==================================================</span>');
            break;
    }
}

// Export functions to window for access from main.js
window.detailedProgress = {
    handleProgressStageChange,
    updateDetailedProgress,
    updateSubTaskProgress,
    addToProgressLog,
    showProcessingIndicator,
    hideProcessingIndicator,
    updateProcessingStatus
}; 