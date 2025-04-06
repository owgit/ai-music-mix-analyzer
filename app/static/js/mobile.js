/**
 * Mobile enhancements for Mix Analyzer
 * Handles touch interactions, swipe gestures, and mobile-specific optimizations
 */
document.addEventListener('DOMContentLoaded', function() {
    // Mobile-specific enhancements
    if (window.innerWidth <= 768) {
        enhanceTouchForUpload();
        enhanceTabsForMobile();
        setupSwipeNavigation();
        // Ensure first tab is activated by default
        activateFirstTab();
    }
    
    // Add resize listener to apply mobile enhancements when resizing to mobile view
    window.addEventListener('resize', function() {
        if (window.innerWidth <= 768) {
            enhanceTouchForUpload();
            enhanceTabsForMobile();
        }
    });
});

// Ensure the first tab is activated by default on mobile
function activateFirstTab() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (tabButtons.length > 0 && tabContents.length > 0) {
        // Clear any active states
        tabButtons.forEach(button => button.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Activate first tab and content
        tabButtons[0].classList.add('active');
        tabContents[0].classList.add('active');
        
        // Scroll to first tab to ensure it's visible
        scrollTabIntoView(tabButtons[0]);
    }
}

// Function to enhance touch feedback and UX for upload section
function enhanceTouchForUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    
    if (!uploadArea || !fileInput) return;
    
    // Add better touch feedback
    uploadArea.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.98)';
        this.style.borderColor = 'var(--primary-color)';
        this.style.backgroundColor = '#f0f4ff';
    }, { passive: true });
    
    uploadArea.addEventListener('touchend', function() {
        this.style.transform = 'scale(1)';
        this.style.borderColor = 'rgba(67, 97, 238, 0.3)';
        this.style.backgroundColor = 'var(--card-bg)';
    }, { passive: true });
    
    // Ensure specific file types work on mobile
    fileInput.addEventListener('click', function(e) {
        // On some mobile browsers, explicit file types need to be clicked specifically
        console.log('File input clicked on mobile device');
    });
    
    // Make upload button more prominent on mobile
    const uploadButton = document.getElementById('upload-button');
    if (uploadButton) {
        uploadButton.style.padding = '15px 20px';
        uploadButton.style.fontSize = '16px';
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

// Function to enhance tab experience for mobile
function enhanceTabsForMobile() {
    const tabsContainer = document.querySelector('.tabs');
    const tabButtons = document.querySelectorAll('.tab-button');
    
    if (!tabsContainer || !tabButtons.length) return;
    
    // Add a tap indicator pulsing animation to the first tab if no tab is active
    const hasActiveTab = Array.from(tabButtons).some(tab => tab.classList.contains('active'));
    if (!hasActiveTab && tabButtons.length > 0) {
        tabButtons[0].classList.add('tap-indicator');
        
        // Remove the indicator once a tab is tapped
        tabsContainer.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('tap-indicator'));
        }, { once: true });
    }
    
    // Improve scroll behavior
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            scrollTabIntoView(button);
        });
    });
    
    // Add visual hint that tabs are swipeable
    addSwipeHint(tabsContainer);
}

