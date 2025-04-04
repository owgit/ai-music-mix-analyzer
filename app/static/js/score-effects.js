/**
 * Score Cards Enhancement Effects
 * Provides advanced visual effects and interactive animations for score cards
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize frequency score effects
    initFrequencyScoreEffects();
    
    // Initialize dynamics score effects
    initDynamicsScoreEffects();
    
    // Initialize stereo field score effects
    initStereoWidthScoreEffects();
    initStereoPhaseScoreEffects();
    
    // Listen for score updates
    observeScoreChanges();
});

/**
 * Initialize the special effects for the frequency score card
 */
function initFrequencyScoreEffects() {
    const frequencyScoreElement = document.getElementById('frequency-score');
    const frequencyCard = frequencyScoreElement?.closest('.score-card');
    const frequencyMeter = frequencyCard?.querySelector('.frequency-meter');
    const particlesContainer = frequencyCard?.querySelector('.frequency-particles');
    
    if (!frequencyScoreElement || !frequencyCard || !frequencyMeter || !particlesContainer) {
        return;
    }
    
    // Initial setup based on current score
    updateFrequencyMeter(frequencyScoreElement, frequencyMeter);
    
    // Add particle generation on hover
    frequencyCard.addEventListener('mouseenter', () => {
        generateFrequencyParticles(particlesContainer);
    });
    
    // Add click effect
    frequencyCard.addEventListener('click', () => {
        // Flash effect
        frequencyCard.style.boxShadow = '0 0 30px var(--primary-color)';
        setTimeout(() => {
            frequencyCard.style.boxShadow = '';
        }, 500);
        
        // Generate more particles
        generateFrequencyParticles(particlesContainer, 15);
        
        // Pulse animation on score
        frequencyScoreElement.classList.add('score-pulse');
        setTimeout(() => {
            frequencyScoreElement.classList.remove('score-pulse');
        }, 800);
    });
    
    // Add floating wave effect (subtle background animation)
    createWaveEffect(frequencyCard);
}

/**
 * Initialize the special effects for the dynamics score card
 */
function initDynamicsScoreEffects() {
    const dynamicsScoreElement = document.getElementById('dynamics-score');
    const dynamicsCard = dynamicsScoreElement?.closest('.score-card');
    const dynamicsMeter = dynamicsCard?.querySelector('.dynamics-meter');
    
    if (!dynamicsScoreElement || !dynamicsCard || !dynamicsMeter) {
        return;
    }
    
    // Initial setup based on current score
    updateDynamicsMeter(dynamicsScoreElement, dynamicsMeter);
    
    // Add dynamics wave animation
    initDynamicsWaveAnimation(dynamicsCard);
    
    // Add click effect
    dynamicsCard.addEventListener('click', () => {
        // Flash effect
        dynamicsCard.style.boxShadow = '0 0 30px #5e60ce';
        setTimeout(() => {
            dynamicsCard.style.boxShadow = '';
        }, 500);
        
        // Pulse animation on score
        dynamicsScoreElement.classList.add('score-pulse');
        setTimeout(() => {
            dynamicsScoreElement.classList.remove('score-pulse');
        }, 800);
        
        // Create ripple effect
        createDynamicsRipple(dynamicsCard, event);
    });
}

/**
 * Create a ripple effect when clicking on the dynamics score card
 * @param {HTMLElement} container - The container element
 * @param {Event} event - The click event
 */
function createDynamicsRipple(container, event) {
    const ripple = document.createElement('div');
    ripple.classList.add('dynamics-ripple');
    
    const rect = container.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    
    ripple.style.width = ripple.style.height = `${size}px`;
    ripple.style.left = `${event?.clientX - rect.left - size/2 || rect.width/2 - size/2}px`;
    ripple.style.top = `${event?.clientY - rect.top - size/2 || rect.height/2 - size/2}px`;
    
    container.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 800);
}

