// Initialize Matomo
if (typeof MATOMO_URL !== 'undefined' && typeof MATOMO_SITE_ID !== 'undefined' && MATOMO_URL && MATOMO_SITE_ID) {
    console.log(`Initializing Matomo with URL: ${MATOMO_URL} and site ID: ${MATOMO_SITE_ID}`);
    var _paq = window._paq = window._paq || [];
    _paq.push(['trackPageView']);
    _paq.push(['enableLinkTracking']);
    
    (function() {
        var u = MATOMO_URL;
        // Ensure URL ends with a trailing slash
        if (u && !u.endsWith('/')) {
            u += '/';
        }
        _paq.push(['setTrackerUrl', u+'matomo.php']);
        _paq.push(['setSiteId', MATOMO_SITE_ID]);
        var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
        g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
    })();
    
    // Initialize ad visibility tracking once DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof setupAdVisibilityTracking === 'function') {
            // Ad visibility tracking will be initialized by progress-feedback.js
            console.log('Ad visibility tracking will be initialized by progress-feedback.js');
        }
    });
} else {
    console.log('Matomo analytics disabled or not configured');
}

// Custom tracking functions
function trackUpload(fileName, fileSize, fileType) {
  _paq.push(['trackEvent', 'Upload', 'Track Upload', `${fileName} (${fileType})`, fileSize]);
}

function trackTabChange(fromTab, toTab) {
  _paq.push(['trackEvent', 'Navigation', 'Tab Change', `${fromTab} to ${toTab}`]);
}

function trackPlayback(trackName, action) {
  _paq.push(['trackEvent', 'Playback', action, trackName]);
}

function trackDownload(trackName) {
  _paq.push(['trackEvent', 'Download', 'Track Download', trackName]);
}

// Mix Analyzer specific tracking functions
function trackAnalysisStart(fileName) {
  _paq.push(['trackEvent', 'Analysis', 'Start Analysis', fileName]);
}

function trackAnalysisComplete(fileName, duration) {
  _paq.push(['trackEvent', 'Analysis', 'Complete Analysis', fileName, duration]);
}

function trackScore(category, score) {
  _paq.push(['trackEvent', 'Scores', category, 'Score Value', score]);
}

function trackVisualization(type, trackName) {
  _paq.push(['trackEvent', 'Visualization', type, trackName]);
}

function trackAIInsight(insightType) {
  _paq.push(['trackEvent', 'AI Insights', 'View', insightType]);
}

/**
 * Ad Visibility Tracking System
 * 
 * This module tracks how long users see ad elements on the page:
 * - left-ad-banner
 * - right-ad-banner
 * - mobile-ad-banner
 * 
 * The system:
 * 1. Initializes trackers for each ad element
 * 2. Uses MutationObserver to detect when ads become visible/hidden
 * 3. Calculates visibility duration in seconds
 * 4. Reports metrics to Matomo analytics via trackEvent
 * 5. Handles page unload to ensure all visibility periods are recorded
 * 
 * Events are recorded as: 
 * Category: 'Ads'
 * Action: 'Visibility Duration'
 * Name: [element-id]
 * Value: [duration in seconds]
 */

// Ad visibility tracking
var adVisibilityTrackers = {
    'left-ad-banner': { 
        startTime: null, 
        totalDuration: 0, 
        processing: false, 
        intervalId: null, 
        inViewport: false,
        viewportStartTime: null,
        viewportTotalDuration: 0
    },
    'right-ad-banner': { 
        startTime: null, 
        totalDuration: 0, 
        processing: false, 
        intervalId: null, 
        inViewport: false,
        viewportStartTime: null,
        viewportTotalDuration: 0
    },
    'mobile-ad-banner': { 
        startTime: null, 
        totalDuration: 0, 
        processing: false, 
        intervalId: null, 
        inViewport: false,
        viewportStartTime: null,
        viewportTotalDuration: 0
    }
};

// Flag to prevent duplicate initialization
var adTrackingInitialized = false;

// Debug mode flag - set to true to see detailed logs
var adTrackingDebugMode = false;

