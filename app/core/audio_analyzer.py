import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy import stats
import os
from pydub import AudioSegment
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from .music_theory_data.key_relationships import get_key_relationship_info

def convert_numpy_types(obj):
    """
    Convert NumPy types to standard Python types for JSON serialization.
    Also handles NaN, Inf, and -Inf values.
    
    Args:
        obj: Any Python object that might contain NumPy types
        
    Returns:
        Object with NumPy types converted to standard Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj):
            return 0.0  # Convert NaN to 0.0
        elif np.isinf(obj):
            return 0.0 if obj < 0 else 100.0  # Convert -Inf to 0.0 and Inf to 100.0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_numpy_types(x) for x in obj.tolist()]
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj

def analyze_mix(file_path):
    """
    Analyze an audio file and return metrics about the mix quality.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        print(f"Loading audio file for analysis: {file_path}")
        # Load the audio file with mono=False to preserve stereo
        y, sr = librosa.load(file_path, sr=None, mono=False)
        
        print(f"Loaded audio shape: {y.shape}, dimensions: {y.ndim}")
        
        # Handle mono files by duplicating the channel
        if y.ndim == 1:
            print("Mono file detected, converting to stereo format")
            y = np.vstack((y, y))
        elif y.ndim == 2 and y.shape[0] == 1:
            print("Single channel detected, converting to stereo format")
            y = np.vstack((y[0], y[0]))
        elif y.ndim == 2 and y.shape[0] > 2:
            print("Multi-channel file detected, using first two channels")
            y = y[:2]
        
        print(f"Final audio shape: {y.shape}, dimensions: {y.ndim}")
        
        # Get left and right channels
        y_left = y[0]
        y_right = y[1]
        
        # Create mono version for certain analyses
        y_mono = np.mean(y, axis=0)
        
        # Initialize default results structure
        default_results = {
            "frequency_balance": {
                "band_energy": {
                    "sub_bass": 70.0,
                    "bass": 70.0,
                    "low_mids": 70.0,
                    "mids": 70.0,
                    "high_mids": 70.0,
                    "highs": 70.0,
                    "air": 70.0
                },
                "balance_score": 70.0,
                "analysis": ["Unable to analyze frequency balance."]
            },
            "dynamic_range": {
                "dynamic_range_db": 12.0,
                "crest_factor_db": 15.0,
                "plr": 12.0,
                "dynamic_range_score": 70.0,
                "analysis": ["Unable to analyze dynamic range."]
            },
            "stereo_field": {
                "correlation": 0.5,
                "mid_ratio": 0.7,
                "side_ratio": 0.3,
                "width_score": 70.0,
                "phase_score": 70.0,
                "analysis": ["Unable to analyze stereo field."]
            },
            "clarity": {
                "clarity_score": 70.0,
                "spectral_contrast": 0.5,
                "spectral_flatness": 0.5,
                "spectral_centroid": 2000.0,
                "analysis": ["Unable to analyze clarity."]
            },
            "harmonic_content": {
                "key": "Unknown",
                "harmonic_complexity": 70.0,
                "key_consistency": 70.0,
                "chord_changes_per_minute": 0.0,
                "analysis": ["Unable to analyze harmonic content."],
                "key_relationships": {},
                "top_key_candidates": []
            },
            "transients": {
                "transients_score": 70.0,
                "attack_time": 15.0,
                "transient_density": 2.0,
                "percussion_energy": 20.0,
                "analysis": ["Unable to analyze transients."],
                "transient_data": []
            },
            "3d_spatial": {
                "height_score": 70.0,
                "depth_score": 70.0,
                "width_consistency": 70.0,
                "analysis": ["Unable to analyze 3D spatial imaging."]
            },
            "surround_compatibility": {
                "mono_compatibility": 70.0,
                "phase_score": 70.0,
                "analysis": ["Unable to analyze surround compatibility."]
            },
            "headphone_speaker_optimization": {
                "headphone_score": 70.0,
                "speaker_score": 70.0,
                "analysis": ["Unable to analyze headphone/speaker optimization."]
            }
        }
        
        # Calculate various metrics with error handling
        results = {}
        
        try:
            results["frequency_balance"] = analyze_frequency_balance(y, sr)
        except Exception as e:
            print(f"Error in frequency balance analysis: {str(e)}")
            results["frequency_balance"] = default_results["frequency_balance"]
            
        try:
            results["dynamic_range"] = analyze_dynamic_range(y)
        except Exception as e:
            print(f"Error in dynamic range analysis: {str(e)}")
            results["dynamic_range"] = default_results["dynamic_range"]
            
        try:
            results["stereo_field"] = analyze_stereo_field(y_left, y_right)
        except Exception as e:
            print(f"Error in stereo field analysis: {str(e)}")
            results["stereo_field"] = default_results["stereo_field"]
            
        try:
            results["clarity"] = analyze_clarity(y, sr)
        except Exception as e:
            print(f"Error in clarity analysis: {str(e)}")
            results["clarity"] = default_results["clarity"]
            
        try:
            results["harmonic_content"] = analyze_harmonic_content(y, sr)
        except Exception as e:
            print(f"Error in harmonic content analysis: {str(e)}")
            results["harmonic_content"] = default_results["harmonic_content"]
            
        try:
            results["transients"] = analyze_transients(y_mono, sr)
        except Exception as e:
            print(f"Error in transients analysis: {str(e)}")
            results["transients"] = default_results["transients"]
            
        try:
            results["3d_spatial"] = analyze_3d_spatial(y, sr)
        except Exception as e:
            print(f"Error in 3D spatial analysis: {str(e)}")
            results["3d_spatial"] = default_results["3d_spatial"]
            
        try:
            results["surround_compatibility"] = analyze_surround_compatibility(y, sr)
        except Exception as e:
            print(f"Error in surround compatibility analysis: {str(e)}")
            results["surround_compatibility"] = default_results["surround_compatibility"]
            
        try:
            results["headphone_speaker_optimization"] = analyze_headphone_speaker_optimization(y, sr)
        except Exception as e:
            print(f"Error in headphone/speaker optimization analysis: {str(e)}")
            results["headphone_speaker_optimization"] = default_results["headphone_speaker_optimization"]
        
        # Generate visualizations with the same audio data
        try:
            results["visualizations"] = generate_visualizations(file_path, y=y, sr=sr)
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
            results["visualizations"] = generate_error_visualizations()
        
        # Calculate overall score
        try:
            results["overall_score"] = calculate_overall_score(results)
        except Exception as e:
            print(f"Error calculating overall score: {str(e)}")
            results["overall_score"] = 70.0
        
        # Ensure all numeric values are Python floats
        results = convert_numpy_types(results)
        
        # Verify the structure is complete
        for key in default_results:
            if key not in results:
                results[key] = default_results[key]
            elif not isinstance(results[key], dict):
                results[key] = default_results[key]
            else:
                # Ensure all required fields exist in each section
                for subkey in default_results[key]:
                    if subkey not in results[key]:
                        results[key][subkey] = default_results[key][subkey]
        
        return results
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        # Return a complete error response with default values
        error_results = default_results.copy()
        error_results["error"] = True
        error_results["message"] = str(e)
        error_results["visualizations"] = generate_error_visualizations()
        error_results["overall_score"] = 70.0
        return error_results

