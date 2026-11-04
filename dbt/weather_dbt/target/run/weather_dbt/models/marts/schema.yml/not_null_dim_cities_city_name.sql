select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select city_name
from `weather-513509`.`weather_data_marts`.`dim_cities`
where city_name is null



      
    ) dbt_internal_test