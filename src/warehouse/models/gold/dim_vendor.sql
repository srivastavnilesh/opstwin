select
    row_number() over (order by vendor_id) as vendor_key,
    vendor_id, vendor_name, service_tier
from {{ ref('vendors') }}