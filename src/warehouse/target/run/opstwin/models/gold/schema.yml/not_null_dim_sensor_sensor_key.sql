
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select sensor_key
from "opstwin"."gold"."dim_sensor"
where sensor_key is null



  
  
      
    ) dbt_internal_test