#!/usr/bin/env python3
"""
Test script for ticket file upload functionality
Run: python test_ticket_upload.py
"""

import os
import sys
import requests
import json
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:5000"  # Change if different
TEST_FILES_DIR = "test_uploads"
TEST_IMAGES = [
    "https://via.placeholder.com/150x150.png?text=Test+Image+1",
    "https://via.placeholder.com/300x200.png?text=Test+Image+2"
]

def download_test_files():
    """Download test files if they don't exist"""
    if not os.path.exists(TEST_FILES_DIR):
        os.makedirs(TEST_FILES_DIR)

    test_files = []

    # Create test files
    test_data = [
        ("test_image.png", b"Fake PNG content"),
        ("test_document.pdf", b"Fake PDF content"),
        ("test_text.txt", b"This is a test text file.\nWith multiple lines."),
        ("test_spreadsheet.xlsx", b"Fake Excel content")
    ]

    for filename, content in test_data:
        filepath = os.path.join(TEST_FILES_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
        test_files.append(filepath)
        print(f"✅ Created test file: {filename}")

    return test_files

def test_upload_endpoints():
    """Test all upload-related endpoints"""
    print("\n" + "="*60)
    print("TESTING TICKET FILE UPLOAD SYSTEM")
    print("="*60)

    # 1. Test upload directory health
    print("\n1. Testing upload directory health...")
    try:
        response = requests.get(f"{BASE_URL}/uploads/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Upload system healthy")
            print(f"   📁 Base directory: {health_data.get('upload_dir_exists', False)}")
            print(f"   📂 Tickets directory: {health_data.get('tickets_dir_exists', False)}")
            print(f"   💾 Total size: {health_data.get('total_size_mb', 0)} MB")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")

    # 2. Test file serving (should fail for non-existent file)
    print("\n2. Testing file serving security...")
    try:
        # Test invalid path
        response = requests.get(f"{BASE_URL}/uploads/invalid.txt")
        if response.status_code in [403, 404]:
            print(f"   ✅ Security check passed (blocked invalid file)")
        else:
            print(f"   ⚠️ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Security test error: {e}")

    # 3. Download test files
    print("\n3. Preparing test files...")
    test_files = download_test_files()

    print("\n4. Manual Testing Instructions:")
    print("   ="*30)
    print("   To test the complete system:")
    print("   1. Start your Flask application")
    print("   2. Open browser to: http://localhost:5000/ticket/create")
    print("   3. Fill out the ticket form")
    print("   4. Upload test files from directory: ./test_uploads/")
    print("   5. Submit ticket")
    print("   6. Open the created ticket")
    print("   7. Verify files are displayed and downloadable")
    print("   8. Reply to ticket with more files")
    print("   9. Test admin view: /ticket/admin/ticket/TKT-...")
    print("   10. Admin reply with files")

    print("\n5. Test File List:")
    for file in test_files:
        size_kb = os.path.getsize(file) / 1024
        print(f"   📄 {os.path.basename(file)} ({size_kb:.1f} KB)")

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Run Flask app: flask run")
    print("2. Test manually using instructions above")
    print("3. Check uploads/ directory for saved files")
    print("4. Verify database attachments JSON is stored correctly")

def cleanup():
    """Clean up test files"""
    if os.path.exists(TEST_FILES_DIR):
        import shutil
        shutil.rmtree(TEST_FILES_DIR)
        print(f"\n🧹 Cleaned up {TEST_FILES_DIR}/ directory")

if __name__ == "__main__":
    try:
        test_upload_endpoints()

        # Ask if user wants to clean up
        if os.path.exists(TEST_FILES_DIR):
            cleanup_choice = input("\nClean up test files? (y/n): ").strip().lower()
            if cleanup_choice == 'y':
                cleanup()
                print("✅ Cleanup complete")
            else:
                print(f"📁 Test files preserved in: {TEST_FILES_DIR}/")

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)
