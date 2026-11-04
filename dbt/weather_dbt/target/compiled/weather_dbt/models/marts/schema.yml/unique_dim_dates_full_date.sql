
    
    

with dbt_test__target as (

  select full_date as unique_field
  from `weather-513509`.`weather_data_marts`.`dim_dates`
  where full_date is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1


