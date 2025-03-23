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
    
    Args:
        obj: Any Python object that might contain NumPy types
        
    Returns:
        Object with NumPy types converted to standard Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
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
    
    try:
        # Calculate various metrics
        results = {
            "frequency_balance": analyze_frequency_balance(y, sr),
            "dynamic_range": analyze_dynamic_range(y),
            "stereo_field": analyze_stereo_field(y_left, y_right),
            "clarity": analyze_clarity(y, sr),
            "harmonic_content": analyze_harmonic_content(y, sr),
            "transients": analyze_transients(y_mono, sr)
        }
        
        # Generate visualizations with the same audio data
        try:
            results["visualizations"] = generate_visualizations(file_path, y=y, sr=sr)
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
            results["visualizations"] = generate_error_visualizations()
        
        # Calculate overall score
        results["overall_score"] = calculate_overall_score(results)
        
        # Convert NumPy types to standard Python types
        results = convert_numpy_types(results)
        
        return results
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        # Return a basic error response that can be handled by the frontend
        return {
            "error": True,
            "message": str(e),
            "visualizations": generate_error_visualizations()
        }

def analyze_frequency_balance(y, sr):
    """Analyze the frequency balance of the mix"""
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
            band_energy[band_name] = np.mean(D_db[:, indices])
        else:
            band_energy[band_name] = -80  # Default low value if no frequencies in range
    
    # Normalize values to 0-100 scale
    min_energy = min(band_energy.values())
    max_energy = max(band_energy.values())
    range_energy = max_energy - min_energy if max_energy > min_energy else 1
    
    normalized_energy = {band: ((energy - min_energy) / range_energy) * 100 
                         for band, energy in band_energy.items()}
    
    # Calculate balance score based on ideal curve and deviation
    # Ideal curve has slightly more energy in lows and less in highs
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
    avg_deviation = np.mean(deviations)
    
    # Convert to a 0-100 score (lower deviation is better)
    balance_score = max(0, 100 - avg_deviation)
    
    return {
        "band_energy": normalized_energy,
        "balance_score": balance_score,
        "analysis": get_frequency_balance_analysis(normalized_energy)
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
    # Convert to mono for clarity analysis
    y_mono = np.mean(y, axis=0) if y.ndim > 1 else y
    
    # Calculate spectral contrast with adjusted parameters
    # Reduce n_bands and set fmin to avoid Nyquist frequency issues
    contrast = librosa.feature.spectral_contrast(
        y=y_mono, 
        sr=sr,
        n_bands=4,  # Reduced from default 6
        fmin=20.0,  # Set minimum frequency
        n_fft=2048  # Increased window size
    )
    
    # Calculate spectral flatness
    flatness = np.mean(librosa.feature.spectral_flatness(y=y_mono))
    
    # Calculate spectral centroid
    centroid = np.mean(librosa.feature.spectral_centroid(y=y_mono, sr=sr))
    
    # Calculate clarity score (0-100)
    contrast_score = np.mean(np.abs(contrast)) * 10  # Scale up the contrast
    flatness_score = (1 - flatness) * 100  # Lower flatness is better for clarity
    
    # Combine scores with weights
    clarity_score = (contrast_score * 0.6 + flatness_score * 0.4)
    clarity_score = min(100, max(0, clarity_score))  # Ensure score is 0-100
    
    return {
        "clarity_score": clarity_score,
        "spectral_contrast": float(np.mean(np.abs(contrast))),
        "spectral_flatness": float(flatness),
        "spectral_centroid": float(centroid),
        "analysis": get_clarity_analysis(contrast, flatness, centroid, sr)
    }

def get_clarity_analysis(contrast, flatness, centroid, sr):
    """Generate textual analysis of clarity"""
    analysis = []
    
    if contrast < 1:
        analysis.append("Low spectral contrast may indicate a muddy mix with poor separation between elements.")
    elif contrast > 5:
        analysis.append("High spectral contrast indicates good separation between elements.")
    
    if flatness > 0.3:
        analysis.append("High spectral flatness may indicate noise or lack of tonal focus.")
    
    if centroid < sr/10:
        analysis.append("Low spectral centroid indicates a dark or muffled sound.")
    elif centroid > sr/4:
        analysis.append("High spectral centroid indicates a bright or harsh sound.")
    
    if not analysis:
        analysis.append("Mix appears to have good clarity and separation.")
    
    return analysis

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
        
        # Return paths
        static_prefix = '/static'
        return {
            "waveform": f"{static_prefix}/uploads/{file_id}/waveform.png",
            "spectrogram": f"{static_prefix}/uploads/{file_id}/spectrogram.png",
            "spectrum": f"{static_prefix}/uploads/{file_id}/spectrum.png",
            "chromagram": f"{static_prefix}/uploads/{file_id}/chromagram.png",
            "stereo_field": f"{static_prefix}/uploads/{file_id}/stereo_field.png"
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
    # Weight each component
    weights = {
        "frequency_balance": 0.25,
        "dynamic_range": 0.15,
        "stereo_field": 0.15,
        "clarity": 0.20,
        "harmonic_content": 0.15,
        "transients": 0.10
    }
    
    # Calculate weighted score
    score = (
        weights["frequency_balance"] * results["frequency_balance"]["balance_score"] +
        weights["dynamic_range"] * results["dynamic_range"]["dynamic_range_score"] +
        weights["stereo_field"] * (results["stereo_field"]["width_score"] + results["stereo_field"]["phase_score"]) / 2 +
        weights["clarity"] * results["clarity"]["clarity_score"] +
        weights["harmonic_content"] * results["harmonic_content"]["harmonic_complexity"]
    )
    
    # Add transients score if available
    if "transients" in results and "transients_score" in results["transients"]:
        score += weights["transients"] * results["transients"]["transients_score"]
    
    return round(score, 1)

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