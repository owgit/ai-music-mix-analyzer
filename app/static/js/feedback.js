/**
 * Feedback Modal and Form Handling
 */
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const openFeedbackBtn = document.getElementById('open-feedback-btn');
    const feedbackModal = document.getElementById('feedback-modal');
    const closeFeedbackModal = document.getElementById('close-feedback-modal');
    const feedbackForm = document.getElementById('feedback-form');
    const feedbackStatus = document.getElementById('feedback-status');
    
    // Open the feedback modal
    if (openFeedbackBtn) {
        openFeedbackBtn.addEventListener('click', function() {
            feedbackModal.classList.add('active');
            resetForm();
        });
    }
    
    // Close the feedback modal
    if (closeFeedbackModal) {
        closeFeedbackModal.addEventListener('click', function() {
            feedbackModal.classList.remove('active');
        });
        
        // Also close when clicking on the overlay
        feedbackModal.addEventListener('click', function(e) {
            if (e.target === feedbackModal) {
                feedbackModal.classList.remove('active');
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && feedbackModal.classList.contains('active')) {
                feedbackModal.classList.remove('active');
            }
        });
    }
    
    // Handle form submission
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
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
                consent: document.getElementById('feedback-consent').checked
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
                    // Show success message
                    feedbackStatus.textContent = 'Thank you for your feedback!';
                    feedbackStatus.className = 'feedback-status success';
                    
                    // Clear form
                    resetForm();
                    
                    // Close modal after delay
                    setTimeout(() => {
                        feedbackModal.classList.remove('active');
                    }, 2000);
                } else {
                    // Show error message
                    feedbackStatus.textContent = data.error || 'An error occurred. Please try again.';
                    feedbackStatus.className = 'feedback-status error';
                }
            })
            .catch(error => {
                console.error('Error submitting feedback:', error);
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
                feedbackStatus.textContent = 'Network error. Please try again later.';
                feedbackStatus.className = 'feedback-status error';
            });
        });
    }
    
    // Reset the form to its initial state
    function resetForm() {
        if (feedbackForm) {
            feedbackForm.reset();
            feedbackStatus.textContent = '';
            feedbackStatus.className = 'feedback-status';
        }
    }
    
    // Initialize star rating behavior
    initStarRating();
    
    // Function to initialize star rating interaction
    function initStarRating() {
        const stars = document.querySelectorAll('.star-rating input');
        
        stars.forEach(star => {
            star.addEventListener('change', function() {
                // Add visual feedback when a star is selected
                const starContainer = this.closest('.star-rating');
                const starValue = this.value;
                
                // Optional: add some visual feedback
                starContainer.setAttribute('data-rating', starValue);
            });
        });
    }
}); 