// Intersection Observer to detect if ads are actually in viewport
var adIntersectionObservers = {};

// Debounce function to prevent rapid-fire calls
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

/**
 * Toggle debug mode for ad visibility tracking
 * @param {boolean} enable - Whether to enable or disable debug mode
 */
window.toggleAdTrackingDebug = function(enable) {
    adTrackingDebugMode = enable === undefined ? !adTrackingDebugMode : !!enable;
    console.log(`[Ad Tracking] Debug mode ${adTrackingDebugMode ? 'enabled' : 'disabled'}`);
    return adTrackingDebugMode;
};

/**
 * Conditional logging function that only logs in debug mode
 * @param {string} message - The message to log
 * @param {object} data - Optional data to log
 */
function debugLog(message, data) {
    if (adTrackingDebugMode && console && console.log) {
        if (data !== undefined) {
            console.log(message, data);
        } else {
            console.log(message);
        }
    }
}

/**
 * Format seconds into a readable time string (MM:SS)
 * @param {number} seconds - Total seconds to format
 * @return {string} Formatted time string
 */
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Start a visibility timer for a specific ad banner
 * @param {string} adId - The ID of the ad banner element
 */
function startVisibilityTimer(adId) {
    if (adVisibilityTrackers[adId].intervalId) {
        clearInterval(adVisibilityTrackers[adId].intervalId);
    }
    
    // Only create timer interval if in debug mode
    if (adTrackingDebugMode) {
        adVisibilityTrackers[adId].intervalId = setInterval(() => {
            if (adVisibilityTrackers[adId].startTime) {
                const currentTime = Date.now();
                const elapsedSeconds = Math.round((currentTime - adVisibilityTrackers[adId].startTime) / 1000);
                const totalDuration = adVisibilityTrackers[adId].totalDuration + elapsedSeconds;
                const viewportStatus = adVisibilityTrackers[adId].inViewport ? 'in viewport ✓' : 'out of viewport ✗';
                
                console.log(`[Ad Timer] ${adId} visible for ${formatTime(elapsedSeconds)} (total: ${formatTime(totalDuration)}) - ${viewportStatus}`);
            }
        }, 1000); // Update every second
    }
}

/**
 * Stop the visibility timer for a specific ad banner
 * @param {string} adId - The ID of the ad banner element
 */
function stopVisibilityTimer(adId) {
    if (adVisibilityTrackers[adId].intervalId) {
        clearInterval(adVisibilityTrackers[adId].intervalId);
        adVisibilityTrackers[adId].intervalId = null;
    }
}

/**
 * Check if an ad banner should be considered visible
 * @param {string} adId - The ID of the ad banner element 
 * @returns {boolean} True if the ad should be considered visible
 */
function isAdActuallyVisible(adId) {
    const element = document.getElementById(adId);
    
    if (!element) return false;
    
    // Ad must have visible class
    const hasVisibleClass = element.classList.contains('visible');
    
    // Ad must be in viewport
    const isInViewport = adVisibilityTrackers[adId].inViewport;
    
    // Ad container must have positive dimensions (not hidden by CSS)
    const rect = element.getBoundingClientRect();
    const hasSize = rect.width > 0 && rect.height > 0;
    
    // Ad must not be covered by another element that could block view
    const isNotCovered = !isElementCovered(element);
    
    // Page must be visible (not in another tab)
    const isPageVisible = !document.hidden;
    
    const visibilityDetails = {
        adId,
        hasVisibleClass,
        isInViewport,
        hasSize,
        isNotCovered,
        isPageVisible,
        isFullyVisible: hasVisibleClass && isInViewport && hasSize && isNotCovered && isPageVisible
    };
    
    // Log change in tracking status if there is one
    if (!!adVisibilityTrackers[adId].startTime !== visibilityDetails.isFullyVisible) {
        debugLog(`[Ad Tracking] ${adId} visibility details:`, visibilityDetails);
    }
    
    return visibilityDetails.isFullyVisible;
}

