
  
    

    create or replace table `weather-513509`.`weather_data_marts`.`dim_cities`
      
    
    

    OPTIONS()
    as (
      

WITH city_source AS (
    SELECT
        city_name,
        country_code,
        latitude,
        longitude,
        observation_timestamp
    FROM `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
),

latest_city_info AS (
    SELECT
        -- Surrogate Key deterministik berbasis nama kota
        TO_HEX(MD5(city_name)) AS city_id,
        city_name,
        country_code,
        latitude,
        longitude
    FROM city_source
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY city_name 
        ORDER BY observation_timestamp DESC
    ) = 1
)

SELECT * FROM latest_city_info
    );
  