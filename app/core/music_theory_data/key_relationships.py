"""
Music Theory Key Relationships

This module provides data structures for musical key relationships
including the circle of fifths, relative minor/major keys, and neighboring keys.
"""

# Basic key names
KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MAJOR_KEYS = KEYS.copy()
MINOR_KEYS = [k + 'm' for k in KEYS]
ALL_KEYS = MAJOR_KEYS + MINOR_KEYS

# Circle of fifths (clockwise from C)
CIRCLE_OF_FIFTHS = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']

# Relative minor for each major key
RELATIVE_MINOR = {
    'C': 'Am',
    'G': 'Em',
    'D': 'Bm',
    'A': 'F#m',
    'E': 'C#m',
    'B': 'G#m',
    'F#': 'D#m',
    'C#': 'A#m',
    'G#': 'Fm',  # Enharmonic with A♭/Fm
    'D#': 'Cm',  # Enharmonic with E♭/Cm
    'A#': 'Gm',  # Enharmonic with B♭/Gm
    'F': 'Dm'
}

# Relative major for each minor key (reverse of RELATIVE_MINOR)
RELATIVE_MAJOR = {v: k for k, v in RELATIVE_MINOR.items()}

# Parallel keys (same root, different mode)
def get_parallel_key(key):
    """Get the parallel key (major to minor or minor to major)"""
    if key.endswith('m'):
        return key[:-1]  # Remove 'm' to get parallel major
    else:
        return key + 'm'  # Add 'm' to get parallel minor

# Neighboring keys in the circle of fifths
def get_neighboring_keys(key):
    """
    Get the neighboring keys in the circle of fifths
    (one step clockwise and counterclockwise)
    """
    if key.endswith('m'):  # Minor key
        # For minor keys, use the relative major to navigate the circle
        relative_major = RELATIVE_MAJOR[key]
        major_idx = CIRCLE_OF_FIFTHS.index(relative_major)
        
        cw_major = CIRCLE_OF_FIFTHS[(major_idx + 1) % 12]
        ccw_major = CIRCLE_OF_FIFTHS[(major_idx - 1) % 12]
        
        return [RELATIVE_MINOR[ccw_major], RELATIVE_MINOR[cw_major]]
    else:  # Major key
        major_idx = CIRCLE_OF_FIFTHS.index(key)
        cw = CIRCLE_OF_FIFTHS[(major_idx + 1) % 12]
        ccw = CIRCLE_OF_FIFTHS[(major_idx - 1) % 12]
        return [ccw, cw]

# Common chord progressions by key
COMMON_PROGRESSIONS = {
    'major': [
        ['I', 'IV', 'V'],           # Most basic progression
        ['I', 'vi', 'IV', 'V'],     # 50s progression 
        ['I', 'V', 'vi', 'IV'],     # Popular modern progression
        ['ii', 'V', 'I'],           # Jazz progression
        ['I', 'IV', 'I', 'V']       # Blues turnaround
    ],
    'minor': [
        ['i', 'iv', 'V'],           # Minor with dominant V
        ['i', 'VI', 'VII'],         # Natural minor progression
        ['i', 'iv', 'v'],           # Natural minor progression
        ['i', 'VII', 'VI', 'V'],    # Descending progression
        ['i', 'v', 'VI', 'VII']     # Ascending progression  
    ]
}

# Key modulation relationships
MODULATION_MAP = {
    # Closely related keys for modulation from a major key
    'major_modulations': {
        'dominant': lambda key: CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(key) + 1) % 12],
        'subdominant': lambda key: CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(key) - 1) % 12],
        'relative_minor': lambda key: RELATIVE_MINOR[key],
        'parallel_minor': lambda key: key + 'm',
        'dominant_of_relative': lambda key: get_neighboring_keys(RELATIVE_MINOR[key])[1],
        'supertonic_minor': lambda key: get_neighboring_keys(key)[1] + 'm'
    },
    # Closely related keys for modulation from a minor key
    'minor_modulations': {
        'relative_major': lambda key: RELATIVE_MAJOR[key],
        'dominant_minor': lambda key: get_neighboring_keys(key)[1],
        'subdominant_minor': lambda key: get_neighboring_keys(key)[0],
        'parallel_major': lambda key: key[:-1],  # Remove 'm'
        'mediant_major': lambda key: CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(RELATIVE_MAJOR[key]) + 4) % 12]
    }
}

# Key signatures (number of sharps/flats)
KEY_SIGNATURES = {
    'C': 0,     # No sharps or flats
    'G': 1,     # 1 sharp
    'D': 2,     # 2 sharps
    'A': 3,     # 3 sharps
    'E': 4,     # 4 sharps
    'B': 5,     # 5 sharps
    'F#': 6,    # 6 sharps
    'C#': 7,    # 7 sharps
    'F': -1,    # 1 flat
    'A#': -1,   # Enharmonic with Bb (1 flat)
    'D#': -1,   # Enharmonic with Eb (3 flats)
    'G#': -1,   # Enharmonic with Ab (4 flats)
}

# Generate human-readable key relationship information
def get_key_relationship_info(key):
    """
    Get comprehensive information about a key's relationships
    
    Args:
        key: A string representing the musical key (e.g., 'C', 'Am')
        
    Returns:
        A dictionary containing key relationship information
    """
    is_minor = key.endswith('m')
    
    if is_minor:
        root = key[:-1]
        relative_major = RELATIVE_MAJOR.get(key, "Unknown")
        parallel_major = root
        
        # Get neighboring keys in the circle of fifths
        neighbors = get_neighboring_keys(key)
        
        return {
            "key": key,
            "type": "minor",
            "root_note": root,
            "relative_major": relative_major,
            "parallel_major": parallel_major,
            "neighboring_keys": neighbors,
            "common_progressions": COMMON_PROGRESSIONS['minor'],
            "modulation_options": {
                "relative_major": RELATIVE_MAJOR.get(key, "Unknown"),
                "dominant_minor": get_neighboring_keys(key)[1],
                "subdominant_minor": get_neighboring_keys(key)[0],
                "parallel_major": root,
            }
        }
    else:
        # Major key
        relative_minor = RELATIVE_MINOR.get(key, "Unknown")
        parallel_minor = key + 'm'
        
        # Get neighboring keys in the circle of fifths
        neighbors = get_neighboring_keys(key)
        
        return {
            "key": key,
            "type": "major",
            "root_note": key,
            "relative_minor": relative_minor,
            "parallel_minor": parallel_minor,
            "neighboring_keys": neighbors,
            "common_progressions": COMMON_PROGRESSIONS['major'],
            "modulation_options": {
                "dominant": CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(key) + 1) % 12],
                "subdominant": CIRCLE_OF_FIFTHS[(CIRCLE_OF_FIFTHS.index(key) - 1) % 12],
                "relative_minor": relative_minor,
                "parallel_minor": parallel_minor,
            }
        } 