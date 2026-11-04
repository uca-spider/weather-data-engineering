select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select full_date
from `weather-513509`.`weather_data_marts`.`dim_dates`
where full_date is null



      
    ) dbt_internal_test