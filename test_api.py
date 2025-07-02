"""
Test API Endpoints
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any


async def test_api_endpoints():
    """Test various API endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Movie Streaming API...")
        print("=" * 50)
        
        # Test health check
        print("\n1. Testing Health Check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                else:
                    print(f"❌ Health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test API info
        print("\n2. Testing API Info...")
        try:
            async with session.get(f"{base_url}/info") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API info: {data['name']} v{data['version']}")
                    print(f"   Demo accounts: {len(data['demo_accounts'])} available")
                else:
                    print(f"❌ API info failed: {response.status}")
        except Exception as e:
            print(f"❌ API info error: {e}")
        
        # Test movies endpoint
        print("\n3. Testing Movies Endpoint...")
        try:
            async with session.get(f"{base_url}/api/movies/?page=1&limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Movies endpoint: {data['pagination']['total']} movies found")
                    print(f"   Showing {len(data['data'])} movies")
                    for movie in data['data'][:3]:
                        print(f"   - {movie['title']}")
                else:
                    print(f"❌ Movies endpoint failed: {response.status}")
                    error_data = await response.text()
                    print(f"   Error: {error_data}")
        except Exception as e:
            print(f"❌ Movies endpoint error: {e}")
        
        # Test genres endpoint
        print("\n4. Testing Genres Endpoint...")
        try:
            async with session.get(f"{base_url}/api/genres/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Genres endpoint: {len(data['genres'])} genres found")
                    genre_names = [genre['name'] for genre in data['genres'][:5]]
                    print(f"   Sample genres: {', '.join(genre_names)}")
                else:
                    print(f"❌ Genres endpoint failed: {response.status}")
        except Exception as e:
            print(f"❌ Genres endpoint error: {e}")
        
        # Test authentication
        print("\n5. Testing Authentication...")
        try:
            # Test login
            login_data = {
                "email_or_username": "admin@example.com",
                "password": "admin123"
            }
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get('access_token')
                    print(f"✅ Login successful: {data['token_type']}")
                    
                    # Test protected endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(f"{base_url}/api/auth/me", headers=headers) as me_response:
                        if me_response.status == 200:
                            me_data = await me_response.json()
                            print(f"✅ Protected endpoint: {me_data['email']} ({me_data['username']})")
                        else:
                            print(f"❌ Protected endpoint failed: {me_response.status}")
                else:
                    print(f"❌ Login failed: {response.status}")
                    error_data = await response.text()
                    print(f"   Error: {error_data}")
        except Exception as e:
            print(f"❌ Authentication error: {e}")
        
        # Test movie search
        print("\n6. Testing Movie Search...")
        try:
            async with session.get(f"{base_url}/api/movies/search/?title=action&limit=3") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Search endpoint: {data['pagination']['total']} movies found for 'action'")
                    for movie in data['data'][:2]:
                        print(f"   - {movie['title']} (Rating: {movie['average_rating']})")
                else:
                    print(f"❌ Search endpoint failed: {response.status}")
                    error_data = await response.text()
                    print(f"   Error: {error_data}")
        except Exception as e:
            print(f"❌ Search endpoint error: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API Testing Completed!")
        print(f"📚 API Documentation: {base_url}/docs")
        print(f"🔄 Alternative docs: {base_url}/redoc")


if __name__ == "__main__":
    asyncio.run(test_api_endpoints()) 