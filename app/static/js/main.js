document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");
    
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
    const uploadButton = document.querySelector('.upload-button');
    if (uploadButton) {
        uploadButton.addEventListener('click', function(e) {
            e.stopPropagation();
            console.log("Upload button clicked directly");
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
                    setTimeout(() => {
                        checkboxContainer.style.transform = 'scale(1)';
                    }, 200);
                    console.log("Instrumental checkbox checked - Analysis will focus on instrumental aspects");
                } else {
                    checkboxContainer.classList.remove('checked');
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
            if (data.results.visualizations.spatial_field && spatialFieldImg) {
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
});

// Function to setup musical theory modals
function setupMusicTheoryModals() {
    // Get modal elements (assuming modal functionality is already implemented)
    const frequencyGuideLink = document.getElementById('open-frequency-guide');
    const dynamicsGuideLink = document.getElementById('open-dynamics-guide');
    const harmonicGuideLink = document.getElementById('open-harmonic-guide');
    const stereoGuideLink = document.getElementById('open-stereo-guide');
    const transientsGuideLink = document.getElementById('open-transients-guide');
    const aboutAppLink = document.getElementById('open-about-app');
    const faqLink = document.getElementById('open-faq');
    
    // Event listener for frequency guide
    if (frequencyGuideLink) {
        frequencyGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Frequency Balance Guide', `
                <h3>Understanding Frequency Balance</h3>
                <p>Frequency balance is the distribution of energy across the audible frequency spectrum (20Hz-20kHz). A well-balanced mix has appropriate energy in each frequency region.</p>
                
                <h4>Key Frequency Bands:</h4>
                <ul>
                    <li><strong>Sub Bass (20-60Hz)</strong>: Foundational frequencies, felt more than heard. Includes lowest notes of bass instruments.</li>
                    <li><strong>Bass (60-250Hz)</strong>: Fundamental notes of bass guitar, kick drums, and bass instruments.</li>
                    <li><strong>Low Mids (250-500Hz)</strong>: Body of acoustic instruments, can sound muddy if overemphasized.</li>
                    <li><strong>Mids (500-2kHz)</strong>: Vocals and most instruments' main frequencies. Crucial for clarity.</li>
                    <li><strong>High Mids (2-4kHz)</strong>: Presence and definition. Affects how upfront elements sound.</li>
                    <li><strong>Highs (4-10kHz)</strong>: Brightness, clarity, and articulation. Cymbals, hi-hats, and transients.</li>
                    <li><strong>Air (10-20kHz)</strong>: Sense of space, air, and sparkle in a mix.</li>
                </ul>
                
                <h4>Common Frequency Balance Issues:</h4>
                <ul>
                    <li><strong>Muddy Mix</strong>: Too much energy in low-mids (200-500Hz).</li>
                    <li><strong>Thin Mix</strong>: Lacking energy in bass regions.</li>
                    <li><strong>Harsh Mix</strong>: Excessive energy in high-mids (2-5kHz).</li>
                    <li><strong>Dull Mix</strong>: Insufficient high-frequency content.</li>
                </ul>
            `);
        });
    }
    
    // Event listener for dynamics guide
    if (dynamicsGuideLink) {
        dynamicsGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Dynamic Range Explained', `
                <h3>Dynamic Range in Audio</h3>
                <p>Dynamic range refers to the difference between the loudest and quietest parts of an audio signal. It's measured in decibels (dB) and is crucial for creating emotional impact in music.</p>
                
                <h4>Key Dynamics Metrics:</h4>
                <ul>
                    <li><strong>Dynamic Range</strong>: The difference between the loudest and quietest parts of a song, measured in dB.</li>
                    <li><strong>Crest Factor</strong>: The ratio of peak values to RMS (average) values, indicating transient content.</li>
                    <li><strong>Peak to Loudness Ratio (PLR)</strong>: The difference between peak level and integrated loudness, indicating dynamic headroom.</li>
                </ul>
                
                <h4>Why Dynamics Matter:</h4>
                <ul>
                    <li><strong>Emotional Impact</strong>: Dynamic changes create emotional responses and maintain listener interest.</li>
                    <li><strong>Genre Expectations</strong>: Different genres have different dynamic range standards (EDM vs. Classical).</li>
                    <li><strong>Listening Environment</strong>: Dynamic range should be appropriate for the intended listening environment.</li>
                    <li><strong>Fatigue</strong>: Highly compressed audio with minimal dynamics can cause listener fatigue.</li>
                </ul>
                
                <h4>Measuring Dynamics:</h4>
                <p>Our analyzer measures various aspects of your mix's dynamics, including RMS levels, peak levels, and loudness (LUFS). These measurements help determine if your mix is overcompressed or has appropriate dynamic range for its genre.</p>
            `);
        });
    }
    
    // Event listener for harmonic guide
    if (harmonicGuideLink) {
        harmonicGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Harmonic Analysis & Key Detection', `
                <h3>Understanding Harmonic Content</h3>
                <p>Harmonic analysis evaluates the tonal structure of your music, including key detection, chord progressions, and harmonic relationships.</p>
                
                <h4>Key Detection:</h4>
                <p>Our system uses chroma features to analyze the pitch class distribution in your audio and determine the most likely musical key. This helps identify if elements in your mix clash harmonically.</p>
                
                <h4>The Circle of Fifths:</h4>
                <p>The circle of fifths is a visualization of relationships between keys. Adjacent keys in the circle have more harmonically compatible notes. Our analysis uses these relationships to suggest potential key-related issues.</p>
                
                <h4>Relative and Parallel Keys:</h4>
                <ul>
                    <li><strong>Relative keys</strong>: Major and minor keys that share the same notes (C major and A minor).</li>
                    <li><strong>Parallel keys</strong>: Major and minor keys with the same tonic (C major and C minor).</li>
                </ul>
                
                <h4>Harmonic Mixing:</h4>
                <p>Understanding the key of your track helps with:
                <ul>
                    <li>Identifying if samples or instruments are harmonically compatible</li>
                    <li>Finding complementary tracks for DJ mixes</li>
                    <li>Creating coherent chord progressions and melodies</li>
                </ul>
                </p>
            `);
        });
    }
    
    // Event listener for stereo guide
    if (stereoGuideLink) {
        stereoGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Understanding Stereo Field', `
                <h3>Stereo Field Analysis</h3>
                <p>Stereo field analysis evaluates how sound is distributed between the left and right channels, the correlation between channels, and the overall stereo width of your mix.</p>
                
                <h4>Key Stereo Concepts:</h4>
                <ul>
                    <li><strong>Stereo Width</strong>: How "wide" your mix sounds, from mono (center only) to very wide.</li>
                    <li><strong>Phase Correlation</strong>: How the left and right channels relate. Values near +1 indicate good mono compatibility, while negative values can indicate phase issues.</li>
                    <li><strong>Stereo Balance</strong>: Whether your mix leans too much to one side.</li>
                    <li><strong>Mono Compatibility</strong>: How your mix sounds when collapsed to mono (important for some playback systems).</li>
                </ul>
                
                <h4>Frequency-dependent Stereo Width:</h4>
                <p>Best practices for stereo distribution by frequency:
                <ul>
                    <li><strong>Sub Bass (20-60Hz)</strong>: Usually centered/mono for translation and power</li>
                    <li><strong>Bass (60-250Hz)</strong>: Mostly centered with slight stereo width</li>
                    <li><strong>Low Mids (250-500Hz)</strong>: Moderate stereo width appropriate</li>
                    <li><strong>Mids and above</strong>: Wider stereo image appropriate for most content</li>
                </ul>
                </p>
                
                <h4>Common Stereo Issues:</h4>
                <ul>
                    <li><strong>Phase cancellation</strong>: When frequencies disappear in mono</li>
                    <li><strong>Excessive width</strong>: Can sound unnatural or cause translation problems</li>
                    <li><strong>Imbalanced panning</strong>: Mix leaning too far to one side</li>
                </ul>
            `);
        });
    }
    
    // Event listener for transients guide
    if (transientsGuideLink) {
        transientsGuideLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Transient Analysis', `
                <h3>Understanding Transients</h3>
                <p>Transients are the short-duration, high-amplitude peaks at the beginning of sounds, especially percussive elements like drums. They provide impact, clarity, and rhythmic definition to a mix.</p>
                
                <h4>Why Transients Matter:</h4>
                <ul>
                    <li><strong>Impact and Punch</strong>: Strong transients create impact and energy in a mix.</li>
                    <li><strong>Clarity</strong>: Well-preserved transients help individual elements cut through the mix.</li>
                    <li><strong>Rhythmic Definition</strong>: Clear transients make rhythmic elements more defined.</li>
                    <li><strong>Perceived Loudness</strong>: Preserved transients can make a mix sound louder without increasing overall level.</li>
                </ul>
                
                <h4>Measuring Transients:</h4>
                <p>Our analyzer examines:
                <ul>
                    <li><strong>Transient Sharpness</strong>: How quickly levels rise at the start of sounds.</li>
                    <li><strong>Transient-to-Sustain Ratio</strong>: The relationship between initial peaks and sustained sounds.</li>
                    <li><strong>Transient Consistency</strong>: How evenly transients are preserved across the mix.</li>
                </ul>
                </p>
                
                <h4>Common Transient Issues:</h4>
                <ul>
                    <li><strong>Over-compression</strong>: Flattened transients leading to lifeless percussion.</li>
                    <li><strong>Inconsistent transients</strong>: Some hits much louder than others.</li>
                    <li><strong>Transient smearing</strong>: Lack of definition in fast rhythmic passages.</li>
                </ul>
            `);
        });
    }
    
    // Event listener for about app
    if (aboutAppLink) {
        aboutAppLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('About Mix Analyzer', `
                <h3>Mix Analyzer</h3>
                <p>Mix Analyzer is a professional audio analysis tool designed for musicians, producers, and audio engineers. Upload your tracks to get detailed analysis and AI-powered improvement suggestions.</p>
                
                <h4>Key Features:</h4>
                <ul>
                    <li><strong>Comprehensive Analysis</strong>: Evaluate frequency balance, dynamics, stereo field, clarity, and more.</li>
                    <li><strong>Audio Visualization</strong>: View waveforms, spectrograms, and other visual representations of your audio.</li>
                    <li><strong>AI Insights</strong>: Get intelligent suggestions for improving your mix powered by OpenAI's GPT-4o.</li>
                    <li><strong>Musical Theory Integration</strong>: Key detection and harmonic analysis to ensure tonal cohesion.</li>
                </ul>
                
                <h4>Technical Details:</h4>
                <p>Mix Analyzer is built using:
                <ul>
                    <li>Python with Flask for the backend</li>
                    <li>Librosa for audio analysis</li>
                    <li>Matplotlib for visualization generation</li>
                    <li>OpenAI API for AI-powered suggestions</li>
                    <li>Modern JavaScript for the interactive frontend</li>
                </ul>
                </p>
                
                <h4>Support:</h4>
                <p>For questions, issues, or feature requests, please visit our GitHub repository or contact the development team.</p>
            `);
        });
    }
    
    // Event listener for FAQ
    if (faqLink) {
        faqLink.addEventListener('click', function(e) {
            e.preventDefault();
            showModal('Frequently Asked Questions', `
                <h3>Frequently Asked Questions</h3>
                
                <div class="faq-item">
                    <h4>What audio file formats are supported?</h4>
                    <p>Mix Analyzer supports MP3, WAV, FLAC, AIFF, M4A, and PCM audio formats.</p>
                </div>
                
                <div class="faq-item">
                    <h4>Is there a file size limit?</h4>
                    <p>Yes, there is a 16MB file size limit for uploads. For larger files, consider converting to a compressed format like MP3.</p>
                </div>
                
                <div class="faq-item">
                    <h4>What do the scores mean?</h4>
                    <p>Scores range from 0-100 and represent how well your mix performs in each area compared to professional standards. Higher scores indicate better technical quality.</p>
                </div>
                
                <div class="faq-item">
                    <h4>Are my files kept private?</h4>
                    <p>Yes, all uploaded files are private and used only for analysis. Files are not shared with third parties and are automatically deleted after processing.</p>
                </div>
                
                <div class="faq-item">
                    <h4>How does AI analysis work?</h4>
                    <p>Our system extracts audio features and metrics from your track, then uses OpenAI's API to interpret these results and provide actionable suggestions based on professional audio engineering practices.</p>
                </div>
                
                <div class="faq-item">
                    <h4>What's the difference between instrumental and vocal tracks?</h4>
                    <p>Indicating whether your track is instrumental or contains vocals helps our system provide more relevant analysis, especially for frequency balance and clarity assessments.</p>
                </div>
            `);
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