/**
 * Check if an element is covered by another element
 * @param {HTMLElement} element - The element to check
 * @returns {boolean} True if the element is covered
 */
function isElementCovered(element) {
    // Simple implementation - could be enhanced for more precise detection
    // For now, we'll just consider the element not covered
    return false;
}

/**
 * Start tracking in-viewport visibility for a specific ad banner
 * @param {string} adId - The ID of the ad banner element
 */
function startViewportTracking(adId) {
    if (adVisibilityTrackers[adId].viewportStartTime === null) {
        const startTime = Date.now();
        adVisibilityTrackers[adId].viewportStartTime = startTime;
        debugLog(`[Ad Tracking] Starting viewport tracking for: ${adId}`, {
            adId: adId,
            viewportStartTime: startTime,
            viewportStartTimeFormatted: new Date(startTime).toISOString(),
            currentViewportDuration: adVisibilityTrackers[adId].viewportTotalDuration
        });
    }
}

/**
 * End tracking in-viewport visibility for a specific ad banner
 * @param {string} adId - The ID of the ad banner element
 */
function endViewportTracking(adId) {
    if (adVisibilityTrackers[adId].viewportStartTime !== null) {
        const endTime = Date.now();
        const startTime = adVisibilityTrackers[adId].viewportStartTime;
        const duration = Math.round((endTime - startTime) / 1000);
        
        // Only count durations that are meaningful (at least 1 second)
        if (duration > 0) {
            adVisibilityTrackers[adId].viewportTotalDuration += duration;
            
            debugLog(`[Ad Tracking] Viewport visibility ended for ${adId}`, {
                adId: adId,
                viewportStartTime: startTime,
                viewportStartTimeFormatted: new Date(startTime).toISOString(),
                viewportEndTime: endTime,
                viewportEndTimeFormatted: new Date(endTime).toISOString(),
                viewportDuration: formatTime(duration),
                viewportTotalDuration: formatTime(adVisibilityTrackers[adId].viewportTotalDuration),
                matomoEventParams: ['Ads', 'Viewport Duration', adId, duration]
            });
            
            // Track viewport visibility in Matomo
            if (window._paq) {
                _paq.push(['trackEvent', 'Ads', 'Viewport Duration', adId, duration]);
                debugLog(`[Matomo] Tracked viewport event: ${'Ads'}, ${'Viewport Duration'}, ${adId}, ${duration}`);
            }
        }
        
        adVisibilityTrackers[adId].viewportStartTime = null;
    }
}

/**
 * Update viewport status when it changes
 * @param {string} adId - The ad banner ID
 * @param {boolean} isInViewport - Whether the ad is now in the viewport
 */
function updateViewportStatus(adId, isInViewport) {
    adVisibilityTrackers[adId].inViewport = isInViewport;
    
    // If it's in viewport and we have an active tracking session, start viewport tracking
    if (isInViewport && adVisibilityTrackers[adId].startTime !== null) {
        startViewportTracking(adId);
    } 
    // If it's no longer in viewport, end viewport tracking
    else if (!isInViewport && adVisibilityTrackers[adId].viewportStartTime !== null) {
        endViewportTracking(adId);
    }
}

/**
 * Start tracking visibility for a specific ad banner
 * @param {string} adId - The ID of the ad banner element
 */
