"""
Main routes for the Music Mix Analyzer application
"""

import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_from_directory, Response, current_app
from werkzeug.utils import secure_filename
import uuid
import traceback
import json
from datetime import datetime
from pathlib import Path

from app.core.audio_analyzer import analyze_mix, generate_visualizations, convert_numpy_types, generate_3d_spatial_visualization
from app.core.openai_analyzer import analyze_with_gpt
from app.core.database import calculate_file_hash, find_song_by_hash, save_song, delete_song_by_filename

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'wav', 'flac', 'aiff', 'ogg'}

@main_bp.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')

@main_bp.route('/sitemap.xml')
def sitemap():
    """Generate a sitemap.xml"""
    # Use site domain for explicit HTTPS URLs
    site_domain = request.host
    
    # Define your URLs with explicit https protocol
    urls = [
        {'loc': f'https://{site_domain}/', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '1.0'},
        {'loc': f'https://{site_domain}/about', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.8'},
        {'loc': f'https://{site_domain}/3d-spatial-analysis', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.9'},
        {'loc': f'https://{site_domain}/dolby-atmos-mixing', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.9'},
        {'loc': f'https://{site_domain}/immersive-audio-guide', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.8'},
        {'loc': f'https://{site_domain}/spatial-audio-tips', 'lastmod': datetime.now().strftime('%Y-%m-%d'), 'priority': '0.8'},
        # Add more URLs as needed
    ]
    
    sitemap_xml = render_template('sitemap.xml', urls=urls)
    response = Response(sitemap_xml, mimetype='application/xml')
    
    # Add cache control headers to prevent caching with wrong URL
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@main_bp.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    # Get site domain for explicit HTTPS URLs
    site_domain = request.host
    
    robots_txt = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /uploads/
Disallow: /api/
Disallow: /*.json$

# Specific directives for major crawlers
User-agent: Googlebot
Allow: /
Crawl-delay: 1

User-agent: Bingbot
Allow: /
Crawl-delay: 2

User-agent: Baiduspider
Disallow: /

# Sitemap location - explicitly using HTTPS
Sitemap: https://{site_domain}/sitemap.xml
"""
    return Response(robots_txt, mimetype='text/plain')

@main_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    print("Upload endpoint called")
    
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("No file selected")
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        # Get the instrumental flag
        is_instrumental = request.form.get('is_instrumental', 'false').lower() == 'true'
        print(f"Is instrumental: {is_instrumental}")
        
        # Log all form data for debugging
        print("Form data received:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
        
        # Generate a unique ID for the file
        file_id = secure_filename(os.path.splitext(file.filename)[0])
        
        # Create directory for this upload
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, f"{file_id}.mp3")
        file.save(file_path)
        
        try:
            # Calculate file hash
            file_hash = calculate_file_hash(file_path)
            print(f"File hash: {file_hash}")
            
            # Check if the file already exists in the database
            existing_song = find_song_by_hash(file_hash)
            
            if existing_song:
                print(f"Found existing song: {existing_song['title']}")
                
                # Return the existing analysis results
                try:
                    # Parse the saved analysis JSON
                    results = json.loads(existing_song['analysis_data']) if existing_song['analysis_data'] else None
                    
                    if results:
                        print("Using existing analysis results from database")
                        
                        # Return the cached results
                        response_data = {
                            'filename': file.filename,
                            'results': results,
                            'from_cache': True
                        }
                        
                        return jsonify(response_data)
                    else:
                        print("Existing record found but no analysis data, performing new analysis")
                except Exception as e:
                    print(f"Error parsing existing analysis: {str(e)}")
                    print("Performing new analysis instead")
            
            # If we reach here, we need to analyze the file
            # Analyze the mix with instrumental flag
            results = analyze_mix(file_path, is_instrumental)
            
            # Generate AI insights if possible
            try:
                ai_insights = analyze_with_gpt(results, is_instrumental)
                results["ai_insights"] = ai_insights
                
                # Get the AI provider and model being used
                ai_provider = os.environ.get("AI_PROVIDER", "openai").lower()
                if ai_provider == "openrouter":
                    model_name = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku-20240307")
                else:
                    model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
                    
                # Add the model information to the AI insights
                results["ai_insights"]["model_used"] = model_name
                
            except Exception as e:
                print(f"Error generating AI insights: {str(e)}")
                results["ai_insights"] = {
                    "error": str(e),
                    "summary": "Unable to generate AI insights at this time.",
                    "strengths": ["N/A"],
                    "weaknesses": ["N/A"],
                    "suggestions": ["N/A"],
                    "model_used": "Unknown"
                }
            
            # Regenerate visualizations to ensure they're up to date
            try:
                print("Generating visualizations...")
                visualizations = generate_visualizations(file_path, file_id=file_id)
                results["visualizations"] = visualizations
                print(f"Visualizations generated: {visualizations}")
            except Exception as e:
                print(f"Error generating visualizations: {str(e)}")
                traceback.print_exc()
            
            # Convert NumPy types to standard Python types for JSON serialization
            results = convert_numpy_types(results)
            print("NumPy types converted successfully")
            
            # Save the analysis results to the database
            try:
                save_song(
                    filename=file_id,
                    original_name=file.filename,
                    file_path=file_path,
                    file_hash=file_hash,
                    is_instrumental=is_instrumental,
                    analysis_json=results
                )
                print("Song analysis saved to database")
            except Exception as e:
                print(f"Error saving song to database: {str(e)}")
                traceback.print_exc()
            
            # Return the results
            response_data = {
                'filename': file.filename,
                'results': results,
                'from_cache': False
            }
            
            print("Response data successfully serialized to JSON")
            return jsonify(response_data)
            
        except Exception as e:
            print(f"Error analyzing file: {str(e)}")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@main_bp.route('/regenerate_visualizations/<file_id>', methods=['POST'])
def regenerate_visualizations_route(file_id):
    """Regenerate visualizations for a specific file"""
    try:
        # Construct the path to the uploaded file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id, f"{file_id}.mp3")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Generate visualizations
        visualizations = generate_visualizations(file_path, file_id=file_id)
        
        return jsonify({
            'success': True,
            'visualizations': visualizations
        })
    except Exception as e:
        print(f"Error regenerating visualizations: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/regenerate_stereo_field/<file_id>', methods=['POST'])
def regenerate_stereo_field(file_id):
    """Regenerate just the stereo field visualization with enhanced detection"""
    try:
        # Construct the path to the uploaded file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id, f"{file_id}.mp3")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Import necessary libraries here to avoid circular imports
        import librosa
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Load the audio file with librosa
        y, sr = librosa.load(file_path, sr=None, mono=False)
        
        # Create visualization directory
        vis_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id)
        os.makedirs(vis_dir, exist_ok=True)
        
        # Enhanced stereo detection
        is_stereo = y.ndim > 1 and y.shape[0] >= 2
        channels_identical = False
        
        if is_stereo:
            # Compare samples of left and right channels
            sample_size = min(10000, y.shape[1])
            left_samples = y[0, :sample_size]
            right_samples = y[1, :sample_size]
            
            # Use correlation instead of exact matching for better detection
            correlation = np.corrcoef(left_samples, right_samples)[0, 1]
            channels_identical = correlation > 0.99
            
            print(f"Audio file: {file_id}")
            print(f"Audio shape: {y.shape}, dimensions: {y.ndim}")
            print(f"Channel correlation: {correlation}")
            print(f"Channels effectively identical: {channels_identical}")
        
        # Generate stereo field visualization
        plt.figure(figsize=(10, 4))
        
        if is_stereo and not channels_identical:
            # Plot stereo field
            plt.plot(y[0, :sr], y[1, :sr], '.', alpha=0.1, markersize=1, color='#1f77b4')
            plt.xlabel('Left Channel')
            plt.ylabel('Right Channel')
            plt.title('Stereo Field (First Second)')
            plt.axis('equal')
            plt.grid(True)
        else:
            # Create placeholder for mono audio
            if is_stereo and channels_identical:
                message = f'Identical Channels - Effectively Mono (Correlation: {correlation:.4f})'
            else:
                message = 'Mono Audio - No Stereo Field'
                
            plt.text(0.5, 0.5, message, 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=14)
            plt.axis('off')
        
        plt.tight_layout()
        stereo_path = os.path.join(vis_dir, 'stereo_field.png')
        plt.savefig(stereo_path)
        plt.close()
        
        # Return the path with proper URL format
        stereo_url = f"/static/uploads/{file_id}/stereo_field.png"
        
        return jsonify({
            'success': True,
            'stereo_field_url': stereo_url,
            'is_stereo': is_stereo,
            'channels_identical': channels_identical if is_stereo else None,
            'correlation': float(correlation) if is_stereo else None
        })
    except Exception as e:
        print(f"Error regenerating stereo field: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/static/img/error.png')
def serve_error_image():
    """Serve a placeholder error image"""
    return send_from_directory(current_app.static_folder, 'img/error.png')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@main_bp.route('/3d-spatial-analysis')
def spatial_analysis_guide():
    """3D Spatial Analysis guide page"""
    return render_template('guides/3d-spatial-analysis.html')

@main_bp.route('/dolby-atmos-mixing')
def dolby_atmos_guide():
    """Dolby Atmos Mixing guide page"""
    return render_template('guides/dolby-atmos-mixing.html')

@main_bp.route('/immersive-audio-guide')
def immersive_audio_guide():
    """Immersive Audio guide page"""
    return render_template('guides/immersive-audio-guide.html')

@main_bp.route('/spatial-audio-tips')
def spatial_audio_tips():
    """Spatial Audio Tips guide page"""
    return render_template('guides/spatial-audio-tips.html')

@main_bp.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback submission"""
    try:
        # Get the feedback data from request
        data = request.json
        
        # Validate required fields
        required_fields = ['rating', 'feedback_type', 'message', 'consent']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Ensure consent is provided
        if not data.get('consent'):
            return jsonify({'error': 'Consent is required'}), 400
        
        # Create the feedback directory if it doesn't exist
        feedback_dir = os.path.join(current_app.instance_path, '..', 'app', 'data', 'feedback')
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Create a unique ID for the feedback
        feedback_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Prepare the feedback data
        feedback_data = {
            'id': feedback_id,
            'timestamp': timestamp,
            'rating': data.get('rating'),
            'feedback_type': data.get('feedback_type'),
            'message': data.get('message'),
            'email': data.get('email', ''),  # Optional
            'user_agent': request.user_agent.string,
            'ip_hash': hash(request.remote_addr)  # Store hash instead of actual IP
        }
        
        # Create the filename with timestamp for uniqueness
        date_prefix = datetime.now().strftime('%Y%m%d')
        filename = f"{date_prefix}_{feedback_id}.json"
        file_path = os.path.join(feedback_dir, filename)
        
        # Write the data to file
        with open(file_path, 'w') as f:
            json.dump(feedback_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'feedback_id': feedback_id
        })
        
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/regenerate_spatial_field/<file_id>', methods=['GET', 'POST'])
def regenerate_spatial_field_api(file_id):
    """Regenerate the 3D spatial field visualization for the specified file_id"""
    try:
        # Construct the path to the uploaded file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id, f"{file_id}.mp3")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found', 'success': False}), 404
        
        # Import necessary libraries here to avoid circular imports
        import librosa
        from app.core.audio_analyzer import generate_3d_spatial_visualization
        
        # Load the audio file with librosa
        y, sr = librosa.load(file_path, sr=None, mono=False)
        
        # Create visualization directory
        vis_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id)
        os.makedirs(vis_dir, exist_ok=True)
        
        # Generate the 3D spatial visualization
        spatial_result = generate_3d_spatial_visualization(y, sr, vis_dir)
        
        # Check the result format
        if isinstance(spatial_result, dict) and 'html' in spatial_result and 'image' in spatial_result:
            return jsonify({
                'success': True,
                'image_path': spatial_result['image'],
                'interactive_path': spatial_result['html']
            })
        elif spatial_result:
            # It's just a string path to the image
            return jsonify({
                'success': True,
                'image_path': spatial_result,
                'interactive_path': None
            })
        else:
            raise ValueError("Failed to generate 3D visualization")
            
    except Exception as e:
        print(f"Error regenerating 3D spatial field: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@main_bp.route('/api/delete-track', methods=['POST'])
def delete_track():
    """Delete a track from the database and file system"""
    try:
        # Get the file ID from the request
        data = request.get_json()
        if not data or 'fileId' not in data:
            print("No file ID provided in request")
            return jsonify({'success': False, 'message': 'No file ID provided'}), 400
        
        file_id = data['fileId']
        print(f"Received delete request for file ID: {file_id}")
        
        # Delete from database
        db_result = delete_song_by_filename(file_id)
        print(f"Database deletion result: {db_result}")
        
        if db_result:
            # If database deletion successful, also delete files
            try:
                # Get the upload directory for this file
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id)
                print(f"Checking upload directory: {upload_dir}")
                
                if not os.path.exists(upload_dir):
                    print(f"Upload directory does not exist: {upload_dir}")
                    return jsonify({
                        'success': True, 
                        'message': 'Track deleted from database, but no files found to delete'
                    })
                
                # Delete the audio file
                audio_file = os.path.join(upload_dir, f"{file_id}.mp3")
                deleted_files = []
                
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    deleted_files.append(audio_file)
                    print(f"Deleted audio file: {audio_file}")
                
                # Delete all visualization files (common extensions)
                for ext in ['.png', '.jpg', '.jpeg', '.html']:
                    for f in Path(upload_dir).glob(f"*{ext}"):
                        os.remove(f)
                        deleted_files.append(str(f))
                        print(f"Deleted file: {f}")
                
                # Try to remove the directory
                try:
                    os.rmdir(upload_dir)
                    print(f"Removed directory: {upload_dir}")
                except OSError as e:
                    print(f"Could not remove directory: {e}")
                    # Directory might not be empty, that's okay
                    pass
                
                return jsonify({
                    'success': True, 
                    'message': f'Track deleted successfully. Removed {len(deleted_files)} files'
                })
            except Exception as e:
                # Database deletion succeeded but file deletion failed
                print(f"Error deleting files for {file_id}: {str(e)}")
                return jsonify({
                    'success': True, 
                    'message': 'Track deleted from database but some files may remain',
                    'error': str(e)
                })
        
        # Database deletion failed
        print(f"Database deletion failed for file ID: {file_id}")
        return jsonify({'success': False, 'message': 'Failed to delete track from database'})
        
    except Exception as e:
        print(f"Error deleting track: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500 