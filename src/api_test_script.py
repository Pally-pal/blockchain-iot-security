# test_api.py
"""
Test script for IoT Blockchain Security API
Tests all API endpoints
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    
    print(f"\n[TEST] {description}")
    print(f"  Method: {method}")
    print(f"  URL: {url}")
    
    if data:
        print(f"  Request Data: {json.dumps(data, indent=2)}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n  Status Code: {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print(f"  Response: {json.dumps(response_data, indent=2)}")
            return response.status_code, response_data
        except:
            print(f"  Response: {response.text}")
            return response.status_code, response.text
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None, None

def run_all_tests():
    """Run all API tests"""
    
    print_section("IoT BLOCKCHAIN SECURITY API - TEST SUITE")
    
    # Test 1: Home endpoint
    test_endpoint("GET", "/", description="Home endpoint")
    
    # Test 2: Documentation
    test_endpoint("GET", "/api/docs", description="API documentation")
    
    # Test 3: Health check
    test_endpoint("GET", "/api/health", description="System health check")
    
    # Test 4: Get total records
    test_endpoint("GET", "/api/records", description="Get total records")
    
    # Test 5: Get statistics
    test_endpoint("GET", "/api/stats", description="Get system statistics")
    
    # Test 6: Generate hash
    hash_data = {
        "data": {
            "temperature": 25.5,
            "humidity": 60.2,
            "device": "TEST_001"
        }
    }
    test_endpoint("POST", "/api/hash", data=hash_data, description="Generate hash")
    
    # Test 7: Register data
    register_data = {
        "device_id": "API_TEST_DEVICE_001",
        "sensor_data": {
            "temperature": 25.5,
            "humidity": 60.2,
            "pressure": 1013.25,
            "timestamp": int(time.time())
        }
    }
    status, response = test_endpoint(
        "POST", 
        "/api/register", 
        data=register_data, 
        description="Register IoT data"
    )
    
    # Test 8: Verify data (same data)
    if response and response.get('success'):
        verify_data = {
            "sensor_data": register_data["sensor_data"]
        }
        test_endpoint(
            "POST", 
            "/api/verify", 
            data=verify_data, 
            description="Verify data integrity (original)"
        )
        
        # Test 9: Verify tampered data
        tampered_data = register_data["sensor_data"].copy()
        tampered_data["temperature"] = 35.5  # Changed value
        
        verify_tampered = {
            "sensor_data": tampered_data
        }
        test_endpoint(
            "POST", 
            "/api/verify", 
            data=verify_tampered, 
            description="Verify data integrity (tampered)"
        )
    
    # Test 10: Get audit report
    test_endpoint("GET", "/api/audit", description="Get audit report")
    
    print_section("ALL TESTS COMPLETED")

if __name__ == "__main__":
    print("\nStarting API tests...")
    print("Make sure the API server is running: python src/api_server.py\n")
    
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
