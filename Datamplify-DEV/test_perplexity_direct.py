import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from FlowBoard.views import MappingSuggest
from django.test import RequestFactory
import json

def test_perplexity_mapping():
    """Test Perplexity AI mapping directly without authentication"""
    
    # Create a mock request
    factory = RequestFactory()
    
    # Sample data for testing
    payload = {
        "source": [
            {"name": "id", "type": "int"},
            {"name": "name", "type": "varchar"},
            {"name": "email", "type": "varchar"},
            {"name": "created_date", "type": "datetime"}
        ],
        "target": [
            {"name": "sample_id", "type": "int"},
            {"name": "sample_name", "type": "varchar"},
            {"name": "sample_email", "type": "varchar"},
            {"name": "created_timestamp", "type": "timestamp"}
        ],
        "instruction": "Map id to sample_id, name to sample_name, email to sample_email, and created_date to created_timestamp",
        "ai_provider": "perplexity"
    }
    
    # Create POST request
    request = factory.post('/v1/flowboard/ai/mapping/suggest', 
                          data=json.dumps(payload),
                          content_type='application/json')
    
    # Create view instance and call directly
    view = MappingSuggest()
    
    try:
        response = view.post(request)
        print(f"Status Code: {response.status_code}")
        
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8')
            print(f"Response Content: {content}")
            
            if response.status_code == 200:
                result = json.loads(content)
                print(f"Mappings: {json.dumps(result.get('mappings', []), indent=2)}")
                print(f"Unresolved: {json.dumps(result.get('unresolved', []), indent=2)}")
        else:
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error testing Perplexity mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_perplexity_mapping()
