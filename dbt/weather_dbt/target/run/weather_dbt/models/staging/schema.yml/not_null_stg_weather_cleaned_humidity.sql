select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select humidity
from `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
where humidity is null



      
    ) dbt_internal_test