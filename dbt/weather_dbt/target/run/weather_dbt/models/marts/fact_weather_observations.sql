
  
    

    create or replace table `weather-513509`.`weather_data_marts`.`fact_weather_observations`
      
    partition by observation_date
    cluster by city_id, weather_main

    OPTIONS()
    as (
      

WITH staged AS (
    SELECT * FROM `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
),

cities AS (
    SELECT city_id, city_name FROM `weather-513509`.`weather_data_marts`.`dim_cities`
),

dates AS (
    SELECT date_id, full_date FROM `weather-513509`.`weather_data_marts`.`dim_dates`
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
    );
  