
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        quarantine_reason as value_field,
        count(*) as n_records

    from "opstwin"."silver"."silver_telemetry_quarantine"
    group by quarantine_reason

)

select *
from all_values
where value_field not in (
    'NULL_VALUE'
)



  
  
      
    ) dbt_internal_test