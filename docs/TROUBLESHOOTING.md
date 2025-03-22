# Troubleshooting Guide

This document provides solutions for common issues you might encounter when setting up or running the Mix Analyzer application.

## Installation Issues

### Python Version Compatibility

- **Issue**: Errors related to missing modules or incompatible packages
- **Solution**: This application works best with Python 3.8-3.11. Python 3.12 has some compatibility issues with certain dependencies. Consider downgrading to Python 3.10 or 3.11 if you encounter persistent issues.

### Missing `distutils` Error

- **Issue**: `ModuleNotFoundError: No module named 'distutils'`
- **Solution**: Install setuptools first:
  ```
  pip install --upgrade setuptools
  ```

### NumPy/SciPy Installation Errors

- **Issue**: Errors when building NumPy or SciPy
- **Solution**: Install pre-built wheels:
  ```
  pip install --only-binary=numpy,scipy numpy>=1.26.0 scipy>=1.11.3
  ```

### Librosa Installation Issues

- **Issue**: Errors installing librosa or its dependencies
- **Solution**: Install librosa after NumPy and SciPy:
  ```
  pip install numpy>=1.26.0 scipy>=1.11.3
  pip install librosa==0.10.1
  ```

## Runtime Issues

### Module Import Errors

- **Issue**: `ModuleNotFoundError: No module named 'app.audio_analyzer'; 'app' is not a package`
- **Solution**: 
  1. Make sure you're running the application from the project root directory
  2. Check if there's an `__init__.py` file in the app directory. If not, create one:
     ```
     touch app/__init__.py
     ```
  3. Use the provided run script: `./run.sh`
  4. If running manually, ensure you're in the correct directory:
     ```
     cd /path/to/mix-analyzer
     source venv/bin/activate  # or venv_x86/bin/activate on Apple Silicon
     python app.py
     ```
  5. Run the app structure check script to diagnose issues:
     ```
     ./check_app_structure.py
     ```

### Template Not Found Errors

- **Issue**: `jinja2.exceptions.TemplateNotFound: index.html` or other template files
- **Solution**: 
  1. Make sure the template files exist in the `app/templates` directory
  2. Check that the Flask app is configured to find templates in the correct location:
     ```python
     template_dir = os.path.abspath('app/templates')
     app = Flask(__name__, template_folder=template_dir)
     ```
  3. If you've moved files around, make sure the paths in the Flask app are updated accordingly

### OpenAI API Key Not Working

- **Issue**: AI insights not available or errors related to OpenAI API
- **Solution**: 
  1. Make sure you've set your OpenAI API key in the `.env` file
  2. Verify your API key is valid and has sufficient credits
  3. Check your internet connection

### File Upload Issues

- **Issue**: Nothing happens when selecting an MP3 file
- **Solution**:
  1. Check the browser console for JavaScript errors (F12 or right-click > Inspect > Console)
  2. Make sure the file is an MP3 (the app only accepts .mp3 files)
  3. Check that the file size is under 16MB (the default limit)
  4. Verify that the `app/static/uploads` directory exists and is writable
     ```
     ./check_uploads_dir.py
     ```
  5. Try a different browser (Chrome or Firefox recommended)
  6. Check the server logs for any errors during file processing
  7. If using Safari, try enabling cross-site tracking:
     - Safari > Preferences > Privacy > uncheck "Prevent cross-site tracking"
  8. Try the debug server to see detailed logs:
     ```
     ./debug_upload.py
     ```
     Then visit http://127.0.0.1:5000/test to use the test upload page
  9. Check if the file upload functionality works with a simple test:
     ```
     curl -X POST -F "file=@/path/to/your/file.mp3" http://127.0.0.1:5000/upload
     ```
  10. Verify that your browser's JavaScript is enabled and not blocked by extensions

- **Issue**: Upload fails with server error
- **Solution**:
  1. Check the server logs for Python errors
  2. Make sure all dependencies are properly installed
  3. Verify that the librosa and other audio processing libraries are working correctly:
     ```
     ./test_audio_analysis.py /path/to/your/file.mp3
     ```
  4. Try with a different MP3 file (some files might be corrupted or in an unsupported format)
  5. Check if the audio file can be loaded with pydub and librosa directly:
     ```python
     from pydub import AudioSegment
     import librosa
     
     # Try loading with pydub
     audio = AudioSegment.from_file("/path/to/your/file.mp3")
     print(f"Duration: {len(audio)/1000}s, Channels: {audio.channels}")
     
     # Try loading with librosa
     y, sr = librosa.load("/path/to/your/file.mp3", sr=None)
     print(f"Duration: {len(y)/sr}s, Sample rate: {sr}Hz")
     ```
  6. Check for file permission issues:
     ```
     ls -la app/static/uploads
     ```
  7. Ensure the web server has write permissions to the uploads directory

- **Issue**: "No file part" error when uploading
- **Solution**:
  1. Make sure the form is using `enctype="multipart/form-data"` attribute
  2. Verify that the file input field has the correct name attribute (`name="file"`)
  3. Check if the JavaScript code is correctly creating the FormData object:
     ```javascript
     const formData = new FormData();
     formData.append('file', fileObject);
     ```
  4. Try uploading with a simple HTML form to bypass JavaScript:
     ```html
     <form action="/upload" method="post" enctype="multipart/form-data">
       <input type="file" name="file">
       <button type="submit">Upload</button>
     </form>
     ```

