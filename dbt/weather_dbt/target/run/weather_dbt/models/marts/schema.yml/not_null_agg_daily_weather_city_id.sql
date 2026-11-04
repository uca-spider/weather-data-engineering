select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select city_id
from `weather-513509`.`weather_data_marts`.`agg_daily_weather`
where city_id is null



      
    ) dbt_internal_test