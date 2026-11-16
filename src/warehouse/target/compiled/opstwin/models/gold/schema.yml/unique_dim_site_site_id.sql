
    
    

select
    site_id as unique_field,
    count(*) as n_records

from "opstwin"."gold"."dim_site"
where site_id is not null
group by site_id
having count(*) > 1


