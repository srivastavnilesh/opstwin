
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select site_id
from "opstwin"."gold"."dim_site"
where site_id is null



  
  
      
    ) dbt_internal_test