from openai import OpenAI
import os
import json
import httpx
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

def get_openai_api_key():
    """
    Get the OpenAI API key from environment variables.
    Returns None if the key is not set.
    
    Returns:
        str: The OpenAI API key or None
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.warning("OpenAI API key is not set in the environment")
        return None
    
    # Log the first few characters of the key to verify it's loaded (not the entire key)
    if api_key:
        logger.info(f"OpenAI API key loaded successfully (starts with: {api_key[:3]}...)")
        
    return api_key

def get_openrouter_api_key():
    """
    Get the OpenRouter API key from environment variables.
    Returns None if the key is not set.
    
    Returns:
        str: The OpenRouter API key or None
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        logger.warning("OpenRouter API key is not set in the environment")
        return None
    
    # Log the first few characters of the key to verify it's loaded (not the entire key)
    if api_key:
        logger.info(f"OpenRouter API key loaded successfully (starts with: {api_key[:3]}...)")
        
    return api_key

def strip_markdown(text):
    """
    Remove markdown formatting from text.
    
    Args:
        text: String that may contain markdown formatting
        
    Returns:
        String with markdown formatting removed
    """
    if not text:
        return text
        
    # Remove bold/italic formatting (with DOTALL to match across lines)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)  # Bold
    text = re.sub(r'\*(.+?)\*', r'\1', text, flags=re.DOTALL)      # Italic
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)      # Bold with underscore
    text = re.sub(r'_(.+?)_', r'\1', text, flags=re.DOTALL)        # Italic with underscore
    
    # Remove backticks (code formatting)
    text = re.sub(r'`(.+?)`', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'```(.+?)```', r'\1', text, flags=re.DOTALL)   # Code blocks
    
    # Remove other markdown elements if needed
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text, flags=re.DOTALL)  # Links
    
    return text

def analyze_with_gpt(analysis_results, is_instrumental=None):
    """
    Use AI models (OpenAI or OpenRouter) to provide additional insights on the mix analysis.
    If API keys are not available, returns a default response.
    
    Args:
        analysis_results: Dictionary containing the analysis results from our audio analyzer
        is_instrumental: Boolean indicating if the track is instrumental (None if unknown)
        
    Returns:
        Dictionary containing AI analysis and suggestions
    """
    try:
        # Get the AI provider from environment variable with fallback to OpenAI
        ai_provider = os.environ.get("AI_PROVIDER", "openai").lower()
        logger.info(f"Using AI provider: {ai_provider}")
        
        # Check if we should skip AI analysis
        skip_ai = os.environ.get("SKIP_AI_ANALYSIS", "false").lower() == "true"
        
        if skip_ai:
            logger.info("Skipping AI analysis as per configuration")
            return get_default_ai_response("AI analysis skipped as per configuration")
        
        # Create the prompt with separate system and user messages
        system_prompt, user_message = create_prompt(analysis_results, is_instrumental)
        
        # Call the appropriate API based on the provider
        if ai_provider == "openrouter":
            # Check if OpenRouter API key is available
            api_key = get_openrouter_api_key()
            if not api_key:
                logger.warning("OpenRouter API key not available, skipping AI analysis")
                return get_default_ai_response("OpenRouter API key not available")
            
            sections = analyze_with_openrouter(system_prompt, user_message)
        else:  # Default to OpenAI
            # Check if OpenAI API key is available
            api_key = get_openai_api_key()
            if not api_key:
                logger.warning("OpenAI API key not available, skipping AI analysis")
                return get_default_ai_response("OpenAI API key not available")
                
            sections = analyze_with_openai(system_prompt, user_message)
        
        return sections
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        return get_default_ai_response(f"Error: {str(e)}")

def analyze_with_openai(system_prompt, user_message):
    """
    Use OpenAI's models to analyze the mix data.
    
    Args:
        system_prompt: System prompt for the model
        user_message: User message containing the analysis data
        
    Returns:
        Dictionary containing the parsed sections of the model's response
    """
    try:
        # Get the API key using our secure function
        api_key = get_openai_api_key()
        
        # Get the model from environment variable with fallback to gpt-4o
        model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        logger.info(f"Using OpenAI model: {model}")
        
        # Create a custom HTTP client without proxies
        http_client = httpx.Client(
            timeout=60.0,
            follow_redirects=True
        )
        
        # Create OpenAI client
        client = OpenAI(api_key=api_key, http_client=http_client)
        
        # Call the OpenAI API
        logger.info("Sending request to OpenAI API")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        # Extract the response
        response_text = response.choices[0].message.content
        logger.info("Received response from OpenAI API")
        
        # Parse the response into sections
        return parse_response(response_text)
    
    except Exception as e:
        logger.error(f"Error using OpenAI: {str(e)}")
        raise

