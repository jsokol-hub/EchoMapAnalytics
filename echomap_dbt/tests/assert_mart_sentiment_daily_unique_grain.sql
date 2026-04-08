select published_date_il, sentiment_clean, count(*) as row_count
from {{ ref('mart_sentiment_daily') }}
group by 1, 2
having count(*) > 1
