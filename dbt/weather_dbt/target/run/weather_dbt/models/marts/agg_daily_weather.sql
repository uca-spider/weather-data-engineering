
  
    

    create or replace table `weather-513509`.`weather_data_marts`.`agg_daily_weather`
      
    
    

    OPTIONS()
    as (
      

WITH daily_stats AS (
    SELECT
        f.city_id,
        c.city_name,
        f.date_id,
        f.observation_date,
        COUNT(f.observation_id) AS total_observations,
        ROUND(AVG(f.temperature), 2) AS avg_temperature,
        ROUND(MIN(f.temperature), 2) AS min_temperature,
        ROUND(MAX(f.temperature), 2) AS max_temperature,
        ROUND(AVG(f.feels_like), 2) AS avg_feels_like,
        ROUND(AVG(f.humidity), 2) AS avg_humidity,
        ROUND(AVG(f.pressure), 2) AS avg_pressure,
        ROUND(AVG(f.wind_speed), 2) AS avg_wind_speed,
        -- Mengambil cuaca yang paling sering muncul dalam hari tersebut
        APPROX_TOP_COUNT(f.weather_main, 1)[OFFSET(0)].value AS dominant_weather
    FROM `weather-513509`.`weather_data_marts`.`fact_weather_observations` f
    INNER JOIN `weather-513509`.`weather_data_marts`.`dim_cities` c 
        ON f.city_id = c.city_id
    GROUP BY
        f.city_id,
        c.city_name,
        f.date_id,
        f.observation_date
)

SELECT * FROM daily_stats
    );
  