def analyze_frequency_balance(y, sr):
    """Analyze the frequency balance of the mix"""
    try:
        # Convert to mono for frequency analysis
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        
        # Compute the short-time Fourier transform
        D = np.abs(librosa.stft(y_mono))
        
        # Convert to dB scale
        D_db = librosa.amplitude_to_db(D, ref=np.max)
        
        # Get frequency bands
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Define frequency bands (in Hz)
        bands = {
            "sub_bass": (20, 60),
            "bass": (60, 250),
            "low_mids": (250, 500),
            "mids": (500, 2000),
            "high_mids": (2000, 4000),
            "highs": (4000, 10000),
            "air": (10000, 20000)
        }
        
        # Calculate average energy in each band
        band_energy = {}
        for band_name, (low, high) in bands.items():
            # Find indices for the frequency range
            indices = np.where((freqs >= low) & (freqs <= high))[0]
            if len(indices) > 0:
                # Calculate mean energy in this band
                band_energy[band_name] = float(np.mean(D_db[:, indices]))
            else:
                band_energy[band_name] = -80.0  # Default low value if no frequencies in range
        
        # Normalize values to 0-100 scale
        min_energy = min(band_energy.values())
        max_energy = max(band_energy.values())
        range_energy = max_energy - min_energy if max_energy > min_energy else 1
        
        normalized_energy = {
            band: float(((energy - min_energy) / range_energy) * 100)
            for band, energy in band_energy.items()
        }
        
        # Calculate balance score based on ideal curve and deviation
        ideal_curve = {
            "sub_bass": 85,
            "bass": 90,
            "low_mids": 85,
            "mids": 80,
            "high_mids": 75,
            "highs": 70,
            "air": 65
        }
        
        # Calculate deviation from ideal curve
        deviations = [abs(normalized_energy[band] - ideal_curve[band]) for band in bands.keys()]
        avg_deviation = float(np.mean(deviations))
        
        # Convert to a 0-100 score (lower deviation is better)
        balance_score = float(max(0, min(100, 100 - avg_deviation)))
        
        analysis = get_frequency_balance_analysis(normalized_energy)
        
        return {
            "band_energy": normalized_energy,
            "balance_score": balance_score,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Error in frequency balance analysis: {str(e)}")
        # Return default values
        default_energy = {
            "sub_bass": 70.0,
            "bass": 70.0,
            "low_mids": 70.0,
            "mids": 70.0,
            "high_mids": 70.0,
            "highs": 70.0,
            "air": 70.0
        }
        return {
            "band_energy": default_energy,
            "balance_score": 70.0,
            "analysis": ["Unable to analyze frequency balance."]
        }

def get_frequency_balance_analysis(normalized_energy):
    """Generate textual analysis of frequency balance"""
    analysis = []
    
    # Check for potential issues
    if normalized_energy["sub_bass"] > 95:
        analysis.append("Sub bass is very prominent, which may cause muddiness.")
    elif normalized_energy["sub_bass"] < 40:
        analysis.append("Sub bass is lacking, mix may sound thin.")
        
    if normalized_energy["bass"] > 95:
        analysis.append("Bass is very prominent, which may overpower other elements.")
    elif normalized_energy["bass"] < 40:
        analysis.append("Bass is lacking, mix may lack warmth and foundation.")
    
    if normalized_energy["mids"] < 50:
        analysis.append("Mids are recessed, mix may sound hollow (scooped mids).")
    
    if normalized_energy["high_mids"] > 90:
        analysis.append("High mids are very prominent, may cause listening fatigue.")
    
    if normalized_energy["highs"] > 90:
        analysis.append("Highs are very prominent, mix may sound harsh or brittle.")
    elif normalized_energy["highs"] < 40:
        analysis.append("Highs are lacking, mix may sound dull or muffled.")
    
    # If no issues found
    if not analysis:
        analysis.append("Frequency balance appears good across the spectrum.")
    
    return analysis

def analyze_dynamic_range(y):
    """Analyze the dynamic range of the mix"""
    # Convert to mono for dynamic range analysis
    y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
    
    # Calculate RMS energy in small windows
    frame_length = 2048
    hop_length = 512
    rms = librosa.feature.rms(y=y_mono, frame_length=frame_length, hop_length=hop_length)[0]
    
    # Convert to dB
    rms_db = 20 * np.log10(rms + 1e-8)  # Adding small value to avoid log(0)
    
    # Calculate dynamic range metrics
    crest_factor = np.max(np.abs(y_mono)) / np.sqrt(np.mean(y_mono**2))
    crest_factor_db = 20 * np.log10(crest_factor)
    
    # Calculate percentiles for dynamic range
    p95 = np.percentile(rms_db[rms_db > -80], 95)  # 95th percentile (loud parts)
    p5 = np.percentile(rms_db[rms_db > -80], 5)    # 5th percentile (quiet parts)
    dynamic_range = p95 - p5
    
    # Calculate PLR (Peak to Loudness Ratio)
    peak = np.max(np.abs(y_mono))
    peak_db = 20 * np.log10(peak + 1e-8)
    loudness = np.mean(rms_db[rms_db > -80])
    plr = peak_db - loudness
    
    # Score based on dynamic range (0-100)
    # A good mix typically has at least 10-15 dB of dynamic range
    dr_score = min(100, max(0, dynamic_range * 5))
    
    # Analyze if the mix is over-compressed
    is_overcompressed = dynamic_range < 8
    
    return {
        "dynamic_range_db": dynamic_range,
        "crest_factor_db": crest_factor_db,
        "plr": plr,
        "dynamic_range_score": dr_score,
        "analysis": get_dynamic_range_analysis(dynamic_range, crest_factor_db)
    }

def get_dynamic_range_analysis(dynamic_range, crest_factor_db):
    """Generate textual analysis of dynamic range"""
    analysis = []
    
    if dynamic_range < 6:
        analysis.append("Very compressed mix with minimal dynamic range. May sound fatiguing and lack impact.")
    elif dynamic_range < 10:
        analysis.append("Somewhat compressed mix. Could benefit from more dynamic contrast.")
    elif dynamic_range < 15:
        analysis.append("Good dynamic range for a modern mix.")
    else:
        analysis.append("Excellent dynamic range. Mix has good contrast between quiet and loud sections.")
    
    if crest_factor_db < 10:
        analysis.append("Low crest factor indicates heavy compression or limiting.")
    elif crest_factor_db > 20:
        analysis.append("High crest factor indicates a very dynamic mix with good transient preservation.")
    
    return analysis

def analyze_stereo_field(left, right):
    """Analyze the stereo field of the mix"""
    print("Analyzing stereo field...")
    print(f"Left channel shape: {left.shape}")
    print(f"Right channel shape: {right.shape}")
    
    # Calculate correlation between channels
    correlation = np.corrcoef(left, right)[0, 1]
    print(f"Channel correlation: {correlation:.4f}")
    
    # Calculate mid and side channels
    mid = (left + right) / 2
    side = (left - right) / 2
    
    # Calculate energy in mid and side channels
    mid_energy = np.sum(np.abs(mid)**2)
    side_energy = np.sum(np.abs(side)**2)
    total_energy = mid_energy + side_energy
    
    # Calculate mid/side ratio
    if total_energy > 0:
        mid_ratio = mid_energy / total_energy
        side_ratio = side_energy / total_energy
    else:
        mid_ratio = 1.0
        side_ratio = 0.0
    
    print(f"Mid/Side ratio: {mid_ratio:.4f}/{side_ratio:.4f}")
    
    # Calculate stereo width score
    # A good mix typically has some stereo content but not too extreme
    width_score = 100 * (1 - abs(mid_ratio - 0.7))
    
    # Phase issues detection
    phase_correlation = correlation
    phase_score = max(0, min(100, (phase_correlation + 1) * 50))
    
    print(f"Width score: {width_score:.1f}")
    print(f"Phase score: {phase_score:.1f}")
    
    return {
        "correlation": correlation,
        "mid_ratio": mid_ratio,
        "side_ratio": side_ratio,
        "width_score": width_score,
        "phase_score": phase_score,
        "analysis": get_stereo_field_analysis(correlation, mid_ratio)
    }

def get_stereo_field_analysis(correlation, mid_ratio):
    """Generate textual analysis of stereo field"""
    analysis = []
    
    if correlation < 0:
        analysis.append("Potential phase issues detected. Some frequencies may cancel out in mono playback.")
    elif correlation < 0.3:
        analysis.append("Very wide stereo mix. Check for mono compatibility.")
    elif correlation > 0.9:
        analysis.append("Very narrow stereo image. Mix is almost mono.")
    else:
        analysis.append("Good stereo correlation for a balanced mix.")
    
    if mid_ratio > 0.9:
        analysis.append("Mix is very centered with minimal stereo content.")
    elif mid_ratio < 0.5:
        analysis.append("Mix has very wide stereo content, which may cause phase issues.")
    else:
        analysis.append("Good balance between mid and side content.")
    
    return analysis

def analyze_clarity(y, sr):
    """Analyze the clarity and definition of the mix"""
    try:
        print("Starting clarity analysis...")
        
        # Convert to mono for clarity analysis
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        
        # Ensure we have enough samples for analysis
        if len(y_mono) < sr:
            raise ValueError("Audio file too short for clarity analysis")
            
        # Check for silent audio
        if np.max(np.abs(y_mono)) < 1e-6:
            raise ValueError("Audio file too quiet for clarity analysis")
        
        print("Calculating spectral contrast...")
        # Calculate spectral contrast with adjusted parameters and error handling
        try:
            contrast = librosa.feature.spectral_contrast(
                y=y_mono, 
                sr=sr,
                n_bands=4,  # Reduced from default 6
                fmin=20.0,  # Set minimum frequency
                n_fft=2048,  # Increased window size
                hop_length=512  # Add explicit hop length
            )
            if contrast.size > 0:
                contrast_mean = float(np.nanmean(np.abs(contrast)))
            else:
                contrast_mean = 0.0  # Default value when the array is empty
            print(f"Spectral contrast calculated: {contrast_mean}")
        except Exception as e:
            print(f"Error calculating spectral contrast: {str(e)}")
            contrast_mean = 0.5  # Default value
            contrast = np.zeros((4, 1))  # Default shape for analysis
        
        print("Calculating spectral flatness...")
        # Calculate spectral flatness with error handling
        try:
            flatness = librosa.feature.spectral_flatness(y=y_mono)
            if flatness.size > 0:
                flatness_mean = float(np.nanmean(flatness))
                if np.isnan(flatness_mean):
                    print("Warning: NaN detected in spectral flatness, using default value")
                    flatness_mean = 0.5
            else:
                flatness_mean = 0.5  # Default value when array is empty
            print(f"Spectral flatness calculated: {flatness_mean}")
        except Exception as e:
            print(f"Error calculating spectral flatness: {str(e)}")
            flatness_mean = 0.5  # Default value
        
        print("Calculating spectral centroid...")
        # Calculate spectral centroid with error handling
        try:
            centroid = librosa.feature.spectral_centroid(y=y_mono, sr=sr)
            if centroid.size > 0:
                centroid_mean = float(np.nanmean(centroid))
                if np.isnan(centroid_mean):
                    print("Warning: NaN detected in spectral centroid, using default value")
                    centroid_mean = sr/4
            else:
                centroid_mean = sr/4  # Default value when array is empty
            print(f"Spectral centroid calculated: {centroid_mean}")
        except Exception as e:
            print(f"Error calculating spectral centroid: {str(e)}")
            centroid_mean = sr/4  # Default value
        
        # Calculate clarity score (0-100) with bounds checking
        try:
            # Scale contrast score between 0-100
            contrast_score = min(100, max(0, contrast_mean * 1000))
            if np.isnan(contrast_score):
                contrast_score = 70.0
            
            # Convert flatness to score (lower flatness is better for clarity)
            flatness_score = min(100, max(0, (1 - flatness_mean) * 100))
            if np.isnan(flatness_score):
                flatness_score = 70.0
            
            # Calculate centroid score (optimal range between sr/8 and sr/3)
            centroid_score = min(100, max(0, 100 - abs(centroid_mean - sr/4)/(sr/8)))
            if np.isnan(centroid_score):
                centroid_score = 70.0
            
            # Combine scores with weights
            clarity_score = float(
                contrast_score * 0.4 +    # Weight contrast more as it's most important for clarity
                flatness_score * 0.3 +    # Moderate weight for flatness
                centroid_score * 0.3      # Moderate weight for spectral balance
            )
            
            # Ensure final score is between 0-100 and not NaN
            clarity_score = min(100, max(0, clarity_score))
            if np.isnan(clarity_score):
                clarity_score = 70.0
                
            print(f"Final clarity score calculated: {clarity_score}")
            
        except Exception as e:
            print(f"Error calculating clarity score: {str(e)}")
            clarity_score = 70.0  # Default score
        
        # Generate analysis text
        analysis = get_clarity_analysis(contrast_mean, flatness_mean, centroid_mean, sr)
        
        # Ensure all values are valid for JSON
        result = {
            "clarity_score": float(clarity_score),
            "spectral_contrast": float(contrast_mean),
            "spectral_flatness": float(flatness_mean),
            "spectral_centroid": float(centroid_mean),
            "analysis": analysis
        }
        
        # Final validation of all numeric values
        for key, value in result.items():
            if isinstance(value, (int, float)) and (np.isnan(value) or np.isinf(value)):
                print(f"Warning: Invalid value detected in {key}, using default")
                result[key] = 70.0 if key.endswith('_score') else 0.5
        
        return result
        
    except Exception as e:
        print(f"Error in clarity analysis: {str(e)}")
        return {
            "clarity_score": 70.0,
            "spectral_contrast": 0.5,
            "spectral_flatness": 0.5,
            "spectral_centroid": sr/4 if sr else 2000.0,
            "analysis": [f"Unable to analyze clarity: {str(e)}"]
        }

def get_clarity_analysis(contrast, flatness, centroid, sr):
    """Generate textual analysis of clarity"""
    try:
        analysis = []
        
        # Analyze spectral contrast
        if contrast < 0.1:
            analysis.append("Very low spectral contrast - mix may sound muddy or lacking in definition.")
        elif contrast < 0.3:
            analysis.append("Low spectral contrast - consider enhancing separation between elements.")
        elif contrast < 0.6:
            analysis.append("Moderate spectral contrast - good balance between elements.")
        else:
            analysis.append("High spectral contrast - excellent separation between elements.")
        
        # Analyze spectral flatness
        if flatness < 0.2:
            analysis.append("Low spectral flatness indicates good tonal focus and clarity.")
        elif flatness < 0.4:
            analysis.append("Moderate spectral flatness - good balance of tonal and noise elements.")
        else:
            analysis.append("High spectral flatness may indicate noise or lack of tonal focus.")
        
        # Analyze spectral centroid
        if centroid < sr/8:
            analysis.append("Low spectral centroid - mix may sound dark or muffled.")
        elif centroid < sr/4:
            analysis.append("Good spectral centroid range for balanced clarity.")
        elif centroid < sr/2:
            analysis.append("High spectral centroid - mix may sound bright or harsh.")
        else:
            analysis.append("Very high spectral centroid - consider reducing high frequency content.")
        
        if not analysis:
            analysis.append("Mix appears to have balanced clarity and definition.")
            
        return analysis
        
    except Exception as e:
        print(f"Error generating clarity analysis: {str(e)}")
        return ["Unable to generate detailed clarity analysis."]

def analyze_harmonic_content(y, sr):
    """
    Analyze the harmonic content of the audio, including key detection and harmonic complexity.
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Dictionary containing harmonic analysis results
    """
    try:
        print("Analyzing harmonic content...")
        
        # Convert to mono if needed
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        
        # Compute chromagram - remove n_chroma parameter which is causing issues
        hop_length = 512  # Default hop length
        chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr, hop_length=hop_length)
        
        # Compute key using the chromagram
        key_indices = np.sum(chroma, axis=1)
        key_index = np.argmax(key_indices)
        
        # Map key index to musical key
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        detected_key = keys[key_index]
        
        # Determine if major or minor based on relative minor/major relationship
        minor_index = (key_index + 9) % 12  # Relative minor is 3 semitones down (or 9 up in circle)
        major_chroma = np.sum(chroma[key_index])
        minor_chroma = np.sum(chroma[minor_index])
        
        # If minor energy is higher, it's likely a minor key
        is_minor = minor_chroma > major_chroma
        key_name = f"{detected_key}{'m' if is_minor else ''}"
        
        # Get the top 3 key candidates for additional context
        key_scores = {}
        for i, energy in enumerate(key_indices):
            major_key = keys[i]
            minor_key = keys[i] + 'm'
            # Simple scoring based on energy and major/minor context
            if is_minor:
                key_scores[minor_key] = energy / np.sum(key_indices)
                key_scores[major_key] = energy / np.sum(key_indices) * 0.8  # Slightly lower weight for opposite mode
            else:
                key_scores[major_key] = energy / np.sum(key_indices)
                key_scores[minor_key] = energy / np.sum(key_indices) * 0.8  # Slightly lower weight for opposite mode
        
        # Get top 3 key candidates
        top_keys = sorted(key_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get key relationship info
        key_relationships = get_key_relationship_info(key_name)
        
        # Calculate harmonic complexity based on the distribution of energy across the chromagram
        # More even distribution = more complex harmony
        chroma_entropy = stats.entropy(np.sum(chroma, axis=1))
        max_entropy = np.log(12)  # Maximum possible entropy with 12 pitch classes
        harmonic_complexity = (chroma_entropy / max_entropy) * 100
        
        # Calculate tonal stability - how consistent the key is throughout the track
        # Split audio into segments and analyze key consistency
        frame_length = sr * 5  # 5-second segments
        hop_length = frame_length // 2  # 50% overlap
        
        # If the audio is shorter than the frame length, use the entire audio
        if len(y_mono) < frame_length:
            segments = [y_mono]
        else:
            segments = []
            for i in range(0, len(y_mono) - frame_length, hop_length):
                segments.append(y_mono[i:i+frame_length])
        
        # Calculate key for each segment
        segment_keys = []
        for segment in segments:
            # Remove n_chroma parameter here too
            segment_chroma = librosa.feature.chroma_cqt(y=segment, sr=sr, hop_length=hop_length)
            segment_key_indices = np.sum(segment_chroma, axis=1)
            segment_key_index = np.argmax(segment_key_indices)
            segment_keys.append(segment_key_index)
        
        # Calculate key consistency as percentage of segments with the same key
        if len(segments) > 1:
            key_consistency = (segment_keys.count(key_index) / len(segment_keys)) * 100
        else:
            key_consistency = 100  # If only one segment, key is 100% consistent
        
        # Calculate chord changes per minute (approximate)
        # Use chroma flux to estimate chord change rate
        chroma_flux = librosa.onset.onset_strength(
            y=y_mono, sr=sr
        )
        
        # Estimate chord changes by finding peaks in the chroma flux
        peaks = librosa.util.peak_pick(x=chroma_flux, pre_max=3, post_max=3, pre_avg=3, post_avg=5, delta=0.5, wait=10)
        
        # Calculate chord changes per minute
        duration_minutes = len(y_mono) / sr / 60
        if duration_minutes > 0:
            chord_changes_per_minute = len(peaks) / duration_minutes
        else:
            chord_changes_per_minute = 0
        
        # Generate analysis text
        analysis = []
        
        # Key analysis
        analysis.append(f"Detected key is {key_name}.")
        
        # Add key relationship info to analysis
        if is_minor:
            analysis.append(f"Relative major key is {key_relationships['relative_major']}.")
        else:
            analysis.append(f"Relative minor key is {key_relationships['relative_minor']}.")
            
        # Suggest compatible keys for modulation
        modulation_options = key_relationships["modulation_options"]
        modulation_text = f"Compatible keys for modulation include {', '.join(modulation_options.values())}."
        analysis.append(modulation_text)
        
        # Harmonic complexity analysis
        if harmonic_complexity < 30:
            analysis.append("Simple harmonic structure with few chord changes.")
        elif harmonic_complexity < 60:
            analysis.append("Moderate harmonic complexity with standard chord progressions.")
        else:
            analysis.append("Complex harmonic structure with rich chord progressions.")
        
        # Key consistency analysis
        if key_consistency > 90:
            analysis.append("Very stable key center throughout the track.")
        elif key_consistency > 70:
            analysis.append("Mostly consistent key with some modulations.")
        else:
            analysis.append("Multiple key changes or modulations detected.")
        
        # Chord change rate analysis
        if chord_changes_per_minute < 10:
            analysis.append("Slow chord progression rate, creating a spacious feel.")
        elif chord_changes_per_minute < 30:
            analysis.append("Moderate chord change rate, typical for most music styles.")
        else:
            analysis.append("Fast chord changes, creating harmonic movement and energy.")
        
        # Common chord progressions suggestion
        progression_suggestion = f"Common progressions in this key include: " + \
                               ", ".join([" → ".join(prog) for prog in key_relationships["common_progressions"][:2]])
        analysis.append(progression_suggestion)
        
        return {
            "key": key_name,
            "harmonic_complexity": harmonic_complexity,
            "key_consistency": key_consistency,
            "chord_changes_per_minute": chord_changes_per_minute,
            "analysis": analysis,
            "key_relationships": key_relationships,
            "top_key_candidates": [{"key": k, "confidence": round(v, 2)} for k, v in top_keys]
        }
    except Exception as e:
        print(f"Error analyzing harmonic content: {str(e)}")
        # Return default values
        return {
            "key": "Unknown",
            "harmonic_complexity": 50.0,
            "key_consistency": 50.0,
            "chord_changes_per_minute": 0.0,
            "analysis": ["Unable to analyze harmonic content."],
            "key_relationships": {},
            "top_key_candidates": []
        }

def generate_3d_spatial_visualization(y, sr, vis_dir):
    """Generate 3D spatial visualization."""
    try:
        plt.figure(figsize=(10, 4))
        
        # Ensure stereo audio
        if y.ndim == 1:
            y = np.vstack((y, y))
        
        # Calculate spatial characteristics
        # Height perception (frequency-based)
        freqs = librosa.fft_frequencies(sr=sr)
        D = np.abs(librosa.stft(np.mean(y, axis=0)))
        high_freq_energy = np.mean(D[freqs > 5000])
        low_freq_energy = np.mean(D[freqs < 500])
        height_ratio = high_freq_energy / (low_freq_energy + 1e-6)
        
        # Depth perception (phase-based)
        phase_diff = np.angle(np.correlate(y[0], y[1]))[0]
        depth = np.abs(phase_diff)
        
        # Width (stereo spread)
        width = np.mean(np.abs(y[0] - y[1]))
        
        # Create 3D scatter plot
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        
        # Sample points for visualization
        num_points = 1000
        sample_indices = np.linspace(0, y.shape[1]-1, num_points, dtype=int)
        
        # Calculate point positions
        x = y[0, sample_indices]  # Left channel
        y_coords = y[1, sample_indices]  # Right channel
        z = np.abs(librosa.stft(np.mean(y, axis=0)))[:, sample_indices[::10]]  # Height based on frequency content
        
        # Plot points with color gradient based on energy
        scatter = ax.scatter(x, y_coords, z[0], 
                           c=np.abs(x - y_coords),  # Color based on stereo difference
                           cmap='viridis',
                           alpha=0.6,
                           s=10)
        
        # Add colorbar
        plt.colorbar(scatter, label='Stereo Spread')
        
        # Labels
        ax.set_xlabel('Left Channel')
        ax.set_ylabel('Right Channel')
        ax.set_zlabel('Frequency Energy')
        plt.title('3D Spatial Visualization')
        
        # Save the plot
        spatial_path = os.path.join(vis_dir, 'spatial_field.png')
        plt.savefig(spatial_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return spatial_path
    except Exception as e:
        print(f"Error generating 3D spatial visualization: {str(e)}")
        return None

def generate_visualizations(file_path, y=None, sr=None, file_id=None):
    """Generate visualizations for the audio file and return their paths."""
    import matplotlib.pyplot as plt
    import os
    
    try:
        # Use provided audio data if available, otherwise load from file
        if y is None or sr is None:
            print(f"Loading audio file for visualizations: {file_path}")
            y, sr = librosa.load(file_path, sr=None, mono=False)
            print(f"Loaded audio shape: {y.shape}, dimensions: {y.ndim}")
        
        # Create a directory for visualizations
        if file_id is None:
            file_id = os.path.basename(file_path).split('.')[0]
        
        file_id = str(file_id)
        vis_dir = os.path.join('app/static/uploads', file_id)
        os.makedirs(vis_dir, exist_ok=True)
        print(f"Saving visualizations to: {vis_dir}")
        
        # Convert to mono for some visualizations
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        
        # 1. Waveform
        plt.figure(figsize=(10, 4))
        # Use explicit color instead of relying on prop_cycler
        librosa.display.waveshow(y_mono, sr=sr, color='#1f77b4')
        plt.title('Waveform')
        plt.tight_layout()
        waveform_path = os.path.join(vis_dir, 'waveform.png')
        plt.savefig(waveform_path)
        plt.close()
        print(f"Saved waveform to: {waveform_path}")
        
        # 2. Spectrogram
        plt.figure(figsize=(10, 4))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y_mono)), ref=np.max)
        librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Spectrogram')
        plt.tight_layout()
        spectrogram_path = os.path.join(vis_dir, 'spectrogram.png')
        plt.savefig(spectrogram_path)
        plt.close()
        print(f"Saved spectrogram to: {spectrogram_path}")
        
        # 3. Frequency Spectrum
        plt.figure(figsize=(10, 4))
        S = np.abs(librosa.stft(y_mono))
        fft_freqs = librosa.fft_frequencies(sr=sr)
        spectrum = np.mean(S, axis=1)
        plt.semilogx(fft_freqs, librosa.amplitude_to_db(spectrum, ref=np.max), color='#1f77b4')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude (dB)')
        plt.title('Frequency Spectrum')
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.tight_layout()
        spectrum_path = os.path.join(vis_dir, 'spectrum.png')
        plt.savefig(spectrum_path)
        plt.close()
        print(f"Saved spectrum to: {spectrum_path}")
        
        # 4. Chromagram (Harmonic Content)
        try:
            print(f"Generating chromagram visualization - audio shape: {y_mono.shape}, sr: {sr}")
            
            # Check for extremely short audio files
            if len(y_mono) < sr:
                raise ValueError(f"Audio file too short for chromagram analysis: {len(y_mono)/sr:.2f} seconds")
                
            # Check for silent audio
            if np.max(np.abs(y_mono)) < 1e-6:
                raise ValueError(f"Audio file too quiet for chromagram analysis")
            
            plt.figure(figsize=(10, 4))
            
            # More robust chromagram generation with C-CQT
            try:
                print("Attempting chroma_cqt for chromagram...")
                chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr)
            except Exception as cqt_error:
                print(f"Failed with chroma_cqt: {str(cqt_error)}, trying chroma_stft instead")
                # Fall back to STFT-based chromagram
                chroma = librosa.feature.chroma_stft(y=y_mono, sr=sr)
            
            print(f"Chromagram shape: {chroma.shape}")
            librosa.display.specshow(chroma, y_axis='chroma', x_axis='time')
            plt.colorbar()
            plt.title('Chromagram (Harmonic Content)')
            plt.tight_layout()
            chroma_path = os.path.join(vis_dir, 'chromagram.png')
            plt.savefig(chroma_path)
            plt.close()
            print(f"Saved chromagram to: {chroma_path}")
        except Exception as e:
            print(f"Error generating chromagram: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Create a placeholder image for chromagram
            plt.figure(figsize=(10, 4))
            plt.text(0.5, 0.5, f'Chromagram Error: {str(e)}', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=plt.gca().transAxes, fontsize=12)
            plt.axis('off')
            chroma_path = os.path.join(vis_dir, 'chromagram.png')
            plt.savefig(chroma_path)
            plt.close()
            print(f"Saved chromagram error placeholder to: {chroma_path}")
        
        # 5. Stereo Field
        print(f"Generating stereo field visualization...")
        print(f"Audio shape: {y.shape}, dimensions: {y.ndim}")
        
        # Enhanced stereo detection
        is_stereo = y.ndim > 1 and y.shape[0] >= 2
        channels_identical = False
        
        if is_stereo:
            # Compare more samples for better detection
            sample_size = min(10000, y.shape[1])
            left_samples = y[0, :sample_size]
            right_samples = y[1, :sample_size]
            
            # Use correlation for comparison
            correlation = np.corrcoef(left_samples, right_samples)[0, 1]
            channels_identical = correlation > 0.999  # Allow for tiny differences
            
            print(f"Stereo detection results:")
            print(f"- Is stereo format: {is_stereo}")
            print(f"- Channels identical: {channels_identical}")
            print(f"- Channel correlation: {correlation:.4f}")
        
        plt.figure(figsize=(10, 4))
        
        if is_stereo and not channels_identical:
            print("Generating stereo field plot")
            # Plot more points with higher opacity for better visibility
            plt.plot(y[0, :sr], y[1, :sr], '.', alpha=0.3, markersize=2, color='#1f77b4')
            plt.xlabel('Left Channel')
            plt.ylabel('Right Channel')
            plt.title('Stereo Field (First Second)')
            plt.axis('equal')
            plt.grid(True)
        else:
            print(f"Generating mono/identical channels placeholder")
            message = 'Identical Channels - Effectively Mono' if (is_stereo and channels_identical) else 'Mono Audio - No Stereo Field'
            plt.text(0.5, 0.5, message,
                    horizontalalignment='center',
                    verticalalignment='center',
                    transform=plt.gca().transAxes,
                    fontsize=14)
            plt.axis('off')
        
        plt.tight_layout()
        stereo_path = os.path.join(vis_dir, 'stereo_field.png')
        plt.savefig(stereo_path, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"Saved stereo field visualization to: {stereo_path}")
        
        # 5. 3D Spatial Field
        print(f"Generating 3D spatial field visualization...")
        spatial_path = generate_3d_spatial_visualization(y, sr, vis_dir)
        if spatial_path:
            print(f"Saved 3D spatial field visualization to: {spatial_path}")
        else:
            print("Failed to generate 3D spatial field visualization")
        
        # Return paths
        static_prefix = '/static'
        return {
            "waveform": f"{static_prefix}/uploads/{file_id}/waveform.png",
            "spectrogram": f"{static_prefix}/uploads/{file_id}/spectrogram.png",
            "spectrum": f"{static_prefix}/uploads/{file_id}/spectrum.png",
            "chromagram": f"{static_prefix}/uploads/{file_id}/chromagram.png",
            "stereo_field": f"{static_prefix}/uploads/{file_id}/stereo_field.png",
            "spatial_field": f"{static_prefix}/uploads/{file_id}/spatial_field.png" if spatial_path else f"{static_prefix}/img/error.png"
        }
    except Exception as e:
        print(f"Error in generate_visualizations: {str(e)}")
        import traceback
        traceback.print_exc()
        return generate_error_visualizations(file_id)

def generate_error_visualizations(file_id=None):
    """Generate error placeholder images."""
    static_prefix = '/static'
    return {
        "waveform": f"{static_prefix}/img/error.png",
        "spectrogram": f"{static_prefix}/img/error.png",
        "spectrum": f"{static_prefix}/img/error.png",
        "chromagram": f"{static_prefix}/img/error.png",
        "stereo_field": f"{static_prefix}/img/error.png"
    }

def calculate_overall_score(results):
    """Calculate an overall mix quality score based on all metrics"""
    try:
        # Initialize default scores
        default_scores = {
            "frequency_balance": 70.0,
            "dynamic_range": 70.0,
            "stereo_field": 70.0,
            "clarity": 70.0,
            "harmonic_content": 70.0,
            "transients": 70.0,
            "3d_spatial": 70.0,
            "surround_compatibility": 70.0,
            "headphone_speaker_optimization": 70.0
        }

        # Weight each component
        weights = {
            "frequency_balance": 0.25,
            "dynamic_range": 0.15,
            "stereo_field": 0.15,
            "clarity": 0.20,
            "harmonic_content": 0.15,
            "transients": 0.10,
            "3d_spatial": 0.05,
            "surround_compatibility": 0.05,
            "headphone_speaker_optimization": 0.05
        }
        
        # Calculate weighted score
        score = 0.0
        
        # Add frequency balance score
        try:
            if "frequency_balance" in results and isinstance(results["frequency_balance"], dict):
                score += weights["frequency_balance"] * float(results["frequency_balance"].get("balance_score", default_scores["frequency_balance"]))
            else:
                score += weights["frequency_balance"] * default_scores["frequency_balance"]
        except (TypeError, ValueError):
            score += weights["frequency_balance"] * default_scores["frequency_balance"]
        
        # Add dynamic range score
        try:
            if "dynamic_range" in results and isinstance(results["dynamic_range"], dict):
                score += weights["dynamic_range"] * float(results["dynamic_range"].get("dynamic_range_score", default_scores["dynamic_range"]))
            else:
                score += weights["dynamic_range"] * default_scores["dynamic_range"]
        except (TypeError, ValueError):
            score += weights["dynamic_range"] * default_scores["dynamic_range"]
        
        # Add stereo field score
        try:
            if "stereo_field" in results and isinstance(results["stereo_field"], dict):
                stereo_score = 0.0
                width_score = float(results["stereo_field"].get("width_score", default_scores["stereo_field"]))
                phase_score = float(results["stereo_field"].get("phase_score", default_scores["stereo_field"]))
                stereo_score = (width_score + phase_score) / 2
                score += weights["stereo_field"] * stereo_score
            else:
                score += weights["stereo_field"] * default_scores["stereo_field"]
        except (TypeError, ValueError):
            score += weights["stereo_field"] * default_scores["stereo_field"]
        
        # Add clarity score
        try:
            if "clarity" in results and isinstance(results["clarity"], dict):
                score += weights["clarity"] * float(results["clarity"].get("clarity_score", default_scores["clarity"]))
            else:
                score += weights["clarity"] * default_scores["clarity"]
        except (TypeError, ValueError):
            score += weights["clarity"] * default_scores["clarity"]
        
        # Add harmonic content score
        try:
            if "harmonic_content" in results and isinstance(results["harmonic_content"], dict):
                score += weights["harmonic_content"] * float(results["harmonic_content"].get("harmonic_complexity", default_scores["harmonic_content"]))
            else:
                score += weights["harmonic_content"] * default_scores["harmonic_content"]
        except (TypeError, ValueError):
            score += weights["harmonic_content"] * default_scores["harmonic_content"]
        
        # Add transients score
        try:
            if "transients" in results and isinstance(results["transients"], dict):
                score += weights["transients"] * float(results["transients"].get("transients_score", default_scores["transients"]))
            else:
                score += weights["transients"] * default_scores["transients"]
        except (TypeError, ValueError):
            score += weights["transients"] * default_scores["transients"]
        
        # Add 3D spatial score
        try:
            if "3d_spatial" in results and isinstance(results["3d_spatial"], dict):
                spatial_score = 0.0
                height_score = float(results["3d_spatial"].get("height_score", default_scores["3d_spatial"]))
                depth_score = float(results["3d_spatial"].get("depth_score", default_scores["3d_spatial"]))
                width_score = float(results["3d_spatial"].get("width_consistency", default_scores["3d_spatial"]))
                spatial_score = (height_score + depth_score + width_score) / 3
                score += weights["3d_spatial"] * spatial_score
            else:
                score += weights["3d_spatial"] * default_scores["3d_spatial"]
        except (TypeError, ValueError):
            score += weights["3d_spatial"] * default_scores["3d_spatial"]
        
        # Add surround compatibility score
        try:
            if "surround_compatibility" in results and isinstance(results["surround_compatibility"], dict):
                compatibility_score = 0.0
                mono_score = float(results["surround_compatibility"].get("mono_compatibility", default_scores["surround_compatibility"]))
                phase_score = float(results["surround_compatibility"].get("phase_score", default_scores["surround_compatibility"]))
                compatibility_score = (mono_score + phase_score) / 2
                score += weights["surround_compatibility"] * compatibility_score
            else:
                score += weights["surround_compatibility"] * default_scores["surround_compatibility"]
        except (TypeError, ValueError):
            score += weights["surround_compatibility"] * default_scores["surround_compatibility"]
        
        # Add headphone/speaker optimization score
        try:
            if "headphone_speaker_optimization" in results and isinstance(results["headphone_speaker_optimization"], dict):
                optimization_score = 0.0
                headphone_score = float(results["headphone_speaker_optimization"].get("headphone_score", default_scores["headphone_speaker_optimization"]))
                speaker_score = float(results["headphone_speaker_optimization"].get("speaker_score", default_scores["headphone_speaker_optimization"]))
                optimization_score = (headphone_score + speaker_score) / 2
                score += weights["headphone_speaker_optimization"] * optimization_score
            else:
                score += weights["headphone_speaker_optimization"] * default_scores["headphone_speaker_optimization"]
        except (TypeError, ValueError):
            score += weights["headphone_speaker_optimization"] * default_scores["headphone_speaker_optimization"]

        # Ensure score is between 0 and 100
        score = max(0, min(100, score))
        
        return round(score, 1)
    except Exception as e:
        print(f"Error calculating overall score: {str(e)}")
        return 70.0  # Return a reasonable default score if calculation fails

def analyze_3d_spatial(y, sr):
    """
    Analyze 3D spatial imaging characteristics
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Dictionary containing 3D spatial analysis results
    """
    try:
        print("Analyzing 3D spatial imaging...")
        
        # Ensure stereo audio
        if y.ndim == 1:
            y = np.vstack((y, y))

        # Calculate interaural level differences (ILD) for height perception
        ild = np.mean(np.abs(y[0] - y[1]))
        height_score = min(100, max(0, ild * 100))

        # Calculate interaural time differences (ITD) for depth perception
        correlation = np.corrcoef(y[0], y[1])[0, 1]
        depth_score = min(100, max(0, (1 - abs(correlation)) * 100))

        # Calculate width consistency
        window_size = 2048
        hop_length = 512
        width_variation = np.std([
            np.corrcoef(y[0][i:i+window_size], y[1][i:i+window_size])[0, 1]
            for i in range(0, len(y[0]) - window_size, hop_length)
        ])
        width_consistency = min(100, max(0, 100 - (width_variation * 1000)))

        return {
            "height_score": float(height_score),
            "depth_score": float(depth_score),
            "width_consistency": float(width_consistency),
            "analysis": get_3d_spatial_analysis(height_score, depth_score, width_consistency)
        }
    except Exception as e:
        print(f"Error in 3D spatial analysis: {str(e)}")
        return {
            "height_score": 70.0,
            "depth_score": 70.0,
            "width_consistency": 70.0,
            "analysis": ["Unable to analyze 3D spatial imaging."]
        }


def get_3d_spatial_analysis(height_score, depth_score, width_consistency):
    """Generate textual analysis of 3D spatial imaging"""
    analysis = []
    
    if height_score < 40:
        analysis.append("Limited height perception. Mix may sound flat.")
    elif height_score > 90:
        analysis.append("Excessive height perception. May cause listening fatigue.")

    if depth_score < 40:
        analysis.append("Limited depth perception. Mix may sound two-dimensional.")
    elif depth_score > 90:
        analysis.append("Excessive depth perception. May cause imaging instability.")

    if width_consistency < 40:
        analysis.append("Inconsistent width perception. Stereo image may sound unstable.")

    if not analysis:
        analysis.append("Good 3D spatial imaging with balanced height, depth, and width.")

    return analysis


def analyze_surround_compatibility(y, sr):
    """
    Analyze surround sound compatibility
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Dictionary containing surround compatibility analysis results
    """
    try:
        print("Analyzing surround sound compatibility...")
        
        # Ensure stereo audio
        if y.ndim == 1:
            y = np.vstack((y, y))

        # Calculate mono compatibility
        mono = np.mean(y, axis=0)
        mono_correlation = np.corrcoef(mono, y[0])[0, 1]
        mono_compatibility = min(100, max(0, mono_correlation * 100))

        # Calculate phase relationships
        phase_diff = np.angle(np.correlate(y[0], y[1]))[0]
        phase_score = min(100, max(0, 100 - (abs(phase_diff) * 100)))

        return {
            "mono_compatibility": float(mono_compatibility),
            "phase_score": float(phase_score),
            "analysis": get_surround_compatibility_analysis(mono_compatibility, phase_score)
        }
    except Exception as e:
        print(f"Error in surround compatibility analysis: {str(e)}")
        return {
            "mono_compatibility": 70.0,
            "phase_score": 70.0,
            "analysis": ["Unable to analyze surround compatibility."]
        }


def get_surround_compatibility_analysis(mono_compatibility, phase_score):
    """Generate textual analysis of surround compatibility"""
    analysis = []
    
    if mono_compatibility < 40:
        analysis.append("Poor mono compatibility. May cause phase cancellation in mono playback.")

    if phase_score < 40:
        analysis.append("Potential phase issues. May cause imaging problems in surround systems.")

    if not analysis:
        analysis.append("Good surround sound compatibility with minimal phase issues.")

    return analysis

def analyze_transients(y, sr):
    """
    Analyze transients in the audio signal.
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Dictionary with transient analysis results
    """
    # Calculate onset envelope
    onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Detect onsets
    onsets = librosa.onset.onset_detect(onset_envelope=onset_envelope, sr=sr)
    
    # Calculate transient density (onsets per second)
    duration_sec = len(y) / sr
    transient_density = len(onsets) / duration_sec if duration_sec > 0 else 0
    
    # Calculate average attack time
    if len(onsets) > 0:
        # Convert onsets to time
        onset_times = librosa.frames_to_time(onsets, sr=sr)
        
        # Calculate attack times
        attack_times = []
        for i in range(len(onset_times)):
            # Get onset position in samples
            onset_pos = int(onset_times[i] * sr)
            
            # Define window around onset (100ms before to 50ms after)
            start_pos = max(0, onset_pos - int(0.1 * sr))
            end_pos = min(len(y), onset_pos + int(0.05 * sr))
            
            if start_pos < end_pos:
                # Get segment
                segment = np.abs(y[start_pos:end_pos])
                
                # Find peak position
                peak_pos = np.argmax(segment)
                
                # Calculate attack time in ms (from start to peak)
                attack_time_ms = (peak_pos / sr) * 1000
                
                attack_times.append(attack_time_ms)
        
        average_attack_time = np.mean(attack_times) if attack_times else 15.0  # Default if calculation fails
    else:
        average_attack_time = 15.0  # Default value if no onsets
    
    # Calculate percussion energy (ratio of high frequency transient energy to total energy)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    percussive = librosa.effects.percussive(y)
    percussion_energy = (np.sum(percussive**2) / np.sum(y**2)) * 100 if np.sum(y**2) > 0 else 0
    
    # Calculate transient score based on density, attack time, and percussion energy
    # For density, 1-4 onsets/sec is good for most music
    density_score = 100 - min(100, abs(transient_density - 2.5) * 25)
    
    # For attack time, faster attacks (lower values) are often better but depends on genre
    # 5-15ms is typical for good percussion
    attack_score = 100 - min(100, abs(average_attack_time - 10) * 5)
    
    # For percussion energy, 10-30% is typically good
    percussion_score = 100 - min(100, abs(percussion_energy - 20) * 5)
    
    # Combined score
    transients_score = (density_score + attack_score + percussion_score) / 3
    
    # Generate analysis points
    analysis = []
    
    if transient_density < 1:
        analysis.append("Few transients detected, which could indicate a sparse mix or limited dynamics.")
    elif transient_density < 2:
        analysis.append("Moderate transient density, suitable for slower-paced music.")
    elif transient_density < 4:
        analysis.append("Good transient density, providing rhythmic interest without overcrowding.")
    else:
        analysis.append("High transient density, which may create a busy or energetic feel.")
    
    if average_attack_time < 5:
        analysis.append("Very fast attacks, giving a sharp and aggressive character to percussive elements.")
    elif average_attack_time < 10:
        analysis.append("Fast attacks, providing clarity and impact to transient elements.")
    elif average_attack_time < 20:
        analysis.append("Moderate attack times, balancing impact with smoothness.")
    else:
        analysis.append("Slower attacks, which can sound smoother but may lack impact.")
    
    if percussion_energy < 10:
        analysis.append("Low percussion energy, which may indicate a smoother or less rhythm-focused mix.")
    elif percussion_energy < 20:
        analysis.append("Moderate percussion energy, providing rhythmic drive while maintaining balance.")
    elif percussion_energy < 30:
        analysis.append("Good percussion energy, highlighting rhythmic elements effectively.")
    else:
        analysis.append("High percussion energy, which emphasizes percussive elements strongly.")
    
    # Downsampled transient data for visualization
    # Create a smoothed version of onset envelope for visualization
    hop_length = 512
    frames = range(len(onset_envelope))
    times = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length)
    
    # Downsample to ~100 points for frontend visualization
    if len(onset_envelope) > 100:
        downsample_factor = len(onset_envelope) // 100
        transient_data = onset_envelope[::downsample_factor]
        if len(transient_data) > 100:  # Ensure it's not too large
            transient_data = transient_data[:100]
    else:
        transient_data = onset_envelope
    
    # Normalize for visualization
    max_val = np.max(transient_data) if np.max(transient_data) > 0 else 1
    transient_data = transient_data / max_val
    
    return {
        "transients_score": transients_score,
        "attack_time": average_attack_time,
        "transient_density": transient_density,
        "percussion_energy": percussion_energy,
        "analysis": analysis,
        "transient_data": transient_data.tolist()
    } 

