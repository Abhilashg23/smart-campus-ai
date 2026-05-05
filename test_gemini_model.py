"""
Test script to verify Gemini API model compatibility
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Configure Gemini
genai.configure(api_key=api_key)

# Test different model names
models_to_test = [
    'gemini-pro',
    'models/gemini-pro',
    'gemini-1.5-flash',
    'models/gemini-1.5-flash',
    'gemini-1.5-pro',
    'models/gemini-1.5-pro'
]

print("\nTesting different Gemini model names...\n")

for model_name in models_to_test:
    try:
        print(f"Testing: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello'")
        print(f"  ✅ SUCCESS - Response: {response.text[:50]}")
        print(f"  👉 USE THIS MODEL: {model_name}\n")
        break
    except Exception as e:
        print(f"  ❌ FAILED - {str(e)[:100]}\n")
