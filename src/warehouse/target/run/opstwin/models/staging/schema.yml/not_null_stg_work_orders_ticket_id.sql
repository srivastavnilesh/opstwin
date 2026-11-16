
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select ticket_id
from "opstwin"."staging"."stg_work_orders"
where ticket_id is null



  
  
      
    ) dbt_internal_test