/**
 * Initialize wave animation for the dynamics card
 * @param {HTMLElement} container - The dynamics card container
 */
function initDynamicsWaveAnimation(container) {
    const waveElement = container.querySelector('.dynamics-wave');
    if (!waveElement) return;
    
    // Make the wave visible
    waveElement.style.opacity = '0.15';
    
    // Randomize wave animation speeds slightly for more natural effect
    const beforeEl = window.getComputedStyle(waveElement, '::before');
    const afterEl = window.getComputedStyle(waveElement, '::after');
    
    const beforeDuration = parseFloat(beforeEl.animationDuration) || 13;
    const afterDuration = parseFloat(afterEl.animationDuration) || 7;
    
    // Set slightly random durations for more organic feel
    waveElement.style.setProperty('--before-duration', `${beforeDuration + Math.random()}s`);
    waveElement.style.setProperty('--after-duration', `${afterDuration + Math.random()}s`);
}

/**
 * Create a subtle wave animation in the background
 * @param {HTMLElement} container - The container element
 */
function createWaveEffect(container) {
    if (!container) return;
    
    // Create wave canvas if it doesn't exist
    if (!container.querySelector('.wave-canvas')) {
        const canvas = document.createElement('canvas');
        canvas.className = 'wave-canvas';
        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.zIndex = '0';
        canvas.style.opacity = '0.1';
        canvas.style.pointerEvents = 'none';
        
        container.appendChild(canvas);
        
        // Animation variables
        const ctx = canvas.getContext('2d');
        let time = 0;
        
        // Animation function
        function drawWave() {
            canvas.width = container.offsetWidth;
            canvas.height = container.offsetHeight;
            
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Wave properties
            const amplitude = 5;
            const frequency = 0.02;
            const speed = 0.05;
            
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);
            
            for (let x = 0; x < canvas.width; x++) {
                const y = amplitude * Math.sin(frequency * x + time * speed) + canvas.height / 2;
                ctx.lineTo(x, y);
            }
            
            ctx.strokeStyle = 'var(--primary-color)';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            time++;
            requestAnimationFrame(drawWave);
        }
        
        // Start animation
        drawWave();
    }
}

/**
 * Update the circular meter based on the score value
 * @param {HTMLElement} scoreElement - The score value element
 * @param {HTMLElement} meterElement - The meter circle element
 */
function updateFrequencyMeter(scoreElement, meterElement) {
    if (!scoreElement || !meterElement) return;
    
    const score = parseInt(scoreElement.textContent) || 0;
    const percentage = (score / 100) * 360; // Convert to degrees for conic gradient
    
    // Update the CSS variable that controls the gradient
    meterElement.style.setProperty('--score-percentage', `${percentage}deg`);
    
    // Add a class based on score range for potential color changes
    meterElement.className = 'frequency-meter';
    if (score >= 80) {
        meterElement.classList.add('excellent');
    } else if (score >= 60) {
        meterElement.classList.add('good');
    } else if (score >= 40) {
        meterElement.classList.add('average');
    } else {
        meterElement.classList.add('poor');
    }
}

/**
 * Update the dynamics meter based on the score value
 * @param {HTMLElement} scoreElement - The score value element
 * @param {HTMLElement} meterElement - The meter circle element
 */
function updateDynamicsMeter(scoreElement, meterElement) {
    if (!scoreElement || !meterElement) return;
    
    const score = parseInt(scoreElement.textContent) || 0;
    const percentage = (score / 100) * 360; // Convert to degrees for conic gradient
    
    // Update the CSS variable that controls the gradient
    meterElement.style.setProperty('--dynamics-percentage', `${percentage}deg`);
    
    // Add a class based on score range for potential color changes
    meterElement.className = 'dynamics-meter';
    if (score >= 80) {
        meterElement.classList.add('excellent');
    } else if (score >= 60) {
        meterElement.classList.add('good');
    } else if (score >= 40) {
        meterElement.classList.add('average');
    } else {
        meterElement.classList.add('poor');
    }
}

