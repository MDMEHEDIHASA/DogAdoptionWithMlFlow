#!/usr/bin/env python3
"""
Test script for the enhanced dog breed detection API with adoption centers and redirects
"""

import requests
import json
import webbrowser

# Test the enhanced API
def test_api():
    base_url = "http://localhost:5000"
    
    print("🐕 Testing Enhanced Dog Breed Detection API with Adoption Centers & Redirects")
    print("=" * 80)
    
    # Test 1: Get all adoption centers
    print("\n1. Testing GET /adoption-centers")
    try:
        response = requests.get(f"{base_url}/adoption-centers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['general_centers'])} general adoption centers")
            print(f"✅ Found breed-specific centers for: {', '.join(data['breed_specific_centers'])}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 2: Get adoption centers for a specific breed
    print("\n2. Testing GET /adoption-centers/german_shepherd")
    try:
        response = requests.get(f"{base_url}/adoption-centers/german_shepherd")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} adoption centers for {data['breed']}")
            for i, center in enumerate(data['adoption_centers'][:2], 1):
                print(f"   {i}. {center['name']} - {center['location']}")
                if 'direct_search_url' in center:
                    print(f"      🔗 Direct search: {center['direct_search_url']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 3: Get search URLs for a breed
    print("\n3. Testing GET /search-urls/german%20shepherd")
    try:
        response = requests.get(f"{base_url}/search-urls/german%20shepherd")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search URLs for {data['breed']}:")
            for platform, url in data['search_urls'].items():
                print(f"   {platform}: {url}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    # Test 4: Test redirect functionality
    print("\n4. Testing GET /redirect/german%20shepherd")
    try:
        response = requests.get(f"{base_url}/redirect/german%20shepherd", allow_redirects=False)
        if response.status_code == 302:
            print(f"✅ Redirect successful!")
            print(f"   Redirect URL: {response.headers.get('Location', 'N/A')}")
            print("   🎯 This would take user directly to Petfinder with German Shepherd pre-searched!")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    print("\n" + "=" * 80)
    print("📝 API Endpoints Available:")
    print("   POST /predict - Upload image to detect breed + get adoption centers + redirect URLs")
    print("   GET  /adoption-centers - Get all available adoption centers")
    print("   GET  /adoption-centers/<breed> - Get centers for specific breed")
    print("   GET  /search-urls/<breed> - Get all search URLs for a breed")
    print("   GET  /redirect/<breed> - Direct redirect to Petfinder with breed search")
    
    print("\n💡 Enhanced API Response for /predict:")
    example_response = {
        "breed": "German Shepherd",
        "confidence": 0.95,
        "adoption_centers": [
            {
                "name": "German Shepherd Rescue of Orange County",
                "website": "https://www.gsroc.org",
                "direct_search_url": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
                "phone": "1-714-974-7762",
                "location": "Orange County, CA",
                "description": "Specialized rescue for German Shepherds",
                "search_available": True
            }
        ],
        "direct_search_urls": {
            "petfinder": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
            "adoptapet": "https://www.adoptapet.com/s/adoptable-dogs?breed=German%20Shepherd",
            "aspca": "https://www.aspca.org/adopt-pet?animal=dog&breed=German%20Shepherd"
        },
        "redirect_info": {
            "petfinder_url": "https://www.petfinder.com/search/dogs-for-adoption/?breed=German%20Shepherd",
            "adoptapet_url": "https://www.adoptapet.com/s/adoptable-dogs?breed=German%20Shepherd",
            "aspca_url": "https://www.aspca.org/adopt-pet?animal=dog&breed=German%20Shepherd",
            "note": "Click any URL to search for this breed directly on the adoption website"
        },
        "message": "Found 5 adoption centers for German Shepherd dogs"
    }
    print(json.dumps(example_response, indent=2))
    
    print("\n🎯 How to Test Redirects:")
    print("   1. Open browser and go to: http://localhost:5000/redirect/german%20shepherd")
    print("   2. You'll be redirected to Petfinder with German Shepherd already searched!")
    print("   3. Try other breeds: /redirect/golden%20retriever, /redirect/labrador%20retriever")
    
    print("\n🌐 Demo HTML Page:")
    print("   Open redirect_demo.html in your browser for interactive testing")

if __name__ == "__main__":
    test_api()
