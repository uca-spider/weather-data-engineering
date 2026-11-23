# Data Source: OpenWeatherMap

The pipeline uses a single external API, the OpenWeatherMap
[Current Weather Data](https://openweathermap.org/current) endpoint.
The client lives in `src/ingestion/weather_fetcher.py`.

## Request

```
GET https://api.openweathermap.org/data/2.5/weather
```

| Parameter | Value                                   |
|-----------|-----------------------------------------|
| `q`       | City name, e.g. `Jakarta`               |
| `appid`   | `OPENWEATHER_API_KEY` from the environment |
| `units`   | `metric` (temperature in °C, wind in m/s)  |

One request is made per city, with a 10 second timeout. The constructor raises
`ValueError` if the API key is not set.

## Cities

Default list (`INDONESIAN_CITIES`): Jakarta, Surabaya, Bandung, Medan, Makassar.
Pass another list to `fetch_weather_data(cities=[...])` to change it. The
environment variable `CITIES` is not read by the code.

## Fields kept from the response

| Field                 | Source in API response     |
|-----------------------|----------------------------|
| `city`                | `name`                     |
| `country`             | `sys.country`              |
| `latitude`, `longitude` | `coord.lat`, `coord.lon` |
| `temperature`         | `main.temp`                |
| `feels_like`          | `main.feels_like`          |
| `temp_min`, `temp_max`| `main.temp_min`, `main.temp_max` |
| `pressure`            | `main.pressure` (hPa)      |
| `humidity`            | `main.humidity` (%)        |
| `weather_main`, `weather_description` | `weather[0].main`, `weather[0].description` |
| `wind_speed`          | `wind.speed`               |
| `wind_direction`      | `wind.deg` (may be null)   |
| `cloudiness`          | `clouds.all` (%)           |
| `timestamp`           | Fetch time in UTC, set by the pipeline (not the API's observation time) |
| `data_source`         | Constant `openweathermap`  |

## Error handling

Each city is handled independently. On HTTP 401, 404, any other non-200 status,
a timeout, a connection error or any other exception, the error is logged and
that city is skipped (`None`). The remaining cities are still fetched, and the
log reports `Successfully fetched N/M cities`. There is no retry inside the
fetcher; retries come from the Airflow task settings (2 retries, 5 minute delay)
when run under Airflow.

Because failed cities are skipped rather than raised, a missing city shows up
downstream in the quality audit (city completeness check), not as a task failure.

## Rate limits

The free plan allows 1,000 calls per day. At 5 cities every 6 hours the
pipeline makes 20 calls per day.