window.trackAdVisibilityStart = function(adId) {
    if (adVisibilityTrackers[adId] && !adVisibilityTrackers[adId].processing) {
        adVisibilityTrackers[adId].processing = true;
        
        const isVisible = isAdActuallyVisible(adId);
        const alreadyTracking = adVisibilityTrackers[adId].startTime !== null;
        
        // Only start tracking if element is actually visible
        if (isVisible) {
            // If we're already tracking, we don't need to restart the timer, 
            // but we should log that we received another visibility request
            if (alreadyTracking) {
                debugLog(`[Ad Tracking] Received visibility request for ${adId} (already tracking)`, {
                    adId: adId,
                    currentStartTime: adVisibilityTrackers[adId].startTime,
                    currentStartTimeFormatted: new Date(adVisibilityTrackers[adId].startTime).toISOString(),
                    currentDuration: Math.round((Date.now() - adVisibilityTrackers[adId].startTime) / 1000),
                    totalDuration: adVisibilityTrackers[adId].totalDuration,
                    inViewport: adVisibilityTrackers[adId].inViewport
                });
            } else {
                // Start a new tracking session
                const startTime = Date.now();
                adVisibilityTrackers[adId].startTime = startTime;
                debugLog(`[Ad Tracking] Starting visibility tracking for: ${adId}`, {
                    adId: adId,
                    startTime: startTime,
                    startTimeFormatted: new Date(startTime).toISOString(),
                    currentTotalDuration: adVisibilityTrackers[adId].totalDuration,
                    inViewport: adVisibilityTrackers[adId].inViewport
                });
                
                // Start the real-time timer for this ad
                startVisibilityTimer(adId);
                
                // If it's already in viewport, start viewport tracking as well
                if (adVisibilityTrackers[adId].inViewport) {
                    startViewportTracking(adId);
                }
            }
        } else if (!isVisible && alreadyTracking) {
            // If we're tracking but the ad is no longer visible, stop tracking
            window.trackAdVisibilityEnd(adId);
        }
        
        adVisibilityTrackers[adId].processing = false;
    }
};

/**
 * End tracking visibility for a specific ad banner and record the duration
 * @param {string} adId - The ID of the ad banner element
 */
window.trackAdVisibilityEnd = function(adId) {
    if (adVisibilityTrackers[adId] && !adVisibilityTrackers[adId].processing) {
        adVisibilityTrackers[adId].processing = true;
        
        // End viewport tracking if it's active
        if (adVisibilityTrackers[adId].viewportStartTime !== null) {
            endViewportTracking(adId);
        }
        
        if (adVisibilityTrackers[adId].startTime) {
            // Stop the real-time timer
            stopVisibilityTimer(adId);
            
            const endTime = Date.now();
            const startTime = adVisibilityTrackers[adId].startTime;
            const duration = Math.round((endTime - startTime) / 1000);
            adVisibilityTrackers[adId].totalDuration += duration;
            adVisibilityTrackers[adId].startTime = null;
            
            debugLog(`[Ad Tracking] Visibility ended for ${adId}`, {
                adId: adId,
                startTime: startTime,
                startTimeFormatted: new Date(startTime).toISOString(),
                endTime: endTime,
                endTimeFormatted: new Date(endTime).toISOString(),
                duration: formatTime(duration),
                totalDuration: formatTime(adVisibilityTrackers[adId].totalDuration),
                viewportDuration: formatTime(adVisibilityTrackers[adId].viewportTotalDuration),
                matomoEventParams: ['Ads', 'Visibility Duration', adId, duration]
            });
            
            // Track the event in Matomo
            if (window._paq) {
                _paq.push(['trackEvent', 'Ads', 'Visibility Duration', adId, duration]);
                debugLog(`[Matomo] Tracked event: ${'Ads'}, ${'Visibility Duration'}, ${adId}, ${duration}`);
            }
        }
        
        adVisibilityTrackers[adId].processing = false;
    }
};

/**
 * Re-evaluate visibility of an ad based on its current state
 * @param {string} adId - The ID of the ad banner element
 */
function reevaluateAdVisibility(adId) {
    const isVisible = isAdActuallyVisible(adId);
    const isCurrentlyTracking = adVisibilityTrackers[adId].startTime !== null;
    
    if (isVisible && !isCurrentlyTracking) {
        window.trackAdVisibilityStart(adId);
    } else if (!isVisible && isCurrentlyTracking) {
        window.trackAdVisibilityEnd(adId);
    }
}

/**
 * Set up tracking for ad banner visibility changes
 */
