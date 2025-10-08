"""
Simple test for Google AI API
"""
import os

# Set the API key
os.environ['GOOGLE_AI_API_KEY'] = 'AIzaSyAK2s3xUtZpRcuCCD8SbXqbp8OLNmbtz4c'

try:
    import google.generativeai as genai
    
    # Configure the API
    genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])
    
    print("✅ Google AI package imported successfully")
    print(f"✅ API Key configured: {os.environ['GOOGLE_AI_API_KEY'][:20]}...")
    
    # Test a simple query
    print("\nTesting simple query...")
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    response = model.generate_content(
        "What is 2+2? Answer with just the number.",
        generation_config={
            "temperature": 0.2,
            "top_p": 0.9,
            "max_output_tokens": 100,
        }
    )
    
    print(f"Response: {response.text}")
    print("\n✅ Google AI is working correctly!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
