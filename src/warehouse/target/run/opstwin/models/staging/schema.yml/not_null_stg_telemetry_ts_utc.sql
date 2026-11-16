
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ts_utc
from "opstwin"."staging"."stg_telemetry"
where ts_utc is null



  
  
      
    ) dbt_internal_test