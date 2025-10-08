import requests
import json

# Test the backend AI mapping API directly
def test_backend_mapping():
    url = "http://localhost:8000/v1/flowboard/ai/mapping/suggest"
    
    # Sample data similar to what would come from the UI
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
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test-token"  # Use appropriate auth token
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Mappings: {json.dumps(result.get('mappings', []), indent=2)}")
            print(f"Unresolved: {json.dumps(result.get('unresolved', []), indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing backend API: {e}")

if __name__ == "__main__":
    test_backend_mapping()
