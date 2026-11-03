"""
OpenWeatherMap API Test Script
Purpose: Test API key activation and connection
"""

import os
import requests
import json
from datetime import datetime


def test_api():
    """Test OpenWeatherMap API with current key"""
    
    # Get API key from environment
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    print("=" * 60)
    print("🌦️  OpenWeatherMap API Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API key exists
    if not api_key or api_key == 'get_your_free_key_from_openweathermap':
        print("❌ ERROR: API key not set in .env file")
        print("Please update OPENWEATHER_API_KEY in .env")
        return False
    
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"API Key length: {len(api_key)} characters")
    print()
    
    # Test city
    city = 'Jakarta'
    
    # Build URL
    url = f'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    
    print(f"Testing city: {city}")
    print(f"Endpoint: {url}")
    print()
    print("Making API request...")
    
    try:
        # Make request
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        # Check response
        if response.status_code == 200:
            # Success!
            data = response.json()
            
            print("✅ SUCCESS! API key is working!")
            print("=" * 60)
            print(f"City: {data['name']}, {data['sys']['country']}")
            print(f"Coordinates: {data['coord']['lat']}, {data['coord']['lon']}")
            print(f"Temperature: {data['main']['temp']}°C")
            print(f"Feels Like: {data['main']['feels_like']}°C")
            print(f"Humidity: {data['main']['humidity']}%")
            print(f"Pressure: {data['main']['pressure']} hPa")
            print(f"Weather: {data['weather'][0]['main']} - {data['weather'][0]['description']}")
            print(f"Wind Speed: {data['wind']['speed']} m/s")
            print(f"Cloudiness: {data['clouds']['all']}%")
            print("=" * 60)
            
            return True
            
        elif response.status_code == 401:
            # Unauthorized - API key issue
            print("❌ ERROR 401: Unauthorized")
            print()
            print("Possible reasons:")
            print("1. API key not activated yet (wait 10-30 minutes after registration)")
            print("2. API key is invalid")
            print("3. API key not loaded in container (restart containers)")
            print()
            print("Solution:")
            print("- If just registered: Wait 30 minutes, then retry")
            print("- If updated .env: Run 'docker-compose restart'")
            
            return False
            
        elif response.status_code == 404:
            # City not found
            print(f"❌ ERROR 404: City '{city}' not found")
            return False
            
        else:
            # Other error
            print(f"❌ ERROR {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timeout")
        print("Check your internet connection")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Connection error")
        print("Check your internet connection")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)
