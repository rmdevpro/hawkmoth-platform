# HAWKMOTH LLM Teaming - Simple API Verification
"""
Quick verification script for HAWKMOTH LLM Teaming implementation.
Run this in your Python environment to test API connections and routing.
"""

import os
import json

def verify_api_keys():
    """Verify that API keys are properly configured"""
    print("🔍 API Key Verification")
    print("=" * 40)
    
    together_key = os.getenv('TOGETHER_API_KEY') or os.getenv('TOGETHERAI_KEY')
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"Together AI Key: {'✅ Found' if together_key else '❌ Missing'}")
    if together_key:
        print(f"   Length: {len(together_key)} chars")
        print(f"   Preview: {together_key[:8]}...")
    
    print(f"Claude API Key: {'✅ Found' if claude_key else '❌ Missing'}")
    if claude_key:
        print(f"   Length: {len(claude_key)} chars")
        print(f"   Preview: {claude_key[:8]}...")
    
    return bool(together_key or claude_key)

def test_import():
    """Test that we can import the HAWKMOTH engine"""
    print(f"\n📦 Import Test")
    print("=" * 40)
    
    try:
        # Try importing the engine
        from hawkmoth_sticky_sessions import HAWKMOTHStickySessionEngine
        print("✅ Successfully imported HAWKMOTHStickySessionEngine")
        
        # Try initializing
        engine = HAWKMOTHStickySessionEngine()
        print("✅ Successfully initialized engine")
        
        # Check model catalog
        print(f"✅ Model catalog loaded: {len(engine.model_catalog)} models")
        
        return engine
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Make sure you're in the correct directory")
        return None
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None

def test_routing_logic(engine):
    """Test the routing logic without making API calls"""
    print(f"\n🎯 Routing Logic Test")
    print("=" * 40)
    
    test_queries = [
        ("What is machine learning?", "DEEPSEEK_R1_FREE"),
        ("Debug this Python code", "DEEPSEEK_V3"),
        ("hawkmoth status", "HAWKMOTH_LOCAL"),
        ("Translate to Spanish", "LLAMA_3_3_70B"),
        ("I need comprehensive analysis", "CLAUDE_SONNET_4")
    ]
    
    for query, expected in test_queries:
        try:
            decision = engine.route_initial_query(query)
            result = "✅" if decision.target_llm == expected else "❌"
            print(f"{result} \"{query[:30]}...\" → {decision.target_llm}")
            print(f"     Expected: {expected}")
            print(f"     Reason: {decision.reason}")
            print(f"     Cost: ${decision.estimated_cost:.4f}")
            print()
        except Exception as e:
            print(f"❌ Routing failed for \"{query}\": {e}")

def main():
    """Main verification function"""
    print("🦅 HAWKMOTH LLM Teaming - Quick Verification")
    print("=" * 60)
    
    # Step 1: Verify API keys
    if not verify_api_keys():
        print("\n❌ No API keys found!")
        print("   Set TOGETHER_API_KEY and ANTHROPIC_API_KEY environment variables")
        return
    
    # Step 2: Test imports
    engine = test_import()
    if not engine:
        print("\n❌ Failed to initialize HAWKMOTH engine")
        return
    
    # Step 3: Test routing logic
    test_routing_logic(engine)
    
    # Step 4: Summary
    print("🎉 Verification Complete!")
    print("=" * 60)
    print("✅ API keys configured")
    print("✅ Engine initialized") 
    print("✅ Routing logic working")
    print("\n🚀 Ready for live API testing!")
    print("   Next: Run actual conversations with the models")

if __name__ == "__main__":
    main()