def analyze_with_openrouter(system_prompt, user_message):
    """
    Use OpenRouter's models to analyze the mix data.
    
    Args:
        system_prompt: System prompt for the model
        user_message: User message containing the analysis data
        
    Returns:
        Dictionary containing the parsed sections of the model's response
    """
    try:
        # Get the API key using our secure function
        api_key = get_openrouter_api_key()
        
        # Get the model from environment variable
        model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku-20240307")
        logger.info(f"Using OpenRouter model: {model}")
        
        # Site information for OpenRouter tracking
        site_url = os.environ.get("SITE_URL", "")
        site_title = os.environ.get("SITE_TITLE", "Mix Analyzer")
        
        # Create a custom HTTP client without proxies
        http_client = httpx.Client(
            timeout=60.0,
            follow_redirects=True
        )
        
        # Create OpenAI client with OpenRouter base URL
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            http_client=http_client
        )
        
        # Call the OpenRouter API via OpenAI compatible interface
        logger.info("Sending request to OpenRouter API")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2500,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_title
            }
        )
        
        # Extract the response
        response_text = response.choices[0].message.content
        logger.info("Received response from OpenRouter API")
        
        # Parse the response into sections
        return parse_response(response_text)
    
    except Exception as e:
        logger.error(f"Error using OpenRouter: {str(e)}")
        raise

