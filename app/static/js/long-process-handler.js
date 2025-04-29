/**
 * Long Process Handler
 * Handles long-running server processes with polling
 */

// Polling configuration
const POLL_INTERVAL = 5000; // 5 seconds between status checks
const MAX_POLL_ATTEMPTS = 30; // Maximum 30 attempts (2.5 minutes total)

/**
 * Initiates a long-running process and polls for completion
 * @param {string} trackId - The ID or name of the track being processed
 * @param {function} onProgress - Callback for progress updates
 * @param {function} onComplete - Callback when process completes
 * @param {function} onError - Callback when process errors
 */
function initiateAndPollProcess(trackId, onProgress, onComplete, onError) {
    let pollCount = 0;
    let pollTimer = null;

    // Step 1: Initiate the analysis process
    fetch('/api/analyze/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ track_id: trackId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'processing' || data.status === 'started') {
            // Step 2: Start polling for status updates
            pollTimer = setInterval(() => pollForStatus(trackId), POLL_INTERVAL);
            onProgress({ stage: 'Analysis started', percentage: 5 });
        } else if (data.status === 'completed') {
            // Already completed
            onComplete(data);
        } else {
            // Error starting process
            onError(data.message || 'Failed to start analysis process');
        }
    })
    .catch(error => {
        console.error('Error initiating process:', error);
        onError('Failed to initiate analysis. Please try again.');
    });

    /**
     * Polls the server for process status
     */
    function pollForStatus(trackId) {
        pollCount++;
        
        // Update progress based on poll count
        const progressPercentage = Math.min(5 + (pollCount * 3), 95);
        onProgress({ 
            stage: 'Analysis in progress', 
            percentage: progressPercentage,
            message: `Analysis and visualization generation in progress (${pollCount}/${MAX_POLL_ATTEMPTS})`
        });
        
        // Check if we've exceeded the maximum polling attempts
        if (pollCount >= MAX_POLL_ATTEMPTS) {
            clearInterval(pollTimer);
            onProgress({ 
                stage: 'Taking longer than expected', 
                percentage: 97,
                message: 'Your analysis is taking longer than expected, but still processing. Check back in a few minutes.'
            });
            // Don't call onError, just stop polling but let the process continue in the background
            return;
        }

        // Poll the server for status
        fetch(`/api/analyze/status?track_id=${encodeURIComponent(trackId)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'completed') {
                    // Process completed successfully
                    clearInterval(pollTimer);
                    onComplete(data);
                } else if (data.status === 'error') {
                    // Process encountered an error
                    clearInterval(pollTimer);
                    onError(data.message || 'An error occurred during analysis');
                } else if (data.status === 'processing') {
                    // Still processing, update progress if provided
                    if (data.progress) {
                        onProgress({
                            stage: data.stage || 'Processing',
                            percentage: data.progress,
                            message: data.message || 'Analysis in progress...'
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error polling for status:', error);
                // Don't stop polling on network errors, try again next interval
            });
    }
}

// Export the function for use in main.js
window.initiateAndPollProcess = initiateAndPollProcess; 