#!/usr/bin/env python3
"""
Test script for movies and genres endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_movies_endpoints():
    print("🎬 Testing Movies Endpoints")
    print("=" * 50)
    
    # 1. Test get all movies
    print("1. Testing GET /api/movies/...")
    response = requests.get(f"{BASE_URL}/api/movies/?page=1&limit=3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data['data'])} movies")
        print(f"Total movies: {data['pagination']['total']}")
        print(f"First movie: {data['data'][0]['title']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 2. Test get genres
    print("\n2. Testing GET /api/genres/...")
    response = requests.get(f"{BASE_URL}/api/genres/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'genres' in data:
            genres = data['genres']
            print(f"✅ Success! Found {len(genres)} genres")
            if len(genres) > 0:
                genre_names = [g['name'] for g in genres[:5]]
                print(f"First few genres: {genre_names}")
        else:
            print(f"✅ Success! Found {len(data)} genres")
            if len(data) > 0:
                print(f"First few genres: {data[:5] if len(data) >= 5 else data}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 3. Test search movies
    print("\n3. Testing search movies...")
    response = requests.get(f"{BASE_URL}/api/movies/search/?title=toy&page=1&limit=3")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {len(data['data'])} movies matching 'toy'")
    else:
        print(f"❌ Failed: {response.text}")
    
    # 4. Test get movie by ID
    print("\n4. Testing GET /api/movies/1...")
    response = requests.get(f"{BASE_URL}/api/movies/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'title' in data:
            print(f"✅ Success! Movie: {data['title']}")
        else:
            print(f"✅ Success! Movie data: {list(data.keys())}")
    else:
        print(f"❌ Failed: {response.text}")

if __name__ == "__main__":
    try:
        test_movies_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 