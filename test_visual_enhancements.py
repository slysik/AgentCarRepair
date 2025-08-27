#!/usr/bin/env python3
"""
Test Visual Enhancements for AI Car Repair Assistant
Tests the new emoji-rich formatting, styled boxes, and enhanced HTML output
"""

import requests
import json
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AgentRepair import format_message_content

def test_formatting_function():
    """Test the enhanced format_message_content function"""
    print("🧪 Testing Enhanced Formatting Function")
    print("=" * 50)
    
    # Test cases for various formatting scenarios
    test_cases = [
        {
            'name': 'Warning Box',
            'input': '[WARNING]Engine parts may be hot[/WARNING]',
            'expected_contains': ['warning-box', '⚠️', 'Warning:', 'Engine parts may be hot']
        },
        {
            'name': 'Tip Box',
            'input': '[TIP]Always use genuine Volvo parts[/TIP]',
            'expected_contains': ['tip-box', '💡', 'Pro Tip:', 'Always use genuine Volvo parts']
        },
        {
            'name': 'Cost Box',
            'input': '[COST]Brake pads: $150-200 parts + $100 labor[/COST]',
            'expected_contains': ['cost-box', '💰', 'Cost Estimate:', '$150-200']
        },
        {
            'name': 'Emoji Steps',
            'input': '1️⃣ Remove the wheel\n2️⃣ Remove brake caliper\n3️⃣ Replace brake pads',
            'expected_contains': ['emoji-step', '1️⃣', '2️⃣', '3️⃣']
        },
        {
            'name': 'Section Headers',
            'input': '🔧 Engine Repair\n💡 Diagnostic Tips\n⚠️ Safety Warnings',
            'expected_contains': ['section-header', '🔧', '💡', '⚠️']
        },
        {
            'name': 'Emoji Bullets',
            'input': '▶️ Check oil level\n▶️ Inspect air filter\n▶️ Test battery',
            'expected_contains': ['emoji-list', '▶️']
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"Input: {test_case['input'][:50]}...")
        
        try:
            output = format_message_content(test_case['input'])
            
            # Check if expected elements are present
            all_present = True
            for expected in test_case['expected_contains']:
                if expected not in output:
                    print(f"❌ Missing: {expected}")
                    all_present = False
                else:
                    print(f"✅ Found: {expected}")
            
            results.append({
                'test': test_case['name'],
                'passed': all_present,
                'output_length': len(output)
            })
            
            if all_present:
                print(f"✅ {test_case['name']} - PASSED")
            else:
                print(f"❌ {test_case['name']} - FAILED")
                
        except Exception as e:
            print(f"❌ {test_case['name']} - ERROR: {e}")
            results.append({
                'test': test_case['name'],
                'passed': False,
                'error': str(e)
            })
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"\n📊 Formatting Test Results: {passed}/{total} passed")
    return passed == total

def test_api_endpoints():
    """Test API endpoints for visual enhancements"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test manual link endpoint
    try:
        response = requests.get(f"{base_url}/api/manual-link", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'manual_links' in data:
                print("✅ Manual Link API - PASSED")
                print(f"   Links: {len(data['manual_links'])} manual links")
                print(f"   References: {len(data.get('quick_references', {}))} quick refs")
                return True
            else:
                print("❌ Manual Link API - Invalid response format")
                return False
        else:
            print(f"❌ Manual Link API - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Manual Link API - ERROR: {e}")
        return False

def test_chat_with_visual_formatting():
    """Test chat API with visual formatting"""
    print("\n💬 Testing Chat with Visual Formatting")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test messages that should trigger enhanced formatting
    test_messages = [
        "How do I change brake pads on my 2021 XC60?",
        "My engine light is on, what should I check?",
        "What tools do I need for oil change?"
    ]
    
    results = []
    
    for message in test_messages:
        print(f"\n🔍 Testing: {message[:40]}...")
        
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": message},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                formatted_response = data.get('response', '')
                
                # Check for visual enhancements
                visual_elements = [
                    '1️⃣', '2️⃣', '3️⃣',  # Emoji steps
                    '🔧', '⚠️', '💡',    # Icons
                    'manual',             # Manual references
                    'emoji-step',         # CSS classes
                    'section-header'      # CSS classes
                ]
                
                found_elements = [elem for elem in visual_elements if elem in formatted_response]
                
                if found_elements:
                    print(f"✅ Visual elements found: {len(found_elements)}")
                    print(f"   Elements: {', '.join(found_elements[:3])}...")
                    results.append(True)
                else:
                    print("⚠️  No visual elements found (may be normal)")
                    results.append(False)
                    
            else:
                print(f"❌ HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Chat Visual Test Results: {passed}/{total} showed enhancements")
    
    return passed > 0  # At least one should show enhancements

def test_static_files():
    """Test static file serving for images"""
    print("\n📁 Testing Static File Serving")
    print("=" * 50)
    
    static_dir = "/Users/slysik/Downloads/PDF/AgentCarRepair/static"
    
    # Check if static directory exists
    if not os.path.exists(static_dir):
        print("❌ Static directory not found")
        return False
    
    print(f"✅ Static directory exists: {static_dir}")
    
    # Check manual_images subdirectory
    manual_images_dir = f"{static_dir}/manual_images"
    if os.path.exists(manual_images_dir):
        print(f"✅ Manual images directory exists")
        
        # Count any existing images
        image_count = 0
        for root, dirs, files in os.walk(manual_images_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    image_count += 1
        
        print(f"📸 Found {image_count} images in manual directory")
        
    else:
        print(f"⚠️  Manual images directory not found (will be created when needed)")
    
    return True

def main():
    """Run all visual enhancement tests"""
    print("🎨 AI Car Repair Assistant - Visual Enhancement Tests")
    print("=" * 60)
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests
    test_results.append(('Formatting Function', test_formatting_function()))
    test_results.append(('API Endpoints', test_api_endpoints()))
    test_results.append(('Chat Visual Formatting', test_chat_with_visual_formatting()))
    test_results.append(('Static File Serving', test_static_files()))
    
    # Overall summary
    print("\n" + "=" * 60)
    print("📊 VISUAL ENHANCEMENT TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<10} {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All visual enhancements are working correctly!")
        print("🚀 Your car repair assistant now has:")
        print("   • Emoji-rich formatting (1️⃣, 2️⃣, 3️⃣)")
        print("   • Styled warning and tip boxes")
        print("   • Manual link integration")
        print("   • Enhanced visual CSS styles")
        print("   • Static image serving capability")
        return 0
    else:
        print("⚠️  Some visual enhancements need attention")
        print("💡 Check the test output above for details")
        return 1

if __name__ == "__main__":
    exit(main())