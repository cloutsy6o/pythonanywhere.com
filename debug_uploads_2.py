#!/usr/bin/env python3
"""
Debug upload routes - check registration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# First test upload_routes directly
print("Testing upload_routes.py import...")
try:
    from upload_routes import upload_bp
    print("✅ upload_bp imported successfully")
    print(f"  Name: {upload_bp.name}")
    print(f"  URL prefix: {upload_bp.url_prefix}")
    print(f"  Import name: {upload_bp.import_name}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("Testing with actual app...")

from app import app

# Check registered routes
print("\nRegistered routes containing 'upload':")
found = False
for rule in app.url_map.iter_rules():
    if 'upload' in rule.endpoint.lower() or 'upload' in rule.rule:
        print(f"  {rule.rule} -> {rule.endpoint}")
        found = True

if not found:
    print("  ❌ No upload routes found!")

    print("\nAll registered blueprints:")
    for name, blueprint in app.blueprints.items():
        print(f"  {name}: {blueprint.url_prefix}")
else:
    print("\n✅ Upload routes found!")

# Test URL generation
print("\nTesting URL generation:")
with app.test_request_context():
    try:
        from flask import url_for
        health_url = url_for('upload.upload_health')
        print(f"  Health endpoint: {health_url}")
    except Exception as e:
        print(f"  ❌ URL generation failed: {e}")

print("\n" + "="*50)
print("Quick fix options:")
print("1. Check if upload_bp is registered in app.py")
print("2. Try accessing: http://localhost:5000/uploads/health")
print("3. Restart Flask server if changes were made")
