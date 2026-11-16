
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        priority as value_field,
        count(*) as n_records

    from "opstwin"."staging"."stg_work_orders"
    group by priority

)

select *
from all_values
where value_field not in (
    'P1','P2','P3'
)



  
  
      
    ) dbt_internal_test