window.setupAdVisibilityTracking = function() {
    // Prevent multiple initializations
    if (adTrackingInitialized) {
        debugLog('[Ad Tracking] Tracking already initialized, skipping');
        return;
    }
    
    const adElements = [
        document.getElementById('left-ad-banner'),
        document.getElementById('right-ad-banner'),
        document.getElementById('mobile-ad-banner')
    ].filter(el => el !== null);
    
    if (adElements.length === 0) {
        debugLog('[Ad Tracking] No ad elements found, skipping tracking setup');
        return;
    }
    
    debugLog('[Ad Tracking] Setting up ad visibility tracking', {
        foundElements: adElements.length,
        adIds: adElements.map(el => el.id),
        initialStates: adElements.map(el => ({
            id: el.id,
            isVisible: el.classList.contains('visible')
        }))
    });
    
    // Set up Intersection Observer to detect if ads are in viewport
    const intersectionOptions = {
        root: null, // Use viewport as root
        rootMargin: '0px', // No margin
        threshold: 0.5 // 50% visibility required
    };
    
    const intersectionCallback = (entries) => {
        entries.forEach(entry => {
            const adId = entry.target.id;
            const wasInViewport = adVisibilityTrackers[adId].inViewport;
            const isNowInViewport = entry.isIntersecting;
            
            // Only update and log if the viewport status changed
            if (wasInViewport !== isNowInViewport) {
                debugLog(`[Ad Tracking] ${adId} viewport visibility changed:`, {
                    adId: adId,
                    isInViewport: isNowInViewport,
                    intersectionRatio: entry.intersectionRatio.toFixed(2),
                    timestamp: Date.now(),
                    timestampFormatted: new Date().toISOString()
                });
                
                // Update viewport tracking status
                updateViewportStatus(adId, isNowInViewport);
                
                // Re-evaluate visibility status when viewport status changes
                reevaluateAdVisibility(adId);
            }
        });
    };
    
    const observer = new IntersectionObserver(intersectionCallback, intersectionOptions);
    
    // Set up mutation observers to track when ads become visible or hidden
    const mutationConfig = { attributes: true, attributeFilter: ['class'] };
    
    adElements.forEach(adElement => {
        const adId = adElement.id;
        
        // Set up intersection observer for this ad
        observer.observe(adElement);
        
        // Create a debounced handler for class mutations
        const debouncedHandler = debounce((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'attributes') {
                    const classChanged = mutation.attributeName === 'class';
                    if (classChanged) {
                        debugLog(`[Ad Tracking] ${adId} class changed:`, {
                            adId: adId,
                            classList: Array.from(adElement.classList),
                            isVisible: adElement.classList.contains('visible'),
                            timestamp: Date.now(),
                            timestampFormatted: new Date().toISOString()
                        });
                        
                        // Re-evaluate visibility based on new class state
                        reevaluateAdVisibility(adId);
                    }
                }
            });
        }, 50); // 50ms debounce to avoid rapid-fire events
        
        const mutationObserver = new MutationObserver(debouncedHandler);
        mutationObserver.observe(adElement, mutationConfig);
        debugLog(`[Ad Tracking] Observers attached to ${adElement.id}`);
        
        // Initial check of visibility
        reevaluateAdVisibility(adId);
    });
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        debugLog(`[Ad Tracking] Page visibility changed: ${document.hidden ? 'hidden' : 'visible'}`);
        
        // Re-evaluate all ads when page visibility changes
        Object.keys(adVisibilityTrackers).forEach(adId => {
            reevaluateAdVisibility(adId);
        });
    });
    
    // Handle window resize (which might affect visibility)
    window.addEventListener('resize', debounce(() => {
        debugLog('[Ad Tracking] Window resized, re-evaluating ad visibility');
        
        // Re-evaluate all ads when window size changes
        Object.keys(adVisibilityTrackers).forEach(adId => {
            reevaluateAdVisibility(adId);
        });
    }, 250)); // Debounce resize events
    
    // Track final durations when the page is unloaded
    window.addEventListener('beforeunload', () => {
        displayAdVisibilitySummary();
        
        // Record final durations
        Object.keys(adVisibilityTrackers).forEach(adId => {
            if (adVisibilityTrackers[adId].startTime !== null) {
                window.trackAdVisibilityEnd(adId);
            }
        });
    });
    
    adTrackingInitialized = true;
    console.log('[Ad Tracking] Visibility tracking initialized successfully');
};

