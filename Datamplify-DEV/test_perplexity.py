#!/usr/bin/env python3

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from FlowBoard.ai_llm import query_perplexity_llm
import json

def test_perplexity():
    print("Testing Perplexity API...")
    
    # Check API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        print("ERROR: PERPLEXITY_API_KEY not set")
        return
    
    print(f"API Key: {api_key[:10]}...")
    
    # Simple test prompt
    prompt = """You are a data mapping expert. Create SQL mapping expressions for ETL data transformation.

SOURCE COLUMNS: ["id (int)", "name (varchar)", "created_date (timestamp)"]
TARGET COLUMNS: ["sample_id (int)", "sample_name (varchar)", "date_created (timestamp)"]
INSTRUCTION: i want to create a target from the source dim_samples one to one load

Generate mappings in this EXACT JSON format (no additional text):
{"mappings": [{"target": "target_column_name", "source": "source_column_name", "cast": "target_data_type"}], "unresolved": []}

Rules:
1. Map each target column to the best matching source column
2. Use exact column names from the lists above
3. For one-to-one mapping, map columns with similar names
4. Include data type casting when needed
5. Return valid JSON only"""

    try:
        response = query_perplexity_llm(prompt, 'pplx-7b-online')
        print(f"Raw Response: {response}")
        
        if response:
            # Try to parse as JSON
            try:
                parsed = json.loads(response.strip())
                print(f"Parsed JSON: {parsed}")
                print(f"Mappings count: {len(parsed.get('mappings', []))}")
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print("Trying to clean response...")
                
                # Clean response
                clean = response.strip()
                if clean.startswith('```json'):
                    clean = clean[7:]
                if clean.endswith('```'):
                    clean = clean[:-3]
                clean = clean.strip()
                
                try:
                    parsed = json.loads(clean)
                    print(f"Cleaned and Parsed: {parsed}")
                except:
                    print(f"Still can't parse: {clean}")
        else:
            print("No response from Perplexity")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_perplexity()
