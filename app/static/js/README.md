# Image Modal Component

A lightweight, customizable image modal component for web applications. This component allows users to view images in a larger format with zoom capabilities.

## Features

- Lightweight and dependency-free
- Image zooming with mouse wheel or pinch gestures
- Keyboard navigation support
- Mobile-friendly design
- Customizable appearance
- Error handling for invalid or missing images

## Installation

1. Include the CSS file in your HTML head:
   ```html
   <link rel="stylesheet" href="path/to/modal.css">
   ```

2. Include the JavaScript file at the end of your HTML body:
   ```html
   <script src="path/to/modal.js"></script>
   ```

## Usage

### Basic Usage

The Modal component automatically initializes when the DOM content is loaded. It looks for elements with the class `visualization-container` and makes them clickable to open the modal.

```html
<div class="visualization-container" title="Click to enlarge">
    <img id="my-image" class="visualization-image" src="path/to/image.jpg" alt="Image description">
</div>
```

### Manual Initialization

If you need to initialize the modal manually, you can create a new instance of the `ImageModal` class:

```javascript
const imageModal = new ImageModal();
```

### Opening the Modal Programmatically

You can also open the modal programmatically using the `openModal` function:

```javascript
openModal('path/to/image.jpg', 'Image Title');
```

### Dynamic Content

For dynamic content, you can use the `refreshClickableContainers` method to make newly added images clickable:

```javascript
// After adding new image containers to the DOM
imageModal.refreshClickableContainers();
```

## API Reference

### ImageModal Class

The main class that handles the modal functionality.

#### constructor()

Creates a new instance of the ImageModal class and initializes it.

**Returns:** A new ImageModal instance.

#### init()

Initializes the modal by creating the necessary DOM elements and setting up event listeners.

**Returns:** void

#### refreshClickableContainers()

Refreshes the click event listeners for all visualization containers. Useful when new containers are added dynamically.

**Returns:** void

### Global Functions

#### openModal(imageSrc, imageAlt)

Opens the modal with the specified image.

**Parameters:**
- `imageSrc` (string): The source URL of the image to display in the modal.
- `imageAlt` (string): The alt text or title for the image.

**Returns:** void

## Troubleshooting

### Common Issues

#### Modal doesn't open when clicking on images

Check the following:
- Ensure the modal.js file is properly included in your HTML.
- Verify that your image containers have the class `visualization-container`.
- Check the browser console for any JavaScript errors.
- Make sure the images are properly loaded before trying to open them.

#### Images don't load in the modal

This could be due to:
- Incorrect image paths.
- CORS issues if loading images from a different domain.
- The image file doesn't exist or is corrupted.

The modal includes error handling to display a message when images fail to load.

#### Zoom functionality doesn't work

Zoom is controlled by mouse wheel events or touch gestures. If it's not working:
- Check if your browser supports wheel events.
- Ensure there are no conflicting event listeners on the page.
- Try using a different browser to see if the issue persists.

## License

MIT License 