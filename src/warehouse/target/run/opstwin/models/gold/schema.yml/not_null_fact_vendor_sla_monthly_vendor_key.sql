
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select vendor_key
from "opstwin"."gold"."fact_vendor_sla_monthly"
where vendor_key is null



  
  
      
    ) dbt_internal_test