# HAWKMOTH LLM Teaming - Live API Test
import sys
import os

# Add the working directory to Python path
sys.path.append(r'G:\Claud\HAWKMOTH-Project\working')

from hawkmoth_sticky_sessions import HAWKMOTHStickySessionEngine

def test_hawkmoth_llm_teaming():
    """Test HAWKMOTH LLM Teaming with real API calls"""
    
    print("🦅 HAWKMOTH LLM Teaming - Live API Test")
    print("=" * 60)
    
    # Initialize the engine
    engine = HAWKMOTHStickySessionEngine()
    
    # Test API connections
    print(f"\n🔍 API Connection Status:")
    print(f"   Together AI Key: {'✅ Present' if engine.together_api_key else '❌ Missing'}")
    print(f"   Claude API Key: {'✅ Present' if engine.claude_api_key else '❌ Missing'}")
    
    if not engine.together_api_key and not engine.claude_api_key:
        print("❌ No API keys found! Please set TOGETHER_API_KEY and ANTHROPIC_API_KEY")
        return
    
    # Test queries with different routing
    test_queries = [
        {
            "query": "What is machine learning?",
            "expected_route": "DEEPSEEK_R1_FREE",
            "description": "Simple question → Free tier"
        },
        {
            "query": "Debug this Python function that's causing memory leaks",
            "expected_route": "DEEPSEEK_V3", 
            "description": "Coding task → Development lane"
        },
        {
            "query": "hawkmoth status",
            "expected_route": "HAWKMOTH_LOCAL",
            "description": "Platform command → Local processing"
        },
        {
            "query": "Translate this to Spanish and explain cultural context",
            "expected_route": "LLAMA_3_3_70B",
            "description": "Multilingual task → Llama"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} Different Query Types")
    print("=" * 60)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n[Test {i}] {test['description']}")
        print(f"Query: \"{test['query']}\"")
        
        try:
            # Start new session for each test
            session = engine.start_conversation_session(test['query'])
            session_id = session.session_id
            
            print(f"🎯 Routed to: {session.primary_model}")
            print(f"✅ Expected: {test['expected_route']}")
            print(f"✨ Match: {'✅' if session.primary_model == test['expected_route'] else '❌'}")
            
            # Execute the query
            response, switched = engine.continue_conversation(session_id, test['query'])
            
            print(f"💰 Cost: ${response.actual_cost:.4f}")
            print(f"⚡ Response Time: {response.response_time:.2f}s")
            print(f"📝 Response Preview: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
            
            # Get session summary
            summary = engine.get_session_summary(session_id)
            print(f"🏷️  Model Lane: {summary['model_lane']}")
            
        except Exception as e:
            print(f"❌ Test Failed: {e}")
            print(f"   This might be an API key issue or network connectivity")
    
    # Test sticky session conversation
    print(f"\n🔄 Testing Sticky Session Conversation")
    print("=" * 60)
    
    try:
        # Start a coding session
        session = engine.start_conversation_session("Help me write a Python function")
        session_id = session.session_id
        
        conversation_flow = [
            "Help me write a Python function",
            "Now add error handling to it", 
            "Optimize it for performance",
            "I need comprehensive architecture review"  # Should trigger Claude switch
        ]
        
        for i, message in enumerate(conversation_flow, 1):
            print(f"\n[Turn {i}] User: {message}")
            response, switched = engine.continue_conversation(session_id, message)
            
            if switched:
                print(f"🔄 *** MODEL SWITCHED to {session.primary_model} ***")
            
            print(f"🤖 Model: {session.primary_model}")
            print(f"💰 Cost: ${response.actual_cost:.4f}")
            print(f"📝 Response: {response.content[:150]}{'...' if len(response.content) > 150 else ''}")
        
        # Final session summary
        final_summary = engine.get_session_summary(session_id)
        print(f"\n📊 Final Session Summary:")
        print(f"   Total Cost: ${final_summary['total_cost']:.4f}")
        print(f"   Total Messages: {final_summary['total_messages']}")
        print(f"   Final Model: {final_summary['primary_model']}")
        print(f"   Model Lane: {final_summary['model_lane']}")
        print(f"   Duration: {final_summary['duration_minutes']:.1f} minutes")
        
    except Exception as e:
        print(f"❌ Sticky Session Test Failed: {e}")
        print(f"   This might indicate API configuration issues")
    
    print(f"\n🎉 HAWKMOTH LLM Teaming Test Complete!")
    print(f"   Check the results above to verify routing and API functionality")

if __name__ == "__main__":
    test_hawkmoth_llm_teaming()