/**
 * Display a summary of all ad visibility durations in the console
 */
function displayAdVisibilitySummary() {
    // Calculate current visibility for any active ads
    const summary = {};
    
    Object.keys(adVisibilityTrackers).forEach(adId => {
        let totalSeconds = adVisibilityTrackers[adId].totalDuration;
        let viewportSeconds = adVisibilityTrackers[adId].viewportTotalDuration;
        
        // If currently visible, add the current session time
        if (adVisibilityTrackers[adId].startTime !== null) {
            const currentTime = Date.now();
            const elapsedSeconds = Math.round((currentTime - adVisibilityTrackers[adId].startTime) / 1000);
            totalSeconds += elapsedSeconds;
            
            // If also in viewport, add to viewport time
            if (adVisibilityTrackers[adId].viewportStartTime !== null) {
                const viewportElapsed = Math.round((currentTime - adVisibilityTrackers[adId].viewportStartTime) / 1000);
                viewportSeconds += viewportElapsed;
            }
        }
        
        summary[adId] = {
            totalTime: formatTime(totalSeconds),
            totalSeconds: totalSeconds,
            viewportTime: formatTime(viewportSeconds),
            viewportSeconds: viewportSeconds,
            viewportPercentage: totalSeconds > 0 ? Math.round((viewportSeconds / totalSeconds) * 100) : 0
        };
    });
    
    // Only show the detailed fancy console output if in debug mode
    if (adTrackingDebugMode) {
        // Create a fancy console log dashboard
        console.log('%c Ad Visibility Summary ', 'background: #4361ee; color: white; font-size: 14px; font-weight: bold; padding: 5px;');
        console.log('%c┌─────────────────────┬────────────┬────────────┬─────────┬───────────────┐', 'color: #4361ee');
        console.log('%c│ Ad Banner           │ Total Time │ Viewport   │ VP %    │ Visibility    │', 'color: #4361ee; font-weight: bold');
        console.log('%c├─────────────────────┼────────────┼────────────┼─────────┼───────────────┤', 'color: #4361ee');
        
        // Get the largest total seconds for percentage calculation
        const largestDuration = Math.max(
            ...Object.values(summary).map(item => item.totalSeconds), 
            1  // Prevent division by zero
        );
        
        // Display each ad's statistics
        Object.keys(summary).forEach(adId => {
            const item = summary[adId];
            const percentage = Math.round((item.totalSeconds / largestDuration) * 100);
            const bar = '█'.repeat(Math.floor(percentage / 5)); // 20 chars max
            
            console.log(
                `%c│ %c${adId.padEnd(19)}%c│ %c${item.totalTime.padEnd(10)}%c│ %c${item.viewportTime.padEnd(10)}%c│ %c${item.viewportPercentage.toString().padEnd(7)}%c│ %c${bar.padEnd(15)} %c│`,
                'color: #4361ee',
                'color: #333',
                'color: #4361ee',
                'color: #333',
                'color: #4361ee',
                'color: #38b000; font-weight: bold',
                'color: #4361ee',
                'color: #3a86ff',
                'color: #4361ee',
                `color: ${percentage > 50 ? '#38b000' : '#3a86ff'}`,
                'color: #4361ee'
            );
        });
        
        console.log('%c└─────────────────────┴────────────┴────────────┴─────────┴───────────────┘', 'color: #4361ee');
        console.log('%c Tracking session complete! ', 'background: #4361ee; color: white; font-size: 12px; padding: 3px;');
        
        // Log the raw data for potential debugging
        console.log('[Ad Tracking] Final visibility data:', {
            trackers: JSON.parse(JSON.stringify(adVisibilityTrackers)),
            summary: summary
        });
    } else {
        // Just print a simple summary when not in debug mode
        const totalViewTime = Object.values(summary).reduce((sum, item) => sum + item.totalSeconds, 0);
        const totalViewportTime = Object.values(summary).reduce((sum, item) => sum + item.viewportSeconds, 0);
        
        if (totalViewTime > 0) {
            console.log(`[Ad Tracking] Ad view summary: ${formatTime(totalViewTime)} total time (${formatTime(totalViewportTime)} in viewport)`);
            for (const [adId, data] of Object.entries(summary)) {
                if (data.totalSeconds > 0) {
                    console.log(`  - ${adId}: ${data.totalTime} total, ${data.viewportTime} in viewport (${data.viewportPercentage}%)`);
                }
            }
        }
    }
    
    // Send final viewport statistics to Matomo
    Object.keys(summary).forEach(adId => {
        const data = summary[adId];
        if (data.viewportSeconds > 0 && window._paq) {
            _paq.push(['trackEvent', 'Ads', 'Total Viewport Duration', adId, data.viewportSeconds]);
            debugLog(`[Matomo] Tracked total viewport event: ${'Ads'}, ${'Total Viewport Duration'}, ${adId}, ${data.viewportSeconds}`);
        }
    });
    
    return summary;
}

