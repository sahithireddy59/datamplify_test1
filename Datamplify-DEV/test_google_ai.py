"""
Test script to verify Google AI integration for FlowBoard
"""
import os
import sys
import django

# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from FlowBoard.ai_llm import query_llm, GOOGLE_AI_AVAILABLE

def test_google_ai():
    """Test Google AI integration"""
    print("=" * 60)
    print("Testing Google AI Integration")
    print("=" * 60)
    
    # Check if Google AI is available
    print(f"\n1. Google AI Available: {GOOGLE_AI_AVAILABLE}")
    
    if not GOOGLE_AI_AVAILABLE:
        print("\n❌ Google AI is not available. Please check:")
        print("   - GOOGLE_AI_API_KEY environment variable is set")
        print("   - google-generativeai package is installed")
        return
    
    # Test simple query
    print("\n2. Testing simple query...")
    test_prompt = "What is the capital of France? Answer in one word."
    
    try:
        response = query_llm(test_prompt, provider="google")
        print(f"   Prompt: {test_prompt}")
        print(f"   Response: {response}")
        
        if response:
            print("\n✅ Google AI is working correctly!")
        else:
            print("\n⚠️ Google AI returned None. Check API key and quota.")
            
    except Exception as e:
        print(f"\n❌ Error testing Google AI: {e}")
        import traceback
        traceback.print_exc()
    
    # Test schema mapping scenario
    print("\n3. Testing schema mapping scenario...")
    mapping_prompt = """
    Given source columns: customer_id, first_name, last_name, email
    And target columns: cust_id, full_name, contact_email
    
    Suggest mappings in JSON format:
    {"mappings": [{"source": "...", "target": "...", "expression": "..."}]}
    """
    
    try:
        response = query_llm(mapping_prompt, provider="google")
        print(f"   Response preview: {response[:200] if response else 'None'}...")
        
        if response:
            print("\n✅ Schema mapping test successful!")
        else:
            print("\n⚠️ Schema mapping returned None.")
            
    except Exception as e:
        print(f"\n❌ Error in schema mapping test: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_google_ai()
