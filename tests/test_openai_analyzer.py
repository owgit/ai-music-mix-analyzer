import sys
import os

# Add the parent directory to the path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.openai_analyzer import parse_response

def test_parse_response_with_empty_sections():
    """Test parse_response with a response that has empty sections or missing markers"""
    # Test with an empty response
    result = parse_response("")
    print("Empty response result:", result)
    assert "summary" in result
    assert result["summary"] == "An error occurred while parsing the analysis. Please see the full text below."
    assert result["genre_context"] == "Error parsing genre context."
    assert result["subgenre_context"] == "Error parsing subgenre context."
    
    # Test with a response that has just a summary but no other sections
    result = parse_response("Summary: This is just a summary with no other sections.")
    print("Summary-only response result:", result["summary"])
    assert result["summary"] == "This is just a summary with no other sections."
    
    # Test with a response that has sections with unusual formatting
    unusual_response = """
    Summary: This is a test summary.
    
    Genre Context: This is genre context
    
    Strengths:
    - Strength 1
    """
    result = parse_response(unusual_response)
    print("Unusual response result:", result)
    assert "summary" in result
    assert "genre_context" in result
    assert "strengths" in result
    assert len(result["strengths"]) > 0

def test_parse_response_with_partial_data():
    """Test parse_response with partially formatted data"""
    partial_response = """
    Summary: This is a partial response.
    
    Strengths:
    - Good point 1
    - Good point 2
    
    Weaknesses:
    - Needs improvement
    """
    
    result = parse_response(partial_response)
    print("Partial response result:", result)
    assert result["summary"] == "This is a partial response."
    assert len(result["strengths"]) == 2
    assert len(result["weaknesses"]) == 1
    assert result["genre_context"] == ""  # Empty for optional missing sections
    assert result["subgenre_context"] == ""  # Empty for optional missing sections

if __name__ == "__main__":
    # Run tests directly
    test_parse_response_with_empty_sections()
    test_parse_response_with_partial_data()
    print("All tests passed!") 