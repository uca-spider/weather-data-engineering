
    
    

with child as (
    select date_id as from_field
    from `weather-513509`.`weather_data_marts`.`fact_weather_observations`
    where date_id is not null
),

parent as (
    select date_id as to_field
    from `weather-513509`.`weather_data_marts`.`dim_dates`
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


