"""
Test script to verify the outreach email generator components.
Run this before testing with the full Streamlit app.
"""

import os
from dotenv import load_dotenv
from utils.gemini_client import GeminiClient
from utils.prompt_builder import load_config, build_prompt, parse_email_response

def test_config_loading():
    """Test configuration file loading."""
    print("🔍 Testing config loading...")
    try:
        config = load_config()
        print("✅ Config loaded successfully")
        print(f"   Company: {config.get('company_name')}")
        print(f"   Capabilities: {len(config.get('key_capabilities', []))} items")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_prompt_building():
    """Test prompt builder."""
    print("\n🔍 Testing prompt builder...")
    try:
        config = load_config()
        prompt = build_prompt(
            person_name="Test User",
            linkedin_url="https://linkedin.com/in/testuser",
            company_name="Test Company",
            x_profile_url="https://x.com/testuser",
            config=config
        )
        print("✅ Prompt built successfully")
        print(f"   Prompt length: {len(prompt)} characters")
        return True
    except Exception as e:
        print(f"❌ Prompt building failed: {e}")
        return False

def test_email_parsing():
    """Test email response parsing."""
    print("\n🔍 Testing email parser...")
    try:
        sample_response = """
---EMAIL 1---
SUBJECT: Quick question about your ML annotation pipeline

Hi John,

I noticed your recent LinkedIn post about scaling your computer vision models. 
Labellerr can help reduce your annotation time by 80% with AI-powered auto-labeling.

Would love to share how we've helped similar companies.

Best,
Team

---EMAIL 2---
SUBJECT: Accelerating your data annotation workflow

Hi John,

Saw your discussion on X about model training challenges. Our platform handles 
multi-modal annotation with enterprise-grade security.

Let's chat about your specific needs.

Best,
Team

---EMAIL 3---
SUBJECT: Cost-effective solution for ML data prep

Hi John,

Following your work at Test Company. We've helped teams reduce annotation 
costs by 65% while maintaining quality.

Interested in a quick demo?

Best,
Team
"""
        emails = parse_email_response(sample_response)
        print("✅ Email parsing successful")
        print(f"   Parsed {len(emails)} emails")
        for i, email in enumerate(emails, 1):
            print(f"   Email {i}: Subject = '{email['subject'][:50]}...'")
        return len(emails) == 3
    except Exception as e:
        print(f"❌ Email parsing failed: {e}")
        return False

def test_gemini_client_init():
    """Test Gemini client initialization."""
    print("\n🔍 Testing Gemini client initialization...")
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            print("⚠️  GEMINI_API_KEY not found in .env file")
            print("   Create a .env file with your API key to test full integration")
            return False
        
        client = GeminiClient()
        print("✅ Gemini client initialized successfully")
        print(f"   Model: {client.model}")
        return True
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 OUTREACH EMAIL GENERATOR - COMPONENT TESTS")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Config Loading", test_config_loading()))
    results.append(("Prompt Building", test_prompt_building()))
    results.append(("Email Parsing", test_email_parsing()))
    results.append(("Gemini Client Init", test_gemini_client_init()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before running the app.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
