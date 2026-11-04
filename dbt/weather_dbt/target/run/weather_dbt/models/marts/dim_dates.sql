
  
    

    create or replace table `weather-513509`.`weather_data_marts`.`dim_dates`
      
    
    

    OPTIONS()
    as (
      

WITH distinct_dates AS (
    SELECT DISTINCT
        observation_date
    FROM `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
    WHERE observation_date IS NOT NULL
)

SELECT
    -- Format date_id integer YYYYMMDD (contoh: 20261104)
    CAST(FORMAT_DATE('%Y%m%d', observation_date) AS INT64) AS date_id,
    observation_date AS full_date,
    EXTRACT(YEAR FROM observation_date) AS year,
    EXTRACT(QUARTER FROM observation_date) AS quarter,
    EXTRACT(MONTH FROM observation_date) AS month,
    FORMAT_DATE('%B', observation_date) AS month_name,
    EXTRACT(DAY FROM observation_date) AS day_of_month,
    EXTRACT(DAYOFWEEK FROM observation_date) AS day_of_week,
    FORMAT_DATE('%A', observation_date) AS day_name,
    CASE 
        WHEN EXTRACT(DAYOFWEEK FROM observation_date) IN (1, 7) THEN TRUE 
        ELSE FALSE 
    END AS is_weekend
FROM distinct_dates
    );
  