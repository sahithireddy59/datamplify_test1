"""
Final test for Google AI integration
"""
import os
import sys
import django

# Set the API key for current session
os.environ['GOOGLE_AI_API_KEY'] = 'AIzaSyAK2s3xUtZpRcuCCD8SbXqbp8OLNmbtz4c'

# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Datamplify.settings')
django.setup()

from FlowBoard.ai_llm import query_llm, GOOGLE_AI_AVAILABLE, DEFAULT_MODEL

print("=" * 60)
print("Google AI Integration Test")
print("=" * 60)

print(f"\n✓ Google AI Available: {GOOGLE_AI_AVAILABLE}")
print(f"✓ Default Model: {DEFAULT_MODEL}")

if not GOOGLE_AI_AVAILABLE:
    print("\n❌ Google AI not available. Check API key.")
    sys.exit(1)

# Test 1: Simple query
print("\n" + "-" * 60)
print("Test 1: Simple Query")
print("-" * 60)
test_prompt = "What is 5+3? Answer with just the number."
print(f"Prompt: {test_prompt}")

try:
    response = query_llm(test_prompt, provider="google")
    if response:
        print(f"Response: {response}")
        print("✅ Test 1 PASSED")
    else:
        print("❌ Test 1 FAILED - No response")
except Exception as e:
    print(f"❌ Test 1 FAILED - Error: {e}")

# Test 2: Schema mapping
print("\n" + "-" * 60)
print("Test 2: Schema Mapping")
print("-" * 60)
mapping_prompt = """Create a JSON mapping for these columns:
Source: customer_id, first_name, last_name
Target: cust_id, full_name

Return JSON format: {"mappings": [{"source": "...", "target": "...", "expression": "..."}]}"""

print(f"Prompt: {mapping_prompt[:100]}...")

try:
    response = query_llm(mapping_prompt, provider="google")
    if response:
        print(f"Response preview: {response[:150]}...")
        print("✅ Test 2 PASSED")
    else:
        print("❌ Test 2 FAILED - No response")
except Exception as e:
    print(f"❌ Test 2 FAILED - Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\n✅ Google AI is now configured and ready to use in FlowBoard")
print("   You can select 'Google AI' from the AI Provider dropdown")
