select
    cast(booking_date as date)      as booking_date,
    site_id,
    unit_id,
    cast(is_occupied as boolean)    as is_occupied,
    cast(adr_inr as double)         as adr_inr,
    channel
from read_csv('{{ var("bronze_root") }}/operational/bookings.csv', header = true, auto_detect = true)