def create_prompt(results, is_instrumental=None):
    """
    Create a prompt for GPT-4 based on the mix analysis results.
    
    Args:
        results: Dictionary containing the analysis results
        is_instrumental: Boolean indicating if the track is instrumental
        
    Returns:
        Tuple containing (system_prompt, user_message)
    """
    # Create the system prompt with detailed instructions
    system_prompt = """You are a professional audio engineer and mix analyst with extensive experience across multiple genres. Analyze the mix data provided and give detailed, actionable feedback.

Your analysis should be technical yet accessible, focusing on specific issues and concrete solutions rather than general observations. Include the following sections:

1. Summary: Provide a concise technical assessment of the overall mix quality.

2. Genre Context: Based on the frequency profile, dynamic characteristics, and stereo properties, identify the likely genre of this track and provide genre-specific mixing standards and expectations. Consider common frequency targets, dynamic range expectations, and spatial characteristics for this genre.

3. Subgenre & Style-Specific Context: Based on the audio characteristics, identify potential subgenres or specific production styles this track might fit into. Provide more detailed mixing standards and techniques specific to these subgenres or styles. Consider how production approaches differ within specialized subgenres.

4. Strengths: Identify 2-4 specific positive aspects of the mix.

5. Areas for Improvement: Identify 3-5 specific issues that could be addressed.

6. Suggestions: Provide 3-6 actionable, specific mixing suggestions with technical details (exact frequencies, amount of processing, etc.). These should be precise enough that the producer can immediately implement them.

7. Reference Tracks: Suggest 2-3 specific commercial tracks in the same genre that exemplify good solutions to the identified issues. For each reference, specify exactly what aspects to listen for.

8. Processing Recommendations: Suggest specific processing chains that would address the identified issues. Include specific parameter recommendations (e.g., "Apply a high-pass filter at 100Hz with 12dB/octave slope followed by gentle compression with 2:1 ratio and slow attack"). For each processing chain, explain the musical benefit.

9. Mix Translation Recommendations: Provide specific suggestions for how this mix might translate to different playback systems (headphones, car stereos, club systems, phone speakers, etc.) and what adjustments might improve the mix's translation across different listening environments.

IMPORTANT: DO NOT use any markdown formatting (no asterisks, no bold, no italic, no backticks). Format your response as plain text only. Do not use any HTML tags or other formatting."""

    # Format track type information for user message
    track_type_info = ""
    if is_instrumental is not None:
        track_type_info = f"This is an {'instrumental track' if is_instrumental else 'track with vocals'}."
    
    # Format numerical data for better readability
    frequency_data = "\n".join([
        f"- {band.replace('_', ' ').title()}: {energy:.1f}%" 
        for band, energy in results['frequency_balance']['band_energy'].items()
    ])
    
    # Create user message with analysis results
    user_message = f"""Please analyze the following mix data:

## Frequency Balance
Score: {results['frequency_balance']['balance_score']:.1f}/100
Energy Distribution:
{frequency_data}

Analysis Notes:
- {' '.join(results['frequency_balance']['analysis'])}

## Dynamic Range
Score: {results['dynamic_range']['dynamic_range_score']:.1f}/100
- Dynamic Range: {results['dynamic_range']['dynamic_range_db']:.1f} dB
- Crest Factor: {results['dynamic_range']['crest_factor_db']:.1f} dB
- PLR (Peak to Loudness Ratio): {results['dynamic_range']['plr']:.1f} dB

Analysis Notes:
- {' '.join(results['dynamic_range']['analysis'])}

## Stereo Field
Width Score: {results['stereo_field']['width_score']:.1f}/100
Phase Score: {results['stereo_field']['phase_score']:.1f}/100
- Channel Correlation: {results['stereo_field']['correlation']:.2f}
- Mid/Side Ratio: {results['stereo_field']['mid_ratio']*100:.0f}% / {results['stereo_field']['side_ratio']*100:.0f}%

Analysis Notes:
- {' '.join(results['stereo_field']['analysis'])}

## Clarity
Score: {results['clarity']['clarity_score']:.1f}/100
- Spectral Contrast: {results['clarity']['spectral_contrast']:.2f}
- Spectral Flatness: {results['clarity']['spectral_flatness']:.3f}
- Spectral Centroid: {results['clarity']['spectral_centroid']:.0f} Hz

Analysis Notes:
- {' '.join(results['clarity']['analysis'])}"""

    # Add transients data if available
    if 'transients' in results:
        user_message += f"""

## Transients
Score: {results['transients']['transients_score']:.1f}/100
- Attack Time: {results['transients']['attack_time']:.1f} ms
- Transient Density: {results['transients']['transient_density']:.2f} onsets/sec
- Percussion Energy: {results['transients']['percussion_energy']:.1f}%

Analysis Notes:
- {' '.join(results['transients']['analysis'])}"""

    # Add harmonic content if available
    if 'harmonic_content' in results and results['harmonic_content'].get('key') != 'Unknown':
        # Format key relationship information if available
        key_relationship_info = ""
        if "key_relationships" in results['harmonic_content'] and results['harmonic_content']["key_relationships"]:
            key_rel = results['harmonic_content']["key_relationships"]
            key_rel_type = key_rel.get("type", "unknown")
            
            # Format common progressions
            common_progressions = key_rel.get("common_progressions", [])
            progression_text = ""
            if common_progressions:
                progression_text = "Common Progressions:\n"
                for i, prog in enumerate(common_progressions[:3]):
                    progression_text += f"- {' → '.join(prog)}\n"
            
            # Format modulation options
            modulation_options = key_rel.get("modulation_options", {})
            modulation_text = ""
            if modulation_options:
                modulation_text = "Compatible Keys for Modulation:\n"
                for relation, key in modulation_options.items():
                    modulation_text += f"- {relation.replace('_', ' ').title()}: {key}\n"
                
            # Add key relationship info to harmonic content
            key_relationship_info = f"""
Key Type: {key_rel_type.title()}
{'Relative Minor' if key_rel_type == 'major' else 'Relative Major'}: {key_rel.get('relative_minor' if key_rel_type == 'major' else 'relative_major', 'Unknown')}
Neighboring Keys: {', '.join(key_rel.get('neighboring_keys', []))}
{progression_text}
{modulation_text}"""
        
        # Add top key candidates if available
        top_key_info = ""
        if "top_key_candidates" in results['harmonic_content'] and results['harmonic_content']["top_key_candidates"]:
            top_key_info = "Top Key Candidates:\n"
            for candidate in results['harmonic_content']["top_key_candidates"]:
                top_key_info += f"- {candidate['key']}: {candidate['confidence']:.2f}\n"

        user_message += f"""

## Harmonic Content
- Key: {results['harmonic_content']['key']}
{top_key_info}
- Harmonic Complexity: {results['harmonic_content']['harmonic_complexity']:.1f}%
- Key Consistency: {results['harmonic_content']['key_consistency']:.1f}%
- Chord Changes: {results['harmonic_content']['chord_changes_per_minute']:.1f}/min

Analysis Notes:
- {' '.join(results['harmonic_content']['analysis'])}
{key_relationship_info}"""

    # Add information about track type
    if track_type_info:
        user_message += f"\n\n{track_type_info}"

    return system_prompt, user_message