/**
 * Generate animated particles for the frequency score
 * @param {HTMLElement} container - The particles container
 * @param {number} count - Number of particles to generate (default: 8)
 */
function generateFrequencyParticles(container, count = 8) {
    if (!container) return;
    
    // Clear old particles that might still be animating
    const oldParticles = container.querySelectorAll('.frequency-particle');
    if (oldParticles.length > 20) {
        oldParticles.forEach((p, i) => {
            if (i < oldParticles.length - 10) {
                p.remove();
            }
        });
    }
    
    // Create new particles
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'frequency-particle';
        
        // Random size between 2-8px
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Position near the score value
        const center = container.offsetWidth / 2;
        const midHeight = container.offsetHeight / 2;
        const startX = center + (Math.random() * 20 - 10);
        const startY = midHeight + (Math.random() * 20 - 10);
        
        // Random direction and distance
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 100 + 50;
        const destX = Math.cos(angle) * distance;
        const destY = Math.sin(angle) * distance;
        
        // Set starting position
        particle.style.left = `${startX}px`;
        particle.style.top = `${startY}px`;
        
        // Set custom properties for the animation
        particle.style.setProperty('--x', `${destX}px`);
        particle.style.setProperty('--y', `${destY}px`);
        
        // Set colors (slightly different hues of primary color)
        const hueShift = Math.random() * 20 - 10;
        particle.style.backgroundColor = `hsl(var(--primary-hue, 230), 70%, ${55 + hueShift}%)`;
        particle.style.opacity = '0.8';
        
        // Set animation
        const duration = Math.random() * 1.5 + 0.5;
        particle.style.animation = `float-particle ${duration}s ease-out forwards`;
        
        // Append to container
        container.appendChild(particle);
        
        // Clean up particle after animation completes
        setTimeout(() => {
            particle.remove();
        }, duration * 1000 + 100);
    }
}

/**
 * Generate animated particles for the dynamics score
 * @param {HTMLElement} container - The particles container
 * @param {number} count - Number of particles to generate (default: 8)
 */
function generateDynamicsParticles(container, count = 8) {
    if (!container) return;
    
    // Clear old particles that might still be animating
    const oldParticles = container.querySelectorAll('.dynamics-particle');
    if (oldParticles.length > 20) {
        oldParticles.forEach((p, i) => {
            if (i < oldParticles.length - 10) {
                p.remove();
            }
        });
    }
    
    // Create new particles
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'dynamics-particle';
        
        // Random size between 2-8px
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Position near the score value
        const center = container.offsetWidth / 2;
        const midHeight = container.offsetHeight / 2;
        const startX = center + (Math.random() * 20 - 10);
        const startY = midHeight + (Math.random() * 20 - 10);
        
        // Random direction and distance
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 100 + 50;
        const destX = Math.cos(angle) * distance;
        const destY = Math.sin(angle) * distance;
        
        // Set starting position
        particle.style.left = `${startX}px`;
        particle.style.top = `${startY}px`;
        
        // Set custom properties for the animation
        particle.style.setProperty('--x', `${destX}px`);
        particle.style.setProperty('--y', `${destY}px`);
        
        // Set colors (dynamics blue/purple theme)
        const useBlue = Math.random() > 0.5;
        const color = useBlue ? '#48bfe3' : '#5e60ce';
        particle.style.backgroundColor = color;
        particle.style.opacity = '0.8';
        
        // Set animation
        const duration = Math.random() * 1.5 + 0.5;
        // Use a different animation for dynamics
        particle.style.animation = `float-particle ${duration}s cubic-bezier(0.4, 0, 0.2, 1) forwards`;
        
        // Append to container
        container.appendChild(particle);
        
        // Clean up particle after animation completes
        setTimeout(() => {
            particle.remove();
        }, duration * 1000 + 100);
    }
}

/**
 * Initialize the special effects for the stereo width score card
 */
