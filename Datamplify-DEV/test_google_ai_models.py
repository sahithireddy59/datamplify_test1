"""
Check available Google AI models
"""
import os

# Set the API key
os.environ['GOOGLE_AI_API_KEY'] = 'AIzaSyAK2s3xUtZpRcuCCD8SbXqbp8OLNmbtz4c'

try:
    import google.generativeai as genai
    
    # Configure the API
    genai.configure(api_key=os.environ['GOOGLE_AI_API_KEY'])
    
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
    
except Exception as e:
    print(f"Error: {e}")