def parse_response(response):
    """
    Parse the response from GPT-4 into structured sections.
    
    Args:
        response: String containing GPT-4's response
        
    Returns:
        Dictionary containing the parsed sections
    """
    # Initialize result structure with default empty values
    result = {
        "summary": "",
        "genre_context": "",
        "subgenre_context": "",
        "strengths": [],
        "weaknesses": [],
        "suggestions": [],
        "reference_tracks": [],
        "processing_recommendations": [],
        "translation_recommendations": []
    }
    
    # Handle empty response case immediately
    if not response or response.strip() == "":
        logger.error("Empty response received from GPT-4")
        result["summary"] = "An error occurred while parsing the analysis. Please see the full text below."
        result["genre_context"] = "Error parsing genre context."
        result["subgenre_context"] = "Error parsing subgenre context."
        result["strengths"] = ["See full text"]
        result["weaknesses"] = ["See full text"]
        result["suggestions"] = ["See full text"]
        result["reference_tracks"] = ["See full text"]
        result["processing_recommendations"] = ["See full text"]
        result["translation_recommendations"] = ["See full text"]
        return result
    
    # Try to extract sections from response
    try:
        # Parse summary
        if "Summary:" in response or "SUMMARY:" in response or "Summary" in response:
            summary_start = max(
                response.find("Summary:") + 8 if response.find("Summary:") >= 0 else -100,
                response.find("SUMMARY:") + 8 if response.find("SUMMARY:") >= 0 else -100,
                response.find("Summary\n") + 8 if response.find("Summary\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Genre Context:"),
                    response.find("GENRE CONTEXT:"),
                    response.find("Genre Context"),
                    response.find("Strengths:"),
                    response.find("STRENGTHS:"),
                    response.find("Strengths")
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                result["summary"] = strip_markdown(response[summary_start:next_section].strip())
            else:
                # If no next section found, use the rest of the text
                result["summary"] = strip_markdown(response[summary_start:].strip())
        
        # Parse genre context
        if "Genre Context:" in response or "GENRE CONTEXT:" in response or "Genre Context" in response:
            context_start = max(
                response.find("Genre Context:") + 14 if response.find("Genre Context:") >= 0 else -100,
                response.find("GENRE CONTEXT:") + 14 if response.find("GENRE CONTEXT:") >= 0 else -100,
                response.find("Genre Context\n") + 14 if response.find("Genre Context\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Subgenre"),
                    response.find("SUBGENRE"),
                    response.find("Strengths:"),
                    response.find("STRENGTHS:"),
                    response.find("Strengths")
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                result["genre_context"] = strip_markdown(response[context_start:next_section].strip())
            else:
                # If no next section found, use the rest of the text
                result["genre_context"] = strip_markdown(response[context_start:].strip())
        
        # Parse subgenre context
        if "Subgenre" in response or "SUBGENRE" in response:
            markers = [
                ("Subgenre & Style-Specific Context:", "Subgenre & Style-Specific Context:"),
                ("SUBGENRE & STYLE-SPECIFIC CONTEXT:", "SUBGENRE & STYLE-SPECIFIC CONTEXT:"),
                ("Subgenre & Style Context:", "Subgenre & Style Context:"),
                ("Subgenre Context:", "Subgenre Context:"),
                ("Subgenre:", "Subgenre:")
            ]
            
            valid_positions = []
            for marker_text, _ in markers:
                pos = response.find(marker_text)
                if pos >= 0:
                    valid_positions.append(pos + len(marker_text))
            
            if valid_positions:
                subgenre_start = max(valid_positions)
                
                next_section_positions = [
                    pos for pos in [
                        response.find("Strengths:"),
                        response.find("STRENGTHS:"),
                        response.find("Strengths")
                    ]
                    if pos > 0
                ]
                
                if next_section_positions:
                    next_section = min(next_section_positions)
                    if subgenre_start < next_section:
                        result["subgenre_context"] = strip_markdown(response[subgenre_start:next_section].strip())
                else:
                    # If no next section found, use the rest of the text
                    result["subgenre_context"] = strip_markdown(response[subgenre_start:].strip())
        
        # Parse strengths
        if "Strengths:" in response or "STRENGTHS:" in response or "Strengths" in response:
            strengths_start = max(
                response.find("Strengths:") + 10 if response.find("Strengths:") >= 0 else -100,
                response.find("STRENGTHS:") + 10 if response.find("STRENGTHS:") >= 0 else -100,
                response.find("Strengths\n") + 10 if response.find("Strengths\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Areas for Improvement:"),
                    response.find("AREAS FOR IMPROVEMENT:"),
                    response.find("Areas for Improvement"),
                    response.find("Weaknesses:"),
                    response.find("WEAKNESSES:"),
                    response.find("Weaknesses"),
                    response.find("Suggestions:"),
                    response.find("SUGGESTIONS:"),
                    response.find("Suggestions")
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                strengths_text = response[strengths_start:next_section].strip()
                # Parse bullet points
                result["strengths"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in strengths_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
            else:
                # If no next section found, use the rest of the text
                strengths_text = response[strengths_start:].strip()
                result["strengths"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in strengths_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
        
        # Parse weaknesses
        weakness_markers = [
            ("Areas for Improvement:", 22),
            ("AREAS FOR IMPROVEMENT:", 22),
            ("Areas for Improvement", 22),
            ("Weaknesses:", 11),
            ("WEAKNESSES:", 11),
            ("Weaknesses", 11)
        ]
        
        for marker, offset in weakness_markers:
            if marker in response:
                weaknesses_start = response.find(marker) + offset
                
                next_section_positions = [
                    pos for pos in [
                        response.find("Suggestions:"),
                        response.find("SUGGESTIONS:"),
                        response.find("Suggestions"),
                        response.find("Reference Tracks:"),
                        response.find("REFERENCE TRACKS:"),
                        response.find("Reference Tracks")
                    ]
                    if pos > 0
                ]
                
                if next_section_positions:
                    next_section = min(next_section_positions)
                    weaknesses_text = response[weaknesses_start:next_section].strip()
                    # Parse bullet points
                    result["weaknesses"] = [
                        strip_markdown(point.strip().lstrip('-').strip())
                        for point in weaknesses_text.split('\n')
                        if point.strip() and not point.strip().startswith('#')
                    ]
                else:
                    # If no next section found, use the rest of the text
                    weaknesses_text = response[weaknesses_start:].strip()
                    result["weaknesses"] = [
                        strip_markdown(point.strip().lstrip('-').strip())
                        for point in weaknesses_text.split('\n')
                        if point.strip() and not point.strip().startswith('#')
                    ]
                break
        
        # Parse suggestions
        if "Suggestions:" in response or "SUGGESTIONS:" in response or "Suggestions" in response:
            suggestions_start = max(
                response.find("Suggestions:") + 12 if response.find("Suggestions:") >= 0 else -100,
                response.find("SUGGESTIONS:") + 12 if response.find("SUGGESTIONS:") >= 0 else -100,
                response.find("Suggestions\n") + 12 if response.find("Suggestions\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Reference Tracks:"),
                    response.find("REFERENCE TRACKS:"),
                    response.find("Reference Tracks"),
                    response.find("Processing Recommendations:"),
                    response.find("PROCESSING RECOMMENDATIONS:"),
                    response.find("Processing Recommendations")
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                suggestions_text = response[suggestions_start:next_section].strip()
                # Parse bullet points
                result["suggestions"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in suggestions_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
            else:
                # If no next section found, use the rest of the text
                suggestions_text = response[suggestions_start:].strip()
                result["suggestions"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in suggestions_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
        
        # Parse reference tracks
        if "Reference Tracks:" in response or "REFERENCE TRACKS:" in response or "Reference Tracks" in response:
            references_start = max(
                response.find("Reference Tracks:") + 17 if response.find("Reference Tracks:") >= 0 else -100,
                response.find("REFERENCE TRACKS:") + 17 if response.find("REFERENCE TRACKS:") >= 0 else -100,
                response.find("Reference Tracks\n") + 17 if response.find("Reference Tracks\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Processing Recommendations:"),
                    response.find("PROCESSING RECOMMENDATIONS:"),
                    response.find("Processing Recommendations"),
                    response.find("Mix Translation Recommendations:"),
                    response.find("MIX TRANSLATION RECOMMENDATIONS:"),
                    response.find("Mix Translation Recommendations")
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                references_text = response[references_start:next_section].strip()
                # Parse bullet points
                result["reference_tracks"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in references_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
            else:
                # If no next section found, use the rest of the text
                references_text = response[references_start:].strip()
                result["reference_tracks"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in references_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
        
        # Parse processing recommendations
        if "Processing Recommendations:" in response or "PROCESSING RECOMMENDATIONS:" in response or "Processing Recommendations" in response:
            processing_start = max(
                response.find("Processing Recommendations:") + 27 if response.find("Processing Recommendations:") >= 0 else -100,
                response.find("PROCESSING RECOMMENDATIONS:") + 27 if response.find("PROCESSING RECOMMENDATIONS:") >= 0 else -100,
                response.find("Processing Recommendations\n") + 27 if response.find("Processing Recommendations\n") >= 0 else -100
            )
            
            next_section_positions = [
                pos for pos in [
                    response.find("Mix Translation Recommendations:"),
                    response.find("MIX TRANSLATION RECOMMENDATIONS:"),
                    response.find("Mix Translation Recommendations"),
                    len(response)
                ]
                if pos > 0
            ]
            
            if next_section_positions:
                next_section = min(next_section_positions)
                processing_text = response[processing_start:next_section].strip()
                # Parse bullet points
                result["processing_recommendations"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in processing_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
            else:
                # If no next section found, use the rest of the text
                processing_text = response[processing_start:].strip()
                result["processing_recommendations"] = [
                    strip_markdown(point.strip().lstrip('-').strip())
                    for point in processing_text.split('\n')
                    if point.strip() and not point.strip().startswith('#')
                ]
        
        # Parse mix translation recommendations
        if "Mix Translation Recommendations:" in response or "MIX TRANSLATION RECOMMENDATIONS:" in response or "Mix Translation Recommendations" in response:
            translation_start = max(
                response.find("Mix Translation Recommendations:") + 30 if response.find("Mix Translation Recommendations:") >= 0 else -100,
                response.find("MIX TRANSLATION RECOMMENDATIONS:") + 30 if response.find("MIX TRANSLATION RECOMMENDATIONS:") >= 0 else -100,
                response.find("Mix Translation Recommendations\n") + 30 if response.find("Mix Translation Recommendations\n") >= 0 else -100
            )
            
            translation_text = response[translation_start:].strip()
            # Parse bullet points
            result["translation_recommendations"] = [
                strip_markdown(point.strip().lstrip('-').strip())
                for point in translation_text.split('\n')
                if point.strip() and not point.strip().startswith('#')
            ]
    
    except Exception as e:
        logger.error(f"Error parsing GPT-4 response: {str(e)}")
        # Fallback to a simpler parsing approach
        result["summary"] = "An error occurred while parsing the analysis. Please see the full text below."
        result["genre_context"] = "Error parsing genre context."
        result["subgenre_context"] = "Error parsing subgenre context."
        result["strengths"] = ["See full text"]
        result["weaknesses"] = ["See full text"]
        result["suggestions"] = ["See full text"]
        result["reference_tracks"] = ["See full text"]
        result["processing_recommendations"] = ["See full text"]
        result["translation_recommendations"] = ["See full text"]
    
    # Ensure all lists have at least one item
    for key in ["strengths", "weaknesses", "suggestions", "reference_tracks", "processing_recommendations", "translation_recommendations"]:
        if not result[key]:
            if key == "reference_tracks":
                result[key] = ["No specific reference tracks identified."]
            elif key == "processing_recommendations":
                result[key] = ["No specific processing recommendations provided."]
            elif key == "translation_recommendations":
                result[key] = ["No specific translation recommendations provided."]
            else:
                result[key] = ["No specific " + key + " identified."]
    
    return result 

def get_default_ai_response(reason):
    """
    Returns a default AI response when AI analysis cannot be performed
    
    Args:
        reason: The reason why AI analysis was skipped
        
    Returns:
        Dictionary with default values
    """
    return {
        "info": reason,
        "summary": "AI analysis was not performed. Your audio has been analyzed technically, but AI-powered insights are not available.",
        "strengths": ["Technical analysis complete without AI enhancement"],
        "weaknesses": ["N/A"],
        "suggestions": ["Consider setting up API keys for AI-powered insights"],
        "reference_tracks": ["N/A"],
        "processing_recommendations": ["See technical analysis for details"],
        "translation_recommendations": ["N/A"]
    } 