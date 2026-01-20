"""
Simple script to test Backend API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_cors():
    """Test CORS headers"""
    print("Testing CORS headers...")
    response = requests.options(
        f"{BASE_URL}/api/health",
        headers={"Origin": "http://localhost:5173"}
    )
    print(f"Status: {response.status_code}")
    print(f"CORS Headers:")
    for header in ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 'Access-Control-Allow-Headers']:
        print(f"  {header}: {response.headers.get(header, 'Not set')}")
    print()


def test_auth_missing_header():
    """Test authentication with missing header"""
    print("Testing authentication with missing header...")
    response = requests.get(f"{BASE_URL}/api/user/profile")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_swagger_ui():
    """Test Swagger UI availability"""
    print("Testing Swagger UI...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")
    print(f"Swagger UI available: {response.status_code == 200}")
    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("Backend API Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_root()
        test_cors()
        test_auth_missing_header()
        test_swagger_ui()
        
        print("=" * 60)
        print("✅ All basic tests completed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Open http://localhost:8000/docs to explore all endpoints")
        print("2. Test authentication with valid Telegram initData")
        print("3. Test file upload endpoints with actual images")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the API is running on http://localhost:8000")
        print("Run: python -m backend_api.main")


if __name__ == "__main__":
    main()
