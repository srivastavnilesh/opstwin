
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    sensor_key as unique_field,
    count(*) as n_records

from "opstwin"."gold"."dim_sensor"
where sensor_key is not null
group by sensor_key
having count(*) > 1



  
  
      
    ) dbt_internal_test