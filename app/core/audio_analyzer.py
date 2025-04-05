import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy import stats
import os
from pydub import AudioSegment
import tempfile
import matplotlib
import time  # Add time module for tracking performance
import traceback  # Add traceback for detailed error logging
matplotlib.use('Agg')  # Use non-interactive backend
from .music_theory_data.key_relationships import get_key_relationship_info
import threading
import concurrent.futures

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

def analyze_mix(file_path, is_instrumental=None):
    """
    Analyze an audio file and return metrics about the mix quality.
    
    Args:
        file_path: Path to the audio file
        is_instrumental: Boolean indicating if the track is instrumental (no vocals)
        
    Returns:
        Dictionary containing analysis results
    """
    # Track total analysis time
    total_start_time = time.time()
    
    # Initialize default results at the start of the function
    default_results = {
        "channel_info": {
            "is_mono": True,
            "channel_count": 1,
            "analysis": ["Unable to determine channel information"]
        },
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
    
    try:
        print(f"\n{'='*50}")
        print(f"STARTING ANALYSIS: {file_path}")
        print(f"Is instrumental: {is_instrumental}")
        print(f"{'='*50}\n")
        
        # Step 1: Load audio file
        print(f"Loading audio file for analysis: {file_path}")
        load_start = time.time()
        y, sr = librosa.load(file_path, sr=None, mono=False)
        print(f"Audio loaded in {time.time() - load_start:.2f} seconds")
        print(f"Sample rate: {sr} Hz")
        
        # Check audio shape and calculate duration
        if y.ndim == 1:
            print(f"Loaded audio shape: {y.shape}, dimensions: {y.ndim}")
            print(f"Audio duration: {y.shape[0]/sr:.2f} seconds")
        else:
            print(f"Loaded audio shape: {y.shape}, dimensions: {y.ndim}")
            print(f"Audio duration: {y.shape[1]/sr:.2f} seconds")
        
        # Handle mono files by duplicating the channel
        if y.ndim == 1:
            print("Mono file detected, converting to stereo format")
            y = np.vstack((y, y))
        elif y.ndim == 2 and y.shape[0] == 1:
            print("Single channel detected, converting to stereo format")
            y = np.vstack((y[0], y[0]))
        elif y.ndim == 2 and y.shape[0] > 2:
            print("Multi-channel file detected, using first two channels")
            print(f"Original channels: {y.shape[0]}")
            y = y[:2]
        
        print(f"Final audio shape: {y.shape}, dimensions: {y.ndim}")
        print(f"Max amplitude: Left={np.max(np.abs(y[0])):.4f}, Right={np.max(np.abs(y[1])):.4f}")
        
        # Get left and right channels
        y_left = y[0]
        y_right = y[1]
        
        # Create mono version for certain analyses
        y_mono = np.mean(y, axis=0)
        
        # Calculate various metrics with error handling
        results = {}
        
        # Step 2: Analyze frequency balance
        print(f"\n{'*'*40}")
        print("Step 2: Analyzing frequency balance...")
        start_time = time.time()
        try:
            results["frequency_balance"] = analyze_frequency_balance(y, sr, is_instrumental)
            print(f"Frequency balance analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Balance score: {results['frequency_balance']['balance_score']:.2f}")
            for band, energy in results['frequency_balance']['band_energy'].items():
                print(f"  {band}: {energy:.2f}%")
        except Exception as e:
            print(f"Error in frequency balance analysis: {str(e)}")
            results["frequency_balance"] = default_results["frequency_balance"]
            
        # Step 3: Analyze dynamic range
        print(f"\n{'*'*40}")
        print("Step 3: Analyzing dynamic range...")
        start_time = time.time()
        try:
            results["dynamic_range"] = analyze_dynamic_range(y)
            print(f"Dynamic range analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Dynamic range: {results['dynamic_range']['dynamic_range_db']:.2f} dB")
            print(f"Crest factor: {results['dynamic_range']['crest_factor_db']:.2f} dB")
            print(f"PLR: {results['dynamic_range']['plr']:.2f} dB")
            print(f"Dynamic range score: {results['dynamic_range']['dynamic_range_score']:.2f}")
        except Exception as e:
            print(f"Error in dynamic range analysis: {str(e)}")
            results["dynamic_range"] = default_results["dynamic_range"]
            
        # Step 4: Analyze stereo field
        print(f"\n{'*'*40}")
        print("Step 4: Analyzing stereo field...")
        start_time = time.time()
        try:
            results["stereo_field"] = analyze_stereo_field(y_left, y_right)
            print(f"Stereo field analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Channel correlation: {results['stereo_field']['correlation']:.4f}")
            print(f"Mid/Side ratio: {results['stereo_field']['mid_ratio']:.4f}/{results['stereo_field']['side_ratio']:.4f}")
            print(f"Width score: {results['stereo_field']['width_score']:.2f}")
            print(f"Phase score: {results['stereo_field']['phase_score']:.2f}")
        except Exception as e:
            print(f"Error in stereo field analysis: {str(e)}")
            results["stereo_field"] = default_results["stereo_field"]
            
        # Step 5: Analyze clarity
        print(f"\n{'*'*40}")
        print("Step 5: Analyzing clarity...")
        start_time = time.time()
        try:
            results["clarity"] = analyze_clarity(y, sr, is_instrumental)
            print(f"Clarity analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Clarity score: {results['clarity']['clarity_score']:.2f}")
            print(f"Spectral contrast: {results['clarity']['spectral_contrast']:.4f}")
            print(f"Spectral flatness: {results['clarity']['spectral_flatness']:.4f}")
            print(f"Spectral centroid: {results['clarity']['spectral_centroid']:.2f} Hz")
        except Exception as e:
            print(f"Error in clarity analysis: {str(e)}")
            results["clarity"] = default_results["clarity"]
            
        # Step 6: Analyze harmonic content
        print(f"\n{'*'*40}")
        print("Step 6: Analyzing harmonic content...")
        start_time = time.time()
        try:
            results["harmonic_content"] = analyze_harmonic_content(y, sr)
            print(f"Harmonic content analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Detected key: {results['harmonic_content']['key']}")
            print(f"Harmonic complexity: {results['harmonic_content']['harmonic_complexity']:.2f}%")
            print(f"Key consistency: {results['harmonic_content']['key_consistency']:.2f}%")
            print(f"Chord changes per minute: {results['harmonic_content']['chord_changes_per_minute']:.2f}")
            if 'top_key_candidates' in results['harmonic_content']:
                print("Top key candidates: ", end="")
                for key_candidate in results['harmonic_content']['top_key_candidates'][:3]:
                    print(f"{key_candidate}, ", end="")
                print()
        except Exception as e:
            print(f"Error in harmonic content analysis: {str(e)}")
            results["harmonic_content"] = default_results["harmonic_content"]
            
        # Step 7: Analyze transients
        print(f"\n{'*'*40}")
        print("Step 7: Analyzing transients...")
        start_time = time.time()
        try:
            results["transients"] = analyze_transients(y_mono, sr)
            print(f"Transients analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Transients score: {results['transients']['transients_score']:.2f}")
            print(f"Attack time: {results['transients']['attack_time']:.2f} ms")
            print(f"Transient density: {results['transients']['transient_density']:.2f} onsets/sec")
            print(f"Percussion energy: {results['transients']['percussion_energy']:.2f}%")
            print(f"Detected {len(results['transients'].get('transient_data', []))} transients")
        except Exception as e:
            print(f"Error in transients analysis: {str(e)}")
            results["transients"] = default_results["transients"]
            
        # Step 8: Analyze 3D spatial
        print(f"\n{'*'*40}")
        print("Step 8: Analyzing 3D spatial imaging...")
        start_time = time.time()
        try:
            results["3d_spatial"] = analyze_3d_spatial(y, sr)
            print(f"3D spatial analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Height score: {results['3d_spatial']['height_score']:.2f}%")
            print(f"Depth score: {results['3d_spatial']['depth_score']:.2f}%")
            print(f"Width consistency: {results['3d_spatial']['width_consistency']:.2f}%")
        except Exception as e:
            print(f"Error in 3D spatial analysis: {str(e)}")
            results["3d_spatial"] = default_results["3d_spatial"]
            
        # Step 9: Analyze surround compatibility
        print(f"\n{'*'*40}")
        print("Step 9: Analyzing surround sound compatibility...")
        start_time = time.time()
        try:
            results["surround_compatibility"] = analyze_surround_compatibility(y, sr)
            print(f"Surround compatibility analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Mono compatibility: {results['surround_compatibility']['mono_compatibility']:.2f}%")
            print(f"Phase score: {results['surround_compatibility']['phase_score']:.2f}%")
        except Exception as e:
            print(f"Error in surround compatibility analysis: {str(e)}")
            results["surround_compatibility"] = default_results["surround_compatibility"]
            
        # Step 10: Analyze headphone/speaker optimization
        print(f"\n{'*'*40}")
        print("Step 10: Analyzing headphone/speaker optimization...")
        start_time = time.time()
        try:
            results["headphone_speaker_optimization"] = analyze_headphone_speaker_optimization(y, sr)
            print(f"Headphone/speaker optimization analysis completed in {time.time() - start_time:.2f} seconds")
            print(f"Headphone score: {results['headphone_speaker_optimization']['headphone_score']:.2f}%")
            print(f"Speaker score: {results['headphone_speaker_optimization']['speaker_score']:.2f}%")
        except Exception as e:
            print(f"Error in headphone/speaker optimization analysis: {str(e)}")
            results["headphone_speaker_optimization"] = default_results["headphone_speaker_optimization"]
        
        # Step 11: Generate visualizations
        print(f"\n{'*'*40}")
        print("Step 11: Generating visualizations...")
        start_time = time.time()
        try:
            results["visualizations"] = generate_visualizations(file_path, y=y, sr=sr)
            print(f"Visualizations generated in {time.time() - start_time:.2f} seconds")
            
            # Print the paths to the generated files
            for vis_type, vis_path in results["visualizations"].items():
                if vis_path:
                    print(f"Generated {vis_type}: {vis_path}")
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
            results["visualizations"] = generate_error_visualizations()
        
        # Step 12: Calculate overall score
        print(f"\n{'*'*40}")
        print("Step 12: Calculating overall score...")
        start_time = time.time()
        try:
            results["overall_score"] = calculate_overall_score(results)
            print(f"Overall score calculated in {time.time() - start_time:.2f} seconds")
            print(f"Final overall score: {results['overall_score']:.1f}/100")
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
        
        total_time = time.time() - total_start_time
        print(f"\n{'='*50}")
        print(f"ANALYSIS COMPLETE: {file_path}")
        print(f"Total analysis time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"{'='*50}\n")
        
        return results
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        # Return a complete error response with default values
        error_results = default_results.copy()
        error_results["error"] = True
        error_results["message"] = str(e)
        error_results["visualizations"] = generate_error_visualizations()
        error_results["overall_score"] = 70.0
        
        total_time = time.time() - total_start_time
        print(f"\n{'='*50}")
        print(f"ANALYSIS FAILED: {file_path}")
        print(f"Error: {str(e)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"{'='*50}\n")
        
        return error_results

def analyze_frequency_balance(y, sr, is_instrumental=None):
    """
    Analyze the frequency balance of the mix
    
    Args:
        y: Audio time series
        sr: Sample rate
        is_instrumental: Boolean indicating if the track is instrumental (no vocals)
    
    Returns:
        Dictionary containing frequency balance analysis results
    """
    start_time = time.time()
    try:
        print(f"\n{'-'*30}")
        print("FREQUENCY BALANCE ANALYSIS:")
        print(f"Is instrumental: {is_instrumental}")
        
        # Convert to mono for frequency analysis
        print("Converting to mono for frequency analysis...")
        mono_start = time.time()
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        print(f"Conversion completed in {time.time() - mono_start:.4f} seconds")
        
        # Compute the short-time Fourier transform
        print("Computing STFT...")
        stft_start = time.time()
        D = np.abs(librosa.stft(y_mono))
        print(f"STFT shape: {D.shape}")
        print(f"STFT computed in {time.time() - stft_start:.4f} seconds")
        
        # Convert to dB scale
        print("Converting to dB scale...")
        D_db = librosa.amplitude_to_db(D, ref=np.max)
        
        # Get frequency bands
        freqs = librosa.fft_frequencies(sr=sr)
        print(f"Frequency range: {freqs[0]:.1f}Hz - {freqs[-1]:.1f}Hz with {len(freqs)} points")
        
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
        
        print("Analyzing frequency bands...")
        # Calculate average energy in each band
        band_energy = {}
        for band_name, (low, high) in bands.items():
            band_start = time.time()
            # Find indices for the frequency range
            indices = np.where((freqs >= low) & (freqs <= high))[0]
            if len(indices) > 0:
                # Calculate mean energy in this band
                band_energy[band_name] = float(np.mean(D_db[:, indices]))
                print(f"  {band_name}: {len(indices)} frequency bins, raw energy: {band_energy[band_name]:.2f}dB (calculated in {time.time() - band_start:.4f}s)")
            else:
                band_energy[band_name] = -80.0  # Default low value if no frequencies in range
                print(f"  {band_name}: No frequency bins in range, using default -80.0dB")
        
        # Normalize values to 0-100 scale
        print("Normalizing band energy to 0-100 scale...")
        min_energy = min(band_energy.values())
        max_energy = max(band_energy.values())
        print(f"Raw energy range: {min_energy:.2f}dB to {max_energy:.2f}dB")
        range_energy = max_energy - min_energy if max_energy > min_energy else 1
        
        normalized_energy = {
            band: float(((energy - min_energy) / range_energy) * 100)
            for band, energy in band_energy.items()
        }
        
        # Print normalized energy values
        for band, energy in normalized_energy.items():
            print(f"  {band}: normalized to {energy:.2f}%")
        
        # Calculate balance score based on ideal curve and deviation
        print("Calculating balance score against ideal curve...")
        
        # Use different ideal curves based on whether the track is instrumental or has vocals
        if is_instrumental:
            # Ideal curve for instrumental tracks - more balanced between low and high frequencies
            ideal_curve = {
                "sub_bass": 80,
                "bass": 85,
                "low_mids": 80,
                "mids": 75,
                "high_mids": 70,
                "highs": 70,
                "air": 65
            }
            print("Using ideal curve for instrumental tracks")
        else:
            # Ideal curve for tracks with vocals - more emphasis on mid frequencies
            ideal_curve = {
                "sub_bass": 75,
                "bass": 80,
                "low_mids": 85,
                "mids": 90,  # Higher emphasis on mids for vocals
                "high_mids": 85,
                "highs": 75,
                "air": 65
            }
            print("Using ideal curve for tracks with vocals")
        
        # Calculate deviation from ideal curve
        deviations = [abs(normalized_energy[band] - ideal_curve[band]) for band in bands.keys()]
        for i, band in enumerate(bands.keys()):
            print(f"  {band}: ideal={ideal_curve[band]:.1f}%, actual={normalized_energy[band]:.1f}%, deviation={deviations[i]:.1f}%")
            
        avg_deviation = float(np.mean(deviations))
        print(f"Average deviation from ideal curve: {avg_deviation:.2f}%")
        
        # Convert to a 0-100 score (lower deviation is better)
        balance_score = float(max(0, min(100, 100 - avg_deviation)))
        print(f"Final balance score: {balance_score:.2f}/100")
        
        analysis = get_frequency_balance_analysis(normalized_energy, is_instrumental)
        print("Generated analysis:")
        for item in analysis:
            print(f"  - {item}")
        
        total_time = time.time() - start_time
        print(f"Frequency balance analysis completed in {total_time:.2f} seconds")
        print(f"{'-'*30}\n")
        
        return {
            "band_energy": normalized_energy,
            "balance_score": balance_score,
            "analysis": analysis,
            "is_instrumental": is_instrumental
        }
    except Exception as e:
        print(f"Error in frequency balance analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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
            "analysis": ["Unable to analyze frequency balance."],
            "is_instrumental": is_instrumental
        }

def get_frequency_balance_analysis(normalized_energy, is_instrumental=None):
    """
    Generate textual analysis of frequency balance
    
    Args:
        normalized_energy: Dictionary of normalized energy values for each frequency band
        is_instrumental: Boolean indicating if the track is instrumental (no vocals)
        
    Returns:
        List of analysis points
    """
    analysis = []
    
    # Check for potential issues - different thresholds based on track type
    if is_instrumental:
        # Analysis for instrumental tracks
        
        if normalized_energy["sub_bass"] > 95:
            analysis.append("Sub bass is very prominent, which may cause muddiness in this instrumental track.")
        elif normalized_energy["sub_bass"] < 40:
            analysis.append("Sub bass is lacking, instrumental mix may sound thin without a foundation.")
            
        if normalized_energy["bass"] > 95:
            analysis.append("Bass is very prominent, which may overpower melodic elements in this instrumental track.")
        elif normalized_energy["bass"] < 40:
            analysis.append("Bass is lacking, instrumental mix may lack warmth and impact.")
        
        if normalized_energy["mids"] < 40:
            analysis.append("Mids are recessed, instrumental mix may sound hollow (scooped mids).")
        
        if normalized_energy["high_mids"] > 95:
            analysis.append("High mids are very prominent, instrumental elements may sound harsh.")
        
        if normalized_energy["highs"] > 95:
            analysis.append("Highs are very prominent, instrumental mix may sound brittle or cause ear fatigue.")
        elif normalized_energy["highs"] < 40:
            analysis.append("Highs are lacking, instrumental details may be lost and mix may sound dull.")

        # Additional instrumental-specific analysis
        if normalized_energy["mids"] > normalized_energy["low_mids"] and normalized_energy["mids"] > normalized_energy["high_mids"]:
            analysis.append("Good balance for melodic instrumental elements in the mid-range.")
            
        # Check for extended frequency content
        good_extremes = (normalized_energy["sub_bass"] > 50) and (normalized_energy["air"] > 50)
        if good_extremes:
            analysis.append("Good extended frequency range, providing a full spectrum instrumental sound.")
        
    else:
        # Analysis for tracks with vocals
        
        if normalized_energy["sub_bass"] > 95:
            analysis.append("Sub bass is very prominent, which may mask vocals and cause muddiness.")
        elif normalized_energy["sub_bass"] < 40:
            analysis.append("Sub bass is lacking, mix may sound thin beneath the vocals.")
            
        if normalized_energy["bass"] > 95:
            analysis.append("Bass is very prominent, which may compete with lower vocal registers.")
        elif normalized_energy["bass"] < 40:
            analysis.append("Bass is lacking, vocal-focused mix may lack warmth and foundation.")
        
        # Vocal presence checks
        if normalized_energy["mids"] < 60:
            analysis.append("Mids are recessed, vocals may lack presence and clarity.")
        elif normalized_energy["mids"] > 95:
            analysis.append("Mids are very emphasized, vocals may sound too forward or harsh.")
            
        vocal_presence = normalized_energy["mids"] + normalized_energy["high_mids"]
        if vocal_presence < 140:
            analysis.append("Potential lack of vocal presence in the mid and high-mid range.")
        elif vocal_presence > 180:
            analysis.append("Vocals may be overly emphasized in the mid and high-mid range.")
        
        if normalized_energy["high_mids"] > 95:
            analysis.append("High mids are very prominent, may cause vocal sibilance issues.")
        
        if normalized_energy["highs"] > 95:
            analysis.append("Highs are very prominent, may exaggerate vocal sibilance or create brittleness.")
        elif normalized_energy["highs"] < 40:
            analysis.append("Highs are lacking, vocal air and detail may be lost.")
            
        # Check for potential vocal clarity issues
        if normalized_energy["mids"] > 80 and normalized_energy["low_mids"] > 80:
            analysis.append("Potential vocal clarity issue with both mids and low-mids being prominent.")
    
    # Common analysis for both types
    if len(analysis) == 0:
        if is_instrumental:
            analysis.append("Frequency balance appears well suited for instrumental music.")
        else:
            analysis.append("Frequency balance appears well suited for music with vocals.")
    
    return analysis

def analyze_dynamic_range(y):
    """Analyze the dynamic range of the mix"""
    start_time = time.time()
    try:
        print(f"\n{'-'*30}")
        print("DYNAMIC RANGE ANALYSIS:")
        
        # Convert to mono for dynamic range analysis
        print("Converting to mono for dynamic range analysis...")
        mono_start = time.time()
        y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
        print(f"Conversion completed in {time.time() - mono_start:.4f} seconds")
        print(f"Audio max amplitude: {np.max(np.abs(y_mono)):.4f}")
        
        # Calculate RMS energy in small windows
        print("Calculating RMS energy in windows...")
        rms_start = time.time()
        frame_length = 2048
        hop_length = 512
        print(f"Frame length: {frame_length}, Hop length: {hop_length}")
        rms = librosa.feature.rms(y=y_mono, frame_length=frame_length, hop_length=hop_length)[0]
        print(f"RMS calculation completed in {time.time() - rms_start:.4f} seconds")
        print(f"RMS shape: {rms.shape}")
        print(f"RMS range: {np.min(rms):.6f} to {np.max(rms):.6f}")
        
        # Convert to dB
        print("Converting RMS to dB...")
        rms_db = 20 * np.log10(rms + 1e-8)  # Adding small value to avoid log(0)
        print(f"RMS dB range: {np.min(rms_db):.2f}dB to {np.max(rms_db):.2f}dB")
        
        # Calculate crest factor
        print("Calculating crest factor...")
        peak = np.max(np.abs(y_mono))
        rms_overall = np.sqrt(np.mean(y_mono**2))
        crest_factor = peak / rms_overall
        crest_factor_db = 20 * np.log10(crest_factor)
        print(f"Peak amplitude: {peak:.6f}")
        print(f"Overall RMS: {rms_overall:.6f}")
        print(f"Crest factor: {crest_factor:.2f} ({crest_factor_db:.2f}dB)")
        
        # Calculate percentiles for dynamic range
        print("Calculating dynamic range using percentiles...")
        percentile_start = time.time()
        valid_rms = rms_db[rms_db > -80]  # Only consider non-silent parts
        print(f"Valid RMS samples: {len(valid_rms)} of {len(rms_db)} ({len(valid_rms)/len(rms_db)*100:.1f}%)")
        
        p95 = np.percentile(valid_rms, 95)  # 95th percentile (loud parts)
        p5 = np.percentile(valid_rms, 5)    # 5th percentile (quiet parts)
        dynamic_range = p95 - p5
        print(f"5th percentile: {p5:.2f}dB")
        print(f"95th percentile: {p95:.2f}dB")
        print(f"Dynamic range (p95-p5): {dynamic_range:.2f}dB")
        print(f"Percentile calculation completed in {time.time() - percentile_start:.4f} seconds")
        
        # Calculate PLR (Peak to Loudness Ratio)
        print("Calculating PLR (Peak to Loudness Ratio)...")
        peak_db = 20 * np.log10(peak + 1e-8)
        loudness = np.mean(valid_rms)
        plr = peak_db - loudness
        print(f"Peak level: {peak_db:.2f}dB")
        print(f"Average loudness: {loudness:.2f}dB")
        print(f"PLR: {plr:.2f}dB")
        
        # Score based on dynamic range (0-100)
        print("Calculating dynamic range score...")
        dr_score = min(100, max(0, dynamic_range * 5))
        print(f"Dynamic range score: {dr_score:.2f}/100")
        
        # Analyze if the mix is over-compressed
        is_overcompressed = dynamic_range < 8
        print(f"Is over-compressed: {is_overcompressed}")
        
        analysis = get_dynamic_range_analysis(dynamic_range, crest_factor_db)
        print("Generated analysis:")
        for item in analysis:
            print(f"  - {item}")
        
        total_time = time.time() - start_time
        print(f"Dynamic range analysis completed in {total_time:.2f} seconds")
        print(f"{'-'*30}\n")
        
        return {
            "dynamic_range_db": dynamic_range,
            "crest_factor_db": crest_factor_db,
            "plr": plr,
            "dynamic_range_score": dr_score,
            "analysis": analysis
        }
    except Exception as e:
        print(f"Error in dynamic range analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "dynamic_range_db": 12.0,
            "crest_factor_db": 15.0,
            "plr": 12.0,
            "dynamic_range_score": 70.0,
            "analysis": ["Unable to analyze dynamic range."]
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

def analyze_clarity(y, sr, is_instrumental=None):
    """
    Analyze the clarity and definition of the mix
    
    Args:
        y: Audio time series
        sr: Sample rate
        is_instrumental: Boolean indicating if the track is instrumental (no vocals)
        
    Returns:
        Dictionary containing clarity analysis results
    """
    try:
        print("Starting clarity analysis...")
        print(f"Is instrumental: {is_instrumental}")
        
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
            # First check if audio is too quiet which might cause empty spectral data
            if np.max(np.abs(y_mono)) < 1e-6:  # Lowered threshold to catch only truly silent audio
                print("Audio is very quiet, using default spectral contrast value")
                contrast_mean = 0.5
                contrast = np.zeros((4, 1))  # Default shape for analysis
                successful_fft_params = {"n_fft": 0, "hop_length": 0, "method": "default_quiet"}
            else:
                # Try multiple approaches to get a valid spectral contrast value
                successful_fft_params = {"n_fft": 0, "hop_length": 0, "method": "default"}
                contrast_results = []
                
                # Try different parameters
                for n_fft in [2048, 4096, 1024]:
                    for hop_length in [512, 1024, 256]:
                        try:
                            # Suppress numpy warnings temporarily
                            with np.errstate(all='ignore'):
                                contrast = librosa.feature.spectral_contrast(
                                    y=y_mono,
                                    sr=sr,
                                    n_bands=4,
                                    fmin=20.0,
                                    n_fft=n_fft,
                                    hop_length=hop_length
                                )
                                
                                # Check if we got valid results
                                if contrast.size > 0 and not np.all(np.isnan(contrast)):
                                    # Use absolute values to ensure positive contrast measurements
                                    contrast_abs = np.abs(contrast)
                                    
                                    # Get mean across time and frequency bands
                                    contrast_frame_means = np.nanmean(contrast_abs, axis=0)
                                    if not np.all(np.isnan(contrast_frame_means)) and contrast_frame_means.size > 0:
                                        # Store this calculation result
                                        contrast_result = float(np.nanmean(contrast_frame_means))
                                        if not np.isnan(contrast_result) and not np.isinf(contrast_result):
                                            contrast_results.append({
                                                "value": contrast_result,
                                                "n_fft": n_fft, 
                                                "hop_length": hop_length
                                            })
                                            print(f"Got contrast value {contrast_result:.6f} with n_fft={n_fft}, hop_length={hop_length}")
                        except Exception as e:
                            print(f"Failed with n_fft={n_fft}, hop_length={hop_length}: {str(e)}")
                            continue
                
                # Check if we got any valid results
                if contrast_results:
                    # Sort results by contrast value (descending) and take the highest
                    contrast_results.sort(key=lambda x: x["value"], reverse=True)
                    best_result = contrast_results[0]
                    contrast_mean = best_result["value"]
                    successful_fft_params = {
                        "n_fft": best_result["n_fft"], 
                        "hop_length": best_result["hop_length"],
                        "method": "spectral_contrast"
                    }
                    print(f"Using best contrast value: {contrast_mean:.6f}")
                else:
                    # Alternative approach using DIY spectral contrast
                    print("Using alternative spectral contrast calculation")
                    try:
                        # Calculate STFT
                        stft = np.abs(librosa.stft(y_mono, n_fft=2048, hop_length=512))
                        
                        if stft.size > 0:
                            # Convert to log amplitude
                            log_stft = librosa.amplitude_to_db(stft, ref=np.max)
                            
                            # Split the spectrum into 4 frequency bands
                            band_edges = np.logspace(np.log10(20), np.log10(sr/2), 5)
                            freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
                            
                            band_contrasts = []
                            for i in range(4):
                                # Get indices for this frequency band
                                band_mask = (freqs >= band_edges[i]) & (freqs < band_edges[i+1])
                                
                                if np.any(band_mask):
                                    # Get spectrum for this band
                                    band_spectrum = log_stft[band_mask, :]
                                    
                                    if band_spectrum.size > 0:
                                        # Calculate contrast as the standard deviation
                                        band_contrast = np.std(band_spectrum, axis=0)
                                        if band_contrast.size > 0:
                                            mean_band_contrast = np.nanmean(band_contrast)
                                            if not np.isnan(mean_band_contrast):
                                                band_contrasts.append(mean_band_contrast)
                            
                            if band_contrasts:
                                # Average the contrasts across all bands
                                # Scale to typical spectral contrast range
                                contrast_mean = float(np.nanmean(band_contrasts) / 60)
                                # Ensure the result is in a reasonable range
                                contrast_mean = min(0.9, max(0.1, contrast_mean))
                                successful_fft_params = {
                                    "n_fft": 2048, 
                                    "hop_length": 512,
                                    "method": "alternative_bands_std"
                                }
                            else:
                                # Fallback to basic std dev if band approach failed
                                overall_contrast = np.std(log_stft, axis=0)
                                contrast_mean = float(np.nanmean(overall_contrast) / 60)
                                contrast_mean = min(0.9, max(0.1, contrast_mean))
                                successful_fft_params = {
                                    "n_fft": 2048, 
                                    "hop_length": 512,
                                    "method": "alternative_std"
                                }
                        else:
                            contrast_mean = 0.5
                            successful_fft_params = {"n_fft": 0, "hop_length": 0, "method": "alternative_empty_stft"}
                    except Exception as e:
                        print(f"Alternative calculation failed: {str(e)}")
                        contrast_mean = 0.5
                        successful_fft_params = {"n_fft": 0, "hop_length": 0, "method": "alternative_error"}
            
            # Scale the contrast to make it perceptually meaningful
            # Use a logarithmic scaling to emphasize differences
            if contrast_mean > 0 and contrast_mean < 1:
                # Apply logarithmic scaling to enhance differences
                log_base = 10
                scaled_contrast = np.log(1 + (log_base - 1) * contrast_mean) / np.log(log_base)
                # Store both raw and scaled values
                contrast_raw = contrast_mean
                contrast_mean = scaled_contrast
                print(f"Raw contrast: {contrast_raw:.6f}, Scaled contrast: {contrast_mean:.6f}")
                
                # Add scaling info to fft_params
                successful_fft_params["scaling"] = "logarithmic"
                successful_fft_params["raw_value"] = float(contrast_raw)
            
            # Ensure the value is valid
            if np.isnan(contrast_mean) or np.isinf(contrast_mean):
                print("Warning: Invalid final contrast value, using default")
                contrast_mean = 0.5
                
            print(f"Final spectral contrast: {contrast_mean}")
        except Exception as e:
            print(f"Error calculating spectral contrast: {str(e)}")
            contrast_mean = 0.5  # Default value
            contrast = np.zeros((4, 1))  # Default shape for analysis
            successful_fft_params = {"n_fft": 0, "hop_length": 0, "method": "error_fallback"}
        
        print("Calculating spectral flatness...")
        # Calculate spectral flatness with error handling
        try:
            if np.max(np.abs(y_mono)) < 1e-5:
                print("Audio is very quiet, using default spectral flatness value")
                flatness_mean = 0.5
            else:
                flatness = librosa.feature.spectral_flatness(y=y_mono)
                # More robust checking for valid flatness data
                if flatness.size > 0 and not np.all(np.isnan(flatness)):
                    with np.errstate(all='ignore'):  # Suppress all numpy warnings
                        flatness_mean = float(np.nanmean(flatness))
                        if np.isnan(flatness_mean) or np.isinf(flatness_mean):
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
            if np.max(np.abs(y_mono)) < 1e-5:
                print("Audio is very quiet, using default spectral centroid value")
                centroid_mean = sr/4
            else:
                centroid = librosa.feature.spectral_centroid(y=y_mono, sr=sr)
                # More robust checking for valid centroid data
                if centroid.size > 0 and not np.all(np.isnan(centroid)):
                    with np.errstate(all='ignore'):  # Suppress all numpy warnings
                        centroid_mean = float(np.nanmean(centroid))
                        if np.isnan(centroid_mean) or np.isinf(centroid_mean):
                            print("Warning: Invalid value in spectral centroid mean, using default")
                            centroid_mean = sr/4
                else:
                    print("Empty or invalid centroid array, using default value")
                    centroid_mean = sr/4
            print(f"Spectral centroid calculated: {centroid_mean}")
        except Exception as e:
            print(f"Error calculating spectral centroid: {str(e)}")
            centroid_mean = sr/4  # Default value
        
        # Calculate clarity score (0-100) with bounds checking and adjustments for track type
        try:
            # Different weights for instrumental vs. vocal tracks
            if is_instrumental:
                # For instrumental tracks - higher weight on contrast and flatness
                contrast_weight = 0.5  # Higher contrast weight for instrumental clarity
                flatness_weight = 0.3
                centroid_weight = 0.2
                print("Using instrumental weights for clarity score calculation")
            else:
                # For tracks with vocals - higher weight on centroid for vocal clarity
                contrast_weight = 0.4
                flatness_weight = 0.2
                centroid_weight = 0.4  # Higher centroid weight for vocal clarity
                print("Using vocal weights for clarity score calculation")
            
            # Scale contrast score between 0-100
            contrast_score = min(100, max(0, contrast_mean * 1000))
            if np.isnan(contrast_score):
                contrast_score = 70.0
            
            # Convert flatness to score (lower flatness is better for clarity)
            flatness_score = min(100, max(0, (1 - flatness_mean) * 100))
            if np.isnan(flatness_score):
                flatness_score = 70.0
            
            # Calculate centroid score with different optimal ranges based on track type
            if is_instrumental:
                # For instrumental, a wider range can be optimal
                centroid_score = min(100, max(0, 100 - abs(centroid_mean - sr/4)/(sr/8)))
            else:
                # For vocals, a more specific range focused on vocal clarity
                # Approx 1-5 kHz for vocal clarity
                vocal_clarity_center = sr/8 + sr/6  # Aim for a bit higher centroid for vocals
                centroid_score = min(100, max(0, 100 - abs(centroid_mean - vocal_clarity_center)/(sr/10)))
            
            if np.isnan(centroid_score):
                centroid_score = 70.0
            
            # Combine scores with weights
            clarity_score = float(
                contrast_score * contrast_weight +
                flatness_score * flatness_weight +
                centroid_score * centroid_weight
            )
            
            # Ensure final score is between 0-100 and not NaN
            clarity_score = min(100, max(0, clarity_score))
            if np.isnan(clarity_score):
                clarity_score = 70.0
                
            print(f"Final clarity score calculated: {clarity_score}")
            print(f"Component scores - Contrast: {contrast_score:.1f}, Flatness: {flatness_score:.1f}, Centroid: {centroid_score:.1f}")
            print(f"Component weights - Contrast: {contrast_weight:.1f}, Flatness: {flatness_weight:.1f}, Centroid: {centroid_weight:.1f}")
            
        except Exception as e:
            print(f"Error calculating clarity score: {str(e)}")
            clarity_score = 70.0  # Default score
        
        # Generate analysis text
        analysis = get_clarity_analysis(contrast_mean, flatness_mean, centroid_mean, sr, is_instrumental)
        
        # Ensure all values are valid for JSON
        result = {
            "clarity_score": float(clarity_score),
            "spectral_contrast": float(contrast_mean),
            "spectral_flatness": float(flatness_mean),
            "spectral_centroid": float(centroid_mean),
            "analysis": analysis,
            "is_instrumental": is_instrumental,
            "fft_params": successful_fft_params  # Add the successful FFT parameters
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
            "analysis": [f"Unable to analyze clarity: {str(e)}"],
            "fft_params": {"n_fft": 0, "hop_length": 0, "method": "error"}
        }

def get_clarity_analysis(contrast, flatness, centroid, sr, is_instrumental=None):
    """
    Generate textual analysis of clarity
    
    Args:
        contrast: Spectral contrast value
        flatness: Spectral flatness value
        centroid: Spectral centroid value
        sr: Sample rate
        is_instrumental: Boolean indicating if the track is instrumental (no vocals)
        
    Returns:
        List of analysis points
    """
    try:
        analysis = []
        
        # Analyze spectral contrast
        if is_instrumental:
            # Instrumental tracks often benefit from higher contrast
            if contrast < 0.1:
                analysis.append("Very low spectral contrast - instrumental elements may lack definition and separation.")
            elif contrast < 0.3:
                analysis.append("Low spectral contrast - consider enhancing separation between instrumental elements.")
            elif contrast < 0.6:
                analysis.append("Moderate spectral contrast - good balance between instrumental elements.")
            else:
                analysis.append("High spectral contrast - excellent separation between instrumental elements.")
        else:
            # Vocal tracks need enough contrast for vocal clarity but not too much
            if contrast < 0.1:
                analysis.append("Very low spectral contrast - vocals may lack definition against the backing music.")
            elif contrast < 0.25:
                analysis.append("Low spectral contrast - consider enhancing separation between vocals and background elements.")
            elif contrast < 0.5:
                analysis.append("Moderate spectral contrast - good balance between vocals and instrumental elements.")
            else:
                analysis.append("High spectral contrast - excellent separation between vocal and instrumental elements.")
        
        # Analyze spectral flatness - similar for both types but with different implications
        if is_instrumental:
            if flatness < 0.2:
                analysis.append("Low spectral flatness indicates good tonal focus in instrumental elements.")
            elif flatness < 0.4:
                analysis.append("Moderate spectral flatness - good balance between tonal and textural elements.")
            else:
                analysis.append("High spectral flatness may indicate noise or lack of tonal focus in instrumental parts.")
        else:
            if flatness < 0.2:
                analysis.append("Low spectral flatness indicates good tonal focus, favorable for vocal clarity.")
            elif flatness < 0.4:
                analysis.append("Moderate spectral flatness - good balance between vocal intelligibility and background textures.")
            else:
                analysis.append("High spectral flatness may compromise vocal clarity due to noise or diffuse tonal content.")
        
        # Analyze spectral centroid - different optimal ranges
        if is_instrumental:
            # Instrumental can vary more widely in centroid
            if centroid < sr/8:
                analysis.append("Low spectral centroid - instrumental mix may sound dark or lack brightness.")
            elif centroid < sr/4:
                analysis.append("Good spectral centroid range for balanced instrumental clarity.")
            elif centroid < sr/2:
                analysis.append("High spectral centroid - instrumental mix may sound bright or emphasized in the high end.")
            else:
                analysis.append("Very high spectral centroid - consider reducing excessive high frequency content in instruments.")
        else:
            # Vocals need more specific centroid ranges for clarity
            if centroid < sr/10:
                analysis.append("Low spectral centroid - vocals may sound dark or muffled.")
            elif centroid < sr/6:
                analysis.append("Moderate spectral centroid - adequate for vocal clarity but may benefit from more presence.")
            elif centroid < sr/3:
                analysis.append("Good spectral centroid range for vocal clarity and presence.")
            else:
                analysis.append("Very high spectral centroid - vocals may sound harsh or sibilant, consider reducing high frequency content.")
        
        if not analysis:
            if is_instrumental:
                analysis.append("Mix appears to have good clarity and definition across instrumental elements.")
            else:
                analysis.append("Mix appears to have good vocal clarity and definition against backing elements.")
                
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
        print("Generating 3D spatial visualization...")
        
        # Ensure stereo audio
        if y.ndim == 1:
            y = np.vstack((y, y))
        
        # Check if plotly is installed, if not, fall back to matplotlib
        try:
            import plotly.graph_objects as go
            import plotly.io as pio
            use_plotly = True
            print("Using Plotly for interactive 3D visualization")
        except ImportError:
            use_plotly = False
            print("Plotly not installed, falling back to static matplotlib visualization")
            
        # Sample points for visualization (use fewer points for better performance)
        num_points = min(1000, y.shape[1])
        step = max(1, y.shape[1] // num_points)
        
        # Get samples
        left_channel = y[0, ::step]
        right_channel = y[1, ::step]
        
        # Calculate frequency content for height
        D = np.abs(librosa.stft(np.mean(y, axis=0), n_fft=2048, hop_length=512))
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        
        # Get average frequency energy in high frequency range for height
        high_freq_mask = freqs > 5000
        height_profile = np.mean(D[high_freq_mask], axis=0)
        height_profile = height_profile[:len(left_channel)]  # Match length with channels
        
        # Normalize all dimensions to [-1, 1]
        left_channel = 2 * (left_channel - np.min(left_channel)) / (np.max(left_channel) - np.min(left_channel)) - 1
        right_channel = 2 * (right_channel - np.min(right_channel)) / (np.max(right_channel) - np.min(right_channel)) - 1
        height_profile = 2 * (height_profile - np.min(height_profile)) / (np.max(height_profile) - np.min(height_profile)) - 1
        
        # Calculate stereo width for color mapping
        stereo_width = np.abs(left_channel - right_channel)
        
        if use_plotly:
            # Create interactive Plotly figure
            fig = go.Figure(data=[go.Scatter3d(
                x=left_channel,
                y=right_channel,
                z=height_profile,
                mode='markers',
                marker=dict(
                    size=5,
                    color=stereo_width,
                    colorscale='Viridis',
                    opacity=0.7,
                    colorbar=dict(title='Stereo Width')
                ),
                hovertemplate='Left: %{x:.2f}<br>Right: %{y:.2f}<br>Frequency: %{z:.2f}<br>Width: %{marker.color:.2f}'
            )])
            
            # Customize layout
            fig.update_layout(
                title='3D Spatial Audio Visualization (Interactive)',
                scene=dict(
                    xaxis_title='Left Channel',
                    yaxis_title='Right Channel',
                    zaxis_title='Frequency Energy',
                    aspectmode='cube',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.2),
                        up=dict(x=0, y=0, z=1)
                    )
                ),
                width=900,
                height=700,
                margin=dict(l=0, r=0, b=0, t=40),
                template='plotly_white'
            )
            
            # Save as an HTML file
            spatial_path_html = os.path.join(vis_dir, 'spatial_field.html')
            pio.write_html(fig, file=spatial_path_html, auto_open=False, include_plotlyjs=True, config={"responsive": True})
            
            # Also generate a static image for fallback
            spatial_path = os.path.join(vis_dir, 'spatial_field.png')
            pio.write_image(fig, spatial_path, format='png', width=900, height=700)
            
            print(f"Successfully generated interactive 3D visualization at: {spatial_path_html}")
            print(f"Also generated static fallback at: {spatial_path}")
            
            # Return both paths in a dict
            return {
                'html': f"/static/uploads/{os.path.basename(vis_dir)}/spatial_field.html",
                'image': f"/static/uploads/{os.path.basename(vis_dir)}/spatial_field.png"
            }
            
        else:
            # Fall back to matplotlib for static visualization
            plt.figure(figsize=(12, 8))
            ax = plt.axes(projection='3d')
            
            # Create scatter plot
            scatter = ax.scatter(left_channel, right_channel, height_profile,
                               c=stereo_width,
                               cmap='viridis',
                               alpha=0.6,
                               s=20)
            
            # Add color bar
            plt.colorbar(scatter, label='Stereo Width')
            
            # Set labels and title
            ax.set_xlabel('Left Channel')
            ax.set_ylabel('Right Channel')
            ax.set_zlabel('Frequency Energy')
            plt.title('3D Spatial Audio Visualization')
            
            # Adjust the view angle for better visualization
            ax.view_init(elev=20, azim=45)
            
            # Add grid
            ax.grid(True)
            
            # Enhance the appearance
            ax.xaxis.pane.fill = False
            ax.yaxis.pane.fill = False
            ax.zaxis.pane.fill = False
            
            # Make the background transparent
            ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            
            # Save with high DPI and tight layout
            spatial_path = os.path.join(vis_dir, 'spatial_field.png')
            plt.savefig(spatial_path, dpi=150, bbox_inches='tight', transparent=True)
            plt.close()
            
            print(f"Successfully generated static 3D visualization at: {spatial_path}")
            return f"/static/uploads/{os.path.basename(vis_dir)}/spatial_field.png"
        
    except Exception as e:
        print(f"Error generating 3D spatial visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_visualizations(file_path, y=None, sr=None, file_id=None):
    """Generate visualizations for the audio file and return their paths."""
    import matplotlib.pyplot as plt
    import os
    
    # Dictionary to store visualization paths
    visualizations = {}
    
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
        try:
            plt.figure(figsize=(10, 4))
            # Use explicit color instead of relying on prop_cycler
            librosa.display.waveshow(y_mono, sr=sr, color='#1f77b4')
            plt.title('Waveform')
            plt.tight_layout()
            waveform_path = os.path.join(vis_dir, 'waveform.png')
            plt.savefig(waveform_path)
            plt.close()
            print(f"Generated waveform: /static/uploads/{file_id}/waveform.png")
            visualizations['waveform'] = f"/static/uploads/{file_id}/waveform.png"
        except Exception as e:
            print(f"Error generating waveform: {str(e)}")
            visualizations['waveform'] = "/static/img/error.png"
        
        # 2. Spectrogram
        try:
            plt.figure(figsize=(10, 4))
            D = librosa.amplitude_to_db(np.abs(librosa.stft(y_mono)), ref=np.max)
            librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            plt.tight_layout()
            spectrogram_path = os.path.join(vis_dir, 'spectrogram.png')
            plt.savefig(spectrogram_path)
            plt.close()
            print(f"Generated spectrogram: /static/uploads/{file_id}/spectrogram.png")
            visualizations['spectrogram'] = f"/static/uploads/{file_id}/spectrogram.png"
        except Exception as e:
            print(f"Error generating spectrogram: {str(e)}")
            visualizations['spectrogram'] = "/static/img/error.png"
        
        # 3. Frequency Spectrum
        try:
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
            print(f"Generated spectrum: /static/uploads/{file_id}/spectrum.png")
            visualizations['spectrum'] = f"/static/uploads/{file_id}/spectrum.png"
        except Exception as e:
            print(f"Error generating spectrum: {str(e)}")
            visualizations['spectrum'] = "/static/img/error.png"
        
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
            print(f"Generated chromagram: /static/uploads/{file_id}/chromagram.png")
            visualizations['chromagram'] = f"/static/uploads/{file_id}/chromagram.png"
        except Exception as e:
            print(f"Error generating chromagram: {str(e)}")
            
            # Create a placeholder image for chromagram
            try:
                plt.figure(figsize=(10, 4))
                plt.text(0.5, 0.5, f'Chromagram Error: {str(e)}', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes, fontsize=12)
                plt.axis('off')
                chroma_path = os.path.join(vis_dir, 'chromagram.png')
                plt.savefig(chroma_path)
                plt.close()
                print(f"Generated chromagram placeholder: /static/uploads/{file_id}/chromagram.png")
            except:
                print("Failed to generate chromagram placeholder")
            
            visualizations['chromagram'] = f"/static/uploads/{file_id}/chromagram.png"
        
        # 5. Stereo Field
        try:
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
            print(f"Generated stereo_field: /static/uploads/{file_id}/stereo_field.png")
            visualizations['stereo_field'] = f"/static/uploads/{file_id}/stereo_field.png"
        except Exception as e:
            print(f"Error generating stereo field: {str(e)}")
            visualizations['stereo_field'] = "/static/img/error.png"
        
        # 6. 3D Spatial Field - This is the problematic visualization
        # Make this the last visualization and wrap it in its own try/except
        try:
            print("Generating 3D spatial field visualization...")
            # Use an environment variable to control whether to generate this visualization
            skip_3d = os.environ.get('SKIP_3D_VISUALIZATION', 'false').lower() == 'true'
            
            if skip_3d:
                print("Skipping 3D visualization as configured")
                # Instead of raising an error, create the placeholder directly
                plt.figure(figsize=(10, 4))
                plt.text(0.5, 0.5, '3D Spatial Visualization Disabled', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes, fontsize=14)
                plt.axis('off')
                spatial_path = os.path.join(vis_dir, 'spatial_field.png')
                plt.savefig(spatial_path)
                plt.close()
                visualizations['spatial_field'] = f"/static/uploads/{file_id}/spatial_field.png"
                print(f"Generated spatial_field placeholder: /static/uploads/{file_id}/spatial_field.png")
            else:
                # Only attempt 3D visualization if not skipped
                # Use threading.Timer instead of signal for thread-safe timeout
                import threading
                import concurrent.futures
                
                # Function to generate visualization with timeout
                def generate_with_timeout(y, sr, vis_dir, timeout=30):
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(generate_3d_spatial_visualization, y, sr, vis_dir)
                        try:
                            result = future.result(timeout=timeout)
                            return result
                        except concurrent.futures.TimeoutError:
                            print("3D visualization timed out after 30 seconds")
                            raise TimeoutError("3D visualization timed out")
                
                try:
                    spatial_result = generate_with_timeout(y, sr, vis_dir)
                    
                    if spatial_result:
                        # Check if the result is a dictionary with both HTML and image paths
                        if isinstance(spatial_result, dict) and 'html' in spatial_result and 'image' in spatial_result:
                            print(f"Generated interactive spatial_field: {spatial_result['html']}")
                            print(f"Generated static spatial_field: {spatial_result['image']}")
                            visualizations['spatial_field'] = spatial_result['image']
                            visualizations['spatial_field_interactive'] = spatial_result['html']
                        # Otherwise, it's just a regular string path
                        else:
                            print(f"Generated spatial_field: {spatial_result}")
                            visualizations['spatial_field'] = spatial_result
                    else:
                        raise ValueError("Failed to generate 3D visualization")
                
                except TimeoutError:
                    print("3D visualization timed out")
                    raise
                
        except Exception as e:
            print(f"Error generating 3D spatial field: {str(e)}")
            
            # Create a simple placeholder image
            try:
                plt.figure(figsize=(10, 4))
                plt.text(0.5, 0.5, '3D Spatial Visualization Not Available', 
                        horizontalalignment='center', verticalalignment='center',
                        transform=plt.gca().transAxes, fontsize=14)
                plt.axis('off')
                spatial_path = os.path.join(vis_dir, 'spatial_field.png')
                plt.savefig(spatial_path)
                plt.close()
                visualizations['spatial_field'] = f"/static/uploads/{file_id}/spatial_field.png"
                print(f"Generated spatial_field placeholder: /static/uploads/{file_id}/spatial_field.png")
            except Exception as placeholder_error:
                print(f"Failed to generate placeholder for 3D visualization: {str(placeholder_error)}")
                visualizations['spatial_field'] = "/static/img/error.png"
        
        # Return all visualization paths
        start_time = time.time()
        visualizations_generated_in = time.time() - start_time
        print(f"Visualizations generated in {visualizations_generated_in:.2f} seconds")
        
        return visualizations
        
    except Exception as e:
        print(f"Error in visualizations: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return whatever we managed to generate, or placeholders
        if not visualizations:
            visualizations = {
                'waveform': "/static/img/error.png",
                'spectrogram': "/static/img/error.png",
                'spectrum': "/static/img/error.png",
                'chromagram': "/static/img/error.png",
                'stereo_field': "/static/img/error.png",
                'spatial_field': "/static/img/error.png"
            }
        
        return visualizations

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
    start_time = time.time()
    try:
        print(f"\n{'-'*30}")
        print("3D SPATIAL ANALYSIS:")
        
        # Ensure stereo audio
        if y.ndim == 1:
            print("Converting mono to stereo for 3D analysis...")
            y = np.vstack((y, y))
            print("Conversion complete")

        print(f"Audio shape: {y.shape}")
        print(f"Channel 1 max amplitude: {np.max(np.abs(y[0])):.4f}")
        print(f"Channel 2 max amplitude: {np.max(np.abs(y[1])):.4f}")
        
        # Calculate interaural level differences (ILD) for height perception
        print("Calculating interaural level differences (ILD) for height perception...")
        ild_start = time.time()
        ild = np.mean(np.abs(y[0] - y[1]))
        print(f"ILD: {ild:.6f} (calculated in {time.time() - ild_start:.4f}s)")
        
        height_score = min(100, max(0, ild * 100))
        print(f"Height score: {height_score:.2f}/100")

        # Calculate interaural time differences (ITD) for depth perception
        print("Calculating interaural time differences (ITD) for depth perception...")
        itd_start = time.time()
        correlation = np.corrcoef(y[0], y[1])[0, 1]
        print(f"Channel correlation: {correlation:.6f} (calculated in {time.time() - itd_start:.4f}s)")
        
        depth_score = min(100, max(0, (1 - abs(correlation)) * 100))
        print(f"Depth score: {depth_score:.2f}/100")

        # Calculate width consistency
        print("Calculating width consistency across frequency bands...")
        width_start = time.time()
        window_size = 2048
        hop_length = 512
        print(f"Window size: {window_size}, Hop length: {hop_length}")
        
        # Calculate correlation at different points in the audio
        correlations = []
        for i in range(0, len(y[0]) - window_size, hop_length):
            if i % (hop_length * 20) == 0:  # Print status every 20 windows
                print(f"  Processing window at {i/sr:.2f}s...")
            corr = np.corrcoef(y[0][i:i+window_size], y[1][i:i+window_size])[0, 1]
            correlations.append(corr)
        
        width_variation = np.std(correlations)
        print(f"Number of correlation windows: {len(correlations)}")
        print(f"Correlation range: {min(correlations):.4f} to {max(correlations):.4f}")
        print(f"Width variation (std dev): {width_variation:.6f}")
        print(f"Width consistency calculation completed in {time.time() - width_start:.4f}s")
        
        width_consistency = min(100, max(0, 100 - (width_variation * 1000)))
        print(f"Width consistency score: {width_consistency:.2f}/100")
        
        # Generate analysis text
        analysis = get_3d_spatial_analysis(height_score, depth_score, width_consistency)
        print("Generated analysis:")
        for item in analysis:
            print(f"  - {item}")
        
        total_time = time.time() - start_time
        print(f"3D spatial analysis completed in {total_time:.2f} seconds")
        print(f"{'-'*30}\n")

        return {
            "height_score": float(height_score),
            "depth_score": float(depth_score),
            "width_consistency": float(width_consistency),
            "analysis": analysis
        }
    except Exception as e:
        print(f"Error in 3D spatial analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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