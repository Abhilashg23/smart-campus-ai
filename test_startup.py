#!/usr/bin/env python
"""
Simple test script to start Flask and capture any errors
"""
import sys
import traceback

try:
    print("=" * 60)
    print("Testing Flask App Startup")
    print("=" * 60)
    
    print("\n1. Importing app module...")
    from app import create_app
    print("✓ App module imported successfully")
    
    print("\n2. Creating app instance...")
    app = create_app('development')
    print("✓ App instance created successfully")
    
    print("\n3. Testing app context...")
    with app.app_context():
        from models import db
        print("✓ Database models accessible")
    
    print("\n4. Starting Flask server...")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)
    
except Exception as e:
    print("\n" + "=" * 60)
    print("ERROR OCCURRED:")
    print("=" * 60)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    print("-" * 60)
    traceback.print_exc()
    print("=" * 60)
    sys.exit(1)
