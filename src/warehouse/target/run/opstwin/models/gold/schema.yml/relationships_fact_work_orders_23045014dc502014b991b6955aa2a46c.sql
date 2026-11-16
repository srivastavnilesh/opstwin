
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select vendor_key as from_field
    from "opstwin"."gold"."fact_work_orders"
    where vendor_key is not null
),

parent as (
    select vendor_key as to_field
    from "opstwin"."gold"."dim_vendor"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test