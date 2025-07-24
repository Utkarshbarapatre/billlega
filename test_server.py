#!/usr/bin/env python3
"""
Test script to verify server startup
"""
import os
import sys
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def test_server():
    """Test if the server is running"""
    port = int(os.getenv("PORT", 8000))
    base_url = f"http://localhost:{port}"
    
    print(f"🧪 Testing server at {base_url}")
    
    # Test endpoints
    endpoints = [
        "/health",
        "/api/status",
        "/"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Testing {url}...")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection failed (server not running?)")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
        
        print()

if __name__ == "__main__":
    test_server()