function initStereoWidthScoreEffects() {
    const widthScoreElement = document.getElementById('width-score');
    const widthCard = widthScoreElement?.closest('.score-card');
    const widthMeter = widthCard?.querySelector('.stereo-width-meter');
    
    if (!widthScoreElement || !widthCard || !widthMeter) {
        return;
    }
    
    // Initial setup based on current score
    updateStereoWidthMeter(widthScoreElement, widthMeter);
    
    // Add click effect
    widthCard.addEventListener('click', () => {
        // Flash effect
        widthCard.style.boxShadow = '0 0 30px rgba(78, 99, 220, 0.8)';
        setTimeout(() => {
            widthCard.style.boxShadow = '';
        }, 500);
        
        // Pulse animation on score
        widthScoreElement.classList.add('score-pulse');
        setTimeout(() => {
            widthScoreElement.classList.remove('score-pulse');
        }, 800);
    });
}

/**
 * Initialize the special effects for the stereo phase score card
 */
function initStereoPhaseScoreEffects() {
    const phaseScoreElement = document.getElementById('phase-score');
    const phaseCard = phaseScoreElement?.closest('.score-card');
    const phaseMeter = phaseCard?.querySelector('.stereo-phase-meter');
    const waveElement = phaseCard?.querySelector('.stereo-phase-wave');
    
    if (!phaseScoreElement || !phaseCard || !phaseMeter) {
        return;
    }
    
    // Initial setup based on current score
    updateStereoPhaseeMeter(phaseScoreElement, phaseMeter);
    
    // Activate wave animation
    if (waveElement) {
        waveElement.style.opacity = '0.15';
        
        // Randomize wave animation speeds slightly for more natural effect
        const beforeDuration = 13 + Math.random();
        const afterDuration = 7 + Math.random();
        
        waveElement.style.setProperty('--before-duration', `${beforeDuration}s`);
        waveElement.style.setProperty('--after-duration', `${afterDuration}s`);
    }
    
    // Show waves more prominently on hover
    phaseCard.addEventListener('mouseenter', () => {
        if (waveElement) {
            waveElement.style.opacity = '0.3';
        }
    });
    
    // Return waves to normal opacity on mouseleave
    phaseCard.addEventListener('mouseleave', () => {
        if (waveElement) {
            waveElement.style.opacity = '0.15';
        }
    });
    
    // Add click effect
    phaseCard.addEventListener('click', () => {
        // Flash effect
        phaseCard.style.boxShadow = '0 0 30px rgba(72, 191, 227, 0.8)';
        setTimeout(() => {
            phaseCard.style.boxShadow = '';
        }, 500);
        
        // Pulse animation on score
        phaseScoreElement.classList.add('score-pulse');
        setTimeout(() => {
            phaseScoreElement.classList.remove('score-pulse');
        }, 800);
        
        // Temporarily boost wave opacity
        if (waveElement) {
            waveElement.style.opacity = '0.5';
            setTimeout(() => {
                waveElement.style.opacity = '0.15';
            }, 1000);
        }
    });
}

/**
 * Update the stereo width meter based on the score value
 * @param {HTMLElement} scoreElement - The score value element
 * @param {HTMLElement} meterElement - The meter circle element
 */
function updateStereoWidthMeter(scoreElement, meterElement) {
    if (!scoreElement || !meterElement) return;
    
    const score = parseInt(scoreElement.textContent) || 0;
    const percentage = (score / 100) * 360; // Convert to degrees for conic gradient
    
    // Update the CSS variable that controls the gradient
    meterElement.style.setProperty('--width-percentage', `${percentage}deg`);
    
    // Add a class based on score range for potential color changes
    meterElement.className = 'stereo-width-meter';
    if (score >= 80) {
        meterElement.classList.add('excellent');
    } else if (score >= 60) {
        meterElement.classList.add('good');
    } else if (score >= 40) {
        meterElement.classList.add('average');
    } else {
        meterElement.classList.add('poor');
    }
}

