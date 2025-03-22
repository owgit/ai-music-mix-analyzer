class ImageModal {
    constructor() {
        this.modal = null;
        this.modalImage = null;
        this.currentZoom = 1;
        this.minZoom = 0.5;
        this.maxZoom = 3;
        this.zoomStep = 0.25;
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.imageX = 0;
        this.imageY = 0;
        
        this.init();
    }
    
    init() {
        console.log('Initializing ImageModal');
        
        // Check if modal already exists
        if (document.querySelector('.modal-overlay')) {
            console.log('Modal already exists, skipping initialization');
            return;
        }
        
        // Create modal HTML
        this.createModalHTML();
        
        // Add event listeners
        this.addEventListeners();
        
        // Make all visualization images clickable
        this.makeImagesClickable();
        
        console.log('ImageModal initialization complete');
    }
    
    createModalHTML() {
        // Create modal elements
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal-overlay';
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        
        const modalTitle = document.createElement('div');
        modalTitle.className = 'modal-title';
        
        const closeButton = document.createElement('button');
        closeButton.className = 'close-button';
        closeButton.innerHTML = '&times;';
        closeButton.setAttribute('aria-label', 'Close');
        
        const imageContainer = document.createElement('div');
        imageContainer.className = 'modal-image-container';
        
        const modalImage = document.createElement('img');
        modalImage.className = 'modal-image';
        modalImage.alt = 'Enlarged visualization';
        
        const modalControls = document.createElement('div');
        modalControls.className = 'modal-controls';
        
        const zoomControls = document.createElement('div');
        zoomControls.className = 'zoom-controls';
        
        const zoomOutButton = document.createElement('button');
        zoomOutButton.className = 'zoom-button zoom-out';
        zoomOutButton.innerHTML = '&minus;';
        zoomOutButton.setAttribute('aria-label', 'Zoom out');
        
        const zoomLevel = document.createElement('span');
        zoomLevel.className = 'zoom-level';
        zoomLevel.textContent = '100%';
        
        const zoomInButton = document.createElement('button');
        zoomInButton.className = 'zoom-button zoom-in';
        zoomInButton.innerHTML = '&plus;';
        zoomInButton.setAttribute('aria-label', 'Zoom in');
        
        const resetButton = document.createElement('button');
        resetButton.className = 'zoom-button reset';
        resetButton.textContent = 'Reset';
        resetButton.style.width = 'auto';
        resetButton.style.padding = '0 10px';
        
        // Assemble the modal
        zoomControls.appendChild(zoomOutButton);
        zoomControls.appendChild(zoomLevel);
        zoomControls.appendChild(zoomInButton);
        
        modalControls.appendChild(zoomControls);
        modalControls.appendChild(resetButton);
        
        imageContainer.appendChild(modalImage);
        
        modalContent.appendChild(modalTitle);
        modalContent.appendChild(closeButton);
        modalContent.appendChild(imageContainer);
        modalContent.appendChild(modalControls);
        
        modalOverlay.appendChild(modalContent);
        
        // Add to document
        document.body.appendChild(modalOverlay);
        
        // Store references
        this.modal = modalOverlay;
        this.modalImage = modalImage;
        this.zoomLevel = zoomLevel;
        this.imageContainer = imageContainer;
        this.modalTitle = modalTitle;
        this.zoomOutButton = zoomOutButton;
        this.zoomInButton = zoomInButton;
        this.resetButton = resetButton;
    }
    
    addEventListeners() {
        // Close button
        const closeButton = this.modal.querySelector('.close-button');
        closeButton.addEventListener('click', () => this.closeModal());
        
        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
        
        // Zoom controls
        this.zoomOutButton.addEventListener('click', () => this.zoomOut());
        this.zoomInButton.addEventListener('click', () => this.zoomIn());
        this.resetButton.addEventListener('click', () => this.resetZoom());
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (!this.modal.classList.contains('active')) return;
            
            switch (e.key) {
                case 'Escape':
                    this.closeModal();
                    break;
                case '+':
                case '=':
                    this.zoomIn();
                    break;
                case '-':
                case '_':
                    this.zoomOut();
                    break;
                case '0':
                    this.resetZoom();
                    break;
            }
        });
        
        // Mouse wheel zoom
        this.imageContainer.addEventListener('wheel', (e) => {
            if (!this.modal.classList.contains('active')) return;
            
            e.preventDefault();
            if (e.deltaY < 0) {
                this.zoomIn();
            } else {
                this.zoomOut();
            }
        });
        
        // Drag to pan
        this.modalImage.addEventListener('mousedown', (e) => {
            if (this.currentZoom <= 1) return;
            
            this.isDragging = true;
            this.startX = e.clientX;
            this.startY = e.clientY;
            
            // Get current transform values
            const transform = window.getComputedStyle(this.modalImage).getPropertyValue('transform');
            const matrix = new DOMMatrix(transform);
            this.imageX = matrix.e;
            this.imageY = matrix.f;
            
            this.modalImage.style.cursor = 'grabbing';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            
            const dx = e.clientX - this.startX;
            const dy = e.clientY - this.startY;
            
            this.modalImage.style.transform = `scale(${this.currentZoom}) translate(${this.imageX + dx}px, ${this.imageY + dy}px)`;
        });
        
        document.addEventListener('mouseup', () => {
            if (!this.isDragging) return;
            
            this.isDragging = false;
            this.modalImage.style.cursor = 'grab';
            
            // Update the transform values
            const transform = window.getComputedStyle(this.modalImage).getPropertyValue('transform');
            const matrix = new DOMMatrix(transform);
            this.imageX = matrix.e;
            this.imageY = matrix.f;
        });
    }
    
    makeImagesClickable() {
        // Find all visualization containers and make them clickable
        document.addEventListener('DOMContentLoaded', () => {
            const visualizationContainers = document.querySelectorAll('.visualization-container');
            
            visualizationContainers.forEach(container => {
                container.addEventListener('click', () => {
                    const img = container.querySelector('img');
                    if (img) {
                        // Only open the modal if the image has a valid src
                        if (img.src && img.src !== 'about:blank' && !img.classList.contains('error')) {
                            this.openModal(img.src, img.alt || 'Visualization');
                        } else {
                            console.warn('Cannot open modal: Image source not available or image has error');
                        }
                    }
                });
            });
        });
    }
    
    openModal(imageSrc, title) {
        // Validate image source
        if (!imageSrc || imageSrc === 'about:blank') {
            console.error('Cannot open modal: Invalid image source');
            return;
        }
        
        // Set image source and title
        this.modalImage.src = imageSrc;
        this.modalTitle.textContent = title || 'Visualization';
        
        // Add error handling for the image
        this.modalImage.onerror = () => {
            console.error(`Failed to load image in modal: ${imageSrc}`);
            this.modalImage.alt = 'Error loading image';
            this.modalTitle.textContent = 'Error: Could not load image';
        };
        
        // Reset zoom
        this.resetZoom();
        
        // Show modal
        this.modal.classList.add('active');
        
        // Prevent body scrolling
        document.body.style.overflow = 'hidden';
    }
    
    closeModal() {
        // Hide modal
        this.modal.classList.remove('active');
        
        // Allow body scrolling
        document.body.style.overflow = '';
        
        // Reset zoom
        this.resetZoom();
    }
    
    zoomIn() {
        if (this.currentZoom >= this.maxZoom) return;
        
        this.currentZoom += this.zoomStep;
        this.updateZoom();
    }
    
    zoomOut() {
        if (this.currentZoom <= this.minZoom) return;
        
        this.currentZoom -= this.zoomStep;
        this.updateZoom();
    }
    
    resetZoom() {
        this.currentZoom = 1;
        this.imageX = 0;
        this.imageY = 0;
        this.updateZoom();
    }
    
    updateZoom() {
        // Update zoom level display
        this.zoomLevel.textContent = `${Math.round(this.currentZoom * 100)}%`;
        
        // Apply zoom to image
        this.modalImage.style.transform = `scale(${this.currentZoom}) translate(${this.imageX}px, ${this.imageY}px)`;
        
        // Update cursor style
        this.modalImage.style.cursor = this.currentZoom > 1 ? 'grab' : 'default';
        
        // Enable/disable zoom buttons
        this.zoomOutButton.disabled = this.currentZoom <= this.minZoom;
        this.zoomInButton.disabled = this.currentZoom >= this.maxZoom;
    }
    
    refreshClickableContainers() {
        // Find all visualization containers and make them clickable
        const visualizationContainers = document.querySelectorAll('.visualization-container');
        
        visualizationContainers.forEach(container => {
            // Remove existing click event listeners
            const newContainer = container.cloneNode(true);
            container.parentNode.replaceChild(newContainer, container);
            
            // Add new click event listener
            newContainer.addEventListener('click', () => {
                const img = newContainer.querySelector('img');
                if (img && img.src && img.src !== 'about:blank' && !img.classList.contains('error')) {
                    this.openModal(img.src, img.alt || 'Visualization');
                } else {
                    console.warn('Cannot open modal: Image source not available or image has error');
                }
            });
        });
        
        console.log('Refreshed clickable containers');
    }
}

// Initialize the modal
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM content loaded, initializing ImageModal');
    
    try {
        // Initialize the modal and make it globally accessible
        window.imageModal = new ImageModal();
        console.log('ImageModal initialized successfully');
    } catch (error) {
        console.error('Error initializing ImageModal:', error);
    }
}); 