- **Issue**: CORS (Cross-Origin Resource Sharing) errors
- **Solution**:
  1. If you're accessing the app from a different domain or port, you may need to enable CORS:
     ```python
     from flask_cors import CORS
     
     app = Flask(__name__)
     CORS(app)  # Enable CORS for all routes
     ```
  2. Install the Flask-CORS extension:
     ```
     pip install flask-cors
     ```
  3. If you're running the frontend separately from the backend, make sure to use the correct URL for API requests

- **Issue**: "Object of type float32 is not JSON serializable" error
- **Solution**:
  1. This error occurs when trying to convert NumPy data types to JSON. NumPy's data types like float32 are not natively supported by Python's JSON encoder.
  2. Add a custom JSON encoder to your Flask app:
     ```python
     import json
     import numpy as np
     
     class NumpyEncoder(json.JSONEncoder):
         def default(self, obj):
             if isinstance(obj, np.integer):
                 return int(obj)
             if isinstance(obj, np.floating):
                 return float(obj)
             if isinstance(obj, np.ndarray):
                 return obj.tolist()
             return super(NumpyEncoder, self).default(obj)
     
     # Configure Flask app to use custom encoder
     app = Flask(__name__)
     app.json_encoder = NumpyEncoder
     ```
  3. When manually converting to JSON in your code, use the custom encoder:
     ```python
     json_data = json.dumps(data, cls=NumpyEncoder)
     ```
  4. This issue is common when working with libraries like librosa and numpy that use their own data types.

### Visualization Errors

- **Issue**: Visualizations not displaying or errors generating them
- **Solution**:
  1. Make sure matplotlib is properly installed
  2. Check that the uploaded file is a valid audio file
  3. Try with a different MP3 file

- **Issue**: 404 errors when loading visualization images
- **Solution**:
  1. Check if the visualization files are being generated correctly:
     ```
     # Replace 'filename.png' with the actual filename from the console error
     curl http://localhost:5000/debug/visualizations/uploads/your_file_id/filename.png
     ```
  2. Ensure the static folder is configured correctly in Flask:
     ```python
     static_dir = os.path.abspath('app/static')
     app = Flask(__name__, static_folder=static_dir)
     ```
  3. Check if the paths in the visualization URLs are correct:
     - They should start with `/static/uploads/...`
     - Open your browser's developer tools (F12) and look at the Network tab
     - Check the actual URL being requested for the images
  4. Verify that the uploads directory has the correct permissions:
     ```
     ls -la app/static/uploads
     ```
  5. If using a production server like Nginx or Apache, make sure it's configured to serve static files

- **Issue**: Visualization zoom feature not working
- **Solution**:
  1. Make sure the modal.js and modal.css files are properly loaded:
     - Check the browser console for any JavaScript errors
     - Verify that the files are included in the HTML:
       ```html
       <link rel="stylesheet" href="{{ url_for('static', filename='css/modal.css') }}">
       <script src="{{ url_for('static', filename='js/modal.js') }}"></script>
       ```
  2. Check if the visualization containers have the correct class:
     ```html
     <div class="visualization-container" title="Click to enlarge">
         <img id="waveform-img" src="..." alt="Waveform">
     </div>
     ```
  3. Try clearing your browser cache or using a different browser
  4. If using Safari, check if JavaScript is enabled and not restricted
  5. For keyboard shortcuts (+ to zoom in, - to zoom out, 0 to reset), make sure no other browser extensions are capturing these keys

- **Issue**: Error: `'_process_plot_var_args' object has no attribute 'prop_cycler'`
- **Solution**: This is a compatibility issue between matplotlib and librosa. The application has been updated to handle this error, but if you encounter it:
  1. Update matplotlib to the latest version: `pip install --upgrade matplotlib`
  2. When using librosa's display functions, explicitly specify colors:
     ```python
     librosa.display.waveshow(y, sr=sr, color='blue')  # Instead of relying on prop_cycler
     ```
  3. Use a try-except block around visualization code to handle potential errors

## Platform-Specific Issues

### macOS

- **Issue**: Installation errors on macOS
- **Solution**: Install required system libraries:
  ```
  brew install libsndfile
  ```

#### Apple Silicon (M1/M2/M3) Specific Issues

- **Issue**: Errors building matplotlib or other packages with C extensions
- **Solution**: Use pre-built wheels instead of building from source:
  ```
  pip install --only-binary=:all: matplotlib
  ```

- **Issue**: `Invalid configuration 'arm64-apple-darwin': machine 'arm64-apple' not recognized`
- **Solution**: This is a build configuration issue. Try installing the latest versions:
  ```
  pip install matplotlib>=3.8.0 --only-binary=:all:
  ```

- **Issue**: Other build failures on Apple Silicon
- **Solution**: Install Rosetta 2 for better compatibility:
  ```
  softwareupdate --install-rosetta
  ```
  Then create a new virtual environment with x86_64 architecture:
  ```
  arch -x86_64 python -m venv venv_x86
  source venv_x86/bin/activate
  ```

### Windows

- **Issue**: DLL load errors or missing libraries
- **Solution**: Install Visual C++ Redistributable:
  [Download Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Linux

- **Issue**: Missing system libraries
- **Solution**: Install required packages:
  ```
  sudo apt-get install libsndfile1 ffmpeg
  ```

## Still Having Issues?

If you're still experiencing problems after trying these solutions, please open an issue on the GitHub repository with:

1. Your operating system and Python version
2. The exact error message
3. Steps you've already tried
4. Any relevant logs or output 