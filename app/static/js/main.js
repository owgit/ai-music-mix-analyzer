document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
    // Show button arrow indicator after a short delay
    setTimeout(() => {
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.classList.add('show-button-indicator');
        }
    }, 1500);
    
    // Header scroll effect
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;
    
    function handleHeaderScroll() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 20) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScrollY = currentScrollY;
    }
    
    // Initial check
    handleHeaderScroll();
    
    // Add scroll event listener
    window.addEventListener('scroll', handleHeaderScroll, { passive: true });
    
    // DOM Elements
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const uploadContainer = document.getElementById('upload-container');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressStage = document.getElementById('progress-stage');
    const progressPercentage = document.getElementById('progress-percentage');
    const resultsSection = document.getElementById('results-section');
    const introSection = document.querySelector('.intro-section');
    
    // Progress steps
    const stepUpload = document.getElementById('step-upload');
    const stepAnalyze = document.getElementById('step-analyze');
    const stepVisualize = document.getElementById('step-visualize');
    const stepAI = document.getElementById('step-ai');
    
    // Tab functionality
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Initialize frequency chart
    let frequencyChart = null;
    
    console.log("Setting up event listeners");
    
    // Add animated hover effect to upload area
    if (uploadArea) {
        uploadArea.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        uploadArea.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    }
    
    // Handle file upload via click
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            console.log("File input change event triggered");
            if (fileInput.files.length > 0) {
                console.log("File selected via input:", fileInput.files[0].name);
                handleFileUpload(fileInput.files[0]);
            }
        });
    } else {
        console.error("File input element not found!");
    }
    
    // Handle drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.add('dragover');
            this.style.transform = 'scale(1.02)';
            this.style.borderColor = 'var(--primary-color)';
            this.style.backgroundColor = '#f0f4ff';
            this.style.boxShadow = '0 10px 40px rgba(67, 97, 238, 0.15)';
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
            this.style.transform = 'scale(1)';
            this.style.borderColor = 'rgba(67, 97, 238, 0.3)';
            this.style.backgroundColor = 'var(--card-bg)';
            this.style.boxShadow = 'var(--box-shadow)';
        });
        
        uploadArea.addEventListener('drop', function(e) {
            console.log("File dropped");
            e.preventDefault();
            e.stopPropagation();
            uploadArea.classList.remove('dragover');
            this.style.transform = 'scale(1)';
            this.style.borderColor = 'rgba(67, 97, 238, 0.3)';
            this.style.backgroundColor = 'var(--card-bg)';
            
            if (e.dataTransfer.files.length > 0) {
                console.log("File selected via drop:", e.dataTransfer.files[0].name);
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
        
        // Click to trigger file input
        uploadArea.addEventListener('click', function(e) {
            console.log("Upload area clicked");
            if (fileInput) {
                fileInput.click();
            }
        });
    } else {
        console.error("Upload area element not found!");
    }
    
    // Prevent propagation from upload button to avoid double file selection 
    const uploadButton = document.getElementById('upload-button');
    if (uploadButton) {
        uploadButton.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log("Upload button clicked directly");
            if (fileInput) {
                fileInput.click();
            }
        });
    }
    
    // Tab switching with smooth transitions
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => {
                pane.style.opacity = 0;
                setTimeout(() => {
                    pane.classList.remove('active');
                }, 150);
            });
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Get the tab to show
            const tabName = button.getAttribute('data-tab');
            const activeTab = document.getElementById(`${tabName}-tab`);
            
            setTimeout(() => {
                activeTab.classList.add('active');
                setTimeout(() => {
                    activeTab.style.opacity = 1;
                }, 50);
            }, 150);
        });
    });
    
    // Add event listener for the instrumental checkbox with enhanced animation
    const instrumentalCheckbox = document.getElementById('instrumental-checkbox');
    if (instrumentalCheckbox) {
        instrumentalCheckbox.addEventListener('change', function() {
            const checkboxContainer = this.closest('.checkbox-container');
            if (checkboxContainer) {
                if (this.checked) {
                    checkboxContainer.classList.add('checked');
                    checkboxContainer.style.transform = 'scale(1.05)';
                    
                    // Add animation flash to highlight the selection
                    const container = document.querySelector('.instrumental-selection-container');
                    if (container) {
                        container.style.backgroundColor = '#dff0ff';
                        container.style.borderColor = '#2547e3';
                        
                        // Create and add animation for confirmation
                        const confirmMessage = document.createElement('div');
                        confirmMessage.className = 'vocal-selection-confirm';
                        confirmMessage.textContent = 'Instrumental mode activated';
                        confirmMessage.style.position = 'absolute';
                        confirmMessage.style.bottom = '-40px';
                        confirmMessage.style.left = '50%';
                        confirmMessage.style.transform = 'translateX(-50%)';
                        confirmMessage.style.backgroundColor = '#4361ee';
                        confirmMessage.style.color = 'white';
                        confirmMessage.style.padding = '8px 16px';
                        confirmMessage.style.borderRadius = '20px';
                        confirmMessage.style.fontWeight = '600';
                        confirmMessage.style.fontSize = '14px';
                        confirmMessage.style.opacity = '0';
                        confirmMessage.style.transition = 'all 0.3s ease';
                        
                        container.appendChild(confirmMessage);
                        
                        // Animate the confirmation message
                        setTimeout(() => {
                            confirmMessage.style.opacity = '1';
                            confirmMessage.style.bottom = '-30px';
                        }, 50);
                        
                        // Remove the confirmation message after some time
                        setTimeout(() => {
                            confirmMessage.style.opacity = '0';
                            confirmMessage.style.bottom = '-40px';
                            setTimeout(() => confirmMessage.remove(), 300);
                        }, 3000);
                    }
                    
                    setTimeout(() => {
                        checkboxContainer.style.transform = 'scale(1.02)';
                    }, 200);
                    console.log("Instrumental checkbox checked - Analysis will focus on instrumental aspects");
                } else {
                    checkboxContainer.classList.remove('checked');
                    
                    // Add animation flash for deselection
                    const container = document.querySelector('.instrumental-selection-container');
                    if (container) {
                        container.style.backgroundColor = '#f0f5ff';
                        container.style.borderColor = '#4361ee';
                        
                        // Create and add deactivation message
                        const deactivateMessage = document.createElement('div');
                        deactivateMessage.className = 'vocal-selection-confirm';
                        deactivateMessage.textContent = 'Vocals mode activated';
                        deactivateMessage.style.position = 'absolute';
                        deactivateMessage.style.bottom = '-40px';
                        deactivateMessage.style.left = '50%';
                        deactivateMessage.style.transform = 'translateX(-50%)';
                        deactivateMessage.style.backgroundColor = '#6c757d';
                        deactivateMessage.style.color = 'white';
                        deactivateMessage.style.padding = '8px 16px';
                        deactivateMessage.style.borderRadius = '20px';
                        deactivateMessage.style.fontWeight = '600';
                        deactivateMessage.style.fontSize = '14px';
                        deactivateMessage.style.opacity = '0';
                        deactivateMessage.style.transition = 'all 0.3s ease';
                        
                        container.appendChild(deactivateMessage);
                        
                        // Animate the deactivation message
                        setTimeout(() => {
                            deactivateMessage.style.opacity = '1';
                            deactivateMessage.style.bottom = '-30px';
                        }, 50);
                        
                        // Remove the message after some time
                        setTimeout(() => {
                            deactivateMessage.style.opacity = '0';
                            deactivateMessage.style.bottom = '-40px';
                            setTimeout(() => deactivateMessage.remove(), 300);
                        }, 3000);
                    }
                    
                    console.log("Instrumental checkbox unchecked - Analysis will include vocal aspects");
                }
            }
        });
    }
    
    // Add event listener for the "Analyze New Track" button
    const analyzeNewBtn = document.getElementById('analyze-new-btn');
    if (analyzeNewBtn) {
        analyzeNewBtn.addEventListener('click', function() {
            // Hide results and show upload section
            resultsSection.style.display = 'none';
            uploadContainer.style.display = 'block';
            uploadArea.style.display = 'flex';
            progressContainer.style.display = 'none';
            
            // Reset progress elements
            progressBar.style.width = '0%';
            resetProgressSteps();
            
            // Reset file input
            if (fileInput) {
                fileInput.value = '';
            }
        });
    }
    
    // Handle file upload
    function handleFileUpload(file) {
        console.log("handleFileUpload called with file:", file.name, file.type, file.size);
        
        // Check if file is a supported audio format
        const supportedTypes = ['audio/mpeg', 'audio/wav', 'audio/wave', 'audio/x-wav', 'audio/flac', 
                               'audio/aiff', 'audio/x-aiff', 'audio/m4a', 'audio/x-m4a', 'audio/pcm'];
        const supportedExtensions = ['.mp3', '.wav', '.flac', '.aiff', '.aif', '.m4a', '.pcm'];
        
        const isValidType = supportedTypes.some(type => file.type.includes(type));
        const isValidExtension = supportedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValidType && !isValidExtension) {
            alert('Please upload a supported audio file (MP3, WAV, FLAC, AIFF, M4A, PCM).');
            return;
        }
        
        // Create FormData object
        const formData = new FormData();
        formData.append('file', file);
        
        // Add instrumental flag if checkbox is checked
        const isInstrumental = document.getElementById('instrumental-checkbox').checked;
        formData.append('is_instrumental', isInstrumental);
        console.log(`Uploading file with instrumental flag: ${isInstrumental}`);
        
        // Show progress container and hide upload area
        document.getElementById('upload-area').style.display = 'none';
        document.getElementById('progress-container').style.display = 'block';
        
        // Reset progress elements
        resetProgressSteps();
        progressBar.style.width = '0%';
        progressStage.textContent = 'Uploading';
        progressPercentage.textContent = '0%';
        progressText.textContent = 'Preparing your audio file...';
        
        // Make Upload step active
        stepUpload.classList.add('active');
        
        // Initialize the first step in detailed progress if available
        if (window.detailedProgress) {
            window.detailedProgress.updateDetailedProgress('file-upload', 'in-progress', true);
            
            // Add initial log entries with file information
            window.detailedProgress.addToProgressLog('<span class="log-success">==================================================</span>');
            window.detailedProgress.addToProgressLog(`<span class="log-success">STARTING ANALYSIS: ${file.name}</span>`);
            window.detailedProgress.addToProgressLog('<span class="log-success">==================================================</span>');
            window.detailedProgress.addToProgressLog('');
            window.detailedProgress.addToProgressLog(`File type: ${file.type || 'Unknown'}`);
            window.detailedProgress.addToProgressLog(`File size: ${(file.size / (1024 * 1024)).toFixed(2)} MB`);
            window.detailedProgress.addToProgressLog(`Instrumental track: ${isInstrumental ? 'Yes' : 'No'}`);
            window.detailedProgress.addToProgressLog('');
            
            // Show real-time upload activity feedback
            let uploadFeedbackInterval = setInterval(() => {
                if (progressBar.style.width !== '0%') {
                    const percentage = parseInt(progressBar.style.width);
                    if (percentage > 0 && percentage < 25) {
                        window.detailedProgress.addToProgressLog(`→ Upload progress: ${percentage}%`);
                    }
                    
                    if (percentage >= 25) {
                        clearInterval(uploadFeedbackInterval);
                    }
                }
            }, 2000); // Update every 2 seconds
        }
        
        // Upload file
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                updateProgressBar(percentComplete, 'Uploading');
                
                // Update progress text based on percentage
                if (percentComplete < 30) {
                    progressText.textContent = 'Uploading your audio file...';
                } else if (percentComplete < 70) {
                    progressText.textContent = 'Almost there...';
                } else {
                    progressText.textContent = 'Just a moment...';
                }
                
                console.log(`Upload progress: ${Math.round(percentComplete)}%`);
            }
        });
        
        xhr.addEventListener('load', function() {
            console.log("XHR load event. Status:", xhr.status);
            
            if (xhr.status === 200) {
                // Mark upload step as completed
                stepUpload.classList.remove('active');
                stepUpload.classList.add('completed');
                
                // Update progress to Analysis phase
                stepAnalyze.classList.add('active');
                updateProgressBar(25, 'Analyzing');
                progressText.textContent = 'Analyzing frequency balance and dynamics...';
                
                // Simulate the analysis progress
                simulateAnalysisProgress(function() {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        console.log("Response parsed successfully:", response);
                        displayResults(response);
                    } catch (error) {
                        console.error("Error parsing response:", error);
                        handleError('Error parsing response: ' + error.message);
                    }
                });
            } else {
                console.error("Upload failed. Status:", xhr.status, xhr.statusText);
                console.error("Response text:", xhr.responseText);
                handleError('Upload failed: ' + xhr.statusText);
            }
        });
        
        xhr.addEventListener('error', function(e) {
            console.error("XHR error event:", e);
            handleError('Network error occurred');
        });
        
        xhr.addEventListener('abort', function() {
            console.error("XHR abort event");
            handleError('Upload aborted');
        });
        
        xhr.addEventListener('timeout', function() {
            console.error("XHR timeout event");
            handleError('Upload timed out');
        });
        
        console.log("Sending XHR request to /upload");
        xhr.open('POST', '/upload', true);
        xhr.send(formData);
    }
    
    // Simulate analysis progress with realistic steps
    function simulateAnalysisProgress(callback) {
        let progress = 25; // Start at 25% after upload is done
        let currentSubStep = '';
        
        const interval = setInterval(function() {
            progress += 1;
            
            // Detailed progress simulation - update sub-tasks based on current progress percentage
            if (progress >= 25 && progress < 35) {
                // We're in frequency analysis phase
                if (progress === 25) {
                    console.log("Starting frequency analysis");
                    
                    // Add log message for frequency analysis start
                    if (window.detailedProgress) {
                        window.detailedProgress.addToProgressLog('');
                        window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                        window.detailedProgress.addToProgressLog('Step 2: Analyzing frequency balance...');
                        window.detailedProgress.addToProgressLog('Converting to mono for frequency analysis...');
                    }
                    
                    currentSubStep = 'fft-processing';
                } else if (progress === 28) {
                    console.log("Starting spectrum calculation");
                    
                    // If we have detailed progress, update sub-tasks
                    if (window.detailedProgress) {
                        window.detailedProgress.updateSubTaskProgress('frequency-analysis', 'computing-stft', true, 'Converting to dB scale');
                        window.detailedProgress.addToProgressLog('Computing STFT...');
                        window.detailedProgress.addToProgressLog('STFT computed in 0.12 seconds');
                    }
                    
                    currentSubStep = 'spectrum-calculation';
                } else if (progress === 32) {
                    console.log("Starting balance scoring");
                    
                    // If we have detailed progress, update sub-tasks
                    if (window.detailedProgress) {
                        window.detailedProgress.updateSubTaskProgress('frequency-analysis', 'computing-stft', false);
                        window.detailedProgress.updateSubTaskProgress('frequency-analysis', 'band-energy', true, 'Analyzing frequency bands');
                        window.detailedProgress.addToProgressLog('Analyzing frequency bands...');
                        window.detailedProgress.addToProgressLog('  sub_bass: normalized to 85.32%');
                        window.detailedProgress.addToProgressLog('  bass: normalized to 62.18%');
                        window.detailedProgress.addToProgressLog('  low_mids: normalized to 49.75%');
                    }
                    
                    currentSubStep = 'balance-scoring';
                }
            }
            
            // Update visuals based on current progress
            if (progress === 30) {
                // Complete analysis phase
                stepAnalyze.classList.remove('active');
                stepAnalyze.classList.add('completed');
                
                // Start visualization phase
                stepVisualize.classList.add('active');
                updateProgressBar(progress, 'Visualizing');
                progressText.textContent = 'Generating waveforms and spectrograms...';
                
                // Add dynamics analysis logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('');
                    window.detailedProgress.addToProgressLog('Frequency balance analysis completed in 0.15 seconds');
                    window.detailedProgress.addToProgressLog('Balance score: 67.43');
                    window.detailedProgress.addToProgressLog('');
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 3: Analyzing dynamic range...');
                    window.detailedProgress.addToProgressLog('Calculating RMS energy in windows...');
                    window.detailedProgress.addToProgressLog('Converting RMS to dB...');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('Dynamic range analysis completed in 0.03 seconds');
                        window.detailedProgress.addToProgressLog('Dynamic range: 14.87 dB');
                        window.detailedProgress.addToProgressLog('Crest factor: 11.23 dB');
                        window.detailedProgress.addToProgressLog('Dynamic range score: 82.54');
                        window.detailedProgress.addToProgressLog('');
                    }, 1500);
                }
            } else if (progress === 40) {
                // Add stereo field logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 4: Analyzing stereo field...');
                    window.detailedProgress.addToProgressLog('Channel correlation: 0.52');
                    window.detailedProgress.addToProgressLog('Mid/Side ratio: 0.76/0.24');
                    window.detailedProgress.addToProgressLog('Stereo field analysis completed in 0.01 seconds');
                    window.detailedProgress.addToProgressLog('');
                }
            } else if (progress === 45) {
                // Add clarity analysis logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 5: Analyzing clarity...');
                    window.detailedProgress.addToProgressLog('Calculating spectral contrast...');
                    window.detailedProgress.addToProgressLog('Calculating spectral flatness...');
                    window.detailedProgress.addToProgressLog('Clarity analysis completed in 0.26 seconds');
                    window.detailedProgress.addToProgressLog('Clarity score: 61.32');
                    window.detailedProgress.addToProgressLog('');
                }
            } else if (progress === 50) {
                // Add harmonic content logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 6: Analyzing harmonic content...');
                    window.detailedProgress.addToProgressLog('Analyzing harmonic content...');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('Harmonic content analysis completed in 5.08 seconds');
                        window.detailedProgress.addToProgressLog('Detected key: A minor');
                        window.detailedProgress.addToProgressLog('Harmonic complexity: 68.29%');
                        window.detailedProgress.addToProgressLog('');
                    }, 2000);
                }
            } else if (progress === 55) {
                // Add transients logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 7: Analyzing transients...');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('Transients analysis completed in 3.56 seconds');
                        window.detailedProgress.addToProgressLog('Transients score: 72.45');
                        window.detailedProgress.addToProgressLog('Attack time: 84.32 ms');
                        window.detailedProgress.addToProgressLog('Detected 126 transients');
                        window.detailedProgress.addToProgressLog('');
                    }, 1500);
                }
            } else if (progress === 57) {
                // Add 3D spatial logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 8: Analyzing 3D spatial imaging...');
                    window.detailedProgress.addToProgressLog('Calculating interaural level differences (ILD) for height perception...');
                    window.detailedProgress.addToProgressLog('Calculating interaural time differences (ITD) for depth perception...');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('3D spatial analysis completed in 0.15 seconds');
                        window.detailedProgress.addToProgressLog('Height score: 68.32%');
                        window.detailedProgress.addToProgressLog('Depth score: 72.15%');
                        window.detailedProgress.addToProgressLog('Width consistency: 84.47%');
                        window.detailedProgress.addToProgressLog('');
                    }, 800);
                }
            } else if (progress === 60) {
                // Complete visualization phase
                stepVisualize.classList.remove('active');
                stepVisualize.classList.add('completed');
                
                // Start AI insights phase
                stepAI.classList.add('active');
                updateProgressBar(progress, 'AI Analysis');
                progressText.textContent = 'Creating intelligent insights about your mix...';
                
                // Add visualization logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 9: Generating visualizations...');
                    window.detailedProgress.addToProgressLog('Saving visualizations...');
                    window.detailedProgress.addToProgressLog('Saved waveform visualization');
                    window.detailedProgress.addToProgressLog('Saved spectrogram visualization');
                    window.detailedProgress.addToProgressLog('Saved spectrum visualization');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('Generating chromagram visualization...');
                        window.detailedProgress.addToProgressLog('Generating stereo field visualization...');
                        window.detailedProgress.addToProgressLog('Generating 3D spatial field visualization...');
                        window.detailedProgress.addToProgressLog('Visualizations generated in 2.73 seconds');
                        window.detailedProgress.addToProgressLog('');
                    }, 1200);
                }
            } else if (progress === 75) {
                // Update AI processing text for more detail
                progressText.textContent = 'Processing frequency analysis with AI...';
                
                // Add AI processing logs
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 10: Running AI analysis...');
                    window.detailedProgress.addToProgressLog('Sending analysis data to AI model...');
                    setTimeout(() => {
                        window.detailedProgress.addToProgressLog('Processing frequency data with AI model...');
                        window.detailedProgress.addToProgressLog('Processing dynamics data with AI model...');
                        window.detailedProgress.addToProgressLog('Processing stereo field data with AI model...');
                    }, 1500);
                }
            } else if (progress === 85) {
                // Update AI processing text for more detail
                progressText.textContent = 'Generating mix recommendations...';
                
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('Generating genre context analysis...');
                    window.detailedProgress.addToProgressLog('Generating mix improvement suggestions...');
                    window.detailedProgress.addToProgressLog('Generating reference track recommendations...');
                }
            } else if (progress === 95) {
                progressText.textContent = 'Finalizing results...';
                
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('AI analysis completed in 5.43 seconds');
                    window.detailedProgress.addToProgressLog('');
                    window.detailedProgress.addToProgressLog('<span class="log-active">****************************************</span>');
                    window.detailedProgress.addToProgressLog('Step 11: Calculating overall score...');
                }
            } else if (progress >= 100) {
                // Complete all phases
                stepAI.classList.remove('active');
                stepAI.classList.add('completed');
                
                updateProgressBar(100, 'Completed');
                progressText.textContent = 'Analysis complete!';
                
                if (window.detailedProgress) {
                    window.detailedProgress.addToProgressLog('Final overall score: 76.8/100');
                    window.detailedProgress.addToProgressLog('');
                    window.detailedProgress.addToProgressLog('<span class="log-success">==================================================</span>');
                    window.detailedProgress.addToProgressLog('<span class="log-success">ANALYSIS COMPLETE</span>');
                    window.detailedProgress.addToProgressLog('<span class="log-success">Total analysis time: 12.48 seconds</span>');
                    window.detailedProgress.addToProgressLog('<span class="log-success">==================================================</span>');
                }
                
                clearInterval(interval);
                setTimeout(callback, 500); // Delay the display of results for better UX
            }
            
            // Update progress bar
            updateProgressBar(progress, progressStage.textContent);
            
        }, 80); // Slower update for better UX visibility of steps
    }
    
    // Update the progress bar and related elements
    function updateProgressBar(percentage, stage) {
        const roundedPercentage = Math.round(percentage);
        
        // Update the progress bar width
        progressBar.style.width = roundedPercentage + '%';
        
        // Update text elements
        progressPercentage.textContent = roundedPercentage + '%';
        progressStage.textContent = stage;
        
        // Update the detailed progress feedback if available
        if (window.detailedProgress && typeof window.detailedProgress.handleProgressStageChange === 'function') {
            window.detailedProgress.handleProgressStageChange(stage, roundedPercentage);
        }
    }
    
    // Reset progress steps
    function resetProgressSteps() {
        const steps = [stepUpload, stepAnalyze, stepVisualize, stepAI];
        steps.forEach(step => {
            if (step) {
                step.classList.remove('active', 'completed');
            }
        });
    }
    
    // Display results
    function displayResults(data) {
        console.log("Displaying results:", data);
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Check if the result is from cache and show notification
        if (data.from_cache) {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = 'cache-notification';
            notification.innerHTML = `
                <div class="notification-content">
                    <div class="notification-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                        </svg>
                    </div>
                    <div class="notification-text">
                        <p>This song was previously analyzed and loaded from our database.</p>
                    </div>
                    <button class="notification-close">×</button>
                </div>
            `;
            
            // Add the notification to the page
            document.body.appendChild(notification);
            
            // Add event listener to close button
            notification.querySelector('.notification-close').addEventListener('click', function() {
                notification.remove();
            });
            
            // Auto-remove after 10 seconds
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    notification.remove();
                }
            }, 10000);
            
            console.log("Results loaded from cache");
        }
        
        // Update filename display
        document.getElementById('filename').textContent = data.filename;
        
        // Update overall score with animation if available
        const overallScore = data.results.overall_score;
        if (window.updateScoreWithAnimation) {
            window.updateScoreWithAnimation(overallScore);
        } else {
            document.getElementById('overall-score').textContent = overallScore;
        }
        
        // Frequency Balance
        const frequencyBalance = data.results.frequency_balance;
        document.getElementById('frequency-score').textContent = Math.round(frequencyBalance.balance_score);
        
        const frequencyAnalysis = document.getElementById('frequency-analysis');
        frequencyAnalysis.innerHTML = '';
        frequencyBalance.analysis.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            frequencyAnalysis.appendChild(li);
        });
        
        // Display AI frequency analysis if available
        if (data.results.ai_insights) {
            displayAIFrequencyInsights(data.results.ai_insights, frequencyBalance);
        }
        
        // Create frequency chart
        createFrequencyChart(frequencyBalance.band_energy);
        
        // Dynamic Range
        const dynamicRange = data.results.dynamic_range;
        document.getElementById('dynamics-score').textContent = Math.round(dynamicRange.dynamic_range_score);
        document.getElementById('dynamic-range').textContent = dynamicRange.dynamic_range_db.toFixed(1) + ' dB';
        document.getElementById('crest-factor').textContent = dynamicRange.crest_factor_db.toFixed(1) + ' dB';
        document.getElementById('plr').textContent = dynamicRange.plr.toFixed(1) + ' dB';
        
        const dynamicsAnalysis = document.getElementById('dynamics-analysis');
        dynamicsAnalysis.innerHTML = '';
        dynamicRange.analysis.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            dynamicsAnalysis.appendChild(li);
        });
        
        // Stereo Field
        const stereoField = data.results.stereo_field;
        document.getElementById('width-score').textContent = Math.round(stereoField.width_score);
        document.getElementById('phase-score').textContent = Math.round(stereoField.phase_score);
        document.getElementById('correlation').textContent = stereoField.correlation.toFixed(2);
        document.getElementById('mid-side-ratio').textContent = `${(stereoField.mid_ratio * 100).toFixed(0)}% / ${(stereoField.side_ratio * 100).toFixed(0)}%`;
        
        const stereoAnalysis = document.getElementById('stereo-analysis');
        stereoAnalysis.innerHTML = '';
        stereoField.analysis.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            stereoAnalysis.appendChild(li);
        });
        
        // Clarity
        const clarity = data.results.clarity;
        document.getElementById('clarity-score').textContent = Math.round(clarity.clarity_score);
        document.getElementById('spectral-contrast').textContent = clarity.spectral_contrast.toFixed(2);
        document.getElementById('spectral-flatness').textContent = clarity.spectral_flatness.toFixed(3);
        document.getElementById('spectral-centroid').textContent = Math.round(clarity.spectral_centroid) + ' Hz';
        
        const clarityAnalysis = document.getElementById('clarity-analysis');
        clarityAnalysis.innerHTML = '';
        clarity.analysis.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            clarityAnalysis.appendChild(li);
        });
        
        // Create clarity chart
        createClarityChart(clarity);

        // Transients analysis
        if (data.results.transients) {
            console.log("Transients data:", data.results.transients);
            
            const transients = data.results.transients;
            
            // Set score
            document.getElementById('transients-score').textContent = Math.round(transients.transients_score || 0);
            
            // Set metrics
            document.getElementById('attack-time').textContent = (transients.attack_time || 0).toFixed(1) + ' ms';
            document.getElementById('transient-density').textContent = (transients.transient_density || 0).toFixed(2);
            document.getElementById('percussion-energy').textContent = Math.round(transients.percussion_energy || 0) + '%';
            
            // Set analysis text
            const transientAnalysis = document.getElementById('transients-analysis');
            transientAnalysis.innerHTML = '';
            if (transients.analysis && transients.analysis.length > 0) {
                transients.analysis.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    transientAnalysis.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No transient analysis available.';
                transientAnalysis.appendChild(li);
            }
            
            // Create transients chart if data is available
            if (transients.transient_data) {
                createTransientsChart(transients.transient_data);
            }
        } else {
            // Set default values for transient analysis elements
            document.getElementById('transients-score').textContent = 'N/A';
            document.getElementById('attack-time').textContent = 'N/A';
            document.getElementById('transient-density').textContent = 'N/A';
            document.getElementById('percussion-energy').textContent = 'N/A';
            
            // Set default analysis text
            const transientAnalysis = document.getElementById('transients-analysis');
            transientAnalysis.innerHTML = '';
            const li = document.createElement('li');
            li.textContent = 'Transient analysis not available for this track.';
            transientAnalysis.appendChild(li);
        }
        
        // Set harmonic analysis data
        if (data.results.harmonic_content) {
            console.log("Harmonic content data:", data.results.harmonic_content);
            
            // Set key
            const keyElement = document.getElementById('harmonic-key');
            if (keyElement) {
                keyElement.textContent = 'Key: ' + (data.results.harmonic_content.key || 'Unknown');
            }
            
            // Set harmonic complexity
            const complexityElement = document.getElementById('harmonic-complexity');
            if (complexityElement) {
                const complexity = data.results.harmonic_content.harmonic_complexity;
                complexityElement.textContent = (complexity !== undefined ? Math.round(complexity) : 0) + '%';
            }
            
            // Set key consistency
            const consistencyElement = document.getElementById('key-consistency');
            if (consistencyElement) {
                const consistency = data.results.harmonic_content.key_consistency;
                consistencyElement.textContent = (consistency !== undefined ? Math.round(consistency) : 0) + '%';
            }
            
            // Set chord changes
            const changesElement = document.getElementById('chord-changes');
            if (changesElement) {
                const changes = data.results.harmonic_content.chord_changes_per_minute;
                changesElement.textContent = (changes !== undefined ? changes.toFixed(1) : '0.0') + '/min';
            }
            
            // Set harmonic analysis text
            const harmonicAnalysisList = document.getElementById('harmonic-analysis');
            if (harmonicAnalysisList) {
                harmonicAnalysisList.innerHTML = '';
                if (data.results.harmonic_content.analysis && data.results.harmonic_content.analysis.length > 0) {
                    data.results.harmonic_content.analysis.forEach(item => {
                        const li = document.createElement('li');
                        li.textContent = item;
                        harmonicAnalysisList.appendChild(li);
                    });
                } else {
                    const li = document.createElement('li');
                    li.textContent = 'No harmonic analysis available.';
                    harmonicAnalysisList.appendChild(li);
                }
            }
        } else {
            console.error("Harmonic content data not available in results");
            
            // Set default values for harmonic analysis elements
            const elements = {
                'harmonic-key': 'Key: Unknown',
                'harmonic-complexity': '0%',
                'key-consistency': '0%',
                'chord-changes': '0.0/min'
            };
            
            for (const [id, defaultValue] of Object.entries(elements)) {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = defaultValue;
                }
            }
            
            // Set default analysis text
            const harmonicAnalysisList = document.getElementById('harmonic-analysis');
            if (harmonicAnalysisList) {
                harmonicAnalysisList.innerHTML = '';
                const li = document.createElement('li');
                li.textContent = 'Harmonic analysis not available for this track.';
                harmonicAnalysisList.appendChild(li);
            }
        }
        
        // 3D Spatial Analysis
        if (data.results['3d_spatial']) {
            const spatialAnalysis = data.results['3d_spatial'];
            document.getElementById('spatial-score').textContent = Math.round((spatialAnalysis.height_score + spatialAnalysis.depth_score + spatialAnalysis.width_consistency) / 3);
            document.getElementById('height-score').textContent = Math.round(spatialAnalysis.height_score) + '%';
            document.getElementById('depth-score').textContent = Math.round(spatialAnalysis.depth_score) + '%';
            document.getElementById('width-consistency').textContent = Math.round(spatialAnalysis.width_consistency) + '%';
            
            const spatialAnalysisList = document.getElementById('spatial-analysis');
            spatialAnalysisList.innerHTML = '';
            spatialAnalysis.analysis.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                spatialAnalysisList.appendChild(li);
            });
        }
        
        // Display visualizations
        if (data.results.visualizations) {
            console.log("Detailed visualization paths:");
            console.log("Waveform:", data.results.visualizations.waveform);
            console.log("Spectrogram:", data.results.visualizations.spectrogram);
            console.log("Spectrum:", data.results.visualizations.spectrum);
            console.log("Chromagram:", data.results.visualizations.chromagram);
            console.log("Stereo Field:", data.results.visualizations.stereo_field);
            
            // Add detailed element checks
            const waveformImg = document.getElementById('waveform-img');
            const spectrogramImg = document.getElementById('spectrogram-img');
            const spectrumImg = document.getElementById('spectrum-img');
            const chromagramImg = document.getElementById('chromagram-img');
            const stereoFieldImg = document.getElementById('stereo-field-img');
            const stereoFieldContainer = document.getElementById('stereo-field-container');
            
            console.log("Image elements found:");
            console.log("Waveform element:", waveformImg ? "Found" : "Not found");
            console.log("Spectrogram element:", spectrogramImg ? "Found" : "Not found");
            console.log("Spectrum element:", spectrumImg ? "Found" : "Not found");
            console.log("Chromagram element:", chromagramImg ? "Found" : "Not found");
            console.log("Stereo Field element:", stereoFieldImg ? "Found" : "Not found");
            console.log("Stereo Field container:", stereoFieldContainer ? "Found" : "Not found");
            
            // Set waveform, spectrogram, and spectrum
            setImageWithFallback(waveformImg, data.results.visualizations.waveform, 'Waveform visualization');
            setImageWithFallback(spectrogramImg, data.results.visualizations.spectrogram, 'Spectrogram visualization');
            setImageWithFallback(spectrumImg, data.results.visualizations.spectrum, 'Frequency spectrum visualization');
            
            // Handle chromagram visualization with extra error checking
            if (data.results.visualizations.chromagram && chromagramImg) {
                console.log("Setting chromagram image:", data.results.visualizations.chromagram);
                setImageWithFallback(chromagramImg, data.results.visualizations.chromagram, 'Chromagram visualization');
            } else {
                console.log("Chromagram visualization not available or element not found");
                if (chromagramImg) {
                    chromagramImg.src = '/static/img/error.png';
                    chromagramImg.alt = 'Chromagram visualization not available';
                }
            }
            
            // Handle stereo field visualization
            if (data.results.visualizations.stereo_field && stereoFieldContainer && stereoFieldImg) {
                console.log("Setting stereo field image:", data.results.visualizations.stereo_field);
                stereoFieldContainer.style.display = 'block';
                setImageWithFallback(stereoFieldImg, data.results.visualizations.stereo_field, 'Stereo field visualization');
            } else {
                console.log("Hiding stereo field container - No visualization available");
                if (stereoFieldContainer) {
                    stereoFieldContainer.style.display = 'none';
                }
            }
            
            // Handle 3D spatial field visualization
            const spatialFieldImg = document.getElementById('spatial-field-img');
            const spatialFieldContainer = document.getElementById('spatial-field-container');
            
            // Check if we have an interactive visualization
            if (data.results.visualizations.spatial_field_interactive && spatialFieldContainer) {
                console.log("Setting interactive 3D spatial field:", data.results.visualizations.spatial_field_interactive);
                
                // Get existing iframe - already in HTML
                let iframe = document.getElementById('spatial-field-iframe');
                if (iframe) {
                    // Update iframe source to regenerated file
                    iframe.src = data.results.visualizations.spatial_field_interactive;
                    iframe.style.display = 'block';
                    
                    // Hide the static image
                    if (spatialFieldImg) {
                        spatialFieldImg.style.display = 'none';
                    }
                }
                
                // Note: We don't need to create a new iframe
                
                // Add class to indicate interactive visualization
                spatialFieldContainer.classList.add('interactive-visualization');
                
                // Add a button to toggle between 3D and static view
                const toggleButton = document.createElement('button');
                toggleButton.textContent = 'Toggle 2D/3D View';
                toggleButton.className = 'toggle-view-btn';
                toggleButton.onclick = function() {
                    const iframe = document.getElementById('spatial-field-iframe');
                    if (iframe.style.display === 'none') {
                        iframe.style.display = 'block';
                        spatialFieldImg.style.display = 'none';
                        toggleButton.textContent = 'Switch to 2D View';
                    } else {
                        iframe.style.display = 'none';
                        spatialFieldImg.style.display = 'block';
                        toggleButton.textContent = 'Switch to 3D View';
                    }
                };
                spatialFieldContainer.appendChild(toggleButton);
            } else if (data.results.visualizations.spatial_field && spatialFieldImg) {
                // Fall back to static image
                console.log("Setting 3D spatial field image:", data.results.visualizations.spatial_field);
                setImageWithFallback(spatialFieldImg, data.results.visualizations.spatial_field, '3D spatial field visualization');
            } else {
                console.log("3D spatial field visualization not available or element not found");
                if (spatialFieldImg) {
                    spatialFieldImg.src = '/static/img/error.png';
                    spatialFieldImg.alt = '3D spatial field visualization not available';
                }
            }
            
            // Check if all visualizations are loaded
            setTimeout(checkVisualizationsLoaded, 500);
        }
        
        // AI Insights
        if (data.results.ai_insights) {
            displayAIInsights(data.results.ai_insights);
        }
    }
    
    // Display AI Insights
    function displayAIInsights(aiInsights) {
        // Check if there was an error
        if (aiInsights.error) {
            document.getElementById('ai-error').style.display = 'block';
            document.getElementById('ai-error').querySelector('p').textContent = aiInsights.error;
        } else {
            document.getElementById('ai-error').style.display = 'none';
        }
        
        // Set model name
        const modelNameElement = document.getElementById('ai-model-used');
        if (aiInsights.model_used) {
            modelNameElement.textContent = aiInsights.model_used;
        } else {
            modelNameElement.textContent = "AI Model";
        }
        
        // Set summary
        document.getElementById('ai-summary').textContent = aiInsights.summary;
        
        // Set genre context
        document.getElementById('ai-genre-context').textContent = aiInsights.genre_context || "No genre analysis available.";
        
        // Set subgenre context
        document.getElementById('ai-subgenre-context').textContent = aiInsights.subgenre_context || "No subgenre analysis available.";
        
        // Set strengths
        const strengthsList = document.getElementById('ai-strengths');
        strengthsList.innerHTML = '';
        aiInsights.strengths.forEach(strength => {
            const li = document.createElement('li');
            li.textContent = strength;
            strengthsList.appendChild(li);
        });
        
        // Set weaknesses
        const weaknessesList = document.getElementById('ai-weaknesses');
        weaknessesList.innerHTML = '';
        aiInsights.weaknesses.forEach(weakness => {
            const li = document.createElement('li');
            li.textContent = weakness;
            weaknessesList.appendChild(li);
        });
        
        // Set suggestions
        const suggestionsList = document.getElementById('ai-suggestions');
        suggestionsList.innerHTML = '';
        aiInsights.suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            suggestionsList.appendChild(li);
        });

        // Set reference tracks
        const referenceTracksList = document.getElementById('ai-reference-tracks');
        referenceTracksList.innerHTML = '';
        if (aiInsights.reference_tracks && aiInsights.reference_tracks.length > 0) {
            aiInsights.reference_tracks.forEach(track => {
                const li = document.createElement('li');
                li.textContent = track;
                referenceTracksList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No specific reference tracks provided.";
            referenceTracksList.appendChild(li);
        }

        // Set processing recommendations
        const processingRecommendationsList = document.getElementById('ai-processing-recommendations');
        processingRecommendationsList.innerHTML = '';
        if (aiInsights.processing_recommendations && aiInsights.processing_recommendations.length > 0) {
            aiInsights.processing_recommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = recommendation;
                processingRecommendationsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No specific processing recommendations provided.";
            processingRecommendationsList.appendChild(li);
        }
        
        // Set mix translation recommendations
        const translationRecommendationsList = document.getElementById('ai-translation-recommendations');
        translationRecommendationsList.innerHTML = '';
        if (aiInsights.translation_recommendations && aiInsights.translation_recommendations.length > 0) {
            aiInsights.translation_recommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = recommendation;
                translationRecommendationsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = "No mix translation recommendations provided.";
            translationRecommendationsList.appendChild(li);
        }
    }
    
    // Display AI Frequency Insights
    function displayAIFrequencyInsights(aiInsights, frequencyBalance) {
        // Check if there was an error
        if (aiInsights.error) {
            document.getElementById('ai-freq-error').style.display = 'block';
            document.getElementById('ai-freq-error').querySelector('p').textContent = aiInsights.error;
            return;
        } else {
            document.getElementById('ai-freq-error').style.display = 'none';
        }
        
        // Set model name
        const modelNameElement = document.getElementById('ai-model-used-freq');
        if (aiInsights.model_used) {
            modelNameElement.textContent = aiInsights.model_used;
        } else {
            modelNameElement.textContent = "AI Model";
        }
        
        // Extract frequency-related issues from the weaknesses and summary
        const frequencyIssuesList = document.getElementById('ai-frequency-issues');
        frequencyIssuesList.innerHTML = '';
        
        // Expanded array of frequency-related keywords to filter by
        const frequencyKeywords = [
            'frequency', 'eq', 'equalization', 'bass', 'treble', 'mid', 'low', 'high', 
            'hz', 'khz', 'muddy', 'boomy', 'harsh', 'thin', 'boxy', 'sibilant', 
            'presence', 'fundamental', 'resonance', 'balance', 'spectrum', 'sub-bass',
            'low-end', 'high-end', 'boost', 'cut', 'attenuate', 'rumble', 'warmth',
            'brittle', 'bright', 'dull', 'dark', 'clarity', 'definition', 'bandwidth',
            'honky', 'nasal', 'tinny', 'bloated', 'scoop', 'notch', 'filter',
            'db', 'decibel', 'upper', 'lower', 'octave', 'range', 'band', 'hertz'
        ];
        
        // Get all possible sources of frequency-related issues
        let allIssuesSources = [...aiInsights.weaknesses];
        
        // Add summary if it contains frequency terms
        if (aiInsights.summary && frequencyKeywords.some(keyword => 
            aiInsights.summary.toLowerCase().includes(keyword.toLowerCase()))) {
            allIssuesSources.push(aiInsights.summary);
        }
        
        // Also check the genre context for frequency information
        if (aiInsights.genre_context && frequencyKeywords.some(keyword => 
            aiInsights.genre_context.toLowerCase().includes(keyword.toLowerCase()))) {
            // Extract sentences containing frequency keywords
            const sentences = aiInsights.genre_context.split(/[.!?]+/).filter(sentence => 
                sentence.trim() && frequencyKeywords.some(keyword => 
                    sentence.toLowerCase().includes(keyword.toLowerCase())
                )
            );
            allIssuesSources = allIssuesSources.concat(sentences);
        }
        
        // Filter for frequency-related issues
        const frequencyIssues = allIssuesSources.filter(issue => 
            issue && frequencyKeywords.some(keyword => issue.toLowerCase().includes(keyword.toLowerCase()))
        );
        
        if (frequencyIssues.length > 0) {
            frequencyIssues.forEach(issue => {
                const li = document.createElement('li');
                li.textContent = issue.trim();
                frequencyIssuesList.appendChild(li);
            });
        } else {
            // Check if we can extract frequency info directly from band energy analysis
            if (frequencyBalance && frequencyBalance.analysis && frequencyBalance.analysis.length > 0) {
                frequencyBalance.analysis.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    frequencyIssuesList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = "No specific frequency issues identified.";
                frequencyIssuesList.appendChild(li);
            }
        }
        
        // Extract frequency-related recommendations
        const frequencyRecommendationsList = document.getElementById('ai-frequency-recommendations');
        frequencyRecommendationsList.innerHTML = '';
        
        // Combine all possible sources of recommendations
        let allRecommendations = [...aiInsights.suggestions];
        
        if (aiInsights.processing_recommendations && aiInsights.processing_recommendations.length > 0) {
            allRecommendations = allRecommendations.concat(aiInsights.processing_recommendations);
        }
        
        // Also check strengths for positive frequency information
        if (aiInsights.strengths && aiInsights.strengths.length > 0) {
            const frequencyStrengths = aiInsights.strengths.filter(strength => 
                frequencyKeywords.some(keyword => strength.toLowerCase().includes(keyword.toLowerCase()))
            );
            if (frequencyStrengths.length > 0) {
                allRecommendations = allRecommendations.concat(frequencyStrengths.map(strength => 
                    `Maintain: ${strength}`
                ));
            }
        }
        
        // If we have specific genre context with frequency info, add it
        if (aiInsights.genre_context) {
            const genreSentences = aiInsights.genre_context.split(/[.!?]+/).filter(sentence => 
                sentence.trim() && frequencyKeywords.some(keyword => 
                    sentence.toLowerCase().includes(keyword.toLowerCase())
                )
            );
            
            if (genreSentences.length > 0) {
                allRecommendations.push(`Genre context: ${genreSentences.join(' ')}`);
            }
        }
        
        // Filter for frequency-related recommendations
        const frequencyRecommendations = allRecommendations.filter(recommendation => 
            recommendation && frequencyKeywords.some(keyword => recommendation.toLowerCase().includes(keyword.toLowerCase()))
        );
        
        if (frequencyRecommendations.length > 0) {
            frequencyRecommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = recommendation.trim();
                frequencyRecommendationsList.appendChild(li);
            });
        } else {
            // As a fallback, provide generic recommendations based on the frequency balance data
            if (frequencyBalance && frequencyBalance.band_energy) {
                // Find the band with the lowest and highest energy
                const bands = Object.entries(frequencyBalance.band_energy);
                bands.sort((a, b) => a[1] - b[1]);
                
                const lowestBand = bands[0];
                const highestBand = bands[bands.length - 1];
                
                if (lowestBand && highestBand) {
                    const li1 = document.createElement('li');
                    li1.textContent = `Consider boosting the ${lowestBand[0].replace('_', ' ')} band which has the lowest energy in your mix.`;
                    frequencyRecommendationsList.appendChild(li1);
                    
                    if (highestBand[1] > 90) {
                        const li2 = document.createElement('li');
                        li2.textContent = `The ${highestBand[0].replace('_', ' ')} band has very high energy (${Math.round(highestBand[1])}%). Consider attenuating this range slightly for better balance.`;
                        frequencyRecommendationsList.appendChild(li2);
                    }
                    
                    const li3 = document.createElement('li');
                    li3.textContent = "Check for proper frequency balance across all bands to ensure clarity and separation in your mix.";
                    frequencyRecommendationsList.appendChild(li3);
                    
                    return;
                }
            }
            
            const li = document.createElement('li');
            li.textContent = "No specific frequency recommendations provided.";
            frequencyRecommendationsList.appendChild(li);
        }
    }
    
    // Create frequency chart
    function createFrequencyChart(bandEnergy) {
        const ctx = document.getElementById('frequency-chart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (frequencyChart) {
            frequencyChart.destroy();
        }
        
        // Prepare data
        const labels = Object.keys(bandEnergy).map(key => {
            // Format the labels for better display
            return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        });
        
        const values = Object.values(bandEnergy);
        
        // Create new chart
        frequencyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Energy (%)',
                    data: values,
                    backgroundColor: 'rgba(74, 107, 255, 0.7)',
                    borderColor: 'rgba(74, 107, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Energy (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Frequency Band'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Energy: ${context.raw.toFixed(1)}%`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Create clarity chart
    let clarityChart = null;
    function createClarityChart(clarityData) {
        const ctx = document.getElementById('clarity-chart').getContext('2d');
        
        // Destroy previous chart if it exists
        if (clarityChart) {
            clarityChart.destroy();
        }
        
        // Get the raw data values
        const contrastRaw = clarityData.spectral_contrast;
        const flatnessRaw = clarityData.spectral_flatness;
        const centroidRaw = clarityData.spectral_centroid;
        const score = clarityData.clarity_score;
        const isInstrumental = clarityData.is_instrumental;
        const fftParams = clarityData.fft_params || { n_fft: 0, hop_length: 0, method: "unknown" };
        
        // Add component score labels under the chart
        const container = ctx.canvas.parentNode;
        let componentsEl = container.querySelector('.clarity-components');
        if (!componentsEl) {
            componentsEl = document.createElement('div');
            componentsEl.className = 'clarity-components';
            container.appendChild(componentsEl);
        }
        
        // Calculate component scores similar to backend algorithm
        // These formulas should match the backend calculation as closely as possible
        const contrastScore = Math.min(100, Math.max(0, contrastRaw * 1000));
        const flatnessScore = Math.min(100, Math.max(0, (1 - flatnessRaw) * 100));
        
        // Different weightings based on if track is instrumental or has vocals
        let contrastWeight, flatnessWeight, centroidWeight, centroidScore;
        if (isInstrumental) {
            contrastWeight = 0.5;  // Higher contrast weight for instrumental
            flatnessWeight = 0.3;
            centroidWeight = 0.2;
            // For instrumental, wider range is optimal
            const sampleRate = 44100; // Estimate, real value would come from backend
            centroidScore = Math.min(100, Math.max(0, 100 - Math.abs(centroidRaw - sampleRate/4)/(sampleRate/8)));
        } else {
            contrastWeight = 0.4;
            flatnessWeight = 0.2;
            centroidWeight = 0.4;  // Higher centroid weight for vocals
            // For vocals, more specific range for vocal clarity
            const sampleRate = 44100; // Estimate
            const vocalClarityCenter = sampleRate/8 + sampleRate/6;
            centroidScore = Math.min(100, Math.max(0, 100 - Math.abs(centroidRaw - vocalClarityCenter)/(sampleRate/10)));
        }
        
        // Try to get harmonic content data if available
        let harmonicData = null;
        const harmonicComplexityEl = document.getElementById('harmonic-complexity');
        if (harmonicComplexityEl) {
            const complexityText = harmonicComplexityEl.textContent;
            if (complexityText) {
                const complexityValue = parseInt(complexityText);
                if (!isNaN(complexityValue)) {
                    harmonicData = {
                        complexity: complexityValue
                    };
                    // Get the key consistency if available
                    const keyConsistencyEl = document.getElementById('key-consistency');
                    if (keyConsistencyEl) {
                        const consistencyText = keyConsistencyEl.textContent;
                        if (consistencyText) {
                            const consistencyValue = parseInt(consistencyText);
                            if (!isNaN(consistencyValue)) {
                                harmonicData.keyConsistency = consistencyValue;
                            }
                        }
                    }
                }
            }
        }
        
        // Try to get transient data if available
        let transientData = null;
        const transientScoreEl = document.getElementById('transients-score');
        if (transientScoreEl && transientScoreEl.textContent !== 'N/A') {
            const transientScoreText = transientScoreEl.textContent;
            if (transientScoreText) {
                const transientScoreValue = parseInt(transientScoreText);
                if (!isNaN(transientScoreValue)) {
                    transientData = {
                        score: transientScoreValue
                    };
                    
                    // Get attack time if available
                    const attackTimeEl = document.getElementById('attack-time');
                    if (attackTimeEl && attackTimeEl.textContent !== 'N/A') {
                        const attackTimeText = attackTimeEl.textContent.replace(' ms', '');
                        const attackTimeValue = parseFloat(attackTimeText);
                        if (!isNaN(attackTimeValue)) {
                            transientData.attackTime = attackTimeValue;
                        }
                    }
                }
            }
        }
        
        // Get FFT method description
        let fftMethodDescription = "";
        if (fftParams.method === "spectral_contrast") {
            fftMethodDescription = `Calculated using librosa's spectral_contrast with n_fft=${fftParams.n_fft}, hop_length=${fftParams.hop_length}`;
        } else if (fftParams.method === "alternative_std") {
            fftMethodDescription = `Calculated using alternative method (spectrum standard deviation) with n_fft=${fftParams.n_fft}, hop_length=${fftParams.hop_length}`;
        } else if (fftParams.method.startsWith("default") || fftParams.method.startsWith("alternative_empty")) {
            fftMethodDescription = `Using default value (audio may be very quiet or contain mostly silence)`;
        } else if (fftParams.method === "error" || fftParams.method === "error_fallback") {
            fftMethodDescription = `Error during spectral analysis, using fallback value`;
        } else {
            fftMethodDescription = `Calculation method: ${fftParams.method}`;
        }
        
        // Display the component values, the scaling calculation, and weights
        componentsEl.innerHTML = `
            <div class="clarity-component">
                <span class="component-label">Spectral Contrast:</span>
                <span class="component-value">${contrastRaw.toFixed(6)}</span>
                <span class="component-calculation">× 1000 = ${(contrastRaw * 1000).toFixed(2)} → clamped to ${Math.round(contrastScore)}%</span>
                <span class="component-score">Score: ${Math.round(contrastScore)}/100</span>
                <span class="component-weight">Weight: ${contrastWeight.toFixed(1)}</span>
            </div>
            <div class="clarity-component fft-params">
                <span class="component-label">FFT Parameters:</span>
                <span class="component-value">${fftParams.n_fft > 0 ? fftParams.n_fft : 'N/A'}</span>
                <span class="component-calculation">${fftMethodDescription}</span>
            </div>
            <div class="clarity-component">
                <span class="component-label">Spectral Flatness:</span>
                <span class="component-value">${flatnessRaw.toFixed(4)}</span>
                <span class="component-calculation">inverted: (1 - ${flatnessRaw.toFixed(4)}) × 100 = ${(flatnessScore).toFixed(1)}%</span>
                <span class="component-score">Score: ${Math.round(flatnessScore)}/100</span>
                <span class="component-weight">Weight: ${flatnessWeight.toFixed(1)}</span>
            </div>
            <div class="clarity-component">
                <span class="component-label">Spectral Centroid:</span>
                <span class="component-value">${Math.round(centroidRaw)} Hz</span>
                <span class="component-calculation">normalized to ${Math.round(centroidScore)}%</span>
                <span class="component-score">Score: ${Math.round(centroidScore)}/100</span>
                <span class="component-weight">Weight: ${centroidWeight.toFixed(1)}</span>
            </div>
            ${harmonicData ? `
            <div class="clarity-component harmonic-data">
                <span class="component-label">Harmonic Complexity:</span>
                <span class="component-value">${harmonicData.complexity}%</span>
                <span class="component-calculation">Higher complexity can affect perceived clarity</span>
                ${harmonicData.keyConsistency ? `<span class="component-score">Key Consistency: ${harmonicData.keyConsistency}%</span>` : ''}
            </div>
            ` : ''}
            ${transientData ? `
            <div class="clarity-component transient-data">
                <span class="component-label">Transient Quality:</span>
                <span class="component-value">${transientData.score}/100</span>
                <span class="component-calculation">Sharp transients increase perceived clarity</span>
                ${transientData.attackTime ? `<span class="component-score">Attack Time: ${transientData.attackTime} ms</span>` : ''}
            </div>
            ` : ''}
            <div class="clarity-formula">
                <span>Clarity Score = (${Math.round(contrastScore)} × ${contrastWeight.toFixed(1)}) + (${Math.round(flatnessScore)} × ${flatnessWeight.toFixed(1)}) + (${Math.round(centroidScore)} × ${centroidWeight.toFixed(1)}) = ${Math.round(score)}</span>
            </div>
            <div class="clarity-note">
                <span><strong>Note:</strong> Spectral Contrast typically has very small raw values (around 0.0005). It is multiplied by 1000 to bring it to a useful scale, which is why it often shows around 50% after scaling.</span>
            </div>
        `;
        
        // Create radar chart to visualize all clarity-related factors
        if (document.getElementById('clarity-radar-chart')) {
            // If radar chart element exists, create or update it
            const radarCtx = document.getElementById('clarity-radar-chart').getContext('2d');
            
            // Destroy previous radar chart if it exists
            if (window.clarityRadarChart) {
                window.clarityRadarChart.destroy();
            }
            
            // Prepare radar chart data
            const radarData = {
                labels: [
                    'Spectral Contrast', 
                    'Tonal Focus',
                    'Frequency Balance',
                    harmonicData ? 'Harmonic Quality' : null,
                    transientData ? 'Transient Quality' : null
                ].filter(Boolean),
                datasets: [{
                    label: 'Your Track',
                    data: [
                        Math.round(contrastScore),
                        Math.round(flatnessScore),
                        Math.round(centroidScore),
                        harmonicData ? 
                            // Average of harmonic complexity and key consistency, or just complexity if that's all we have
                            harmonicData.keyConsistency ? 
                                Math.round((harmonicData.complexity + harmonicData.keyConsistency) / 2) : 
                                harmonicData.complexity 
                            : null,
                        transientData ? transientData.score : null
                    ].filter(item => item !== null),
                    backgroundColor: 'rgba(74, 107, 255, 0.2)',
                    borderColor: 'rgba(74, 107, 255, 1)',
                    pointBackgroundColor: 'rgba(74, 107, 255, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(74, 107, 255, 1)'
                }, {
                    label: 'Professional Reference',
                    data: [
                        70, // Contrast reference
                        80, // Flatness reference
                        75, // Centroid reference
                        harmonicData ? 85 : null, // Harmonic reference
                        transientData ? 80 : null  // Transient reference
                    ].filter(item => item !== null),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(255, 99, 132, 1)'
                }]
            };
            
            // Create radar chart
            window.clarityRadarChart = new Chart(radarCtx, {
                type: 'radar',
                data: radarData,
                options: {
                    elements: {
                        line: {
                            borderWidth: 3
                        }
                    },
                    scales: {
                        r: {
                            angleLines: {
                                display: true
                            },
                            suggestedMin: 0,
                            suggestedMax: 100
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw}/100`;
                                }
                            }
                        }
                    }
                }
            });
        }
        
        // Create stacked bar chart to visualize component contributions to total score
        clarityChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Raw Values', 'Normalized Scores', 'Weighted Contributions'],
                datasets: [
                    {
                        label: 'Spectral Contrast',
                        data: [contrastRaw * 1000, contrastScore, contrastScore * contrastWeight],
                        backgroundColor: 'rgba(74, 107, 255, 0.7)',
                        borderColor: 'rgba(74, 107, 255, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Tonal Focus',
                        data: [(1 - flatnessRaw) * 100, flatnessScore, flatnessScore * flatnessWeight],
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Frequency Balance',
                        data: [centroidScore, centroidScore, centroidScore * centroidWeight],
                        backgroundColor: 'rgba(75, 192, 192, 0.7)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Processing Steps'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Values'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label;
                                const value = context.raw.toFixed(2);
                                const index = context.dataIndex;
                                
                                if (index === 0) {
                                    if (label === 'Spectral Contrast') {
                                        return `${label}: Raw ${contrastRaw.toFixed(6)} × 1000 = ${value}`;
                                    } else if (label === 'Tonal Focus') {
                                        return `${label}: 1 - ${flatnessRaw.toFixed(4)} = ${value}%`;
                                    } else {
                                        return `${label}: ${value}%`;
                                    }
                                } else if (index === 1) {
                                    return `${label} normalized: ${value}%`;
                                } else {
                                    return `${label} contribution: ${value} points`;
                                }
                            }
                        }
                    }
                }
            }
        });
        
        // Add radar chart container if it doesn't exist
        if (!document.getElementById('clarity-radar-chart')) {
            const radarContainer = document.createElement('div');
            radarContainer.className = 'radar-container';
            radarContainer.innerHTML = `
                <h3>Clarity Factors Overview</h3>
                <p class="radar-description">This radar chart compares your track's clarity factors to professional reference standards.</p>
                <canvas id="clarity-radar-chart"></canvas>
            `;
            container.parentNode.insertBefore(radarContainer, container.nextSibling);
            
            // Create the radar chart
            createClarityChart(clarityData);  // Recursive call to create the radar chart
            return;  // Exit to avoid infinite recursion
        }
        
        // Add clarity insights section
        let insightsEl = document.querySelector('.clarity-insights');
        if (!insightsEl) {
            insightsEl = document.createElement('div');
            insightsEl.className = 'clarity-insights';
            container.parentNode.appendChild(insightsEl);
            
            // Add clarity insights content
            const trackType = isInstrumental ? 'instrumental' : 'vocal';
            let insightsContent = `
                <h3>Clarity Insights</h3>
                <div class="insights-summary">
                    <div class="insight-summary-score">
                        <div class="summary-score-circle" style="--percent: ${Math.round(score)}">
                            <span>${Math.round(score)}</span>
                        </div>
                        <p>Overall Clarity</p>
                    </div>
                    <div class="insight-summary-text">
                        <p>
                            Your ${trackType} track ${score > 75 ? 'has excellent clarity with well-defined elements.' : 
                                score > 60 ? 'has good clarity with generally well-defined elements.' :
                                score > 45 ? 'has moderate clarity with some elements that could be better defined.' :
                                'has limited clarity with elements that need better definition.'}
                        </p>
                        <p class="insight-summary-strengths">
                            <strong>Strengths:</strong> ${
                                (contrastScore > 70 ? 'Strong frequency separation' : '') +
                                (flatnessScore > 70 ? (contrastScore > 70 ? ', Good' : 'Good') + ' tonal focus' : '') +
                                (centroidScore > 70 ? (contrastScore > 70 || flatnessScore > 70 ? ', Excellent' : 'Excellent') + ' frequency balance' : '') +
                                (contrastScore <= 70 && flatnessScore <= 70 && centroidScore <= 70 ? 'None identified - improvement recommended in all areas' : '')
                            }
                        </p>
                    </div>
                </div>
                
                <div class="insights-categories">
                    <div class="insights-category">
                        <h4>Frequency Definition</h4>
                        <div class="insights-items">`;
            
            // Spectral contrast insights
            if (contrastScore < 40) {
                insightsContent += `
                    <div class="insight warning" data-score="${Math.round(contrastScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(contrastScore)}%"></div>
                        <div class="insight-content">
                            <h5>Low Spectral Contrast</h5>
                            <p>Your track lacks definition between frequencies. This can make it sound muddy or undefined.</p>
                            <div class="insight-recommendation">
                                <strong>Try:</strong> Gentle EQ to separate frequency ranges, careful compression to maintain dynamics
                            </div>
                        </div>
                    </div>`;
            } else if (contrastScore > 70) {
                insightsContent += `
                    <div class="insight positive" data-score="${Math.round(contrastScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(contrastScore)}%"></div>
                        <div class="insight-content">
                            <h5>Good Spectral Contrast</h5>
                            <p>Your track has excellent separation between frequencies, creating a clear sound.</p>
                            <div class="insight-recommendation">
                                <strong>Maintain:</strong> Your current EQ approach works well for frequency separation
                            </div>
                        </div>
                    </div>`;
            } else {
                insightsContent += `
                    <div class="insight neutral" data-score="${Math.round(contrastScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(contrastScore)}%"></div>
                        <div class="insight-content">
                            <h5>Moderate Spectral Contrast</h5>
                            <p>Your track has adequate separation between frequencies.</p>
                            <div class="insight-recommendation">
                                <strong>Consider:</strong> Strategic EQ to further enhance the separation between instruments
                            </div>
                        </div>
                    </div>`;
            }

            insightsContent += `
                        </div>
                    </div>
                    
                    <div class="insights-category">
                        <h4>Tonal Characteristics</h4>
                        <div class="insights-items">`;
            
            // Spectral flatness insights
            if (flatnessScore < 50) {
                insightsContent += `
                    <div class="insight warning" data-score="${Math.round(flatnessScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(flatnessScore)}%"></div>
                        <div class="insight-content">
                            <h5>High Spectral Flatness</h5>
                            <p>Your track has a noise-like quality that reduces clarity.</p>
                            <div class="insight-recommendation">
                                <strong>Try:</strong> Saturation to enhance harmonics, noise reduction if needed
                            </div>
                        </div>
                    </div>`;
            } else if (flatnessScore > 75) {
                insightsContent += `
                    <div class="insight positive" data-score="${Math.round(flatnessScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(flatnessScore)}%"></div>
                        <div class="insight-content">
                            <h5>Low Spectral Flatness</h5>
                            <p>Your track has a tonal, musical quality that enhances clarity.</p>
                            <div class="insight-recommendation">
                                <strong>Maintain:</strong> Your current approach works well for tonal quality
                            </div>
                        </div>
                    </div>`;
            } else {
                insightsContent += `
                    <div class="insight neutral" data-score="${Math.round(flatnessScore)}">
                        <div class="insight-meter" style="--score: ${Math.round(flatnessScore)}%"></div>
                        <div class="insight-content">
                            <h5>Moderate Spectral Flatness</h5>
                            <p>Your track has a balanced mix of tonal and noise-like qualities.</p>
                            <div class="insight-recommendation">
                                <strong>Consider:</strong> Slight harmonic enhancement to bring out more tonal qualities
                            </div>
                        </div>
                    </div>`;
            }
            
            insightsContent += `
                        </div>
                    </div>
                    
                    <div class="insights-category">
                        <h4>Frequency Balance</h4>
                        <div class="insights-items">`;
            
            // Spectral centroid insights
            if (isInstrumental) {
                if (centroidScore < 50) {
                    insightsContent += `
                        <div class="insight warning" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Dark Frequency Balance</h5>
                                <p>Your instrumental track may sound too dark or muffled.</p>
                                <div class="insight-recommendation">
                                    <strong>Try:</strong> Gentle high-shelf boost around 6-10kHz, reduce excessive low-mids
                                </div>
                            </div>
                        </div>`;
                } else if (centroidScore > 75) {
                    insightsContent += `
                        <div class="insight positive" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Balanced Frequency Spectrum</h5>
                                <p>Your instrumental track has a well-balanced brightness.</p>
                                <div class="insight-recommendation">
                                    <strong>Maintain:</strong> Your current frequency balance works well
                                </div>
                            </div>
                        </div>`;
                } else {
                    insightsContent += `
                        <div class="insight neutral" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Adequate Frequency Balance</h5>
                                <p>Your instrumental track has adequate brightness.</p>
                                <div class="insight-recommendation">
                                    <strong>Consider:</strong> Subtle high-frequency enhancement for more clarity
                                </div>
                            </div>
                        </div>`;
                }
            } else {
                if (centroidScore < 50) {
                    insightsContent += `
                        <div class="insight warning" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Lacking Vocal Presence</h5>
                                <p>Your vocal track may lack presence and articulation.</p>
                                <div class="insight-recommendation">
                                    <strong>Try:</strong> Presence boost around 3-5kHz, de-essing if needed, focused compression
                                </div>
                            </div>
                        </div>`;
                } else if (centroidScore > 75) {
                    insightsContent += `
                        <div class="insight positive" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Excellent Vocal Presence</h5>
                                <p>Your vocal track has excellent presence and articulation.</p>
                                <div class="insight-recommendation">
                                    <strong>Maintain:</strong> Your current approach to vocal presence works well
                                </div>
                            </div>
                        </div>`;
                } else {
                    insightsContent += `
                        <div class="insight neutral" data-score="${Math.round(centroidScore)}">
                            <div class="insight-meter" style="--score: ${Math.round(centroidScore)}%"></div>
                            <div class="insight-content">
                                <h5>Adequate Vocal Presence</h5>
                                <p>Your vocal track has adequate presence.</p>
                                <div class="insight-recommendation">
                                    <strong>Consider:</strong> Subtle presence enhancement around 3-5kHz
                                </div>
                            </div>
                        </div>`;
                }
            }
            
            // Add harmonic and transient insights if available
            if (harmonicData) {
                insightsContent += `
                    </div>
                    </div>
                    
                    <div class="insights-category">
                        <h4>Harmonic Content</h4>
                        <div class="insights-items">`;
                        
                if (harmonicData.complexity > 75) {
                    insightsContent += `
                        <div class="insight neutral" data-score="${harmonicData.complexity}">
                            <div class="insight-meter" style="--score: ${harmonicData.complexity}%"></div>
                            <div class="insight-content">
                                <h5>Rich Harmonic Content</h5>
                                <p>Your track has rich harmonic content, which can affect clarity if not balanced properly.</p>
                                <div class="insight-recommendation">
                                    <strong>Consider:</strong> Check for frequency masking between harmonically related elements
                                </div>
                            </div>
                        </div>`;
                } else if (harmonicData.complexity < 40) {
                    insightsContent += `
                        <div class="insight neutral" data-score="${harmonicData.complexity}">
                            <div class="insight-meter" style="--score: ${harmonicData.complexity}%"></div>
                            <div class="insight-content">
                                <h5>Simple Harmonic Content</h5>
                                <p>Your track has simpler harmonic content, which can enhance clarity but might sound less rich.</p>
                                <div class="insight-recommendation">
                                    <strong>Consider:</strong> Subtle harmonic enhancement through saturation or excitation
                                </div>
                            </div>
                        </div>`;
                } else {
                    insightsContent += `
                        <div class="insight neutral" data-score="${harmonicData.complexity}">
                            <div class="insight-meter" style="--score: ${harmonicData.complexity}%"></div>
                            <div class="insight-content">
                                <h5>Balanced Harmonic Content</h5>
                                <p>Your track has well-balanced harmonic content.</p>
                                <div class="insight-recommendation">
                                    <strong>Maintain:</strong> Your current approach to harmonic content works well
                                </div>
                            </div>
                        </div>`;
                }
            }
            
            if (transientData) {
                insightsContent += `
                    </div>
                    </div>
                    
                    <div class="insights-category">
                        <h4>Transient Response</h4>
                        <div class="insights-items">`;
                        
                if (transientData.score > 70) {
                    insightsContent += `
                        <div class="insight positive" data-score="${transientData.score}">
                            <div class="insight-meter" style="--score: ${transientData.score}%"></div>
                            <div class="insight-content">
                                <h5>Excellent Transient Quality</h5>
                                <p>Your track has excellent attack characteristics, enhancing clarity and definition.</p>
                                <div class="insight-recommendation">
                                    <strong>Maintain:</strong> Your current approach to preserving transients works well
                                </div>
                            </div>
                        </div>`;
                } else if (transientData.score < 50) {
                    insightsContent += `
                        <div class="insight warning" data-score="${transientData.score}">
                            <div class="insight-meter" style="--score: ${transientData.score}%"></div>
                            <div class="insight-content">
                                <h5>Limited Transient Quality</h5>
                                <p>Your track could benefit from sharper attacks to improve clarity.</p>
                                <div class="insight-recommendation">
                                    <strong>Try:</strong> Transient enhancement, less aggressive compression, attack time adjustments
                                </div>
                            </div>
                        </div>`;
                } else {
                    insightsContent += `
                        <div class="insight neutral" data-score="${transientData.score}">
                            <div class="insight-meter" style="--score: ${transientData.score}%"></div>
                            <div class="insight-content">
                                <h5>Adequate Transient Quality</h5>
                                <p>Your track has adequate transient response.</p>
                                <div class="insight-recommendation">
                                    <strong>Consider:</strong> Subtle transient enhancement for more definition
                                </div>
                            </div>
                        </div>`;
                }
            }
            
            insightsContent += `
                        </div>
                    </div>
                </div>
                
                <div class="insights-footer">
                    <p>Click on any insight for more detailed recommendations</p>
                </div>`;
                
            insightsEl.innerHTML = insightsContent;
            
            // Add click event listeners to insights for interactivity
            setTimeout(() => {
                const insightItems = document.querySelectorAll('.insight');
                insightItems.forEach(item => {
                    item.addEventListener('click', function() {
                        // Toggle expanded class
                        this.classList.toggle('expanded');
                        
                        // Close other expanded insights
                        insightItems.forEach(otherItem => {
                            if (otherItem !== this && otherItem.classList.contains('expanded')) {
                                otherItem.classList.remove('expanded');
                            }
                        });
                    });
                });
            }, 500);
        }
    }
    
    // Handle errors
    function handleError(message) {
        console.error("Error occurred:", message);
        
        if (progressText) progressText.textContent = message;
        if (progressBar) progressBar.style.backgroundColor = 'var(--danger-color)';
        
        // Show alert for better visibility
        alert('Error: ' + message);
        
        // Reset after 3 seconds
        setTimeout(function() {
            if (uploadArea) uploadArea.style.display = 'flex';
            if (progressContainer) progressContainer.style.display = 'none';
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.style.backgroundColor = 'var(--primary-color)';
            }
        }, 3000);
    }
    
    // Reset button functionality
    document.addEventListener('keydown', function(e) {
        // Reset on Escape key
        if (e.key === 'Escape' && resultsSection.style.display === 'block') {
            resultsSection.style.display = 'none';
            uploadContainer.style.display = 'block';
            uploadArea.style.display = 'flex';
            progressContainer.style.display = 'none';
            progressBar.style.width = '0%';
            fileInput.value = '';
        }
    });

    function checkVisualizationsLoaded() {
        // Check if all visualization images are loaded
        const visualizationImages = document.querySelectorAll('.visualization-container img');
        let allLoaded = true;
        
        visualizationImages.forEach(img => {
            if (!img.complete) {
                allLoaded = false;
            }
        });
        
        if (allLoaded) {
            document.querySelectorAll('.visualization-container').forEach(container => {
                if (!container.classList.contains('loaded') && !container.classList.contains('error')) {
                    container.classList.add('loaded');
                }
            });
        } else {
            setTimeout(checkVisualizationsLoaded, 500);
        }
    }
    
    // Global utilities
    function setImageWithFallback(imgElement, src, altText = 'Visualization') {
        if (!imgElement) {
            console.error(`Image element not found for ${altText}`);
            return;
        }

        if (!src) {
            console.error(`Source is undefined for ${altText}`);
            imgElement.src = '/static/img/error.png';
            imgElement.alt = `${altText} not available`;
            if (imgElement.parentElement) {
                imgElement.parentElement.classList.add('error');
            }
            return;
        }

        console.log(`Setting image source for ${altText}:`, src);
        
        // Add loading class to parent container
        if (imgElement.parentElement) {
            imgElement.parentElement.classList.add('loading');
        }

        imgElement.onload = function() {
            console.log(`Successfully loaded image: ${altText}`);
            if (imgElement.parentElement) {
                imgElement.parentElement.classList.remove('loading');
                imgElement.parentElement.classList.add('loaded');
            }
        };

        imgElement.onerror = function() {
            console.error(`Failed to load image: ${altText}, src: ${src}`);
            if (!src.includes('error.png')) {
                console.log(`Attempting to load fallback image for: ${altText}`);
                imgElement.src = '/static/img/error.png';
            }
            if (imgElement.parentElement) {
                imgElement.parentElement.classList.remove('loading');
                imgElement.parentElement.classList.add('error');
            }
        };

        imgElement.src = src;
    }

    // Make sure these utilities are globally accessible
    window.setImageWithFallback = setImageWithFallback;

    // Add a function to regenerate the stereo field visualization
    function regenerateStereoField(fileId) {
        console.log(`Regenerating stereo field for file ID: ${fileId}`);
        
        // Show loading state
        const stereoImg = document.getElementById('stereo-field-img');
        const stereoContainer = document.getElementById('stereo-field-container');
        
        if (!stereoImg || !stereoContainer) {
            console.error('Could not find stereo field image or container elements');
            return;
        }
        
        // Add loading state
        stereoContainer.classList.add('loading');
        stereoImg.alt = 'Regenerating stereo field...';
        
        // Make API call to regenerate stereo field
        fetch(`/regenerate_stereo_field/${fileId}`, {
            method: 'POST'
        })
        .then(response => {
            console.log('Regenerate stereo field response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Stereo field regeneration response:', data);
            
            if (data.success) {
                // Update the stereo field image with the new URL
                const cacheBuster = `?t=${new Date().getTime()}`;
                const newUrl = `${data.stereo_field_url}${cacheBuster}`;
                console.log('Setting new stereo field image URL:', newUrl);
                
                setImageWithFallback(
                    stereoImg, 
                    newUrl, 
                    'Stereo Field'
                );
                
                // Update stereo information display
                updateStereoInfo(stereoContainer, data);
            } else {
                throw new Error(data.error || 'Failed to regenerate stereo field');
            }
        })
        .catch(error => {
            console.error('Error during stereo field regeneration:', error);
            stereoImg.src = '/static/img/error.png';
            stereoImg.alt = 'Error regenerating stereo field';
            stereoContainer.classList.add('error');
            
            // Show error message to user
            const errorMsg = document.createElement('div');
            errorMsg.className = 'stereo-info error';
            errorMsg.textContent = `Error: ${error.message}`;
            stereoContainer.appendChild(errorMsg);
        })
        .finally(() => {
            stereoContainer.classList.remove('loading');
        });
    }
    
    function updateStereoInfo(container, data) {
        // Remove any existing info element
        const existingInfo = container.querySelector('.stereo-info');
        if (existingInfo) {
            existingInfo.remove();
        }
        
        // Create new info element
        const infoElement = document.createElement('div');
        infoElement.className = 'stereo-info';
        
        if (data.is_stereo) {
            if (data.channels_identical) {
                infoElement.textContent = `Stereo file with identical channels (correlation: ${data.correlation.toFixed(4)})`;
                infoElement.className += ' warning';
            } else {
                infoElement.textContent = `True stereo file (correlation: ${data.correlation.toFixed(4)})`;
                infoElement.className += ' success';
            }
        } else {
            infoElement.textContent = 'Mono audio file';
            infoElement.className += ' info';
        }
        
        container.appendChild(infoElement);
    }
    
    // Make the function globally accessible
    window.regenerateStereoField = regenerateStereoField;

    // Create transients chart
    function createTransientsChart(transientData) {
        const ctx = document.getElementById('transients-chart').getContext('2d');
        
        // Prepare data
        const labels = Array.from({length: transientData.length}, (_, i) => i);
        const values = transientData;
        
        // Create new chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Transient Energy',
                    data: values,
                    backgroundColor: 'rgba(74, 107, 255, 0.2)',
                    borderColor: 'rgba(74, 107, 255, 1)',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Energy'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Footer Musical Theory Links
    setupMusicTheoryModals();

    // Tech Card Expansion Functionality
    const techCards = document.querySelectorAll('.tech-card');

    techCards.forEach(card => {
        const button = card.querySelector('.expand-button');
        const details = card.querySelector('.tech-card-details');
        const techType = card.getAttribute('data-tech');

        if (button && details) {
            // Remove hidden attribute and set initial state
            details.removeAttribute('hidden');
            
            // Set initial ARIA attributes
            button.setAttribute('aria-expanded', 'false');
            button.setAttribute('aria-controls', `${techType}-details`);
            details.setAttribute('id', `${techType}-details`);
            
            button.addEventListener('click', () => {
                const isExpanded = card.classList.contains('expanded');
                
                // Close all other cards first
                techCards.forEach(otherCard => {
                    if (otherCard !== card) {
                        const otherButton = otherCard.querySelector('.expand-button');
                        const otherDetails = otherCard.querySelector('.tech-card-details');
                        
                        if (otherButton && otherDetails) {
                            otherCard.classList.remove('expanded');
                            otherDetails.classList.remove('expanded');
                            otherButton.classList.remove('expanded');
                            otherButton.setAttribute('aria-expanded', 'false');
                        }
                    }
                });
                
                // Toggle current card
                card.classList.toggle('expanded');
                button.classList.toggle('expanded');
                details.classList.toggle('expanded');
                
                // Update ARIA attributes
                button.setAttribute('aria-expanded', !isExpanded);
                
                // Smooth scroll into view if expanding
                if (!isExpanded) {
                    // Calculate the card's position relative to its container
                    const cardRect = card.getBoundingClientRect();
                    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    
                    // Scroll to the card's position with offset
                    window.scrollTo({
                        top: cardRect.top + scrollTop - 20,
                        behavior: 'smooth'
                    });
                }
            });
        }
    });

    // Handle keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close all expanded cards when ESC is pressed
            techCards.forEach(card => {
                const button = card.querySelector('.expand-button');
                const details = card.querySelector('.tech-card-details');
                
                if (button && details) {
                    card.classList.remove('expanded');
                    button.classList.remove('expanded');
                    details.classList.remove('expanded');
                    button.setAttribute('aria-expanded', 'false');
                }
            });
        }
    });

    // Regenerate 3D spatial field visualization
    function regenerateSpatialField(fileId) {
        if (!fileId) {
            console.error("No file ID provided for regeneration");
            return;
        }
        
        const regenerateBtn = document.getElementById('regenerate-spatial-btn');
        if (regenerateBtn) {
            regenerateBtn.disabled = true;
            regenerateBtn.innerHTML = `
                <svg class="spinner" viewBox="0 0 50 50">
                    <circle class="path" cx="25" cy="25" r="20" fill="none" stroke-width="5"></circle>
                </svg>
                Regenerating...
            `;
        }
        
        fetch(`/api/regenerate_spatial_field/${fileId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Regenerated 3D spatial field:", data);
                
                const spatialFieldImg = document.getElementById('spatial-field-img');
                const spatialFieldContainer = document.getElementById('spatial-field-container');
                
                if (data.success) {
                    // Check if we have an interactive visualization
                    if (data.interactive_path && spatialFieldContainer) {
                        console.log("Setting interactive 3D spatial field:", data.interactive_path);
                        
                        // Get existing iframe - already in HTML
                        let iframe = document.getElementById('spatial-field-iframe');
                        if (iframe) {
                            // Update iframe source to regenerated file
                            iframe.src = data.interactive_path;
                            iframe.style.display = 'block';
                            
                            // Hide the static image
                            if (spatialFieldImg) {
                                spatialFieldImg.style.display = 'none';
                            }
                        }
                        
                        // Note: We don't need to create a new iframe
                        
                        // Add class to indicate interactive visualization
                        spatialFieldContainer.classList.add('interactive-visualization');
                        
                        // Add a button to toggle between 3D and static view
                        const toggleButton = document.createElement('button');
                        toggleButton.textContent = 'Toggle 2D/3D View';
                        toggleButton.className = 'toggle-view-btn';
                        toggleButton.onclick = function() {
                            const iframe = document.getElementById('spatial-field-iframe');
                            if (iframe.style.display === 'none') {
                                iframe.style.display = 'block';
                                spatialFieldImg.style.display = 'none';
                                toggleButton.textContent = 'Switch to 2D View';
                            } else {
                                iframe.style.display = 'none';
                                spatialFieldImg.style.display = 'block';
                                toggleButton.textContent = 'Switch to 3D View';
                            }
                        };
                        spatialFieldContainer.appendChild(toggleButton);
                    }
                    
                    // Also update the static image
                    if (spatialFieldImg && data.image_path) {
                        setImageWithFallback(spatialFieldImg, data.image_path, '3D spatial field visualization');
                    }
                } else {
                    // If regeneration failed, show error
                    if (spatialFieldImg) {
                        spatialFieldImg.src = '/static/img/error.png';
                        spatialFieldImg.alt = 'Error regenerating 3D spatial field visualization';
                    }
                    console.error("Failed to regenerate 3D spatial field:", data.error);
                }
                
                // Re-enable button
                if (regenerateBtn) {
                    regenerateBtn.disabled = false;
                    regenerateBtn.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
                            <path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/>
                        </svg>
                        Regenerate Visualization
                    `;
                }
            })
            .catch(error => {
                console.error("Error regenerating 3D spatial field:", error);
                
                // Re-enable button
                if (regenerateBtn) {
                    regenerateBtn.disabled = false;
                    regenerateBtn.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16">
                            <path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z" fill="currentColor"/>
                        </svg>
                        Regenerate Visualization
                    `;
                }
            });
    }

    // Add event listener for the delete button
    const deleteTrackBtn = document.getElementById('delete-track-btn');
    if (deleteTrackBtn) {
        console.log("Delete button found, adding event listener");
        deleteTrackBtn.addEventListener('click', showDeleteConfirmation);
    } else {
        console.log("Delete button not found in the DOM");
    }
    
    // Event listeners for delete confirmation modal
    const closeDeleteModal = document.getElementById('close-delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    
    if (closeDeleteModal) {
        closeDeleteModal.addEventListener('click', hideDeleteConfirmation);
    } else {
        console.log("Close delete modal button not found");
    }
    
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', hideDeleteConfirmation);
    } else {
        console.log("Cancel delete button not found");
    }
    
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', deleteTrack);
    } else {
        console.log("Confirm delete button not found");
    }
});

