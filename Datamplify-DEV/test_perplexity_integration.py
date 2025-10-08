import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from FlowBoard.ai_llm import query_perplexity_llm
from FlowBoard.views import MappingSuggest
import json

def test_perplexity_ai_integration():
    """Test Perplexity AI integration directly"""
    
    # Test 1: Direct Perplexity API call
    print("=== Testing Direct Perplexity API Call ===")
    
    prompt = """
    You are a data mapping expert. Generate precise column mappings based on the following:

    Source Schema:
    - id (int)
    - name (varchar)
    - email (varchar)
    - created_date (datetime)

    Target Schema:
    - sample_id (int)
    - sample_name (varchar)
    - sample_email (varchar)
    - created_timestamp (timestamp)

    Instruction: Map id to sample_id, name to sample_name, email to sample_email, and created_date to created_timestamp

    Return ONLY a JSON object in this exact format:
    {
        "mappings": [
            {"target": "sample_id", "source": "id", "cast": "int"},
            {"target": "sample_name", "source": "name", "cast": "varchar"},
            {"target": "sample_email", "source": "email", "cast": "varchar"},
            {"target": "created_timestamp", "source": "created_date", "cast": "timestamp"}
        ]
    }
    """
    
    try:
        response = query_perplexity_llm(prompt, model="sonar")
        print(f"Perplexity Response: {response}")
        
        if response:
            # Try to parse JSON from response
            import re
            
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response
            if "```json" in cleaned_response:
                cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                cleaned_response = re.sub(r'\s*```', '', cleaned_response)
            elif "```" in cleaned_response:
                cleaned_response = re.sub(r'```\s*', '', cleaned_response)
                cleaned_response = re.sub(r'\s*```', '', cleaned_response)
            
            # Try to find JSON object
            json_match = re.search(r'\{[\s\S]*\}', cleaned_response)
            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_json = json.loads(json_str)
                    print(f"Parsed JSON: {json.dumps(parsed_json, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Attempted to parse: {json_str}")
            else:
                print("No JSON object found in response")
        else:
            print("No response from Perplexity API")
            
    except Exception as e:
        print(f"Error testing Perplexity API: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Test the mapping logic from views.py
    print("\n=== Testing Mapping Logic ===")
    
    try:
        from FlowBoard.views import MappingSuggest
        
        # Create sample data
        source = [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "varchar"},
            {"name": "email", "type": "varchar"},
            {"name": "created_date", "type": "datetime"}
        ]
        
        target = [
            {"name": "sample_id", "type": "int"},
            {"name": "sample_name", "type": "varchar"},
            {"name": "sample_email", "type": "varchar"},
            {"name": "created_timestamp", "type": "timestamp"}
        ]
        
        instruction = "Map id to sample_id, name to sample_name, email to sample_email, and created_date to created_timestamp"
        ai_provider = "perplexity"
        
        # Create view instance
        view = MappingSuggest()
        
        # Test the AI mapping logic directly (bypass authentication)
        try:
            # Call the internal method that handles AI mapping
            result = view._generate_ai_mappings(source, target, instruction, ai_provider)
            print(f"AI Mapping Result: {json.dumps(result, indent=2)}")
        except AttributeError:
            print("_generate_ai_mappings method not found, testing inline logic...")
            
            # Test the logic inline
            from FlowBoard.ai_llm import query_llm
            
            # Build prompt
            prompt = f"""
You are a data mapping expert. Generate precise column mappings based on the following:

Source Schema:
{json.dumps(source, indent=2)}

Target Schema:
{json.dumps(target, indent=2)}

Instruction: {instruction}

Return ONLY a JSON object in this exact format:
{{
    "mappings": [
        {{"target": "<target_column>", "source": "<source_column>", "cast": "<data_type>"}}
    ]
}}
"""
            
            ai_response = query_llm(prompt, provider=ai_provider)
            print(f"AI Response: {ai_response}")
            
            if ai_response:
                # Parse the response
                import re
                
                cleaned_response = ai_response
                if "```json" in cleaned_response:
                    cleaned_response = re.sub(r'```json\s*', '', cleaned_response)
                    cleaned_response = re.sub(r'\s*```', '', cleaned_response)
                elif "```" in cleaned_response:
                    cleaned_response = re.sub(r'```\s*', '', cleaned_response)
                    cleaned_response = re.sub(r'\s*```', '', cleaned_response)
                
                json_match = re.search(r'\{[\s\S]*\}', cleaned_response)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        parsed_result = json.loads(json_str)
                        mappings = parsed_result.get('mappings', [])
                        print(f"Extracted Mappings: {json.dumps(mappings, indent=2)}")
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Attempted to parse: {json_str}")
            
    except Exception as e:
        print(f"Error testing mapping logic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_perplexity_ai_integration()
