select published_date_il, category_clean, count(*) as row_count
from {{ ref('mart_category_daily') }}
group by 1, 2
having count(*) > 1
