"""
Weather Data Fetcher
Fetch weather data from OpenWeatherMap API for multiple cities
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherFetcher:
    """Fetch weather data from OpenWeatherMap API"""
    
    def __init__(self):
        """Initialize with API key from environment"""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = 'https://api.openweathermap.org/data/2.5/weather'
        
        if not self.api_key or self.api_key == 'get_your_free_key_from_openweathermap':
            raise ValueError("OpenWeatherMap API key not configured")
    
    def fetch_city_weather(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data for a single city
        
        Args:
            city: City name (e.g., 'Jakarta')
            
        Returns:
            Dictionary with weather data or None if failed
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            logger.info(f"Fetching weather for {city}...")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant fields
                weather_data = {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'latitude': data['coord']['lat'],
                    'longitude': data['coord']['lon'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'temp_min': data['main']['temp_min'],
                    'temp_max': data['main']['temp_max'],
                    'pressure': data['main']['pressure'],
                    'humidity': data['main']['humidity'],
                    'weather_main': data['weather'][0]['main'],
                    'weather_description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'wind_direction': data['wind'].get('deg'),
                    'cloudiness': data['clouds']['all'],
                    'timestamp': datetime.utcnow().isoformat(),
                    'data_source': 'openweathermap'
                }
                
                logger.info(f"✅ {city}: {weather_data['temperature']}°C, {weather_data['weather_description']}")
                return weather_data
                
            elif response.status_code == 401:
                logger.error(f"❌ API key unauthorized for {city}")
                return None
                
            elif response.status_code == 404:
                logger.error(f"❌ City not found: {city}")
                return None
                
            else:
                logger.error(f"❌ Error {response.status_code} for {city}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout fetching data for {city}")
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Connection error for {city}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Unexpected error for {city}: {str(e)}")
            return None
    
    def fetch_multiple_cities(self, cities: List[str]) -> List[Dict]:
        """
        Fetch weather data for multiple cities
        
        Args:
            cities: List of city names
            
        Returns:
            List of weather data dictionaries
        """
        logger.info(f"Fetching weather for {len(cities)} cities...")
        
        results = []
        for city in cities:
            data = self.fetch_city_weather(city)
            if data:
                results.append(data)
        
        logger.info(f"Successfully fetched {len(results)}/{len(cities)} cities")
        return results


# Default cities for Indonesia
INDONESIAN_CITIES = [
    'Jakarta',
    'Surabaya',
    'Bandung',
    'Medan',
    'Makassar'
]


def fetch_weather_data(cities: Optional[List[str]] = None) -> List[Dict]:
    """
    Main function to fetch weather data
    
    Args:
        cities: Optional list of cities (defaults to Indonesian cities)
        
    Returns:
        List of weather data dictionaries
    """
    if cities is None:
        cities = INDONESIAN_CITIES
    
    fetcher = WeatherFetcher()
    return fetcher.fetch_multiple_cities(cities)


if __name__ == "__main__":
    # Test the module
    print("Testing Weather Fetcher...")
    data = fetch_weather_data()
    print(f"\nFetched {len(data)} records:")
    for record in data:
        print(f"  - {record['city']}: {record['temperature']}°C")
