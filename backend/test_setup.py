#!/usr/bin/env python3
"""
Test script to verify the Legal Assistant API setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if all required environment variables are set"""
    print("🔍 Testing Environment Variables...")
    
    required_vars = [
        'GOOGLE_API_KEY',
        'TAVILY_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n🚨 Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All environment variables are set")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain_google_genai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_google_genai: {e}")
        return False
    
    try:
        from langchain_community.tools import TavilySearchResults
        print("✅ TavilySearchResults imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TavilySearchResults: {e}")
        return False
    
    try:
        from langgraph.graph import StateGraph
        print("✅ LangGraph StateGraph imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LangGraph: {e}")
        return False
    
    return True

def test_langgraph_setup():
    """Test the LangGraph setup"""
    print("\n🔍 Testing LangGraph Setup...")
    
    try:
        from reflexion_graph import app as legal_agent_app
        print("✅ Legal agent app imported successfully")
        
        # Test the graph structure
        graph = legal_agent_app.get_graph()
        print(f"✅ Graph has {len(graph.nodes)} nodes")
        print(f"✅ Graph entry point: {graph.entry_point}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to test LangGraph setup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_invocation():
    """Test a simple invocation of the legal agent"""
    print("\n🔍 Testing Simple Invocation...")
    
    try:
        from reflexion_graph import app as legal_agent_app
        from langchain_core.messages import HumanMessage
        
        # Test with a simple message
        test_message = "What is the basic structure of a legal case?"
        
        print(f"Testing with message: {test_message}")
        
        # This might fail due to API limits or other issues, but we can see where it fails
        response = legal_agent_app.invoke({"messages": [HumanMessage(content=test_message)]})
        
        print("✅ LangGraph invocation successful!")
        print(f"Response type: {type(response)}")
        if isinstance(response, dict):
            print(f"Response keys: {list(response.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph invocation failed: {e}")
        print("This might be due to API limits, network issues, or configuration problems")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Legal Assistant API Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Module Imports", test_imports),
        ("LangGraph Setup", test_langgraph_setup),
        ("Simple Invocation", test_simple_invocation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your setup looks good.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Common issues:")
        print("1. Missing environment variables (GOOGLE_API_KEY, TAVILY_API_KEY)")
        print("2. Network connectivity issues")
        print("3. API rate limits or quotas")
        print("4. Missing dependencies")

if __name__ == "__main__":
    main()
