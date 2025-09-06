# HAWKMOTH Persistent Storage - Test and Validation Script
import os
import sys
import time
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from persistent_storage_iter1 import HAWKMOTHPersistentStorage
from storage_integration_iter1 import HAWKMOTHStorageManager

def test_basic_storage():
    """Test basic storage operations"""
    print("🧪 Testing HAWKMOTH Persistent Storage System...")
    
    # Initialize storage
    storage = HAWKMOTHPersistentStorage()
    print("✅ Storage system initialized")
    
    # Test workspace creation
    result = storage.create_workspace("test-project", "Test project for validation")
    assert result["success"], f"Workspace creation failed: {result.get('error')}"
    workspace_id = result["workspace_id"]
    print(f"✅ Workspace created: {workspace_id}")
    
    # Test file saving with different storage layers
    test_files = [
        ("README.md", "# Test Project\n\nThis is a test", "git"),
        ("main.py", "print('Hello HAWKMOTH!')", "git"),
        ("config.json", '{"test": true}', "dataset"),
        ("temp.txt", "Temporary file content", "local")
    ]
    
    for file_path, content, layer in test_files:
        result = storage.save_file(workspace_id, file_path, content, layer)
        assert result["success"], f"File save failed for {file_path}: {result.get('error')}"
        print(f"✅ Saved {file_path} to {layer} storage")
    
    # Test file loading
    for file_path, expected_content, layer in test_files:
        result = storage.load_file(workspace_id, file_path)
        assert result["success"], f"File load failed for {file_path}: {result.get('error')}"
        assert result["content"] == expected_content, f"Content mismatch for {file_path}"
        print(f"✅ Loaded {file_path} from storage")
    
    # Test file listing
    result = storage.list_files(workspace_id)
    assert result["success"], f"File listing failed: {result.get('error')}"
    assert len(result["files"]) == len(test_files), "File count mismatch"
    print(f"✅ Listed {len(result['files'])} files")
    
    # Test storage stats
    stats = storage.get_storage_stats()
    print(f"✅ Storage stats: {json.dumps(stats, indent=2)}")
    
    # Cleanup
    storage.cleanup()
    print("✅ Storage cleanup completed")
    
    return True

def test_storage_manager():
    """Test storage manager integration"""
    print("\n🧪 Testing HAWKMOTH Storage Manager...")
    
    # Initialize storage manager
    manager = HAWKMOTHStorageManager()
    print("✅ Storage manager initialized")
    
    # Test project workspace creation
    result = manager.create_project_workspace("sample-project", "Sample project for testing")
    assert result["success"], f"Project creation failed: {result.get('error')}"
    print(f"✅ Project workspace created: {result['project_name']}")
    
    # Test current workspace info
    result = manager.get_current_workspace_info()
    assert result["success"], f"Workspace info failed: {result.get('error')}"
    print(f"✅ Current workspace: {result['project_name']} ({result['file_count']} files)")
    
    # Test file operations
    result = manager.save_project_file("test.py", "# Test Python file\nprint('Hello from HAWKMOTH')")
    assert result["success"], f"File save failed: {result.get('error')}"
    print("✅ File saved to project")
    
    result = manager.load_project_file("test.py")
    assert result["success"], f"File load failed: {result.get('error')}"
    print(f"✅ File loaded: {len(result['content'])} characters")
    
    result = manager.list_project_files()
    assert result["success"], f"File listing failed: {result.get('error')}"
    print(f"✅ Project files listed: {len(result['files'])} files")
    
    # Test HAWKMOTH status
    status = manager.get_hawkmoth_status()
    assert status["success"], f"Status failed: {status.get('error')}"
    print("✅ HAWKMOTH status retrieved")
    
    # Test workspace switching (create another workspace first)
    result = manager.create_project_workspace("another-project", "Another test project")
    assert result["success"], f"Second project creation failed: {result.get('error')}"
    
    result = manager.switch_workspace("sample-project")
    assert result["success"], f"Workspace switch failed: {result.get('error')}"
    print("✅ Workspace switching works")
    
    # Cleanup
    manager.cleanup()
    print("✅ Storage manager cleanup completed")
    
    return True

