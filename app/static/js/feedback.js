/**
 * Enhanced Feedback Modal and Form Handling
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const openFeedbackBtn = document.getElementById('open-feedback-btn');
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackStatus = document.getElementById('feedback-status');
    
    // Create floating feedback button for mobile
    createFloatingFeedbackButton();
    
    // Add beta tag to feedback button
    addBetaTag();
    
    // Open the feedback modal
    const openFeedbackModal = () => {
        feedbackModal.classList.add('active');
        resetForm();
        
        // Track modal open in analytics if available
        if (window._paq) {
            _paq.push(['trackEvent', 'Feedback', 'Open Modal', 'Beta Feedback']);
        }
    };
    
    if (openFeedbackBtn) {
        openFeedbackBtn.addEventListener('click', openFeedbackModal);
    }
    
    // Close the feedback modal
    const closeFeedbackModalFn = (e) => {
        if (e) {
            e.preventDefault();
        }
        feedbackModal.classList.remove('active');
        
        // Track modal close in analytics if available
        if (window._paq) {
            _paq.push(['trackEvent', 'Feedback', 'Close Modal', 'Beta Feedback']);
        }
    };
    
    if (closeFeedbackModal) {
        closeFeedbackModal.addEventListener('click', closeFeedbackModalFn);
        
        // Also close when clicking on the overlay
        feedbackModal.addEventListener('click', function(e) {
            if (e.target === feedbackModal) {
                closeFeedbackModalFn();
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && feedbackModal.classList.contains('active')) {
                closeFeedbackModalFn();
            }
        });
    }
    
    // Create or locate success animation container
    let successAnimation = feedbackModal.querySelector('.feedback-success-animation');
    if (!successAnimation) {
        successAnimation = document.createElement('div');
        successAnimation.className = 'feedback-success-animation';
        successAnimation.innerHTML = `
            <div class="checkmark-circle">
                <div class="checkmark"></div>
            </div>
            <span class="checkmark-text">Thank you for your feedback!</span>
        `;
        feedbackModal.querySelector('.feedback-modal-content').appendChild(successAnimation);
    }
    
    // Form validation
    const validateForm = () => {
        const rating = document.querySelector('input[name="rating"]:checked');
        const feedbackType = document.getElementById('feedback-type');
        const message = document.getElementById('feedback-message');
        const consent = document.getElementById('feedback-consent');
        
        let isValid = true;
        let errorMessage = '';
        
        // Reset previous error states
        [feedbackType, message].forEach(el => {
            if (el) el.classList.remove('error');
        });
        
        // Check required fields
        if (!rating) {
            isValid = false;
            errorMessage = 'Please provide a rating.';
        } else if (feedbackType && feedbackType.value === "") {
            isValid = false;
            errorMessage = 'Please select a feedback type.';
            feedbackType.classList.add('error');
        } else if (message && message.value.trim() === "") {
            isValid = false;
            errorMessage = 'Please enter your feedback message.';
            message.classList.add('error');
        } else if (consent && !consent.checked) {
            isValid = false;
            errorMessage = 'Please consent to having your feedback stored.';
        }
        
        if (!isValid && errorMessage) {
            feedbackStatus.textContent = errorMessage;
            feedbackStatus.className = 'feedback-status error';
        }
        
        return isValid;
    };
    
    // Handle form submission
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (!validateForm()) {
                return;
            }
            
            // Show loading state
            const submitBtn = document.getElementById('submit-feedback');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Submitting...';
            submitBtn.disabled = true;
            
            feedbackStatus.textContent = '';
            feedbackStatus.className = 'feedback-status';
            
            // Get form data
            const formData = {
                email: document.getElementById('feedback-email').value,
                rating: document.querySelector('input[name="rating"]:checked').value,
                feedback_type: document.getElementById('feedback-type').value,
                message: document.getElementById('feedback-message').value,
                consent: document.getElementById('feedback-consent').checked,
                url: window.location.href,
                user_agent: navigator.userAgent,
                timestamp: new Date().toISOString()
            };
            
            // Submit the feedback
            fetch('/api/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                // Reset button state
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    // Hide the form
                    feedbackForm.style.display = 'none';
                    
                    // Show success animation
                    successAnimation.classList.add('active');
                    
                    // Track successful submission in analytics if available
                    if (window._paq) {
                        _paq.push(['trackEvent', 'Feedback', 'Submit Success', formData.feedback_type, parseInt(formData.rating)]);
                    }
                    
                    // Close modal after delay
                    setTimeout(() => {
                        closeFeedbackModalFn();
                        // Reset for next time after a short delay
                        setTimeout(() => {
                            resetForm();
                            feedbackForm.style.display = 'block';
                            successAnimation.classList.remove('active');
                        }, 300);
                    }, 3000);
                } else {
                    // Show error message
                    feedbackStatus.textContent = data.error || 'An error occurred. Please try again.';
                    feedbackStatus.className = 'feedback-status error';
                    
                    // Track error in analytics if available
                    if (window._paq) {
                        _paq.push(['trackEvent', 'Feedback', 'Submit Error', data.error || 'Unknown error']);
                    }
                }
            })
            .catch(error => {
                console.error('Error submitting feedback:', error);
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
                feedbackStatus.textContent = 'Network error. Please try again later.';
                feedbackStatus.className = 'feedback-status error';
                
                // Track network error in analytics if available
                if (window._paq) {
                    _paq.push(['trackEvent', 'Feedback', 'Network Error', error.toString().substring(0, 100)]);
                }
            });
        });
    }
    
    // Reset the form to its initial state
    function resetForm() {
        if (feedbackForm) {
            feedbackForm.reset();
            feedbackStatus.textContent = '';
            feedbackStatus.className = 'feedback-status';
            
            // Reset any error states
            const formElements = feedbackForm.querySelectorAll('input, select, textarea');
            formElements.forEach(el => {
                el.classList.remove('error');
            });
        }
    }
    
    // Initialize star rating behavior with enhanced animation
    initStarRating();
    
    // Function to initialize star rating interaction
    function initStarRating() {
        const stars = document.querySelectorAll('.star-rating input');
        const starLabels = document.querySelectorAll('.star-rating label');
        
        // Add hover animation class
        starLabels.forEach(label => {
            label.addEventListener('mouseover', function() {
                this.classList.add('hover');
            });
            
            label.addEventListener('mouseout', function() {
                this.classList.remove('hover');
            });
        });
        
        stars.forEach(star => {
            star.addEventListener('change', function() {
                // Add visual feedback when a star is selected
                const starContainer = this.closest('.star-rating');
                const starValue = this.value;
                
                // Visual feedback
                starContainer.setAttribute('data-rating', starValue);
                
                // Label animation for the selected rating
                starLabels.forEach(label => {
                    label.classList.remove('selected');
                });
                
                // Get all labels for stars up to the selected rating
                const selectedLabels = Array.from(starLabels).filter((label, index) => 
                    (5 - index) <= parseInt(starValue)
                );
                
                // Add selected class with delay for animation effect
                selectedLabels.forEach((label, index) => {
                    setTimeout(() => {
                        label.classList.add('selected');
                    }, index * 50);
                });
                
                // Track rating selection in analytics if available
                if (window._paq) {
                    _paq.push(['trackEvent', 'Feedback', 'Rating Selected', 'Stars', parseInt(starValue)]);
                }
            });
        });
    }
    
    // Create floating feedback button for mobile
    function createFloatingFeedbackButton() {
        // Check if button already exists
        if (document.querySelector('.floating-feedback-button')) {
            return;
        }
        
        const floatingBtn = document.createElement('div');
        floatingBtn.className = 'floating-feedback-button';
        floatingBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 12h-2v-2h2v2zm0-4h-2V6h2v4z"/></svg>`;
        document.body.appendChild(floatingBtn);
        
        // Show the button only on mobile
        if (window.innerWidth <= 768) {
            setTimeout(() => {
                floatingBtn.classList.add('visible');
            }, 2000);
        }
        
        // Handle click to open feedback modal
        floatingBtn.addEventListener('click', openFeedbackModal);
        
        // Update visibility on resize
        window.addEventListener('resize', debounce(function() {
            if (window.innerWidth <= 768) {
                floatingBtn.classList.add('visible');
            } else {
                floatingBtn.classList.remove('visible');
            }
        }, 250));
    }
    
    // Add beta tag to feedback button
    function addBetaTag() {
        const feedbackButton = document.getElementById('open-feedback-btn');
        if (feedbackButton && !feedbackButton.querySelector('.beta-tag')) {
            const betaTag = document.createElement('span');
            betaTag.className = 'beta-tag';
            betaTag.textContent = 'Beta';
            feedbackButton.appendChild(betaTag);
            
            // Add pulse indicator
            const pulse = document.createElement('span');
            pulse.className = 'feedback-button-pulse';
            feedbackButton.appendChild(pulse);
        }
    }
    
    // Utility function to debounce events
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }
}); 