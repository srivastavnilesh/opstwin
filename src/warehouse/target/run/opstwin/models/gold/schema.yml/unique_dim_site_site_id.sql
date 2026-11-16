
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    site_id as unique_field,
    count(*) as n_records

from "opstwin"."gold"."dim_site"
where site_id is not null
group by site_id
having count(*) > 1



  
  
      
    ) dbt_internal_test