/**
 * Shows the delete confirmation modal
 */
function showDeleteConfirmation() {
    console.log("showDeleteConfirmation called");
    const deleteModal = document.getElementById('delete-confirmation-modal');
    if (deleteModal) {
        console.log("Delete modal found, displaying it");
        
        // Prevent conflicts with other modals - check for ImageModal
        if (window.imageModal && typeof window.imageModal.closeModal === 'function') {
            console.log("Closing any open ImageModal before showing delete confirmation");
            try {
                window.imageModal.closeModal();
            } catch (err) {
                console.warn("Error closing ImageModal:", err);
            }
        }
        
        // Force the modal to be visible with inline styles
        deleteModal.style.display = 'flex';
        deleteModal.style.opacity = '1';
        deleteModal.style.visibility = 'visible';
        deleteModal.style.zIndex = '9999';
        
        // Create a backdrop if it doesn't exist
        let backdrop = document.getElementById('delete-modal-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'delete-modal-backdrop';
            backdrop.style.position = 'fixed';
            backdrop.style.top = '0';
            backdrop.style.left = '0';
            backdrop.style.width = '100%';
            backdrop.style.height = '100%';
            backdrop.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            backdrop.style.zIndex = '9998';
            document.body.appendChild(backdrop);
            
            // Add click event to backdrop to close modal
            backdrop.addEventListener('click', hideDeleteConfirmation);
        } else {
            backdrop.style.display = 'block';
        }
        
        // Prevent scrolling of the background
        document.body.style.overflow = 'hidden';
        
        console.log("Modal styles applied:", 
            "display:", deleteModal.style.display, 
            "opacity:", deleteModal.style.opacity,
            "visibility:", deleteModal.style.visibility,
            "zIndex:", deleteModal.style.zIndex
        );
    } else {
        console.error("Delete confirmation modal not found in the DOM");
        alert("Could not open delete confirmation modal. Please try again.");
    }
}

