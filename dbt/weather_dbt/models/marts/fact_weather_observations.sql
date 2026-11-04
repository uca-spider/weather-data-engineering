{{ config(
    materialized='table',
    partition_by={
      "field": "observation_date",
      "data_type": "date",
      "granularity": "day"
    },
    cluster_by=["city_id", "weather_main"]
) }}

WITH staged AS (
    SELECT * FROM {{ ref('stg_weather_cleaned') }}
),

cities AS (
    SELECT city_id, city_name FROM {{ ref('dim_cities') }}
),

dates AS (
    SELECT date_id, full_date FROM {{ ref('dim_dates') }}
)

SELECT
    s.observation_id,
    c.city_id,
    d.date_id,
    s.observation_timestamp,
    s.observation_date,
    s.temperature,
    s.feels_like,
    s.temp_min,
    s.temp_max,
    s.pressure,
    s.humidity,
    s.weather_main,
    s.weather_description,
    s.wind_speed,
    s.wind_direction,
    s.cloudiness,
    s.data_source,
    s.transformed_at
FROM staged s
INNER JOIN cities c 
    ON s.city_name = c.city_name
INNER JOIN dates d 
    ON s.observation_date = d.full_date