// Function to add temporary visual hint for swipeable tabs
function addSwipeHint(tabsContainer) {
    // Check if user has seen the hint before
    if (localStorage.getItem('tabSwipeHintShown')) return;
    
    const hint = document.createElement('div');
    hint.className = 'swipe-hint';
    hint.innerHTML = '<div class="swipe-icon"></div><span>Swipe to see more tabs</span>';
    
    // Style the hint
    Object.assign(hint.style, {
        position: 'absolute',
        top: tabsContainer.offsetTop + tabsContainer.offsetHeight + 'px',
        left: '50%',
        transform: 'translateX(-50%)',
        backgroundColor: 'rgba(67, 97, 238, 0.9)',
        color: 'white',
        padding: '8px 16px',
        borderRadius: '20px',
        zIndex: '1000',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        fontSize: '14px',
        opacity: '0',
        transition: 'opacity 0.3s ease'
    });
    
    // Apply styles to the swipe icon
    const swipeIcon = hint.querySelector('.swipe-icon');
    Object.assign(swipeIcon.style, {
        width: '20px',
        height: '20px',
        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 4h6v6'%3E%3C/path%3E%3Cpath d='M10 20H4v-6'%3E%3C/path%3E%3Cpath d='M20 10L4 10'%3E%3C/path%3E%3C/svg%3E")`,
        backgroundSize: 'contain',
        backgroundRepeat: 'no-repeat',
        marginRight: '8px'
    });
    
    document.body.appendChild(hint);
    
    // Show the hint with animation
    setTimeout(() => {
        hint.style.opacity = '1';
        
        // Hide after 3 seconds
        setTimeout(() => {
            hint.style.opacity = '0';
            setTimeout(() => hint.remove(), 300);
            localStorage.setItem('tabSwipeHintShown', 'true');
        }, 3000);
    }, 1000);
}

// Scroll active tab into view with better positioning
function scrollTabIntoView(activeTab) {
    if (!activeTab) return;
    
    const tabsContainer = document.querySelector('.tabs');
    if (!tabsContainer) return;
    
    // Calculate the center position
    const containerWidth = tabsContainer.offsetWidth;
    const tabWidth = activeTab.offsetWidth;
    const tabLeft = activeTab.offsetLeft;
    
    // Center the tab if possible
    const scrollPosition = tabLeft - (containerWidth / 2) + (tabWidth / 2);
    
    // Smooth scroll to position
    tabsContainer.scrollTo({
        left: Math.max(0, scrollPosition),
        behavior: 'smooth'
    });
}

// Setup swipe navigation between tabs
function setupSwipeNavigation() {
    let startX, startTime;
    const tabContent = document.querySelector('.tab-content');
    const tabButtons = document.querySelectorAll('.tab-button');
    
    if (tabContent && tabButtons.length) {
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

function enhanceAnalysisForMobile() {
    // Get all analysis cards and enhance them
    const analysisCards = document.querySelectorAll('.analysis-card, .ai-section-card, .metrics-container');
    
    analysisCards.forEach(card => {
        // Add tap ripple effect for better feedback
        card.addEventListener('touchstart', function(e) {
            const ripple = document.createElement('div');
            ripple.className = 'tap-ripple';
            
            // Position ripple at tap location
            const rect = this.getBoundingClientRect();
            const x = e.touches[0].clientX - rect.left;
            const y = e.touches[0].clientY - rect.top;
            
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        }, {passive: true});
    });
    
    // Improve scrolling in analysis tabs
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => {
        pane.style.overscrollBehavior = 'contain';
        
        // Add slight padding at bottom for better scroll experience
        pane.style.paddingBottom = '30px';
    });
    
    // Make analysis list items more space-efficient
    const analysisItems = document.querySelectorAll('.analysis-card li, .ai-section-card li');
    analysisItems.forEach(item => {
        item.style.minHeight = '36px';
        item.style.display = 'flex';
        item.style.alignItems = 'flex-start';
        
        // Remove any default bullet points (we handle these with CSS)
        item.style.listStyleType = 'none';
    });
    
    // Optimize headers for better space usage
    const sectionHeaders = document.querySelectorAll('.ai-section-card h4, .analysis-card h3');
    sectionHeaders.forEach(header => {
        header.style.marginTop = '0';
        header.style.marginBottom = '8px';
    });
    
    // Make sure the content spans the full width
    const contentSections = document.querySelectorAll('.ai-frequency-card, .ai-section-card');
    contentSections.forEach(section => {
        section.style.width = '100%';
        section.style.boxSizing = 'border-box';
        section.style.maxWidth = '100%';
    });
} 