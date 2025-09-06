# HAWKMOTH Components 1 & 2 - Integration Test Suite
import sys
import os
import time
import json
import asyncio

# Add working directory to path
sys.path.append(os.path.dirname(__file__))

print("🦅 HAWKMOTH Components 1 & 2 - Integration Test Suite")
print("=" * 60)

def test_component_files():
    """Test that all component files are present"""
    print("\n📁 Component File Validation")
    print("-" * 30)
    
    # Component 1 files
    component1_files = [
        "persistent_storage_iter1.py",
        "storage_integration_iter1.py", 
        "storage_api_iter1.py"
    ]
    
    # Component 2 files
    component2_files = [
        "app_with_file_upload_iter1.py",
        "frontend_with_file_upload_final.html"
    ]
    
    all_present = True
    
    for file in component1_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ Component 1: {file} ({size:,} bytes)")
        else:
            print(f"❌ Component 1: {file} - MISSING")
            all_present = False
    
    for file in component2_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ Component 2: {file} ({size:,} bytes)")
        else:
            print(f"❌ Component 2: {file} - MISSING")
            all_present = False
    
    return all_present

def test_component_integration():
    """Test integration between components"""
    print("\n🔗 Component Integration Validation")
    print("-" * 30)
    
    try:
        # Test Component 1 imports
        from persistent_storage_iter1 import HAWKMOTHPersistentStorage
        from storage_integration_iter1 import HAWKMOTHStorageManager
        print("✅ Component 1: Storage imports successful")
        
        # Test storage initialization
        storage = HAWKMOTHPersistentStorage()
        print("✅ Component 1: Storage initialization successful")
        
        # Test storage manager
        manager = HAWKMOTHStorageManager()
        print("✅ Component 1: Storage manager initialization successful")
        
        # Clean up
        storage.cleanup()
        manager.cleanup()
        print("✅ Component 1: Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Component integration failed: {e}")
        return False

def test_app_features():
    """Test app file features"""
    print("\n🚀 Component 2: App Features Validation")
    print("-" * 30)
    
    try:
        with open("app_with_file_upload_iter1.py", "r") as f:
            app_content = f.read()
        
        features = [
            ("Storage import", "from storage_integration_iter1 import"),
            ("File upload endpoint", "/upload"),
            ("Multiple upload", "/upload-multiple"), 
            ("File download", "/download"),
            ("CORS middleware", "CORSMiddleware"),
            ("File management", "/files"),
            ("Storage commands", "_is_storage_command"),
            ("Enhanced status", "/enhanced-status"),
            ("Workspace management", "/workspaces")
        ]
        
        all_features_present = True
        for feature_name, feature_check in features:
            if feature_check in app_content:
                print(f"✅ {feature_name}")
            else:
                print(f"❌ {feature_name}")
                all_features_present = False
        
        return all_features_present
        
    except Exception as e:
        print(f"❌ App features test failed: {e}")
        return False

def test_frontend_features():
    """Test frontend features"""
    print("\n🎨 Component 2: Frontend Features Validation")
    print("-" * 30)
    
    try:
        with open("frontend_with_file_upload_final.html", "r") as f:
            frontend_content = f.read()
        
        features = [
            ("File upload UI", "upload-zone"),
            ("Drag and drop", "dragenter"),
            ("Progress indication", "progress-bar"),
            ("File browser", "file-list"),
            ("Tab interface", "tab-content"),
            ("File grid view", "file-grid"),
            ("Workspace selector", "workspaceSelect"),
            ("File management", "file-management"),
            ("System status", "system-status"),
            ("Modal dialogs", "modal")
        ]
        
        all_features_present = True
        for feature_name, feature_check in features:
            if feature_check in frontend_content:
                print(f"✅ {feature_name}")
            else:
                print(f"❌ {feature_name}")
                all_features_present = False
        
        return all_features_present
        
    except Exception as e:
        print(f"❌ Frontend features test failed: {e}")
        return False

def test_storage_functionality():
    """Test basic storage functionality"""
    print("\n💾 Storage Functionality Test")
    print("-" * 30)
    
    try:
        from storage_integration_iter1 import HAWKMOTHStorageManager
        
        # Initialize storage manager
        manager = HAWKMOTHStorageManager()
        print("✅ Storage manager initialized")
        
        # Create test workspace
        result = manager.create_project_workspace("test-integration", "Integration test workspace")
        if result['success']:
            print("✅ Test workspace created")
        else:
            print(f"❌ Workspace creation failed: {result['error']}")
            return False
        
        # Save test file
        result = manager.save_project_file("test.txt", "This is a test file for integration testing")
        if result['success']:
            print(f"✅ Test file saved to {result['storage_layer']} storage")
        else:
            print(f"❌ File save failed: {result['error']}")
            return False
        
        # Load test file
        result = manager.load_project_file("test.txt")
        if result['success']:
            print("✅ Test file loaded successfully")
        else:
            print(f"❌ File load failed: {result['error']}")
            return False
        
        # List files
        result = manager.list_project_files()
        if result['success'] and len(result['files']) > 0:
            print(f"✅ File listing successful ({len(result['files'])} files)")
        else:
            print("❌ File listing failed")
            return False
        
        # Clean up
        manager.cleanup()
        print("✅ Storage functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Storage functionality test failed: {e}")
        return False

def test_deployment_readiness():
    """Test deployment readiness"""
    print("\n🚀 Deployment Readiness Check")
    print("-" * 30)
    
    checks = [
        ("All component files present", test_component_files),
        ("Component integration working", test_component_integration),
        ("App features complete", test_app_features),
        ("Frontend features complete", test_frontend_features),
        ("Storage functionality working", test_storage_functionality)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {check_name}: Error - {e}")
    
    print(f"\n📊 Deployment Readiness: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 COMPONENTS 1 & 2 ARE FULLY INTEGRATED AND READY!")
        print("✅ Ready to begin Component 3: Claude File Integration")
        return True
    else:
        print("⚠️ Some integration issues need to be resolved")
        return False

def main():
    """Run comprehensive integration test"""
    print("Starting HAWKMOTH Components 1 & 2 integration test...")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_deployment_readiness()
    
    print("\n" + "=" * 60)
    if success:
        print("🦅 HAWKMOTH INTEGRATION TEST RESULT: ✅ PASSED")
        print("\n📋 Components Status:")
        print("✅ Component 1: Persistent Storage System - COMPLETE")
        print("✅ Component 2: File Upload Handling System - COMPLETE")
        print("🔄 Component 3: Claude File Integration - READY TO START")
        
        print("\n🚀 Next Steps:")
        print("1. Start the file upload system for testing")
        print("2. Test file upload workflow")
        print("3. Begin Component 3 implementation")
        print("4. Add Claude file integration capabilities")
        
    else:
        print("🦅 HAWKMOTH INTEGRATION TEST RESULT: ❌ FAILED")
        print("⚠️ Please resolve integration issues before proceeding")
    
    print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