def test_storage_layer_selection():
    """Test automatic storage layer selection"""
    print("\n🧪 Testing Storage Layer Selection...")
    
    storage = HAWKMOTHPersistentStorage()
    
    # Test layer determination
    test_cases = [
        ("main.py", "print('hello')", "git"),
        ("config.json", '{"key": "value"}', "git"),
        ("README.md", "# Project", "git"),
        ("large_data.txt", "x" * 150000, "dataset"),  # Large file
        ("temp.log", "log entry", "local")
    ]
    
    for file_path, content, expected_layer in test_cases:
        determined_layer = storage._determine_storage_layer(file_path, content)
        print(f"✅ {file_path} -> {determined_layer} (expected: {expected_layer})")
    
    storage.cleanup()
    return True

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🧪 Testing Error Handling...")
    
    storage = HAWKMOTHPersistentStorage()
    
    # Test loading non-existent file
    result = storage.load_file("invalid-workspace", "nonexistent.txt")
    assert not result["success"], "Should fail for invalid workspace"
    print("✅ Properly handles invalid workspace")
    
    # Test saving to non-existent workspace
    result = storage.save_file("invalid-workspace", "test.txt", "content")
    assert not result["success"], "Should fail for invalid workspace"
    print("✅ Properly handles save to invalid workspace")
    
    # Test listing files in non-existent workspace
    result = storage.list_files("invalid-workspace")
    assert not result["success"], "Should fail for invalid workspace"
    print("✅ Properly handles list files for invalid workspace")
    
    storage.cleanup()
    return True

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🦅 HAWKMOTH Persistent Storage - Comprehensive Test Suite")
    print("=" * 60)
    
    test_results = []
    
    try:
        test_results.append(("Basic Storage", test_basic_storage()))
    except Exception as e:
        print(f"❌ Basic Storage Test Failed: {e}")
        test_results.append(("Basic Storage", False))
    
    try:
        test_results.append(("Storage Manager", test_storage_manager()))
    except Exception as e:
        print(f"❌ Storage Manager Test Failed: {e}")
        test_results.append(("Storage Manager", False))
    
    try:
        test_results.append(("Layer Selection", test_storage_layer_selection()))
    except Exception as e:
        print(f"❌ Layer Selection Test Failed: {e}")
        test_results.append(("Layer Selection", False))
    
    try:
        test_results.append(("Error Handling", test_error_handling()))
    except Exception as e:
        print(f"❌ Error Handling Test Failed: {e}")
        test_results.append(("Error Handling", False))
    
    # Print test summary
    print("\n" + "=" * 60)
    print("🦅 HAWKMOTH Storage Test Results:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! HAWKMOTH Persistent Storage is ready for integration.")
        return True
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
        return False

def demonstrate_usage():
    """Demonstrate typical usage patterns"""
    print("\n🦅 HAWKMOTH Storage Usage Demonstration")
    print("=" * 60)
    
    # Initialize storage manager
    manager = HAWKMOTHStorageManager()
    
    # Create a development project
    print("\n1. Creating a new development project...")
    result = manager.create_project_workspace("demo-app", "Demo application for HAWKMOTH")
    print(f"   Project created: {result['project_name']}")
    
    # Save some project files
    print("\n2. Creating project files...")
    
    # Main application file
    app_code = '''# Demo Application
from fastapi import FastAPI

app = FastAPI(title="Demo App")

@app.get("/")
async def root():
    return {"message": "Hello from HAWKMOTH!"}
'''
    manager.save_project_file("src/main.py", app_code)
    print("   ✅ src/main.py saved")
    
    # Configuration file
    config = {
        "app_name": "demo-app",
        "version": "1.0.0",
        "hawkmoth_enabled": True
    }
    manager.save_project_file("config/app.json", json.dumps(config, indent=2))
    print("   ✅ config/app.json saved")
    
    # Documentation
    docs = '''# Demo App Documentation

This is a demo application created with HAWKMOTH.

## Features
- FastAPI backend
- HAWKMOTH persistent storage
- Automated deployment

## Development
Developed using HAWKMOTH's persistent storage system.
'''
    manager.save_project_file("docs/README.md", docs)
    print("   ✅ docs/README.md saved")
    
    # List all files
    print("\n3. Project file structure:")
    result = manager.list_project_files()
    for file_info in result['files']:
        print(f"   📁 {file_info['path']} ({file_info['storage_layer']})")
    
    # Show workspace info
    print("\n4. Workspace information:")
    info = manager.get_current_workspace_info()
    print(f"   Project: {info['project_name']}")
    print(f"   Files: {info['file_count']}")
    print(f"   Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['created_at']))}")
    
    # Demonstrate loading a file
    print("\n5. Loading and modifying a file...")
    result = manager.load_project_file("src/main.py")
    print(f"   Loaded {len(result['content'])} characters from main.py")
    
    # Modify and save
    modified_code = result['content'] + '''
@app.get("/status")
async def status():
    return {"status": "running", "storage": "HAWKMOTH"}
'''
    manager.save_project_file("src/main.py", modified_code)
    print("   ✅ Updated main.py with new endpoint")
    
    # Show storage statistics
    print("\n6. Storage statistics:")
    status = manager.get_hawkmoth_status()
    stats = status['storage_statistics']
    print(f"   Total files: {stats['total_files']}")
    print(f"   Storage layers: {stats['storage_layers']}")
    print(f"   HF available: {stats['hf_available']}")
    
    # Cleanup
    manager.cleanup()
    print("\n✅ Demonstration completed!")

if __name__ == "__main__":
    # Run comprehensive tests
    success = run_comprehensive_test()
    
    if success:
        # If tests pass, run demonstration
        demonstrate_usage()
        
        print("\n🦅 HAWKMOTH Persistent Storage System Ready!")
        print("\nNext Steps:")
        print("1. Integrate storage system into main HAWKMOTH app")
        print("2. Add storage API endpoints")
        print("3. Create file browser UI")
        print("4. Test with HuggingFace deployment")
        print("5. Begin development workflow transition")
    else:
        print("\n⚠️ Tests failed. Please fix issues before proceeding.")
