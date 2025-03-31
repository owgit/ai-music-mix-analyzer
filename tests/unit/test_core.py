"""
Unit tests for core functionality
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the path
root_dir = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(root_dir))

# Import the modules to test
from app.core.utils import get_file_extension, is_valid_audio_file, generate_unique_filename


def test_get_file_extension():
    """Test the get_file_extension function"""
    assert get_file_extension('test.mp3') == 'mp3'
    assert get_file_extension('test.wav') == 'wav'
    assert get_file_extension('test.mp3.bak') == 'bak'
    assert get_file_extension('test') == ''
    assert get_file_extension('') == ''


def test_is_valid_audio_file():
    """Test the is_valid_audio_file function"""
    assert is_valid_audio_file('test.mp3') is True
    assert is_valid_audio_file('test.wav') is True
    assert is_valid_audio_file('test.flac') is True
    assert is_valid_audio_file('test.ogg') is True
    assert is_valid_audio_file('test.txt') is False
    assert is_valid_audio_file('test.jpg') is False
    assert is_valid_audio_file('test') is False


def test_generate_unique_filename():
    """Test the generate_unique_filename function"""
    # Test that the function generates a string
    result = generate_unique_filename('test.mp3')
    assert isinstance(result, str)
    
    # Test that the extension is preserved
    assert result.endswith('.mp3')
    
    # Test that different calls generate different filenames
    result2 = generate_unique_filename('test.mp3')
    assert result != result2 