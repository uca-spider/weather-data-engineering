select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select city_name
from `weather-513509`.`weather_data_staging`.`stg_weather_cleaned`
where city_name is null



      
    ) dbt_internal_test