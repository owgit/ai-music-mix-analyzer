/**
 * Mobile enhancements for Mix Analyzer
 * Handles touch interactions, swipe gestures, and mobile-specific optimizations
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a mobile device
    const isMobile = window.matchMedia('(max-width: 768px)').matches;
    
    if (isMobile) {
        initMobileEnhancements();
    }
    
    // Listen for window resize to apply or remove mobile enhancements
    window.addEventListener('resize', function() {
        const nowMobile = window.matchMedia('(max-width: 768px)').matches;
        if (nowMobile && !isMobile) {
            initMobileEnhancements();
        }
    });
    
    function initMobileEnhancements() {
        console.log('Initializing mobile enhancements');
        
        // Enhance tab navigation for mobile
        enhanceTabsForMobile();
        
        // Add touch support for upload area
        enhanceTouchForUpload();
        
        // Optimize visualizations for touch devices
        enhanceVisualizationsForTouch();
        
        // Add visual feedback for touch interactions
        addTouchFeedback();
    }
    
    function enhanceTabsForMobile() {
        const tabsContainer = document.querySelector('.tabs');
        const tabButtons = document.querySelectorAll('.tab-button');
        
        if (!tabsContainer || !tabButtons.length) return;
        
        // Scroll active tab into view
        function scrollActiveTabIntoView() {
            const activeTab = document.querySelector('.tab-button.active');
            if (activeTab) {
                // Calculate the scroll position to center the active tab
                const containerWidth = tabsContainer.offsetWidth;
                const tabWidth = activeTab.offsetWidth;
                const tabLeft = activeTab.offsetLeft;
                
                const scrollPosition = tabLeft - (containerWidth / 2) + (tabWidth / 2);
                tabsContainer.scrollTo({
                    left: scrollPosition,
                    behavior: 'smooth'
                });
            }
        }
        
        // Call this when a tab is clicked
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Wait a bit for the active class to be applied
                setTimeout(scrollActiveTabIntoView, 10);
            });
        });
        
        // Initial scroll to active tab
        setTimeout(scrollActiveTabIntoView, 100);
        
        // Add tab swipe navigation
        let startX, startTime;
        const tabContent = document.querySelector('.tab-content');
        
        if (tabContent) {
            tabContent.addEventListener('touchstart', function(e) {
                startX = e.touches[0].clientX;
                startTime = Date.now();
            }, { passive: true });
            
            tabContent.addEventListener('touchend', function(e) {
                if (!startX) return;
                
                const endX = e.changedTouches[0].clientX;
                const deltaX = endX - startX;
                const deltaTime = Date.now() - startTime;
                
                // Check if it's a valid swipe (fast enough and long enough)
                if (deltaTime < 250 && Math.abs(deltaX) > 50) {
                    const activeTab = document.querySelector('.tab-button.active');
                    if (activeTab) {
                        const index = Array.from(tabButtons).indexOf(activeTab);
                        
                        if (deltaX > 0 && index > 0) {
                            // Swipe right, go to previous tab
                            tabButtons[index - 1].click();
                        } else if (deltaX < 0 && index < tabButtons.length - 1) {
                            // Swipe left, go to next tab
                            tabButtons[index + 1].click();
                        }
                    }
                }
                
                startX = null;
            }, { passive: true });
        }
    }
    
    function enhanceTouchForUpload() {
        const uploadArea = document.getElementById('upload-area');
        const fileInput = document.getElementById('file-input');
        const uploadButton = document.getElementById('upload-button');
        
        if (!uploadArea) return;
        
        // Add better touch feedback
        uploadArea.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.borderColor = 'var(--primary-color)';
            this.style.backgroundColor = '#f0f4ff';
        }, { passive: true });
        
        uploadArea.addEventListener('touchend', function(e) {
            this.style.transform = 'scale(1)';
            this.style.borderColor = 'rgba(67, 97, 238, 0.3)';
            this.style.backgroundColor = 'var(--card-bg)';
            
            // Critical fix: Trigger file selection on touchend
            if (fileInput) {
                fileInput.click();
            }
        }, { passive: true });
        
        // Make sure the upload button works correctly on mobile
        if (uploadButton) {
            uploadButton.addEventListener('touchend', function(e) {
                e.stopPropagation(); // Prevent double triggering
                
                if (fileInput) {
                    fileInput.click();
                }
            }, { passive: false });
        }
        
        // Make keyboard accessible
        uploadArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                if (fileInput) {
                    fileInput.click();
                }
            }
        });
    }
    
    function enhanceVisualizationsForTouch() {
        const visualizationContainers = document.querySelectorAll('.visualization-container');
        
        visualizationContainers.forEach(container => {
            // Add tap indicator for images
            container.addEventListener('touchstart', function() {
                this.classList.add('touched');
            }, { passive: true });
            
            container.addEventListener('touchend', function() {
                this.classList.remove('touched');
            }, { passive: true });
        });
    }
    
    function addTouchFeedback() {
        // Add touch feedback to all interactive elements
        const interactiveElements = document.querySelectorAll('button, .upload-button, .tab-button, .regenerate-btn');
        
        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', function() {
                this.classList.add('touch-active');
            }, { passive: true });
            
            element.addEventListener('touchend', function() {
                this.classList.remove('touch-active');
                
                // Small delay to show feedback before action
                setTimeout(() => {
                    this.blur();
                }, 150);
            }, { passive: true });
        });
    }
}); 