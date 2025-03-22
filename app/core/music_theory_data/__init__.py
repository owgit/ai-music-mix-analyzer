"""
Music Theory Data Module

This package contains data structures and functions related to music theory
for use in audio analysis and music production contexts.
"""

from .key_relationships import (
    KEYS, 
    MAJOR_KEYS, 
    MINOR_KEYS, 
    ALL_KEYS,
    CIRCLE_OF_FIFTHS,
    RELATIVE_MINOR,
    RELATIVE_MAJOR,
    COMMON_PROGRESSIONS,
    KEY_SIGNATURES,
    get_key_relationship_info,
    get_parallel_key,
    get_neighboring_keys
)

__all__ = [
    'KEYS',
    'MAJOR_KEYS',
    'MINOR_KEYS',
    'ALL_KEYS',
    'CIRCLE_OF_FIFTHS',
    'RELATIVE_MINOR',
    'RELATIVE_MAJOR',
    'COMMON_PROGRESSIONS',
    'KEY_SIGNATURES',
    'get_key_relationship_info',
    'get_parallel_key',
    'get_neighboring_keys'
] 