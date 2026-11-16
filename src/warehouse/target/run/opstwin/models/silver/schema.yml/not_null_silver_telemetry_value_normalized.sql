
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select value_normalized
from "opstwin"."silver"."silver_telemetry"
where value_normalized is null



  
  
      
    ) dbt_internal_test