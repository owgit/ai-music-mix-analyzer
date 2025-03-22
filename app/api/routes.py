"""
API routes for the Music Mix Analyzer application
"""

from flask import Blueprint, jsonify, request
import os
import traceback

from app.core.audio_analyzer import analyze_mix, convert_numpy_types
from app.api import require_api_key

# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/test-data', methods=['GET'])
@require_api_key
def test_data():
    """Return test data for frontend development"""
    return jsonify({
        'message': 'API is working',
        'data': {
            'frequency_bands': {
                'sub_bass': 10,
                'bass': 15,
                'low_mids': 20,
                'mids': 25,
                'high_mids': 20,
                'highs': 15,
                'air': 5
            },
            'scores': {
                'frequency_balance': 85,
                'dynamic_range': 75,
                'stereo_field': 90,
                'clarity': 80,
                'overall': 82
            }
        }
    })

@api_bp.route('/analyze/<file_id>', methods=['GET'])
@require_api_key
def analyze_file(file_id):
    """Analyze a specific file and return the results"""
    try:
        # Sanitize file_id to prevent path traversal
        file_id = os.path.basename(file_id)
        
        # Construct the path to the uploaded file
        from flask import current_app
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id, f"{file_id}.mp3")
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Analyze the mix
        results = analyze_mix(file_path)
        
        # Convert NumPy types to standard Python types for JSON serialization
        results = convert_numpy_types(results)
        
        return jsonify({
            'file_id': file_id,
            'results': results
        })
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 