def analyze_headphone_speaker_optimization(y, sr):
    """
    Analyze headphone and speaker optimization
    
    Args:
        y: Audio time series
        sr: Sample rate
    
    Returns:
        Dictionary containing headphone/speaker optimization results
    """
    try:
        print("Analyzing headphone/speaker optimization...")
        
        # Ensure stereo audio
        if y.ndim == 1:
            y = np.vstack((y, y))

        # Calculate crossfeed simulation
        crossfeed_factor = 0.6
        crossfed = y[0] * crossfeed_factor + y[1] * (1 - crossfeed_factor)
        crossfeed_score = min(100, max(0, np.corrcoef(crossfed, y[0])[0, 1] * 100))

        # Calculate bass management
        bass_energy = np.sum(np.abs(y[0][:sr//10] + y[1][:sr//10]))
        bass_score = min(100, max(0, bass_energy * 100))

        return {
            "headphone_score": float(crossfeed_score),
            "speaker_score": float(bass_score),
            "analysis": get_headphone_speaker_analysis(crossfeed_score, bass_score)
        }
    except Exception as e:
        print(f"Error in headphone/speaker optimization analysis: {str(e)}")
        return {
            "headphone_score": 70.0,
            "speaker_score": 70.0,
            "analysis": ["Unable to analyze headphone/speaker optimization."]
        }


def get_headphone_speaker_analysis(headphone_score, speaker_score):
    """Generate textual analysis of headphone/speaker optimization"""
    analysis = []
    
    if headphone_score < 40:
        analysis.append("Poor headphone optimization. May cause listening fatigue.")
    elif headphone_score > 90:
        analysis.append("Excessive headphone optimization. May reduce stereo width.")

    if speaker_score < 40:
        analysis.append("Poor speaker optimization. Bass may sound weak.")
    elif speaker_score > 90:
        analysis.append("Excessive speaker optimization. Bass may overpower the mix.")

    if not analysis:
        analysis.append("Good optimization for both headphones and speakers.")

    return analysis