/**
 * Generate a report suitable for potential ad buyers
 * Shows detailed metrics about ad visibility
 */
window.generateAdBuyerReport = function() {
    const summary = displayAdVisibilitySummary();
    
    // Create a more detailed report specifically for ad buyers
    console.log('%c Ad Performance Report for Potential Buyers ', 'background: #38b000; color: white; font-size: 16px; font-weight: bold; padding: 8px;');
    
    // Calculate total session time
    const sessionStart = performance.timing ? performance.timing.navigationStart : Date.now();
    const sessionDuration = Math.round((Date.now() - sessionStart) / 1000);
    const formattedSessionTime = formatTime(sessionDuration);
    
    // Calculate overall visibility metrics
    const totalVisibleTime = Object.values(summary).reduce((sum, item) => sum + item.totalSeconds, 0);
    const totalViewportTime = Object.values(summary).reduce((sum, item) => sum + item.viewportSeconds, 0);
    const overallViewportPercentage = totalVisibleTime > 0 ? Math.round((totalViewportTime / totalVisibleTime) * 100) : 0;
    
    // Print session overview
    console.log('%c Session Overview ', 'background: #3a86ff; color: white; font-weight: bold; padding: 4px;');
    console.log(`Total session duration: ${formattedSessionTime}`);
    console.log(`Total ad visible time: ${formatTime(totalVisibleTime)} (${Math.round((totalVisibleTime / sessionDuration) * 100)}% of session)`);
    console.log(`Total viewport time: ${formatTime(totalViewportTime)} (${Math.round((totalViewportTime / sessionDuration) * 100)}% of session)`);
    console.log(`Overall viewport efficiency: ${overallViewportPercentage}%`);
    
    // Banner specific metrics
    console.log('%c Individual Banner Performance ', 'background: #3a86ff; color: white; font-weight: bold; padding: 4px;');
    
    Object.keys(summary).forEach(adId => {
        const data = summary[adId];
        if (data.totalSeconds > 0) {
            console.log(`%c${adId}`, 'font-weight: bold; color: #333; font-size: 14px;');
            console.log(`  • Total visible time: ${data.totalTime} (${Math.round((data.totalSeconds / sessionDuration) * 100)}% of session)`);
            console.log(`  • Time in viewport: ${data.viewportTime} (${data.viewportPercentage}% visibility efficiency)`);
            console.log(`  • Session coverage: ${Math.round((data.totalSeconds / sessionDuration) * 100)}% of user's time`);
            
            // Calculate viewability metrics (IAB standard is 50% of ad visible for 2+ seconds)
            const meetsIABStandard = data.viewportSeconds >= 2;
            console.log(`  • IAB viewability standard met: ${meetsIABStandard ? '✓ Yes' : '✗ No'}`);
            
            // Provide insights and recommendations
            if (data.viewportPercentage < 40) {
                console.log(`  • %cInsight: Low viewport efficiency. Consider repositioning this ad.`, 'color: #e63946;');
            } else if (data.viewportPercentage > 75) {
                console.log(`  • %cInsight: Excellent viewport visibility!`, 'color: #38b000;');
            }
            
            console.log(''); // Add space between banners
        }
    });
    
    // Print technical notes
    console.log('%c Technical Notes ', 'background: #3a86ff; color: white; font-weight: bold; padding: 4px;');
    console.log('• Total visible time: Duration the ad had the "visible" CSS class');
    console.log('• Time in viewport: Duration the ad was actually visible on screen');
    console.log('• Visibility efficiency: Percentage of visible time the ad was in the viewport');
    console.log('• IAB standard: Interactive Advertising Bureau standard for ad viewability');
    
    console.log('%c Report generated at: ' + new Date().toLocaleString(), 'font-style: italic; color: #333;');
    
    return summary;
};

