import os
import requests
import json

# Test Perplexity API directly
api_key = os.getenv('PERPLEXITY_API_KEY')
print('API Key status:', 'SET' if api_key else 'NOT SET')

if api_key:
    url = 'https://api.perplexity.ai/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'sonar',
        'messages': [
            {
                'role': 'user',
                'content': 'Generate JSON mapping for columns id->sample_id, name->sample_name. Return only: {"mappings": [{"target": "sample_id", "source": "id", "cast": "int"}]}'
            }
        ],
        'temperature': 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print('Status Code:', response.status_code)
        print('Response:', response.text)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            print('AI Content:', content)
        else:
            print('Error response:', response.text)
            
    except Exception as e:
        print('Error:', str(e))
else:
    print('No API key found')
