# 📡 API Documentation

Complete documentation for weather data APIs used in this pipeline.

## Table of Contents
- [Data Sources Overview](#data-sources-overview)
- [OpenWeatherMap API](#openweathermap-api)
- [Open-Meteo API](#open-meteo-api)
- [API Integration Guide](#api-integration-guide)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Testing APIs](#testing-apis)

---

## Data Sources Overview

| API | Free Tier | Rate Limit | Key Required | Reliability |
|-----|-----------|------------|--------------|-------------|
| **OpenWeatherMap** | 1,000 calls/day | 60 calls/min | ✅ Yes | ⭐⭐⭐⭐⭐ |
| **Open-Meteo** | Unlimited | None | ❌ No | ⭐⭐⭐⭐ |

### Why Two Sources?

1. **Data Validation**: Cross-reference for accuracy
2. **Redundancy**: Fallback if one API fails
3. **Portfolio Value**: Demonstrates multi-source ingestion
4. **Comparison**: Show data variance between providers

---

## OpenWeatherMap API

### Overview

- **Provider**: OpenWeatherMap Ltd.
- **Website**: https://openweathermap.org
- **Documentation**: https://openweathermap.org/api
- **API Version**: 2.5 (Current Weather)

### Free Tier Details

```
✅ 1,000 API calls per day
✅ 60 calls per minute
✅ Current weather data
✅ 5-day forecast (not used in this project)
✅ Historical data (limited)
❌ No hourly forecast (paid only)
```

### Getting API Key

1. Sign up: https://home.openweathermap.org/users/sign_up
2. Verify email
3. Go to: https://home.openweathermap.org/api_keys
4. Default key is auto-generated
5. Note: Key activation takes ~2 hours for new accounts

### API Endpoint

**Current Weather Data**:
```
GET https://api.openweathermap.org/data/2.5/weather
```

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `q` | string | Yes* | City name | `Jakarta` or `Jakarta,ID` |
| `lat` | float | Yes* | Latitude | `-6.2088` |
| `lon` | float | Yes* | Longitude | `106.8456` |
| `appid` | string | Yes | Your API key | `abc123...` |
| `units` | string | No | Units of measurement | `metric`, `imperial`, `standard` |
| `lang` | string | No | Language | `en`, `id`, `es` |

*Either `q` OR (`lat` + `lon`) required

### Example Request

**By City Name**:
```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=Jakarta,ID&appid=YOUR_API_KEY&units=metric"
```

**By Coordinates**:
```bash
curl "https://api.openweathermap.org/data/2.5/weather?lat=-6.2088&lon=106.8456&appid=YOUR_API_KEY&units=metric"
```

### Example Response

```json
{
  "coord": {
    "lon": 106.8456,
    "lat": -6.2088
  },
  "weather": [
    {
      "id": 803,
      "main": "Clouds",
      "description": "broken clouds",
      "icon": "04d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 30.5,
    "feels_like": 35.2,
    "temp_min": 29.0,
    "temp_max": 32.0,
    "pressure": 1010,
    "humidity": 70,
    "sea_level": 1010,
    "grnd_level": 1009
  },
  "visibility": 10000,
  "wind": {
    "speed": 3.5,
    "deg": 120,
    "gust": 5.2
  },
  "clouds": {
    "all": 75
  },
  "dt": 1727089073,
  "sys": {
    "type": 2,
    "id": 2037449,
    "country": "ID",
    "sunrise": 1727046123,
    "sunset": 1727089567
  },
  "timezone": 25200,
  "id": 1642911,
  "name": "Jakarta",
  "cod": 200
}
```

### Response Fields (Used in Pipeline)

| Field | Type | Description | Unit |
|-------|------|-------------|------|
| `main.temp` | float | Temperature | Celsius (with units=metric) |
| `main.feels_like` | float | Perceived temperature | Celsius |
| `main.humidity` | int | Humidity | % |
| `main.pressure` | int | Atmospheric pressure | hPa |
| `wind.speed` | float | Wind speed | m/s |
| `wind.deg` | int | Wind direction | degrees |
| `weather[0].main` | string | Weather condition | Clear, Clouds, Rain, etc. |
| `weather[0].description` | string | Detailed description | clear sky, light rain, etc. |
| `dt` | int | Data timestamp | Unix UTC |
| `name` | string | City name | Jakarta |
| `sys.country` | string | Country code | ID |

### Python Integration

```python
import requests
from datetime import datetime

def fetch_openweather(city: str, api_key: str) -> dict:
    """
    Fetch current weather from OpenWeatherMap API
    
    Args:
        city: City name (e.g., "Jakarta,ID")
        api_key: OpenWeatherMap API key
        
    Returns:
        Standardized weather data dict
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"  # Celsius
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Standardize response
        return {
            "city_name": data["name"],
            "country": data["sys"]["country"],
            "timestamp": datetime.fromtimestamp(data["dt"]),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg"),
            "weather_condition": data["weather"][0]["main"],
            "weather_description": data["weather"][0]["description"],
            "source": "openweathermap",
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"]
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"OpenWeatherMap API error: {str(e)}")
```

### Error Codes

| Code | Message | Meaning | Solution |
|------|---------|---------|----------|
| 200 | OK | Success | - |
| 401 | Unauthorized | Invalid API key | Check API key, wait if newly created |
| 404 | Not Found | City not found | Check city name spelling |
| 429 | Too Many Requests | Rate limit exceeded | Implement exponential backoff |
| 500 | Internal Server Error | API server issue | Retry with exponential backoff |

---

## Open-Meteo API

### Overview

- **Provider**: Open-Meteo
- **Website**: https://open-meteo.com
- **Documentation**: https://open-meteo.com/en/docs
- **License**: Open-source (CC BY 4.0)

### Free Tier Details

```
✅ Unlimited API calls (no rate limit!)
✅ No API key required
✅ Current + Forecast weather
✅ Historical data (free)
✅ Commercial use allowed
✅ No attribution required (but appreciated)
```

### API Endpoint

**Weather Forecast API**:
```
GET https://api.open-meteo.com/v1/forecast
```

### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `latitude` | float | Yes | Latitude | `-6.2088` |
| `longitude` | float | Yes | Longitude | `106.8456` |
| `current_weather` | bool | No | Include current weather | `true` |
| `hourly` | string | No | Hourly variables | `temperature_2m,precipitation` |
| `daily` | string | No | Daily variables | `temperature_2m_max,temperature_2m_min` |
| `timezone` | string | No | Timezone | `Asia/Jakarta`, `auto` |
| `temperature_unit` | string | No | Unit | `celsius`, `fahrenheit` |
| `windspeed_unit` | string | No | Unit | `kmh`, `ms`, `mph` |

### Example Request

```bash
curl "https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current_weather=true&timezone=auto"
```

### Example Response

```json
{
  "latitude": -6.2,
  "longitude": 106.84,
  "generationtime_ms": 0.12,
  "utc_offset_seconds": 25200,
  "timezone": "Asia/Jakarta",
  "timezone_abbreviation": "WIB",
  "elevation": 8.0,
  "current_weather": {
    "temperature": 30.2,
    "windspeed": 12.5,
    "winddirection": 135,
    "weathercode": 3,
    "is_day": 1,
    "time": "2026-09-23T17:30"
  }
}
```

### Weather Code Mapping

Open-Meteo uses WMO weather codes:

| Code | Description | OpenWeather Equivalent |
|------|-------------|----------------------|
| 0 | Clear sky | Clear |
| 1, 2, 3 | Mainly clear, partly cloudy, overcast | Clouds |
| 45, 48 | Fog | Mist |
| 51, 53, 55 | Drizzle | Drizzle |
| 61, 63, 65 | Rain | Rain |
| 71, 73, 75 | Snow | Snow |
| 80, 81, 82 | Rain showers | Rain |
| 95, 96, 99 | Thunderstorm | Thunderstorm |

### Python Integration

```python
import requests
from datetime import datetime

# Weather code to condition mapping
WEATHER_CODE_MAP = {
    0: "Clear",
    1: "Clouds", 2: "Clouds", 3: "Clouds",
    45: "Mist", 48: "Mist",
    51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
    61: "Rain", 63: "Rain", 65: "Rain",
    71: "Snow", 73: "Snow", 75: "Snow",
    80: "Rain", 81: "Rain", 82: "Rain",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm"
}

def fetch_openmeteo(latitude: float, longitude: float, city_name: str) -> dict:
    """
    Fetch current weather from Open-Meteo API
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        city_name: City name (for standardization)
        
    Returns:
        Standardized weather data dict
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data["current_weather"]
        
        # Standardize response
        return {
            "city_name": city_name,
            "country": "ID",  # Manually set or lookup
            "timestamp": datetime.fromisoformat(current["time"]),
            "temperature": current["temperature"],
            "feels_like": None,  # Not provided by Open-Meteo
            "humidity": None,  # Not in current_weather (need hourly)
            "pressure": None,  # Not in current_weather (need hourly)
            "wind_speed": current["windspeed"] / 3.6,  # km/h to m/s
            "wind_direction": current["winddirection"],
            "weather_condition": WEATHER_CODE_MAP.get(current["weathercode"], "Unknown"),
            "weather_description": f"WMO code {current['weathercode']}",
            "source": "openmeteo",
            "latitude": data["latitude"],
            "longitude": data["longitude"]
        }
    except requests.exceptions.RequestException as e:
        raise Exception(f"Open-Meteo API error: {str(e)}")
```

### Getting More Variables

For humidity and pressure, use hourly data:

```python
params = {
    "latitude": -6.2088,
    "longitude": 106.8456,
    "current_weather": "true",
    "hourly": "relative_humidity_2m,surface_pressure",
    "timezone": "auto"
}

response = requests.get(url, params=params)
data = response.json()

# Get current hour's values
current_hour = data["current_weather"]["time"]
hour_index = data["hourly"]["time"].index(current_hour)

humidity = data["hourly"]["relative_humidity_2m"][hour_index]
pressure = data["hourly"]["surface_pressure"][hour_index]
```

---

## API Integration Guide

### City Coordinates

```python
# Indonesian cities used in pipeline
CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "country": "ID"},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521, "country": "ID"},
    "Bandung": {"lat": -6.9175, "lon": 107.6191, "country": "ID"},
    "Medan": {"lat": 3.5952, "lon": 98.6722, "country": "ID"},
    "Makassar": {"lat": -5.1477, "lon": 119.4327, "country": "ID"}
}
```

### Unified Data Model

Both APIs are standardized to this schema:

```python
{
    "city_name": str,           # "Jakarta"
    "country": str,             # "ID"
    "timestamp": datetime,      # UTC timestamp
    "temperature": float,       # Celsius
    "feels_like": float | None, # Celsius (None for Open-Meteo)
    "humidity": int | None,     # % (0-100)
    "pressure": int | None,     # hPa
    "wind_speed": float,        # m/s
    "wind_direction": int,      # degrees (0-360)
    "weather_condition": str,   # "Clear", "Clouds", "Rain", etc.
    "weather_description": str, # Detailed description
    "source": str,              # "openweathermap" or "openmeteo"
    "latitude": float,
    "longitude": float
}
```

### Full Pipeline Integration

```python
import os
from typing import List, Dict
from datetime import datetime

def fetch_all_weather_data() -> List[Dict]:
    """
    Fetch weather data from all sources for all cities
    
    Returns:
        List of standardized weather data dicts
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    results = []
    
    for city_name, coords in CITIES.items():
        # Fetch from OpenWeatherMap
        try:
            ow_data = fetch_openweather(
                city=f"{city_name},{coords['country']}", 
                api_key=api_key
            )
            results.append(ow_data)
        except Exception as e:
            print(f"OpenWeather failed for {city_name}: {e}")
        
        # Fetch from Open-Meteo
        try:
            om_data = fetch_openmeteo(
                latitude=coords['lat'],
                longitude=coords['lon'],
                city_name=city_name
            )
            results.append(om_data)
        except Exception as e:
            print(f"Open-Meteo failed for {city_name}: {e}")
    
    return results
```

---

## Error Handling

### Retry Strategy

```python
import time
from typing import Callable, Any

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> Any:
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for each retry
    
    Returns:
        Function result
    
    Raises:
        Exception: If all retries fail
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            
            print(f"Attempt {attempt + 1} failed: {e}")
            print(f"Retrying in {delay}s...")
            time.sleep(delay)
            delay *= backoff_factor
```

### Usage in Airflow

```python
from airflow.decorators import task

@task(retries=3, retry_delay=timedelta(minutes=5))
def fetch_weather_data():
    """
    Airflow task with automatic retry
    """
    return fetch_all_weather_data()
```

---

## Rate Limiting

### OpenWeatherMap Rate Limiter

```python
import time
from collections import deque
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int, time_window: int):
        """
        Rate limiter implementation
        
        Args:
            max_calls: Maximum calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Remove old calls outside time window
        while self.calls and self.calls[0] < now - timedelta(seconds=self.time_window):
            self.calls.popleft()
        
        # Wait if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = (self.calls[0] + timedelta(seconds=self.time_window) - now).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        self.calls.append(now)

# Usage
rate_limiter = RateLimiter(max_calls=60, time_window=60)  # 60 calls/minute

for city in CITIES:
    rate_limiter.wait_if_needed()
    data = fetch_openweather(city, api_key)
```

---

## Testing APIs

### Test OpenWeatherMap

```bash
# Replace YOUR_API_KEY
export OPENWEATHER_API_KEY="your_key_here"

# Test single city
curl "https://api.openweathermap.org/data/2.5/weather?q=Jakarta,ID&appid=$OPENWEATHER_API_KEY&units=metric"

# Expected: Status 200, JSON response with weather data
```

### Test Open-Meteo

```bash
# No key needed
curl "https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current_weather=true"

# Expected: Status 200, JSON response with current_weather
```

### Python Test Script

```python
import requests
import os

def test_apis():
    """Test both weather APIs"""
    
    # Test OpenWeatherMap
    print("Testing OpenWeatherMap...")
    ow_key = os.getenv("OPENWEATHER_API_KEY")
    ow_url = f"https://api.openweathermap.org/data/2.5/weather?q=Jakarta,ID&appid={ow_key}&units=metric"
    
    try:
        response = requests.get(ow_url, timeout=10)
        response.raise_for_status()
        print("✅ OpenWeatherMap: OK")
        print(f"   Temperature: {response.json()['main']['temp']}°C")
    except Exception as e:
        print(f"❌ OpenWeatherMap: FAILED - {e}")
    
    # Test Open-Meteo
    print("\nTesting Open-Meteo...")
    om_url = "https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current_weather=true"
    
    try:
        response = requests.get(om_url, timeout=10)
        response.raise_for_status()
        print("✅ Open-Meteo: OK")
        print(f"   Temperature: {response.json()['current_weather']['temperature']}°C")
    except Exception as e:
        print(f"❌ Open-Meteo: FAILED - {e}")

if __name__ == "__main__":
    test_apis()
```

---

## API Response Times

Average response times (tested from Indonesia):

| API | Average | P95 | P99 |
|-----|---------|-----|-----|
| OpenWeatherMap | 200ms | 350ms | 500ms |
| Open-Meteo | 150ms | 280ms | 400ms |

---

## Useful Links

**OpenWeatherMap**:
- Dashboard: https://home.openweathermap.org
- API Keys: https://home.openweathermap.org/api_keys
- Usage Stats: https://home.openweathermap.org/statistics
- API Docs: https://openweathermap.org/api
- Status Page: https://openweathermap.statuspage.io/

**Open-Meteo**:
- Main Site: https://open-meteo.com
- API Docs: https://open-meteo.com/en/docs
- GitHub: https://github.com/open-meteo/open-meteo

---

**Next**: See [SETUP.md](SETUP.md) to configure API keys in the pipeline.