/**
 * Update the stereo phase meter based on the score value
 * @param {HTMLElement} scoreElement - The score value element
 * @param {HTMLElement} meterElement - The meter circle element
 */
function updateStereoPhaseeMeter(scoreElement, meterElement) {
    if (!scoreElement || !meterElement) return;
    
    const score = parseInt(scoreElement.textContent) || 0;
    const percentage = (score / 100) * 360; // Convert to degrees for conic gradient
    
    // Update the CSS variable that controls the gradient
    meterElement.style.setProperty('--phase-percentage', `${percentage}deg`);
    
    // Add a class based on score range for potential color changes
    meterElement.className = 'stereo-phase-meter';
    if (score >= 80) {
        meterElement.classList.add('excellent');
    } else if (score >= 60) {
        meterElement.classList.add('good');
    } else if (score >= 40) {
        meterElement.classList.add('average');
    } else {
        meterElement.classList.add('poor');
    }
}

/**
 * Generate animated particles for the stereo width score
 * @param {HTMLElement} container - The particles container
 * @param {number} count - Number of particles to generate (default: 8)
 */
function generateStereoWidthParticles(container, count = 8) {
    if (!container) return;
    
    // Clear old particles that might still be animating
    const oldParticles = container.querySelectorAll('.stereo-width-particle');
    if (oldParticles.length > 20) {
        oldParticles.forEach((p, i) => {
            if (i < oldParticles.length - 10) {
                p.remove();
            }
        });
    }
    
    // Create new particles
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'stereo-width-particle';
        
        // Random size between 2-8px
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Position near the score value
        const center = container.offsetWidth / 2;
        const midHeight = container.offsetHeight / 2;
        const startX = center + (Math.random() * 20 - 10);
        const startY = midHeight + (Math.random() * 20 - 10);
        
        // Random direction and distance
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 100 + 50;
        const destX = Math.cos(angle) * distance;
        const destY = Math.sin(angle) * distance;
        
        // Set starting position
        particle.style.left = `${startX}px`;
        particle.style.top = `${startY}px`;
        
        // Set custom properties for the animation
        particle.style.setProperty('--x', `${destX}px`);
        particle.style.setProperty('--y', `${destY}px`);
        
        // Set colors (stereo width blues)
        const hueShift = Math.random() * 20 - 10;
        particle.style.backgroundColor = `rgba(78, 99, 220, ${0.7 + Math.random() * 0.3})`;
        
        // Set animation
        const duration = Math.random() * 1.5 + 0.5;
        particle.style.animation = `float-particle ${duration}s ease-out forwards`;
        
        // Append to container
        container.appendChild(particle);
        
        // Clean up particle after animation completes
        setTimeout(() => {
            particle.remove();
        }, duration * 1000 + 100);
    }
}

/**
 * Generate animated particles for the stereo phase score
 * @param {HTMLElement} container - The particles container
 * @param {number} count - Number of particles to generate (default: 8)
 */
