select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select total_observations
from `weather-513509`.`weather_data_marts`.`agg_daily_weather`
where total_observations is null



      
    ) dbt_internal_test