// Add event listeners once DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Ad visibility tracking is initialized by progress-feedback.js
  // No need to call setupAdVisibilityTracking() here

  // Make the summary and debug functions available globally for manual checking
  window.showAdVisibilitySummary = displayAdVisibilitySummary;
  window.generateAdBuyerReport = window.generateAdBuyerReport || generateAdBuyerReport;
  
  console.log('[Ad Tracking] To view ad visibility summary anytime, run: showAdVisibilitySummary()');
  console.log('[Ad Tracking] To generate a detailed report for ad buyers, run: generateAdBuyerReport()');
  console.log('[Ad Tracking] To enable debug mode, run: toggleAdTrackingDebug(true)');

  // Track tab changes
  const tabElements = document.querySelectorAll('[role="tab"]');
  let currentTab = '';
  
  tabElements.forEach(tab => {
    tab.addEventListener('click', function() {
      const newTab = this.getAttribute('aria-label') || this.textContent;
      if (currentTab !== newTab) {
        trackTabChange(currentTab || 'none', newTab);
        currentTab = newTab;
      }
    });
  });

  // Track file uploads
  const uploadInputs = document.querySelectorAll('input[type="file"]');
  uploadInputs.forEach(input => {
    input.addEventListener('change', function() {
      if (this.files && this.files[0]) {
        const file = this.files[0];
        trackUpload(file.name, file.size, file.type);
        trackAnalysisStart(file.name);
      }
    });
  });

  // Track visualization clicks
  const visualizations = document.querySelectorAll('.visualization-container img');
  visualizations.forEach(viz => {
    viz.addEventListener('click', function() {
      const vizType = this.getAttribute('data-track-name') || 'Unknown';
      trackVisualization('View', vizType);
    });
  });

  // Track scores when they're updated
  const observeScores = () => {
    const scoreElements = {
      'Overall': document.getElementById('overall-score'),
      'Frequency': document.getElementById('frequency-score'),
      'Dynamics': document.getElementById('dynamics-score'),
      'Width': document.getElementById('width-score'),
      'Phase': document.getElementById('phase-score'),
      'Clarity': document.getElementById('clarity-score'),
      'Transients': document.getElementById('transients-score')
    };

    for (const [category, element] of Object.entries(scoreElements)) {
      if (element && element.textContent !== '0') {
        trackScore(category, parseFloat(element.textContent));
      }
    }
  };

  // Track AI Insights view
  const aiTab = document.querySelector('[data-tab="ai-insights"]');
  if (aiTab) {
    aiTab.addEventListener('click', () => {
      trackAIInsight('View AI Analysis');
    });
  }

  // Track downloads
  const downloadLinks = document.querySelectorAll('[data-track-download]');
  downloadLinks.forEach(link => {
    link.addEventListener('click', function() {
      const trackName = this.getAttribute('data-track-download') || this.getAttribute('download') || 'Unknown Track';
      trackDownload(trackName);
    });
  });

  // Observe score changes
  const observer = new MutationObserver(observeScores);
  const scoreElements = document.querySelectorAll('.score-value');
  scoreElements.forEach(element => {
    observer.observe(element, { childList: true, characterData: true, subtree: true });
  });
});