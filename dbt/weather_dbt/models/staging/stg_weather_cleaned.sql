{{ config(
    materialized='view'
) }}

WITH source_data AS (
    SELECT
        city,
        country,
        CAST(latitude AS FLOAT64) AS latitude,
        CAST(longitude AS FLOAT64) AS longitude,
        CAST(temperature AS FLOAT64) AS temperature,
        CAST(feels_like AS FLOAT64) AS feels_like,
        CAST(temp_min AS FLOAT64) AS temp_min,
        CAST(temp_max AS FLOAT64) AS temp_max,
        CAST(pressure AS INT64) AS pressure,
        CAST(humidity AS INT64) AS humidity,
        weather_main,
        weather_description,
        CAST(wind_speed AS FLOAT64) AS wind_speed,
        CAST(wind_direction AS INT64) AS wind_direction,
        CAST(cloudiness AS INT64) AS cloudiness,
        timestamp AS observation_timestamp,
        data_source
    FROM {{ source('raw_weather', 'raw_weather_data') }}
),

deduplicated AS (
    SELECT
        -- Surrogate Key unik per observasi per kota
        TO_HEX(MD5(CONCAT(city, '_', CAST(observation_timestamp AS STRING)))) AS observation_id,
        city AS city_name,
        COALESCE(country, 'ID') AS country_code,
        latitude,
        longitude,
        temperature,
        feels_like,
        temp_min,
        temp_max,
        pressure,
        humidity,
        weather_main,
        weather_description,
        wind_speed,
        wind_direction,
        cloudiness,
        observation_timestamp,
        DATE(observation_timestamp) AS observation_date,
        COALESCE(data_source, 'openweathermap') AS data_source,
        CURRENT_TIMESTAMP() AS transformed_at
    FROM source_data
    WHERE city IS NOT NULL
      AND observation_timestamp IS NOT NULL
    -- Ambil baris pertama jika ada duplikat kombinasi city + timestamp
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY city, observation_timestamp 
        ORDER BY observation_timestamp DESC
    ) = 1
)

SELECT * FROM deduplicated
