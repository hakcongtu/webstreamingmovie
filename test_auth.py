#!/usr/bin/env python3
"""
Test script for authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    print("🔐 Testing Authentication Flow")
    print("=" * 50)
    
    # 1. Login
    print("1. Testing login...")
    login_data = {
        "email_or_username": "admin@movieapi.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Login successful!")
        print(f"Token: {token[:50]}...")
        print(f"Token type: {token_data['token_type']}")
        print(f"Expires in: {token_data['expires_in']} seconds")
        
        # 2. Test /me endpoint
        print("\n2. Testing /me endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"/me Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ /me successful!")
            print(f"User: {user_data['username']} ({user_data['email']})")
            print(f"Superuser: {user_data['is_superuser']}")
        else:
            print(f"❌ /me failed: {response.text}")
        
        # 3. Test /users endpoint
        print("\n3. Testing /users endpoint...")
        response = requests.get(f"{BASE_URL}/api/auth/users", headers=headers)
        print(f"/users Status: {response.status_code}")
        
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ /users successful!")
            print(f"Total users: {users_data['total']}")
            print(f"Active users: {users_data['active_count']}")
            print(f"Superusers: {users_data['superuser_count']}")
        else:
            print(f"❌ /users failed: {response.text}")
        
        # 4. Test debug token endpoint
        print("\n4. Testing debug token endpoint...")
        response = requests.get(f"{BASE_URL}/api/auth/debug-token", headers=headers)
        print(f"Debug token Status: {response.status_code}")
        
        if response.status_code == 200:
            debug_data = response.json()
            print(f"✅ Debug token successful!")
            print(f"Token valid: {debug_data['token_valid']}")
            print(f"User ID: {debug_data['user_id']}")
            print(f"Superuser: {debug_data['is_superuser']}")
        else:
            print(f"❌ Debug token failed: {response.text}")
            
    else:
        print(f"❌ Login failed: {response.text}")

if __name__ == "__main__":
    try:
        test_auth()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 