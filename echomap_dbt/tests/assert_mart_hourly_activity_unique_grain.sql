select published_date_il, published_hour_il, count(*) as row_count
from {{ ref('mart_hourly_activity') }}
group by 1, 2
having count(*) > 1