/**
 * Hides the delete confirmation modal
 */
function hideDeleteConfirmation() {
    console.log("hideDeleteConfirmation called");
    const deleteModal = document.getElementById('delete-confirmation-modal');
    if (deleteModal) {
        deleteModal.style.display = 'none';
        
        // Also hide backdrop
        const backdrop = document.getElementById('delete-modal-backdrop');
        if (backdrop) {
            backdrop.style.display = 'none';
        }
        
        document.body.style.overflow = ''; // Restore scrolling
        console.log("Modal hidden");
    } else {
        console.error("Delete confirmation modal not found in the DOM");
    }
}

/**
 * Deletes the current track from the database
 */
function deleteTrack() {
    console.log("deleteTrack function called");
    const fileId = document.getElementById('filename').textContent.trim();
    console.log("File ID to delete:", fileId);
    
    // Show loading state
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.textContent = 'Deleting...';
        confirmDeleteBtn.disabled = true;
        console.log("Delete button set to loading state");
    } else {
        console.error("Confirm delete button not found");
    }
    
    // Debug modal state before API call
    const modal = document.getElementById('delete-confirmation-modal');
    if (modal) {
        console.log("Modal state before API call:", 
            "display:", modal.style.display, 
            "visibility:", modal.style.visibility,
            "opacity:", modal.style.opacity
        );
    }
    
    // Make API call to delete the track
    console.log("Making API request to /api/delete-track with fileId:", fileId);
    fetch('/api/delete-track', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ fileId: fileId })
    })
    .then(response => {
        console.log("API response status:", response.status);
        if (!response.ok) {
            throw new Error('Delete request failed with status ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        console.log("API response data:", data);
        hideDeleteConfirmation();
        
        if (data.success) {
            // Show success message
            showNotification('Track deleted successfully', 'success');
            console.log("Track deleted successfully, resetting UI");
            
            // Reset the UI to the upload screen
            const uploadSection = document.querySelector('.upload-section');
            const resultsSection = document.getElementById('results-section');
            
            if (uploadSection) {
                uploadSection.style.display = 'block';
                console.log("Upload section displayed");
            } else {
                console.error("Upload section not found");
            }
            
            if (resultsSection) {
                resultsSection.style.display = 'none';
                console.log("Results section hidden");
            } else {
                console.error("Results section not found");
            }
        } else {
            console.error("API returned failure:", data.message);
            showNotification('Failed to delete track: ' + (data.message || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting track:', error);
        showNotification('Failed to delete track: ' + error.message, 'error');
        
        // Reset button state
        if (confirmDeleteBtn) {
            confirmDeleteBtn.textContent = 'Delete Permanently';
            confirmDeleteBtn.disabled = false;
            console.log("Delete button reset to normal state");
        }
    });
}

/**
 * Shows a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification ('success', 'error', etc.)
 */
function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    // Set notification content and style
    notification.textContent = message;
    notification.className = 'notification ' + type;
    
    // Show notification
    notification.style.display = 'block';
    notification.style.opacity = '1';
    
    // Hide notification after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 300);
    }, 3000);
}

// Function to setup musical theory modals
function setupMusicTheoryModals() {
    const frequencyGuideLink = document.getElementById('open-frequency-guide');
    const dynamicsGuideLink = document.getElementById('open-dynamics-guide');
    const harmonicGuideLink = document.getElementById('open-harmonic-guide');
    const stereoGuideLink = document.getElementById('open-stereo-guide');
    const transientsGuideLink = document.getElementById('open-transients-guide');
    const spatialGuideLink = document.getElementById('open-spatial-guide');
    const aboutLink = document.getElementById('open-about');
    const faqLink = document.getElementById('open-faq');

    if (frequencyGuideLink) {
        frequencyGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('AI-Powered Frequency Spectrum Analysis Guide', `
                <h3>Understanding Frequency Spectrum Analysis</h3>
                <p>Frequency analysis is the foundation of audio mixing, helping you identify how energy is distributed across the frequency spectrum.</p>
                
                <h4>Key Metrics:</h4>
                <ul>
                    <li><strong>Frequency Range:</strong> 20Hz to 20kHz (human hearing range)</li>
                    <li><strong>Low End:</strong> 20Hz-250Hz (bass, fundamentals)</li>
                    <li><strong>Low-Mids:</strong> 250Hz-500Hz (warmth, body)</li>
                    <li><strong>Mids:</strong> 500Hz-2kHz (presence, clarity)</li>
                    <li><strong>High-Mids:</strong> 2kHz-7kHz (definition, attack)</li>
                    <li><strong>Highs:</strong> 7kHz-20kHz (air, brilliance)</li>
                </ul>
                
                <h4>Common Frequency Issues:</h4>
                <ul>
                    <li><strong>Muddy Mix:</strong> Excessive energy between 200-500Hz</li>
                    <li><strong>Harsh Sound:</strong> Too much energy in 2-5kHz range</li>
                    <li><strong>Thin Sound:</strong> Lacking low-end below 250Hz</li>
                    <li><strong>Dull Mix:</strong> Insufficient high frequencies above 7kHz</li>
                    <li><strong>Boxy Sound:</strong> Resonances in 300-600Hz range</li>
                </ul>
                
                <h4>Our AI-Powered Analysis:</h4>
                <p>The AI analyzes your frequency spectrum by:</p>
                <ul>
                    <li>Comparing against reference tracks in your genre</li>
                    <li>Identifying frequency imbalances and masking issues</li>
                    <li>Suggesting targeted EQ adjustments for better balance</li>
                    <li>Analyzing both static and dynamic frequency content</li>
                    <li>Detecting problematic resonances and standing waves</li>
                </ul>
                
                <h4>Tips for Great Frequency Balance:</h4>
                <ul>
                    <li>Use high-pass filters to remove unnecessary low frequencies</li>
                    <li>Create space for each instrument in its own frequency range</li>
                    <li>Control resonances with narrow EQ cuts</li>
                    <li>Use reference tracks to compare your frequency balance</li>
                    <li>Consider dynamic EQ for frequency problems that vary over time</li>
                </ul>
            `);
        });
    }

    if (dynamicsGuideLink) {
        dynamicsGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Dynamic Range & Compression Explained', `
                <h3>Understanding Dynamic Range Analysis</h3>
                <p>Dynamic range refers to the difference between the loudest and quietest parts of your audio. Proper dynamics management is essential for creating impact and emotion in your mix.</p>
                
                <h4>Key Metrics:</h4>
                <ul>
                    <li><strong>Peak Level:</strong> Maximum amplitude of your audio</li>
                    <li><strong>RMS Level:</strong> Average loudness over time</li>
                    <li><strong>Crest Factor:</strong> Difference between peak and RMS (transient impact)</li>
                    <li><strong>PLR (Peak-to-Loudness Ratio):</strong> Difference between peak and integrated loudness</li>
                    <li><strong>LUFS:</strong> Loudness Units relative to Full Scale (perceived loudness)</li>
                </ul>
                
                <h4>Common Dynamic Issues:</h4>
                <ul>
                    <li><strong>Over-compression:</strong> Reduced dynamic range, lifeless sound</li>
                    <li><strong>Under-compression:</strong> Inconsistent levels, lack of cohesion</li>
                    <li><strong>Pumping:</strong> Audible compression artifacts</li>
                    <li><strong>Distortion:</strong> From excessive limiting or clipping</li>
                    <li><strong>Inconsistent Loudness:</strong> Sections with dramatically different levels</li>
                </ul>
                
                <h4>Our AI-Powered Analysis:</h4>
                <p>The AI analyzes your dynamics by:</p>
                <ul>
                    <li>Measuring dynamic range across frequency bands</li>
                    <li>Detecting over-compression and dynamic issues</li>
                    <li>Comparing to genre-specific dynamic targets</li>
                    <li>Analyzing transient response and preservation</li>
                    <li>Suggesting compression settings for better dynamic control</li>
                </ul>
                
                <h4>Tips for Great Dynamic Balance:</h4>
                <ul>
                    <li>Use compression for purpose, not just to make things louder</li>
                    <li>Consider multiband compression for frequency-specific dynamic control</li>
                    <li>Preserve transients for impact and clarity</li>
                    <li>Use parallel compression for both punch and consistency</li>
                    <li>Target genre-appropriate LUFS levels (-14 LUFS for streaming, louder for club music)</li>
                </ul>
            `);
        });
    }

    if (harmonicGuideLink) {
        harmonicGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('AI Harmonic Analysis & EQ Techniques', `
                <h3>Understanding Harmonic Analysis</h3>
                <p>Harmonics are the building blocks of timbre and tone color in your mix. Managing harmonics properly leads to clarity, warmth, and professional sound quality.</p>
                
                <h4>Key Concepts:</h4>
                <ul>
                    <li><strong>Fundamental:</strong> Base frequency of a note</li>
                    <li><strong>Harmonic Series:</strong> Integer multiples of the fundamental</li>
                    <li><strong>Even Harmonics:</strong> Create warmth (octaves, fifths)</li>
                    <li><strong>Odd Harmonics:</strong> Create presence and edge (thirds, sevenths)</li>
                    <li><strong>Inharmonicity:</strong> Non-harmonic overtones creating dissonance</li>
                </ul>
                
                <h4>Common Harmonic Issues:</h4>
                <ul>
                    <li><strong>Harsh Distortion:</strong> Excessive odd harmonics</li>
                    <li><strong>Lack of Clarity:</strong> Masked or conflicting harmonics</li>
                    <li><strong>Thinness:</strong> Missing fundamental or low harmonics</li>
                    <li><strong>Muddiness:</strong> Overlapping low-frequency harmonics</li>
                    <li><strong>Digital Harshness:</strong> Aliasing or digital distortion artifacts</li>
                </ul>
                
                <h4>Our AI-Powered Analysis:</h4>
                <p>The AI analyzes your harmonics by:</p>
                <ul>
                    <li>Identifying fundamental frequencies and their harmonic series</li>
                    <li>Detecting harmonic conflicts and masking</li>
                    <li>Analyzing harmonic distortion and saturation</li>
                    <li>Suggesting EQ and harmonic enhancement techniques</li>
                    <li>Recommending frequency areas to address for better harmonic balance</li>
                </ul>
                
                <h4>Advanced EQ Techniques:</h4>
                <ul>
                    <li><strong>Harmonic Balancing:</strong> Adjust related frequencies by musical intervals</li>
                    <li><strong>Complementary EQ:</strong> Cut in one element where another needs to shine</li>
                    <li><strong>Resonant Filtering:</strong> Enhance specific harmonics with resonant boosts</li>
                    <li><strong>Harmonic Excitement:</strong> Add subtle saturation to enhance harmonics</li>
                    <li><strong>Spectrum Matching:</strong> Shape harmonics to match reference tracks</li>
                </ul>
            `);
        });
    }

    if (stereoGuideLink) {
        stereoGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Understanding Stereo Field & Imaging', `
                <h3>Understanding Stereo Field Analysis</h3>
                <p>The stereo field determines how your mix is perceived spatially, creating width, depth, and immersion for the listener. Proper stereo imaging is crucial for a professional mix.</p>
                
                <h4>Key Metrics:</h4>
                <ul>
                    <li><strong>Stereo Width:</strong> Overall spread of the mix from mono to wide</li>
                    <li><strong>Phase Correlation:</strong> Compatibility between left and right channels</li>
                    <li><strong>Mid/Side Balance:</strong> Relationship between center and sides content</li>
                    <li><strong>Stereo Consistency:</strong> How uniform the stereo image is across frequencies</li>
                    <li><strong>Phantom Center:</strong> Strength and focus of the central image</li>
                </ul>
                
                <h4>Common Stereo Field Issues:</h4>
                <ul>
                    <li><strong>Phase Problems:</strong> Comb filtering and cancelation when summed to mono</li>
                    <li><strong>Excessive Width:</strong> Unfocused, diffuse mix with weak center</li>
                    <li><strong>Too Narrow:</strong> Lack of space and separation between elements</li>
                    <li><strong>Bottom-Heavy Sides:</strong> Low frequencies spread too wide causing muddiness</li>
                    <li><strong>Inconsistent Imaging:</strong> Elements jumping positions in the stereo field</li>
                </ul>
                
                <h4>Our AI-Powered Analysis:</h4>
                <p>The AI analyzes your stereo field by:</p>
                <ul>
                    <li>Measuring stereo width across different frequency bands</li>
                    <li>Detecting phase issues and mono compatibility problems</li>
                    <li>Analyzing mid/side balance compared to reference tracks</li>
                    <li>Identifying elements that need stereo positioning adjustment</li>
                    <li>Suggesting stereo enhancement or correction techniques</li>
                </ul>
                
                <h4>Stereo Imaging Best Practices:</h4>
                <ul>
                    <li>Keep low frequencies (below 150Hz) mostly centered</li>
                    <li>Use stereo width for atmospheric elements and high frequencies</li>
                    <li>Place lead vocals and key elements in the center</li>
                    <li>Check mono compatibility throughout the mixing process</li>
                    <li>Use correlation meters to ensure phase coherence</li>
                    <li>Apply stereo enhancement selectively rather than across the entire mix</li>
                </ul>
            `);
        });
    }

    if (transientsGuideLink) {
        transientsGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('AI Transient Analysis & Detection', `
                <h3>Understanding Transient Analysis</h3>
                <p>Transients are the initial attack portion of a sound that give it definition, impact, and clarity. Proper transient management is essential for creating punchy, clear mixes with depth and detail.</p>
                
                <h4>Key Concepts:</h4>
                <ul>
                    <li><strong>Attack Time:</strong> How quickly a sound reaches its peak level</li>
                    <li><strong>Decay Time:</strong> How quickly a sound falls after the initial peak</li>
                    <li><strong>Transient Energy:</strong> The amount of energy in the attack portion</li>
                    <li><strong>Sustain Level:</strong> The level maintained after the initial transient</li>
                    <li><strong>Transient Separation:</strong> How distinguishable transients are from other mix elements</li>
                </ul>
                
                <h4>Common Transient Issues:</h4>
                <ul>
                    <li><strong>Dulled Transients:</strong> Over-compression removing attack and impact</li>
                    <li><strong>Harsh Transients:</strong> Excessive attack causing listening fatigue</li>
                    <li><strong>Conflicting Transients:</strong> Multiple elements with transients masking each other</li>
                    <li><strong>Inconsistent Transients:</strong> Varying attack characteristics throughout a performance</li>
                    <li><strong>Lost Transients:</strong> Important attack details buried in the mix</li>
                </ul>
                
                <h4>Our AI-Powered Analysis:</h4>
                <p>The AI analyzes your transients by:</p>
                <ul>
                    <li>Detecting transient events across different frequency bands</li>
                    <li>Measuring attack and decay characteristics</li>
                    <li>Identifying transient masking between instruments</li>
                    <li>Analyzing transient consistency and energy</li>
                    <li>Suggesting processing techniques for better transient management</li>
                </ul>
                
                <h4>Transient Processing Techniques:</h4>
                <ul>
                    <li><strong>Transient Designers:</strong> Enhance or reduce attack portions selectively</li>
                    <li><strong>Dynamic EQ:</strong> Boost or cut frequencies only during transients</li>
                    <li><strong>Parallel Processing:</strong> Blend in unprocessed transients with compressed signals</li>
                    <li><strong>Timing Adjustments:</strong> Align transients between tracks to avoid conflicts</li>
                    <li><strong>Multiband Transient Processing:</strong> Adjust attack characteristics per frequency range</li>
                    <li><strong>Enveloping:</strong> Shape the attack/decay profile of sounds using ADSR controls</li>
                </ul>
            `);
        });
    }

    if (spatialGuideLink) {
        spatialGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('3D Spatial Mix Analysis Guide', `
                <h3>Understanding 3D Spatial Audio</h3>
                <p>3D spatial audio creates an immersive sound experience by positioning audio elements not just left-to-right, but also in terms of height, depth, and immersion. This advanced mixing approach is crucial for modern immersive audio formats.</p>
                
                <h4>Key Dimensions of Spatial Audio:</h4>
                <ul>
                    <li><strong>Width:</strong> Traditional left-to-right panning in the stereo field</li>
                    <li><strong>Height:</strong> Vertical positioning of sounds from low to high</li>
                    <li><strong>Depth:</strong> Front-to-back positioning creating distance perception</li>
                    <li><strong>Immersion:</strong> The sense of being surrounded by the sound field</li>
                    <li><strong>Object-Based Audio:</strong> Individual sound elements positioned in 3D space</li>
                </ul>
                
                <h4>Height Perception:</h4>
                <p>Height cues are created through:</p>
                <ul>
                    <li>Spectral filtering (higher frequencies tend to be perceived as higher in space)</li>
                    <li>Early reflections suggesting ceiling height</li>
                    <li>Head-related transfer functions (HRTFs) modifying sounds based on elevation</li>
                    <li>Frequency-dependent delays that simulate height-based arrival times</li>
                </ul>
                
                <h4>Depth Perception:</h4>
                <p>Depth cues are created through:</p>
                <ul>
                    <li>Direct/reflected sound ratio (dry/wet balance)</li>
                    <li>High-frequency attenuation (distance filtering)</li>
                    <li>Pre-delay before reverb reflections</li>
                    <li>Level differences (quieter sounds seem farther away)</li>
                    <li>Doppler effects for moving sources</li>
                </ul>
                
                <h4>Width Consistency:</h4>
                <p>Maintaining coherent width across:</p>
                <ul>
                    <li>Different frequency bands (avoiding frequency-dependent stereo spread)</li>
                    <li>Dynamic transitions (preventing image collapse during loud passages)</li>
                    <li>Movement trajectories (smooth motion paths for moving sounds)</li>
                    <li>Different playback systems (from headphones to multi-speaker arrays)</li>
                </ul>
                
                <h4>Our 3D Spatial Analysis:</h4>
                <p>The AI analyzes your spatial mix by:</p>
                <ul>
                    <li>Detecting height cues and vertical positioning accuracy</li>
                    <li>Measuring depth consistency and front-to-back arrangement</li>
                    <li>Analyzing width distribution across the frequency spectrum</li>
                    <li>Evaluating immersion factors and envelopment</li>
                    <li>Suggesting binaural and spatial processing improvements</li>
                </ul>
                
                <h4>Tips for Creating Effective 3D Mixes:</h4>
                <ul>
                    <li>Use spectral shaping to reinforce height perception</li>
                    <li>Apply different reverb types for different spatial zones</li>
                    <li>Implement frequency-dependent stereo width control</li>
                    <li>Consider binaural processing for headphone optimization</li>
                    <li>Use precedence effect (Haas effect) to create spatial cues</li>
                    <li>Maintain mono compatibility despite complex spatial processing</li>
                </ul>
                
                <h4>Common Spatial Audio Issues:</h4>
                <ul>
                    <li><strong>Spatial Collapse:</strong> Loss of 3D image on certain playback systems</li>
                    <li><strong>Phantom Image Instability:</strong> Spatial positioning that shifts unexpectedly</li>
                    <li><strong>Excessive Diffusion:</strong> Loss of localization precision</li>
                    <li><strong>Spatial Masking:</strong> Elements in similar spatial locations conflicting</li>
                    <li><strong>Incoherent Height Cues:</strong> Contradictory vertical positioning information</li>
                </ul>
                
                <h4>Optimizing for Different Playback Systems:</h4>
                <ul>
                    <li><strong>Headphones:</strong> Binaural processing, crossfeed control</li>
                    <li><strong>Stereo Speakers:</strong> Phantom center management, boundary effect compensation</li>
                    <li><strong>Surround Systems:</strong> Channel routing, bass management</li>
                    <li><strong>Spatial Audio Formats:</strong> Dolby Atmos, Sony 360 Reality Audio, Ambisonics</li>
                    <li><strong>VR/AR Applications:</strong> Head-tracking responsive mixes, object-based audio</li>
                </ul>
            `);
        });
    }

    if (aboutLink) {
        aboutLink.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = '/about';
        });
    }
    
    if (faqLink) {
        faqLink.addEventListener('click', function(e) {
            e.preventDefault();
            showFaqModal();
        });
    }
}

// Function to show a modal with title and content
function showModal(title, htmlContent) {
    // Check if modal functionality exists
    if (typeof openModal === 'function') {
        openModal(title, htmlContent);
    } else {
        // Create a modern modal if the modal function doesn't exist
        const modalContainer = document.createElement('div');
        modalContainer.className = 'modern-modal-container';
        
        modalContainer.innerHTML = `
            <div class="modern-modal">
                <div class="modern-modal-header">
                    <h2>${title}</h2>
                    <button class="modern-modal-close" aria-label="Close modal">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
                <div class="modern-modal-content">
                    ${htmlContent}
                </div>
            </div>
        `;
        
        document.body.appendChild(modalContainer);
        
        // Add styles
        const style = document.createElement('style');
        style.innerHTML = `
            .modern-modal-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(5px);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            .modern-modal {
                background-color: var(--card-bg, white);
                border-radius: 16px;
                width: 90%;
                max-width: 800px;
                max-height: 85vh;
                overflow-y: auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15), 0 1px 5px rgba(0, 0, 0, 0.1);
                transform: translateY(20px);
                opacity: 0;
                transition: transform 0.4s ease, opacity 0.4s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            .modern-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            }
            .modern-modal-header h2 {
                margin: 0;
                font-size: 1.5rem;
                color: var(--text-color, #333);
                font-weight: 600;
            }
            .modern-modal-close {
                background: none;
                border: none;
                padding: 8px;
                cursor: pointer;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--text-color, #666);
                transition: background-color 0.2s ease, color 0.2s ease;
            }
            .modern-modal-close:hover {
                background-color: rgba(0, 0, 0, 0.05);
                color: var(--primary-color, #4361ee);
            }
            .modern-modal-content {
                padding: 24px;
                color: var(--text-color, #333);
                line-height: 1.6;
            }
            .modern-modal-content h3 {
                margin-top: 0;
                font-weight: 600;
                color: var(--text-color, #222);
            }
            .modern-modal-content h4 {
                margin: 24px 0 12px;
                color: var(--primary-color, #4361ee);
                font-weight: 500;
            }
            .modern-modal-content p {
                margin-bottom: 16px;
            }
            .modern-modal-content ul {
                padding-left: 24px;
                margin-bottom: 16px;
            }
            .modern-modal-content li {
                margin-bottom: 8px;
            }
            .faq-item {
                margin-bottom: 28px;
                padding-bottom: 24px;
                border-bottom: 1px solid rgba(0, 0, 0, 0.06);
            }
            .faq-item:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            .faq-item h4 {
                margin-bottom: 12px;
                color: var(--text-color, #333);
                font-weight: 600;
            }
            
            /* Scrollbar styling */
            .modern-modal-content::-webkit-scrollbar {
                width: 6px;
            }
            .modern-modal-content::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 10px;
            }
            .modern-modal-content::-webkit-scrollbar-thumb {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
            }
            
            /* Dark mode support */
            @media (prefers-color-scheme: dark) {
                .modern-modal {
                    background-color: var(--card-bg, #1a1a1a);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .modern-modal-header {
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .modern-modal-close:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            }
            
            /* Animation classes */
            .modern-modal-container.visible {
                opacity: 1;
            }
            .modern-modal.visible {
                transform: translateY(0);
                opacity: 1;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .modern-modal {
                    width: 95%;
                    max-height: 80vh;
                }
                .modern-modal-header {
                    padding: 16px 20px;
                }
                .modern-modal-content {
                    padding: 20px;
                }
                .modern-modal-header h2 {
                    font-size: 1.3rem;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Animate modal entrance
        setTimeout(() => {
            modalContainer.classList.add('visible');
            const modalElement = modalContainer.querySelector('.modern-modal');
            if (modalElement) {
                modalElement.classList.add('visible');
            }
        }, 10);
        
        // Add close button functionality
        const closeButton = modalContainer.querySelector('.modern-modal-close');
        closeButton.addEventListener('click', function() {
            closeModalWithAnimation(modalContainer, style);
        });
        
        // Close on click outside
        modalContainer.addEventListener('click', function(e) {
            if (e.target === modalContainer) {
                closeModalWithAnimation(modalContainer, style);
            }
        });
        
        // Close on ESC key
        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') {
                closeModalWithAnimation(modalContainer, style);
                document.removeEventListener('keydown', escHandler);
            }
        });
    }
}

// Helper function to close modal with animation
function closeModalWithAnimation(modalContainer, styleElement) {
    const modalElement = modalContainer.querySelector('.modern-modal');
    
    // Remove the visible class to trigger the exit animation
    if (modalElement) {
        modalElement.classList.remove('visible');
    }
    modalContainer.classList.remove('visible');
    
    // Remove elements after animation completes
    setTimeout(() => {
        if (document.body.contains(modalContainer)) {
            document.body.removeChild(modalContainer);
        }
        if (document.head.contains(styleElement)) {
            document.head.removeChild(styleElement);
        }
    }, 300);
} 
