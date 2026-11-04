select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select observation_date
from `weather-513509`.`weather_data_marts`.`agg_daily_weather`
where observation_date is null



      
    ) dbt_internal_test