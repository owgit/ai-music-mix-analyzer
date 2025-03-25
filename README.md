# Music Mix Analyzer - Professional Audio Analysis Tool

<p align="center">
  <img src="app/static/img/music-analyzer-icon.svg" alt="Music Mix Analyzer Logo" width="180" />
</p>

A powerful Flask-based web application for audio mixing analysis, mastering assistance, and professional music production visualization. Perfect for sound engineers, music producers, and audio enthusiasts.

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Website: mixanalytic.com](https://img.shields.io/badge/Website-mixanalytic.com-blue.svg)](https://mixanalytic.com)
[![GitHub: owgit/ai-music-mix-analyzer](https://img.shields.io/badge/GitHub-owgit/ai--music--mix--analyzer-green.svg)](https://github.com/owgit/ai-music-mix-analyzer)

## 🎧 Features

- **Audio Analysis**: Upload and analyze audio files (mp3, wav, flac) with professional-grade tools
- **Visualization Suite**: Generate high-resolution spectrograms and waveform visualizations
- **Stereo Field Analysis**: Comprehensive stereo imaging and phase correlation analysis
- **AI-Powered Mix Feedback**: Get intelligent suggestions using advanced audio algorithms
- **Frequency Response**: Analyze frequency distribution and identify problematic areas
- **Dynamic Range**: Measure compression levels and dynamic range in your mixes
- **Security**: Enterprise-grade file handling with robust security measures

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
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

### Running the Application

#### Standard Run
```bash
python wsgi.py
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
- `file`: Audio file (mp3, wav, flac)
- `isInstrumental`: Boolean indicating if the track is instrumental

### Regenerate Visualizations

```
GET /regenerate_visualizations/<file_id>
```

Parameters:
- `file_id`: UUID of the uploaded file

### Regenerate Stereo Field

```
GET /regenerate_stereo_field/<file_id>
```

Parameters:
- `file_id`: UUID of the uploaded file

## 🔒 Security Features

- Rate limiting with Flask-Limiter
- Content Security Policy (CSP) headers
- Secure file uploads with:
  - File extension validation
  - MIME type validation
  - UUID-based filenames
  - Maximum file size limit (100MB)
- Input validation for all endpoints
- Directory traversal protection
- X-Content-Type-Options, X-Frame-Options, X-XSS-Protection headers
- Strict-Transport-Security in production

## 💡 Development

### Project Structure

```
music/
├── app/                  # Main application code
│   ├── __init__.py       # Application factory
│   ├── routes.py         # Main route definitions
│   ├── api/              # API endpoints
│   ├── core/             # Core audio processing logic
│   ├── static/           # Static files
│   │   ├── css/          # CSS files
│   │   ├── js/           # JavaScript files
│   │   └── img/          # Images and icons
│   └── templates/        # HTML templates
├── config/               # Configuration files
│   ├── .env.example      # Example environment variables
│   └── docker/           # Docker configuration files
│       ├── Dockerfile    # Container definition
│       └── docker-compose.yml # Multi-container setup
├── docs/                 # Documentation
│   ├── CONTRIBUTING.md   # Contribution guidelines
│   └── TROUBLESHOOTING.md # Common issues and solutions
├── scripts/              # Utility scripts
│   ├── security_check.py # Security audit script
│   ├── generate_secret_key.py # Key generation
│   ├── run.sh            # Start the application
│   └── stop.sh           # Stop the application
├── tests/                # Test suite
├── uploads/              # Audio file uploads
├── logs/                 # Application logs
├── .env.example          # Example environment variables
├── requirements.txt      # Python dependencies
├── wsgi.py               # WSGI entry point
└── LICENSE               # License information
```

### Docker Configuration

The Docker setup includes:

- Base image: `python:3.9-slim`
- Required system dependencies (libsndfile1, ffmpeg)
- Volume mapping for persistent storage of uploads
- Port mapping: 5001 (host) -> 5000 (container)
- Environment variable support, including OpenAI API key

### Security Audit

Run the security check script to identify potential security issues:

```bash
python scripts/security_check.py
```

This script checks for common security misconfigurations and vulnerabilities.

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
| **API Keys** |  |  |
| `OPENAI_API_KEY` | Your OpenAI API key | None (required) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key (optional) | None |
| **Model Configuration** |  |  |
| `AI_PROVIDER` | Which AI provider to use ("openai" or "openrouter") | "openai" |
| `OPENAI_MODEL` | OpenAI model to use | "gpt-4o-mini" |
| `OPENROUTER_MODEL` | OpenRouter model to use | "anthropic/claude-3-haiku-20240307" |
| **Security** |  |  |
| `API_KEY` | Internal API authentication key | Generated |
| `SECRET_KEY` | Flask secret key | Generated |
| **Analytics** |  |  |
| `ENABLE_ANALYTICS` | Whether to enable analytics | "false" |
| `MATOMO_URL` | Analytics platform URL | None |
| `MATOMO_SITE_ID` | Analytics site ID | None |

### Sanitizing Environment Files

To prevent accidentally committing API keys and secrets:

```bash
python scripts/sanitize_env.py
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

### Script Directory Structure

Scripts are organized in a modular structure for better maintainability:

```
scripts/
├── __init__.py          # Makes scripts a Python package
├── run_checks.py        # Comprehensive check runner
├── utils/               # Utility scripts
│   ├── __init__.py
│   ├── env_loader.py    # Environment variable loader
│   ├── sanitize_env.py  # Environment file sanitizer
│   └── migrate_uploads.py # Uploads directory migration
├── setup/               # Setup scripts
│   ├── __init__.py
│   ├── generate_secret_key.py # Secret key generator
│   └── setup_apple_silicon.sh # Apple Silicon setup
├── checks/              # Validation scripts
│   ├── __init__.py
│   ├── check_app_structure.py # App structure validation
│   ├── check_env_consistency.py # Environment validation
│   ├── security_check.py # Security audit
│   └── ... (other check scripts)
└── docker/              # Docker-related scripts
    ├── __init__.py
    ├── run.sh           # Start Docker containers
    ├── stop.sh          # Stop Docker containers
    └── update.sh        # Update Docker containers
```

### Common Script Tasks

**Environment Setup**:
```bash
# Generate a new secure secret key
python -m scripts.setup.generate_secret_key --update-env

# Check environment configuration
python -m scripts.checks.check_env_consistency
```

**Security**:
```bash
# Sanitize environment files (remove API keys)
python -m scripts.utils.sanitize_env

# Run security check
python -m scripts.checks.security_check
```

**Docker Management**:
```bash
# Start Docker containers
./scripts/docker/run.sh

# Stop Docker containers
./scripts/docker/stop.sh
```

**Project Validation**:
```bash
# Run all project checks
python scripts/run_checks.py
```

## 🖥️ User Interface

## 🔍 How It Works

The application combines advanced DSP (Digital Signal Processing) algorithms with modern web technologies to provide deep insights into your mix:

- **Frequency Balance**: Evaluates if your mix has proper distribution across the frequency spectrum (20Hz-20kHz)
- **Dynamic Range**: Measures the difference between the loudest and quietest parts using industry-standard metrics
- **Stereo Field**: Analyzes the stereo image, panning, and phase correlation between channels
- **Clarity**: Detects potential masking issues or muddiness that could affect mix translation

Additionally, the application can leverage OpenAI's GPT-4o to provide AI-powered insights and professional suggestions for improving your mix quality.

## 📊 Technical Details

### Audio Analysis

The application performs these professional-grade analyses:

1. **Frequency Balance Analysis**:
   - Divides the frequency spectrum into critical bands (sub-bass, bass, low-mids, mids, high-mids, highs, air)
   - Measures energy distribution using FFT analysis
   - Compares to industry-standard reference curves
   - Identifies potential issues like muddy bass (200-300Hz buildup) or harsh highs (2-5kHz peaks)

2. **Dynamic Range Analysis**:
   - Calculates dynamic range in dB
   - Measures crest factor
   - Evaluates peak-to-loudness ratio
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

### Visualizations

The application generates several visualizations to help you understand your mix:

1. **Waveform**: Shows the amplitude of the audio over time
2. **Spectrogram**: Displays frequency content over time
3. **Frequency Spectrum**: Shows the average energy at each frequency
4. **Stereo Field**: Visualizes the relationship between left and right channels

All visualizations are interactive:
- Click on any visualization to open it in a larger view
- Use the zoom controls (+ and -) to zoom in and out
- Drag to pan around when zoomed in
- Press the Reset button to return to the original view
- Keyboard shortcuts: + to zoom in, - to zoom out, 0 to reset, Esc to close

### AI Insights

When an OpenAI API key is provided, the application uses GPT-4o to:

- Provide a summary of the mix quality
- Identify strengths of the mix
- Point out areas for improvement
- Offer specific suggestions for enhancing the mix

## 🔧 Requirements

- Python 3.8+
- Dependencies listed in requirements.txt
- OpenAI API key (optional, for AI-powered mix recommendations)

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

## 🔑 Keywords

audio analysis, music production tool, mix analyzer, mastering assistant, frequency analysis, stereo field analyzer, dynamic range measurement, phase correlation, music production software, audio engineering, sound engineering, spectral analysis, waveform visualization, audio processing, mix analytics, mixanalytic

---

© 2023 Uygar Duzgun. All rights reserved. | [mixanalytic.com](https://mixanalytic.com)

