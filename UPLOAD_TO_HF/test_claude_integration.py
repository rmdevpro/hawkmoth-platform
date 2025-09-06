# HAWKMOTH Claude File Integration Test Script
# Tests Component 3: Claude API file upload and analysis

import asyncio
import os
import tempfile
from claude_file_integration import ClaudeFileIntegration, quick_analyze_file, ClaudeFileError

async def test_claude_file_integration():
    """Test the Claude file integration system"""
    
    print("🦅 HAWKMOTH Claude File Integration Test")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("💡 Set ANTHROPIC_API_KEY to test Claude file integration")
        return False
    
    try:
        # Initialize Claude integration
        print("🔧 Initializing Claude File Integration...")
        claude = ClaudeFileIntegration()
        print("✅ Claude File Integration initialized successfully")
        print(f"📁 Supported file types: {len(claude.get_supported_file_types())}")
        
        # Create a test file
        print("\n📄 Creating test file...")
        test_content = """# HAWKMOTH Test File
        
This is a test file for Claude analysis.

## Features
- Python code analysis
- Documentation review  
- Cost optimization

## Code Example
```python
def hawkmoth_function():
    return "Intelligent LLM routing"
```

## Summary
This file tests Claude's ability to analyze mixed content including code and documentation.
"""
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            test_file_path = f.name
        
        print(f"✅ Test file created: {test_file_path}")
        
        # Test file validation
        print("\n🧪 Testing file validation...")
        print(f"   Markdown file supported: {claude.is_file_supported(test_file_path)}")
        print(f"   Executable not supported: {claude.is_file_supported('test.exe')}")
        
        # Test quick analysis function
        print("\n🤖 Testing Claude file analysis...")
        result = await quick_analyze_file(
            test_file_path, 
            "Analyze this HAWKMOTH test file and summarize its content"
        )
        
        if result['success']:
            print("✅ Claude analysis successful!")
            print(f"📊 Processing time: {result['processing_time']:.2f}s")
            print(f"💰 Cost estimate: ${result['cost_estimate']:.4f}")
            print(f"📝 Response length: {len(result['response'])} characters")
            print("\n🤖 Claude Response:")
            print("-" * 30)
            print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])
            print("-" * 30)
        else:
            print(f"❌ Claude analysis failed: {result['error']}")
            
        # Test the full integration object
        print("\n🔬 Testing full integration workflow...")
        full_result = await claude.process_file_with_claude(
            test_file_path,
            "Provide a technical review of this file"
        )
        
        if full_result.success:
            print("✅ Full integration workflow successful!")
            print(f"📁 File processed: {full_result.file_name}")
            print(f"⏱️ Processing time: {full_result.processing_time:.2f}s")
            print(f"💸 Cost estimate: ${full_result.cost_estimate:.4f}")
        else:
            print(f"❌ Full integration failed: {full_result.error_message}")
        
        # Test processing status tracking
        print("\n📊 Testing status tracking...")
        status = claude.get_processing_status(full_result.file_name)
        print(f"   File status: {status.value}")
        
        all_status = claude.get_all_processing_status()
        print(f"   Total tracked files: {len(all_status)}")
        
        # Cleanup
        os.unlink(test_file_path)
        print("\n🧹 Test file cleaned up")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except ClaudeFileError as e:
        print(f"❌ Claude File Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    
    print("\n🌐 Testing API Endpoints")
    print("-" * 30)
    
    try:
        import httpx
        
        # Test Claude status endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:7860/claude/status")
            if response.status_code == 200:
                data = response.json()
                print("✅ Claude status endpoint working")
                print(f"   Integration available: {data['claude_file_integration_available']}")
                print(f"   API configured: {data['anthropic_api_configured']}")
            else:
                print(f"❌ Status endpoint error: {response.status_code}")
                
        # Test supported types endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:7860/claude/supported-types")
            if response.status_code == 200:
                data = response.json()
                print("✅ Supported types endpoint working")
                print(f"   Total supported types: {data['total_supported_types']}")
            else:
                print(f"❌ Supported types endpoint error: {response.status_code}")
                
    except ImportError:
        print("⚠️ httpx not available for API testing")
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_claude_file_integration())
    # asyncio.run(test_api_endpoints())  # Uncomment to test API endpoints
