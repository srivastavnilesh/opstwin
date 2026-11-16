
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select reading_id
from "opstwin"."silver"."silver_telemetry"
where reading_id is null



  
  
      
    ) dbt_internal_test