function generateStereoPhaseParticles(container, count = 8) {
    if (!container) return;
    
    // Clear old particles that might still be animating
    const oldParticles = container.querySelectorAll('.stereo-phase-particle');
    if (oldParticles.length > 20) {
        oldParticles.forEach((p, i) => {
            if (i < oldParticles.length - 10) {
                p.remove();
            }
        });
    }
    
    // Create new particles
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'stereo-phase-particle';
        
        // Random size between 2-8px
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Position near the score value
        const center = container.offsetWidth / 2;
        const midHeight = container.offsetHeight / 2;
        const startX = center + (Math.random() * 20 - 10);
        const startY = midHeight + (Math.random() * 20 - 10);
        
        // Random direction and distance
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 100 + 50;
        const destX = Math.cos(angle) * distance;
        const destY = Math.sin(angle) * distance;
        
        // Set starting position
        particle.style.left = `${startX}px`;
        particle.style.top = `${startY}px`;
        
        // Set custom properties for the animation
        particle.style.setProperty('--x', `${destX}px`);
        particle.style.setProperty('--y', `${destY}px`);
        
        // Set colors (phase uses blue-purple gradients)
        const useBlue = Math.random() > 0.5;
        const color = useBlue ? 'rgba(72, 191, 227, 0.8)' : 'rgba(94, 96, 206, 0.8)';
        particle.style.backgroundColor = color;
        
        // Set animation
        const duration = Math.random() * 1.5 + 0.5;
        particle.style.animation = `stereo-phase-particle-float ${duration}s cubic-bezier(0.4, 0, 0.2, 1) forwards`;
        
        // Append to container
        container.appendChild(particle);
        
        // Clean up particle after animation completes
        setTimeout(() => {
            particle.remove();
        }, duration * 1000 + 100);
    }
}

/**
 * Observe score value changes to update effects
 */
function observeScoreChanges() {
    // Observe frequency score changes
    observeFrequencyScoreChanges();
    
    // Observe dynamics score changes
    observeDynamicsScoreChanges();
    
    // Observe stereo width score changes
    observeStereoWidthScoreChanges();
    
    // Observe stereo phase score changes
    observeStereoPhaseScoreChanges();
}

/**
 * Observe frequency score value changes to update effects
 */
function observeFrequencyScoreChanges() {
    const frequencyScoreElement = document.getElementById('frequency-score');
    const frequencyCard = frequencyScoreElement?.closest('.score-card');
    const frequencyMeter = frequencyCard?.querySelector('.frequency-meter');
    
    if (!frequencyScoreElement || !frequencyMeter) return;
    
    // Use MutationObserver to detect when the score value changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                updateFrequencyMeter(frequencyScoreElement, frequencyMeter);
                
                // Generate particles when score changes
                const particlesContainer = frequencyCard.querySelector('.frequency-particles');
                if (particlesContainer) {
                    generateFrequencyParticles(particlesContainer, 12);
                }
                
                // Add a temporary highlight pulse class
                frequencyScoreElement.classList.add('score-updated');
                setTimeout(() => {
                    frequencyScoreElement.classList.remove('score-updated');
                }, 1000);
            }
        });
    });
    
    observer.observe(frequencyScoreElement, { 
        characterData: true, 
        childList: true,
        subtree: true 
    });
}

/**
 * Observe dynamics score value changes to update effects
 */
function observeDynamicsScoreChanges() {
    const dynamicsScoreElement = document.getElementById('dynamics-score');
    const dynamicsCard = dynamicsScoreElement?.closest('.score-card');
    const dynamicsMeter = dynamicsCard?.querySelector('.dynamics-meter');
    
    if (!dynamicsScoreElement || !dynamicsMeter) return;
    
    // Use MutationObserver to detect when the score value changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                updateDynamicsMeter(dynamicsScoreElement, dynamicsMeter);
                
                // Add a temporary highlight pulse class
                dynamicsScoreElement.classList.add('score-updated');
                setTimeout(() => {
                    dynamicsScoreElement.classList.remove('score-updated');
                }, 1000);
                
                // Update wave animation intensity based on score
                const waveElement = dynamicsCard.querySelector('.dynamics-wave');
                if (waveElement) {
                    const score = parseInt(dynamicsScoreElement.textContent) || 0;
                    const intensity = 0.15 + (score / 200); // Between 0.15 and 0.65
                    waveElement.style.opacity = intensity.toString();
                }
            }
        });
    });
    
    observer.observe(dynamicsScoreElement, { 
        characterData: true, 
        childList: true,
        subtree: true 
    });
}

/**
 * Observe stereo width score value changes to update effects
 */
