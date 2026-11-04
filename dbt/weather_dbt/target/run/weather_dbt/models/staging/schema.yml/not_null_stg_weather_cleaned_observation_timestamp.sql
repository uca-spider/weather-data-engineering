select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select observation_timestamp
from `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
where observation_timestamp is null



      
    ) dbt_internal_test