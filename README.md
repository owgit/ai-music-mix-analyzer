# Music Mix Analyzer - Professional Audio Analysis Tool

<p align="center">
  <img src="app/static/img/music-analyzer-icon.svg" alt="Music Mix Analyzer Logo" width="180" />
</p>

A powerful Flask-based web application for audio mixing analysis, mastering assistance, and professional music production visualization. Perfect for sound engineers, music producers, and audio enthusiasts.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Website: mixanalytic.com](https://img.shields.io/badge/Website-mixanalytic.com-blue.svg)](https://mixanalytic.com)
[![GitHub: owgit/ai-music-mix-analyzer](https://img.shields.io/badge/GitHub-owgit/ai--music--mix--analyzer-green.svg)](https://github.com/owgit/ai-music-mix-analyzer)

## 🎧 Features

- **Audio Analysis**: Upload and analyze audio files (mp3, wav, flac, aiff, ogg) with professional-grade tools
- **Visualization Suite**: Generate high-resolution spectrograms and waveform visualizations
- **Stereo Field Analysis**: Comprehensive stereo imaging and phase correlation analysis
- **AI-Powered Mix Feedback**: Get intelligent suggestions using OpenAI's GPT models or alternative AI providers
- **Tab-specific AI Insights**: Context-specific AI analysis for each audio feature (frequency, dynamics, stereo, etc.)
- **Frequency Response**: Analyze frequency distribution across 7 distinct bands and identify problematic areas
- **Dynamic Range**: Measure compression levels and dynamic range in your mixes with multiple metrics
- **Harmonic Content**: Analyze key detection and harmonic complexity
- **Transient Analysis**: Evaluate percussion energy and attack characteristics
- **3D Spatial Analysis**: Visualize and analyze height, depth, and width perception in your mixes
- **Security**: Enterprise-grade file handling with robust security measures
- **About Page**: Comprehensive information about the tool, its features, and how to use it
- **Guides**: Detailed user guides for making the most of the analysis features
- **Music Theory Integration**: Analysis based on music theory principles from the music_theory_data module

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Basic understanding of audio engineering concepts

### Installation

#### Option 1: Standard Installation

1. Clone the repository
```bash
git clone https://github.com/owgit/ai-music-mix-analyzer.git
cd ai-music-mix-analyzer
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit the .env file with your actual API keys
# Generate a secret key: python scripts/generate_secret_key.py --update-env
```

#### Option 2: Docker Installation

1. Clone the repository
```bash
git clone https://github.com/owgit/ai-music-mix-analyzer.git
cd ai-music-mix-analyzer
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit the .env file with your actual API keys
# Generate a secret key: python scripts/generate_secret_key.py --update-env
```

3. Run the application using Docker Compose
```bash
docker-compose up -d
```

Or use the provided script:
```bash
chmod +x run.sh
./run.sh
```

4. To stop the Docker container:
```bash
docker-compose down
```

Or use the provided script:
```bash
chmod +x stop.sh
./stop.sh
```

### Updating the Application

To update the application to the latest version, use the provided update script:

```bash
chmod +x update.sh
./update.sh
```

The script will:
- Pull the latest changes from the Git repository
- Rebuild Docker containers
- Restart the application with the latest code

### Running the Application

#### Standard Run
```bash
python wsgi.py
```

Or use the management script:
```bash
python manage.py run
```

The application will start on `http://127.0.0.1:5001`.

#### Docker Run
When using Docker, the application will be available at `http://localhost:5001`.

## 🔌 API Endpoints

### Upload Audio File

```
POST /upload
```

Parameters:
- `file`: Audio file (mp3, wav, flac, aiff, ogg)
- `is_instrumental`: Boolean indicating if the track is instrumental

### Regenerate Visualizations

```
POST /regenerate_visualizations/<file_id>
```

Parameters:
- `file_id`: ID of the uploaded file

### Analyze File (API)

```
GET /api/analyze/<file_id>
```

Parameters:
- `file_id`: ID of the uploaded file
- `api_key`: Your API key (via X-API-Key header or query parameter)

## 🔒 Security Features

- Rate limiting with Flask-Limiter (200 requests per day, 50 per hour)
- Content Security Policy (CSP) headers
- Secure file uploads with:
  - File extension validation
  - MIME type validation
  - Secure filenames
  - Maximum file size limit (50MB)
- Input validation for all endpoints
- Directory traversal protection
- X-Content-Type-Options, X-Frame-Options, X-XSS-Protection headers
- Strict-Transport-Security in production
- Docker deployment with non-root user and secure permissions
- API key authentication for API endpoints
- Health check monitoring for Docker containers

## 💡 Development

### Project Structure

```
music/
├── app/                  # Main application code
│   ├── __init__.py       # Application factory
│   ├── routes.py         # Main route definitions
│   ├── api/              # API endpoints
│   ├── core/             # Core audio processing logic
│   │   ├── audio_analyzer.py  # Audio analysis engine
│   │   ├── openai_analyzer.py # AI integration
│   │   ├── utils.py      # Utility functions
│   │   └── music_theory_data/ # Music theory reference data
│   ├── data/             # Application data storage
│   ├── static/           # Static files
│   │   ├── css/          # CSS files
│   │   ├── js/           # JavaScript files
│   │   └── img/          # Images and icons
│   ├── templates/        # HTML templates
│   │   ├── guides/       # User guides
│   │   ├── index.html    # Main application page
│   │   └── about.html    # About page
│   ├── utils/            # Utility functions
│   └── healthcheck.py    # Docker health check endpoint
├── config/               # Configuration files
│   ├── .env.example      # Example environment variables
│   └── docker/           # Docker configuration files
├── docs/                 # Documentation
├── scripts/              # Utility scripts
│   ├── security_check.py # Security audit script
│   ├── generate_secret_key.py # Key generation
│   └── sanitize_env.py   # Environment sanitizer
├── tests/                # Test suite
├── uploads/              # Audio file uploads
├── logs/                 # Application logs
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker Compose configuration
├── docker-compose.override.yml.example # Example Docker override
├── Dockerfile            # Docker container definition
├── wsgi.py               # WSGI entry point
├── manage.py             # Management script
├── run.sh                # Script to start the application
├── stop.sh               # Script to stop the application
├── update.sh             # Script to update the application
└── LICENSE               # License information
```

### Docker Configuration

The Docker setup includes:

- Base image: `python:3.9-slim`
- Required system dependencies (libsndfile1, ffmpeg)
- Volume mapping for persistent storage of uploads and cache
- Port mapping: 5001 (host) -> 5000 (container)
- Resource limits: 4GB max memory, 1GB reservation
- Non-root user for security (UID:GID 1007:1008)
- Health monitoring with regular checks
- Log rotation with 20MB max file size and 5 file limit
- Automatic environment detection (dev, test, prod)

### Security Audit

Run the security check script to identify potential security issues:

```bash
python scripts/security_check.py
```

Or use the management script:

```bash
python manage.py check --security
```

These scripts check for common security misconfigurations and vulnerabilities.

## 📄 Environment Configuration

### Environment Files

The project uses a structured approach to environment variables:

1. **Root `.env` File**
   - Primary source of all configuration variables
   - Contains API keys, model settings, security keys and application settings
   - Created from `.env.example` when setting up the project
   - Values defined here are used by both standard and Docker installations

2. **Docker-specific Settings**
   - `config/docker/.env` contains only Docker-specific overrides
   - These values extend or override the root .env file settings when using Docker

3. **Local Overrides**
   - `docker-compose.override.yml` allows additional customization for your local Docker installation
   - Created from `docker-compose.override.yml.example`

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| **AI Integration** |  |  |
| `AI_PROVIDER` | Which AI provider to use ("openai" or "openrouter") | "openai" |
| `OPENAI_API_KEY` | Your OpenAI API key | None (required if using OpenAI) |
| `OPENAI_MODEL` | OpenAI model to use | "gpt-4o-mini" |
| `OPENROUTER_API_KEY` | Your OpenRouter API key | None (required if using OpenRouter) |
| `OPENROUTER_MODEL` | OpenRouter model to use | "anthropic/claude-3-haiku-20240307" |
| `SITE_URL` | Site URL for OpenRouter tracking | None (optional) |
| `SITE_TITLE` | Site title for OpenRouter tracking | "Mix Analyzer" |
| **Security** |  |  |
| `API_KEY` | Internal API authentication key | Generated |
| `SECRET_KEY` | Flask secret key | Generated |
| `FLASK_APP` | Flask application entry point | "app.py" |
| `FLASK_ENV` | Flask environment | "development" |
| **Analytics** |  |  |
| `ENABLE_ANALYTICS` | Whether to enable analytics | "false" |
| `MATOMO_URL` | Analytics platform URL | None |
| `MATOMO_SITE_ID` | Analytics site ID | None |
| **Other** |  |  |
| `PYTHONUNBUFFERED` | Forces Python to run unbuffered | "1" |

### Available AI Models

#### OpenAI Models (Default provider)
- `gpt-4o-2024-11-20` (Latest version with enhanced creative writing)
- `gpt-4o-2024-08-06` (Previous GPT-4o version)
- `gpt-4o-mini` (Fast, cost-effective model, default)
- `gpt-4-turbo-2024-04-09` (With vision capabilities)
- `gpt-3.5-turbo` (Cost-effective for simpler tasks)

#### OpenRouter Models (Alternative provider)
- `anthropic/claude-3-opus-20240229` (Anthropic's most powerful model)
- `anthropic/claude-3-sonnet-20240229` (Good balance of performance and speed)
- `anthropic/claude-3-haiku-20240307` (Fast, cost-effective)
- `google/gemini-1.5-pro-latest` (Google's advanced model)
- `meta-llama/llama-3-70b-instruct` (Meta's powerful open model)
- `mistralai/mistral-large-latest` (Mistral's flagship model)
- `mistralai/mixtral-8x7b-instruct` (Strong open-source mixture of experts model)
- Many other models accessible through OpenRouter

### OpenRouter Variants
OpenRouter supports various model variants that can be added as suffixes:

- Static variants (model-specific):
  - `:free` - Free tier with low rate limits
  - `:beta` - Unmoderated by OpenRouter
  - `:extended` - Longer context length
  - `:thinking` - Reasoning enabled by default

- Dynamic variants (work with all models):
  - `:online` - Runs web search queries automatically
  - `:nitro` - Prioritizes throughput over cost
  - `:floor` - Prioritizes cost-effectiveness over speed

Example: `anthropic/claude-3-haiku-20240307:nitro`

### Sanitizing Environment Files

To prevent accidentally committing API keys and secrets:

```bash
python scripts/sanitize_env.py
```

Or use the management script:

```bash
python manage.py security --sanitize
```

This script removes sensitive information from all environment files before committing.

## 🛠 Script Organization & Project Management

### Management Script

The project includes a unified management script (`manage.py`) that provides a streamlined interface for common tasks:

```bash
# Run the Flask application
./manage.py run [--production] [--port PORT]

# Run project checks
./manage.py check [--all|--project|--security|--env|--imports|--uploads]

# Set up the environment
./manage.py setup [--generate-key] [--apple-silicon]

# Run Docker commands
./manage.py docker --start|--stop|--update

# Handle security tasks
./manage.py security --sanitize [--dry-run] | --check
```

### Helper Scripts

Additional scripts are provided for convenience:

- `run.sh`: Start the application in Docker
- `stop.sh`: Stop the Docker containers
- `update.sh`: Update the application to the latest version

## 🔍 How It Works

The application combines advanced DSP (Digital Signal Processing) algorithms with modern web technologies to provide deep insights into your mix:

### Audio Analysis

The application performs these professional-grade analyses:

1. **Frequency Balance Analysis**:
   - Divides the frequency spectrum into 7 critical bands:
     - Sub-bass (20-60Hz)
     - Bass (60-250Hz)
     - Low-mids (250-500Hz)
     - Mids (500-2kHz)
     - High-mids (2-4kHz)
     - Highs (4-10kHz)
     - Air (10-20kHz)
   - Measures energy distribution using FFT analysis
   - Compares to industry-standard reference curves
   - Identifies potential issues like muddy bass (200-300Hz buildup) or harsh highs (2-5kHz peaks)

2. **Dynamic Range Analysis**:
   - Calculates dynamic range in dB
   - Measures crest factor
   - Evaluates peak-to-loudness ratio (PLR)
   - Detects over-compression

3. **Stereo Field Analysis**:
   - Measures correlation between channels
   - Analyzes mid/side balance
   - Detects phase issues
   - Evaluates stereo width

4. **Clarity Analysis**:
   - Measures spectral contrast
   - Analyzes spectral flatness
   - Evaluates spectral centroid
   - Identifies potential masking issues

5. **Harmonic Content Analysis**:
   - Key detection
   - Harmonic complexity measurement
   - Key consistency evaluation

6. **Transient Analysis**:
   - Attack time measurement
   - Transient density evaluation
   - Percussion energy analysis

7. **3D Spatial Analysis**:
   - Height perception measurement
   - Depth perception analysis
   - Width consistency evaluation
   - Interactive 3D visualization
   - Color-coded stereo width mapping
   - Surround compatibility assessment
   - Headphone/speaker optimization

### AI-Powered Mix Feedback

When an AI API key is provided, the application can:

- Provide a summary of the mix quality with genre context
- Identify strengths of the mix
- Point out areas for improvement
- Offer specific suggestions for enhancing the mix
- Recommend reference tracks for comparison
- Suggest specific processing techniques
- Deliver context-specific insights within each tab:
  - Frequency-specific recommendations in the Frequency Balance tab
  - Dynamics recommendations in the Dynamic Range tab
  - Stereo field suggestions in the Stereo Analysis tab
  - Spatial enhancement ideas in the 3D Spatial tab

The AI analysis is performed using either:
- OpenAI's GPT models (default)
- Alternative providers through OpenRouter (Claude, Gemini, Llama, Mistral, etc.)

## 📊 Visualizations

The application generates several visualizations to help you understand your mix:

1. **Waveform**: Shows the amplitude of the audio over time
2. **Spectrogram**: Displays frequency content over time
3. **Frequency Spectrum**: Shows the average energy at each frequency
4. **Stereo Field**: Visualizes the relationship between left and right channels
5. **3D Spatial Field**: Interactive 3D visualization of your mix's spatial characteristics

All visualizations are interactive:
- Click on any visualization to open it in a larger view
- Use the zoom controls to zoom in and out
- Drag to pan around when zoomed in
- Rotate and adjust the 3D visualization for different perspectives
- Press the Reset button to return to the original view

## 🧪 Testing

The project includes comprehensive testing using pytest:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run specific test files
pytest tests/test_audio_analyzer.py
```

The test suite covers:
- Audio analysis functionality
- API endpoints
- Security features
- UI functionality (using Selenium)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request or create issues for bugs and feature requests.

## 📝 License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License - see the [LICENSE](LICENSE) file for details. This license prohibits commercial use of this software without explicit permission.

## 🌐 Official Website

Visit [mixanalytic.com](https://mixanalytic.com) for the latest version, documentation, and online features.

## 👨‍💻 Author

Developed by Uygar Duzgun
- Website: [uygarduzgun.com](https://uygarduzgun.com)
- Project: [mixanalytic.com](https://mixanalytic.com)
- GitHub: [owgit](https://github.com/owgit)
- Support: [Buy Me a Coffee](https://buymeacoffee.com/uygarduzgun)

## 🔑 Keywords

audio analysis, music production tool, mix analyzer, mastering assistant, frequency analysis, stereo field analyzer, dynamic range measurement, phase correlation, music production software, audio engineering, sound engineering, spectral analysis, waveform visualization, audio processing, mix analytics, mixanalytic, AI mix feedback, GPT-4o

---

© 2024 Uygar Duzgun. All rights reserved. | [mixanalytic.com](https://mixanalytic.com)