function observeStereoWidthScoreChanges() {
    const widthScoreElement = document.getElementById('width-score');
    const widthCard = widthScoreElement?.closest('.score-card');
    const widthMeter = widthCard?.querySelector('.stereo-width-meter');
    
    if (!widthScoreElement || !widthMeter) return;
    
    // Use MutationObserver to detect when the score value changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                updateStereoWidthMeter(widthScoreElement, widthMeter);
                
                // Add a temporary highlight pulse class
                widthScoreElement.classList.add('score-updated');
                setTimeout(() => {
                    widthScoreElement.classList.remove('score-updated');
                }, 1000);
            }
        });
    });
    
    observer.observe(widthScoreElement, { 
        characterData: true, 
        childList: true,
        subtree: true 
    });
}

/**
 * Observe stereo phase score value changes to update effects
 */
function observeStereoPhaseScoreChanges() {
    const phaseScoreElement = document.getElementById('phase-score');
    const phaseCard = phaseScoreElement?.closest('.score-card');
    const phaseMeter = phaseCard?.querySelector('.stereo-phase-meter');
    
    if (!phaseScoreElement || !phaseMeter) return;
    
    // Use MutationObserver to detect when the score value changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'characterData' || mutation.type === 'childList') {
                updateStereoPhaseeMeter(phaseScoreElement, phaseMeter);
                
                // Add a temporary highlight pulse class
                phaseScoreElement.classList.add('score-updated');
                setTimeout(() => {
                    phaseScoreElement.classList.remove('score-updated');
                }, 1000);
                
                // Update wave animation intensity based on score
                const waveElement = phaseCard.querySelector('.stereo-phase-wave');
                if (waveElement) {
                    const score = parseInt(phaseScoreElement.textContent) || 0;
                    const intensity = 0.15 + (score / 500); // Between 0.15 and 0.35
                    waveElement.style.opacity = intensity.toString();
                }
            }
        });
    });
    
    observer.observe(phaseScoreElement, { 
        characterData: true, 
        childList: true,
        subtree: true 
    });
}

// Add CSS for animation classes
function addDynamicStyles() {
    const styleSheet = document.createElement('style');
    styleSheet.innerText = `
        .score-pulse {
            animation: scorePulse 0.8s ease-out;
        }
        
        .score-updated {
            animation: scoreUpdate 0.6s ease-out;
        }
        
        @keyframes scorePulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        
        @keyframes scoreUpdate {
            0% { opacity: 0.5; transform: scale(0.9); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        /* Frequency meter classes */
        .frequency-meter.excellent {
            background: conic-gradient(
                #4CAF50 0%, 
                #4CAF50 var(--score-percentage), 
                #e9ecef var(--score-percentage), 
                #e9ecef 100%
            );
        }
        
        .frequency-meter.good {
            background: conic-gradient(
                #2196F3 0%, 
                #2196F3 var(--score-percentage), 
                #e9ecef var(--score-percentage), 
                #e9ecef 100%
            );
        }
        
        .frequency-meter.average {
            background: conic-gradient(
                #FF9800 0%, 
                #FF9800 var(--score-percentage), 
                #e9ecef var(--score-percentage), 
                #e9ecef 100%
            );
        }
        
        .frequency-meter.poor {
            background: conic-gradient(
                #F44336 0%, 
                #F44336 var(--score-percentage), 
                #e9ecef var(--score-percentage), 
                #e9ecef 100%
            );
        }
        
        /* Dynamics ripple effect */
        .dynamics-ripple {
            position: absolute;
            top: 0;
            left: 0;
            width: 0;
            height: 0;
            background-color: rgba(94, 96, 206, 0.2);
            border-radius: 50%;
            transform: scale(0);
            pointer-events: none;
            z-index: 0;
            animation: ripple 0.8s ease-out forwards;
        }
        
        @keyframes ripple {
            0% { transform: scale(0); opacity: 0.5; }
            100% { transform: scale(2); opacity: 0; }
        }
    `;
    document.head.appendChild(styleSheet);
}

// Add dynamic styles on load
addDynamicStyles(); 