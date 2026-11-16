select
    row_number() over (order by site_id) as site_key,
    site_id, site_name, city, asset_class, units, base_adr_inr
from {{ ref('sites') }}