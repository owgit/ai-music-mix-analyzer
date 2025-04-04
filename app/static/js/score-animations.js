/**
 * Enhanced Score Animations
 * Provides interactive and engaging visual effects for the score display
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const scoreCircle = document.querySelector('.score-circle');
    const scoreValue = document.getElementById('overall-score');
    const scoreParticles = document.querySelector('.score-particles');
    const scoreMarks = document.querySelector('.score-circle-marks');
    
    // Variables
    let currentScore = 0;
    let targetScore = 0;
    let animationFrameId = null;
    
    // Create progress marks around the circle
    function createProgressMarks() {
        // Create 20 marks around the circle
        for (let i = 0; i < 20; i++) {
            const mark = document.createElement('div');
            mark.classList.add('progress-mark');
            mark.style.position = 'absolute';
            mark.style.width = '2px';
            mark.style.height = '8px';
            mark.style.backgroundColor = 'rgba(67, 97, 238, 0.3)';
            mark.style.transform = `rotate(${i * 18}deg) translateY(-75px)`;
            mark.style.transformOrigin = 'center 75px';
            mark.style.opacity = '0.7';
            mark.style.transition = 'all 0.3s ease';
            scoreMarks.appendChild(mark);
        }
    }
    
    // Update the circular progress based on score
    function updateProgressCircle(score) {
        // Update the circle gradient based on score percentage
        const percentage = score * 3.6; // Convert score to degrees (0-100 to 0-360)
        scoreCircle.style.background = `conic-gradient(
            var(--primary-color) 0%, 
            var(--primary-color) ${percentage}deg, 
            #e9ecef ${percentage}deg, 
            #e9ecef 360deg
        )`;
        
        // Update mark colors based on progress
        const marks = scoreMarks.querySelectorAll('.progress-mark');
        marks.forEach((mark, index) => {
            const markDegree = index * 18;
            if (markDegree <= percentage) {
                mark.style.backgroundColor = 'var(--primary-color)';
                mark.style.boxShadow = '0 0 5px var(--primary-color)';
                mark.style.height = '10px';
            } else {
                mark.style.backgroundColor = 'rgba(67, 97, 238, 0.3)';
                mark.style.boxShadow = 'none';
                mark.style.height = '8px';
            }
        });
    }
    
    // Create particle effect
    function createParticles() {
        // Clear existing particles
        scoreParticles.innerHTML = '';
        
        // Create new particles
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            
            // Random position, size, and direction
            const size = Math.random() * 6 + 2;
            const startAngle = Math.random() * Math.PI * 2;
            const startX = Math.cos(startAngle) * 50;
            const startY = Math.sin(startAngle) * 50;
            
            // Set particle properties
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `calc(50% + ${startX}px)`;
            particle.style.top = `calc(50% + ${startY}px)`;
            
            // Random direction away from center
            const tx = startX * (Math.random() * 2 + 2);
            const ty = startY * (Math.random() * 2 + 2);
            particle.style.setProperty('--tx', `${tx}px`);
            particle.style.setProperty('--ty', `${ty}px`);
            
            // Animation
            particle.style.animation = `particleFade ${Math.random() * 1 + 0.5}s ease-out forwards`;
            particle.style.animationDelay = `${Math.random() * 0.3}s`;
            
            scoreParticles.appendChild(particle);
        }
    }
    
    // Animate score change
    function animateScoreChange(newScore) {
        // Cancel any previous animation
        if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
        }
        
        targetScore = parseInt(newScore);
        currentScore = parseInt(scoreValue.textContent);
        
        // If no change or initial load with zero
        if (currentScore === targetScore) {
            updateProgressCircle(targetScore);
            return;
        }
        
        // Apply animation class for visual effect
        scoreValue.classList.add('score-updated');
        scoreCircle.classList.add('score-achieved');
        
        // Create particle effect if score improved
        if (targetScore > currentScore) {
            createParticles();
        }
        
        // Animate the score change
        const animate = () => {
            // Calculate step size based on difference
            const diff = targetScore - currentScore;
            const step = Math.max(1, Math.abs(Math.floor(diff / 10)));
            
            if (Math.abs(diff) <= step) {
                // Last step
                currentScore = targetScore;
                scoreValue.textContent = targetScore;
                updateProgressCircle(targetScore);
                return;
            }
            
            // Increment or decrement
            currentScore += diff > 0 ? step : -step;
            scoreValue.textContent = currentScore;
            updateProgressCircle(currentScore);
            
            // Continue animation
            animationFrameId = requestAnimationFrame(animate);
        };
        
        // Start animation
        animate();
    }
    
    // Interactive events
    function setupInteractions() {
        // Shine effect on click
        scoreCircle.addEventListener('click', () => {
            scoreCircle.style.boxShadow = '0 0 30px var(--primary-color)';
            setTimeout(() => {
                scoreCircle.style.boxShadow = '';
            }, 500);
            
            // Create particles on click too
            createParticles();
        });
        
        // Listen for score changes
        // This serves as a hook that main.js can call to trigger animations
        // Using MutationObserver to detect when the score value changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    const newScore = scoreValue.textContent;
                    if (newScore && !isNaN(newScore) && parseInt(newScore) !== currentScore) {
                        animateScoreChange(newScore);
                    }
                }
            });
        });
        
        observer.observe(scoreValue, { 
            characterData: true, 
            childList: true,
            subtree: true 
        });
    }
    
    // Initialize
    function init() {
        if (!scoreCircle || !scoreValue || !scoreParticles || !scoreMarks) {
            console.error('Score animation elements not found');
            return;
        }
        
        createProgressMarks();
        setupInteractions();
        
        // Initialize with current score
        const initialScore = parseInt(scoreValue.textContent) || 0;
        updateProgressCircle(initialScore);
    }
    
    // Start initialization
    init();
});

// Hook function that can be called from main.js
window.updateScoreWithAnimation = function(newScore) {
    const scoreValue = document.getElementById('overall-score');
    if (scoreValue) {
        // This will trigger the MutationObserver
        scoreValue.textContent = newScore;
        
        // Also add animation classes
        const scoreCircle = document.querySelector('.score-circle');
        if (scoreCircle) {
            scoreCircle.classList.add('score-achieved');
            setTimeout(() => {
                scoreCircle.classList.remove('score-achieved');
            }, 800);
        }
    }
}; 