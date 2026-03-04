"""
Internationalization module for EchoMap Analytics.
Auto-detects browser language, provides RU/EN toggle.
"""

import streamlit as st

TRANSLATIONS = {
    # === Main page ===
    "app_title": {
        "ru": "EchoMap Analytics",
        "en": "EchoMap Analytics",
    },
    "app_subtitle": {
        "ru": "Платформа для анализа новостей из Telegram-каналов. Помогает увидеть тренды, всплески и закономерности в потоке событий.",
        "en": "A platform for analyzing Telegram news channels. Helps identify trends, spikes, and patterns in the flow of events.",
    },
    "filters": {
        "ru": "Фильтры",
        "en": "Filters",
    },
    "date_range": {
        "ru": "Период",
        "en": "Date range",
    },
    "event_types": {
        "ru": "Тип событий",
        "en": "Event types",
    },
    "channels": {
        "ru": "Каналы",
        "en": "Channels",
    },
    "regions": {
        "ru": "Регионы",
        "en": "Regions",
    },
    "messages_count": {
        "ru": "Сообщений",
        "en": "Messages",
    },
    "days_in_sample": {
        "ru": "Дней в выборке",
        "en": "Days in sample",
    },
    "channels_count": {
        "ru": "Каналов",
        "en": "Channels",
    },
    "locations_count": {
        "ru": "Упомянуто мест",
        "en": "Locations mentioned",
    },
    "categories_count": {
        "ru": "Типов событий",
        "en": "Event types",
    },
    "tab_dynamics": {
        "ru": "Как менялся поток новостей",
        "en": "News flow dynamics",
    },
    "tab_map": {
        "ru": "Где происходили события",
        "en": "Where events happened",
    },
    "tab_data": {
        "ru": "Таблица сообщений",
        "en": "Messages table",
    },
    "dynamics_desc": {
        "ru": "Этот график показывает, **сколько сообщений публиковалось** в каждый период. Резкие всплески обычно означают крупные события.",
        "en": "This chart shows **how many messages were published** in each period. Sharp spikes usually indicate major events.",
    },
    "by_category": {
        "ru": "Разбивка по типам событий",
        "en": "Breakdown by event type",
    },
    "by_category_desc": {
        "ru": "Показывает, какие темы доминировали в каждый момент.",
        "en": "Shows which topics dominated at each point in time.",
    },
    "map_desc": {
        "ru": "Каждая точка на карте — это новость, привязанная к конкретному месту. Цвет точки показывает тип события.",
        "en": "Each dot on the map is a news item tied to a specific location. The color indicates the event type.",
    },
    "table_desc": {
        "ru": "Последние 50 сообщений из выборки. Используйте фильтры слева для уточнения.",
        "en": "Last 50 messages from the selection. Use the filters on the left to refine.",
    },
    "go_to_pages": {
        "ru": "**Перейдите к детальному анализу** через страницы в боковом меню.",
        "en": "**Go to detailed analysis** via the pages in the sidebar.",
    },
    "time_scale": {
        "ru": "Масштаб времени",
        "en": "Time scale",
    },
    "hourly": {"ru": "По часам", "en": "Hourly"},
    "3h": {"ru": "По 3 часа", "en": "3 hours"},
    "6h": {"ru": "По 6 часов", "en": "6 hours"},
    "daily": {"ru": "По дням", "en": "Daily"},
    "weekly": {"ru": "По неделям", "en": "Weekly"},
    "messages": {"ru": "Сообщений", "en": "Messages"},
    "event_type": {"ru": "Тип события", "en": "Event type"},
    "count": {"ru": "Количество", "en": "Count"},
    "loading_data": {"ru": "Загружаю данные...", "en": "Loading data..."},
    "loading_data_background": {
        "ru": "Данные подгружаются в фоне. Дашборд появится через несколько секунд.",
        "en": "Data is loading in the background. The dashboard will appear in a moment.",
    },
    "loading_taking_long": {
        "ru": "Загрузка занимает больше времени, чем обычно. Возможно, кэш ещё не готов или нет доступа к БД.",
        "en": "Loading is taking longer than usual. The cache may not be ready or the database may be unreachable.",
    },
    "load_now_btn": {"ru": "Загрузить на этой странице", "en": "Load on this page"},
    "nav_sections": {"ru": "Разделы", "en": "Sections"},
    "nav_home": {"ru": "Главная", "en": "Home"},

    # === Frequency analysis (page 1) ===
    "freq_title": {
        "ru": "Как часто упоминались ключевые темы",
        "en": "How often key topics were mentioned",
    },
    "freq_desc": {
        "ru": "Здесь мы считаем, **как часто в новостях встречались слова**, связанные с Ираном, эскалацией и военными действиями. Всплеск упоминаний часто предшествует крупным событиям.",
        "en": "Here we count **how often words appeared in the news** related to Iran, escalation, and military actions. A spike in mentions often precedes major events.",
    },
    "keyword_mentions": {
        "ru": "Упоминания ключевых слов",
        "en": "Keyword mentions",
    },
    "keyword_chart_desc": {
        "ru": "Красная линия показывает, сколько раз за период в новостях встретились слова вроде «Иран», «удар», «ракета», «ЦАХАЛ» и другие из нашего словаря. Пунктирная линия — общий объём сообщений для сравнения.",
        "en": "The red line shows how many times per period words like 'Iran', 'strike', 'missile', 'IDF' and others from our dictionary appeared. The dotted line is the total message volume for comparison.",
    },
    "keyword_matches": {
        "ru": "Совпадения с ключевыми словами",
        "en": "Keyword matches",
    },
    "total_messages": {
        "ru": "Всего сообщений",
        "en": "Total messages",
    },
    "total_matches_found": {
        "ru": "Всего найдено совпадений",
        "en": "Total matches found",
    },
    "relevant_share": {
        "ru": "Доля релевантных сообщений",
        "en": "Share of relevant messages",
    },
    "unusual_spikes": {
        "ru": "Необычные всплески",
        "en": "Unusual spikes",
    },
    "spikes_desc": {
        "ru": "Система сравнивает текущий уровень упоминаний со средним за прошлые периоды. Если значение **резко выше нормы** — это всплеск (красный треугольник). Такие всплески могут быть сигналом важных событий.",
        "en": "The system compares the current level of mentions with the average of past periods. If the value is **sharply above normal** — it's a spike (red triangle). Such spikes can signal important events.",
    },
    "actual_value": {"ru": "Фактическое значение", "en": "Actual value"},
    "normal_level": {"ru": "Обычный уровень (среднее)", "en": "Normal level (average)"},
    "threshold": {"ru": "Граница нормы", "en": "Threshold"},
    "spikes": {"ru": "Всплески", "en": "Spikes"},
    "spikes_found": {
        "ru": "Найдено **{}** необычных всплесков. Наведите на треугольники, чтобы увидеть даты.",
        "en": "Found **{}** unusual spikes. Hover over the triangles to see dates.",
    },
    "no_spikes": {
        "ru": "Необычных всплесков не найдено. Попробуйте снизить чувствительность в боковом меню.",
        "en": "No unusual spikes found. Try lowering the sensitivity in the sidebar.",
    },
    "escalation_topics": {
        "ru": "О чём писали: темы эскалации",
        "en": "What was reported: escalation topics",
    },
    "escalation_topics_desc": {
        "ru": "Новости разбиты на 5 тематических направлений. Каждая линия показывает, как часто за период появлялись сообщения на эту тему. Если несколько линий растут одновременно — это сигнал нарастающей напряжённости.",
        "en": "News is divided into 5 thematic areas. Each line shows how often messages on this topic appeared per period. If several lines grow simultaneously — it's a signal of rising tension.",
    },
    "cat_military": {"ru": "Военные действия", "en": "Military actions"},
    "cat_casualties": {"ru": "Жертвы и разрушения", "en": "Casualties & damage"},
    "cat_diplomatic": {"ru": "Дипломатия и политика", "en": "Diplomacy & politics"},
    "cat_missiles": {"ru": "Ракеты, ПВО, сирены", "en": "Missiles, air defense, sirens"},
    "cat_regional": {"ru": "Расширение конфликта на регион", "en": "Regional conflict spread"},
    "event_stats": {
        "ru": "Общая статистика по типам событий",
        "en": "Overall statistics by event type",
    },
    "event_stats_desc": {
        "ru": "Сколько сообщений в каждой категории за весь выбранный период.",
        "en": "How many messages in each category for the entire selected period.",
    },
    "crescendo": {
        "ru": "Эффект крещендо",
        "en": "Crescendo effect",
    },
    "crescendo_desc": {
        "ru": "**Крещендо** — это когда несколько тем начинают расти одновременно. Например, растут и военные действия, и дипломатический кризис, и ракетные обстрелы. Такое совпадение — один из самых сильных предвестников эскалации.",
        "en": "**Crescendo** is when multiple topics start growing simultaneously. For example, military actions, diplomatic crisis, and missile strikes all rise together. Such coincidence is one of the strongest precursors of escalation.",
    },
    "crescendo_strength": {"ru": "Сила крещендо", "en": "Crescendo strength"},
    "topics_growing": {"ru": "Сколько тем растёт одновременно", "en": "How many topics grow simultaneously"},
    "sensitivity": {
        "ru": "Чувствительность обнаружения всплесков",
        "en": "Spike detection sensitivity",
    },
    "comparison_period": {
        "ru": "Период для сравнения (в точках)",
        "en": "Comparison period (in points)",
    },

    # === Geo (page 2) ===
    "geo_title": {"ru": "География событий", "en": "Event geography"},
    "geo_desc": {
        "ru": "Где именно происходили события, о которых писали Telegram-каналы? Карта и графики ниже показывают географию конфликта.",
        "en": "Where exactly did the events reported by Telegram channels happen? The map and charts below show the geography of the conflict.",
    },
    "interactive_map": {"ru": "Интерактивная карта", "en": "Interactive map"},
    "map_hint": {
        "ru": "Каждая точка — новость. Наведите на точку, чтобы прочитать текст. Цвет = тип события.",
        "en": "Each dot is a news item. Hover to read the text. Color = event type.",
    },
    "top_locations": {"ru": "Самые упоминаемые места", "en": "Most mentioned locations"},
    "top_locations_desc": {
        "ru": "Какие города и локации упоминались чаще всего.",
        "en": "Which cities and locations were mentioned most often.",
    },
    "regional_activity": {"ru": "Активность по регионам", "en": "Activity by region"},
    "regional_activity_desc": {
        "ru": "Как менялось количество новостей из разных регионов. Рост новостей из конкретного региона может указывать на обострение именно там.",
        "en": "How the volume of news from different regions changed. Growth from a specific region may indicate escalation there.",
    },
    "location_categories": {"ru": "О чём писали в каждом месте", "en": "What was reported at each location"},
    "location_categories_desc": {
        "ru": "Для каждого из топ-10 мест — какие типы событий там происходили.",
        "en": "For each of the top 10 locations — what types of events occurred there.",
    },
    "mentions": {"ru": "Упоминаний", "en": "Mentions"},
    "main_topic": {"ru": "Основная тема", "en": "Main topic"},
    "map_style": {"ru": "Стиль карты", "en": "Map style"},
    "dark": {"ru": "Тёмная", "en": "Dark"},
    "normal": {"ru": "Обычная", "en": "Normal"},
    "light": {"ru": "Светлая", "en": "Light"},
    "dot_size": {"ru": "Размер точек", "en": "Dot size"},

    # === Sentiment (page 3) ===
    "sentiment_title": {"ru": "Эмоциональный фон новостей", "en": "News sentiment"},
    "sentiment_desc": {
        "ru": "Каждое сообщение анализируется нейросетью, которая определяет его **тональность**: негативное, нейтральное или позитивное. Рост негативности в новостях часто сопровождает обострение ситуации.",
        "en": "Each message is analyzed by a neural network that determines its **sentiment**: negative, neutral, or positive. Rising negativity in the news often accompanies escalation.",
    },
    "sentiment_needed": {
        "ru": "Для анализа тональности нужна нейросетевая модель. При первом запуске она скачается (~500 МБ), а анализ 30 000 сообщений занимает около 1-1.5 часа на обычном компьютере.",
        "en": "Sentiment analysis requires a neural network model. On first run it will download (~500 MB), and analyzing 30,000 messages takes about 1-1.5 hours on a regular computer.",
    },
    "run_sentiment": {"ru": "Запустить анализ тональности", "en": "Run sentiment analysis"},
    "sentiment_progress": {"ru": "Анализ тональности: батч {} из {}", "en": "Sentiment analysis: batch {} of {}"},
    "sentiment_from_cache": {
        "ru": "Результаты тональности сохранены на сервере и подгружаются при обновлении данных.",
        "en": "Sentiment results are saved on the server and load automatically when data is refreshed.",
    },
    "overall_picture": {"ru": "Общая картина", "en": "Overall picture"},
    "overall_desc": {
        "ru": "Какая доля сообщений негативная, нейтральная или позитивная.",
        "en": "What share of messages is negative, neutral, or positive.",
    },
    "by_event_type": {"ru": "По типам событий", "en": "By event type"},
    "by_event_type_desc": {
        "ru": "Какие категории новостей несут больше всего негатива.",
        "en": "Which news categories carry the most negativity.",
    },
    "negativity_timeline": {"ru": "Как менялся негативный фон", "en": "How negativity changed over time"},
    "negativity_desc": {
        "ru": "**Индекс негативности** = средний уровень негатива минус позитив. Чем выше красная линия, тем более тревожный тон новостей. Резкий рост индекса может предшествовать эскалации.",
        "en": "**Negativity index** = average negativity minus positivity. The higher the red line, the more alarming the tone of the news. A sharp rise may precede escalation.",
    },
    "negativity_index": {"ru": "Индекс негативности", "en": "Negativity index"},
    "pct_negative": {"ru": "Доля негативных сообщений", "en": "Share of negative messages"},
    "negativity_higher_worse": {"ru": "Негативность (выше = хуже)", "en": "Negativity (higher = worse)"},
    "most_alarming": {"ru": "Самые тревожные сообщения", "en": "Most alarming messages"},
    "most_alarming_desc": {
        "ru": "Топ-20 сообщений с максимальным уровнем негатива по оценке нейросети.",
        "en": "Top 20 messages with the highest negativity score according to the neural network.",
    },
    "negative": {"ru": "Негативные", "en": "Negative"},
    "positive": {"ru": "Позитивные", "en": "Positive"},
    "neutral": {"ru": "Нейтральные", "en": "Neutral"},
    "sentiment_label": {"ru": "Тональность", "en": "Sentiment"},

    # === Escalation signals (page 4) ===
    "signals_title": {"ru": "Сводный индекс напряжённости", "en": "Composite tension index"},
    "signals_desc": {
        "ru": "Все сигналы (частота упоминаний, темы, тональность) объединены в **один индекс** от 0 до 1. Чем выше индекс, тем больше признаков надвигающейся эскалации видно в новостях.",
        "en": "All signals (mention frequency, topics, sentiment) are combined into **one index** from 0 to 1. The higher the index, the more signs of approaching escalation are visible in the news.",
    },
    "event_date": {"ru": "Дата начала операции", "en": "Operation start date"},
    "alert_critical": {"ru": "КРИТИЧЕСКИЙ — множественные сигналы эскалации", "en": "CRITICAL — multiple escalation signals"},
    "alert_high": {"ru": "ВЫСОКИЙ — заметный рост напряжённости", "en": "HIGH — noticeable rise in tension"},
    "alert_elevated": {"ru": "ПОВЫШЕННЫЙ — есть тревожные признаки", "en": "ELEVATED — there are alarming signs"},
    "alert_guarded": {"ru": "УМЕРЕННЫЙ — фоновая активность", "en": "GUARDED — background activity"},
    "alert_low": {"ru": "НИЗКИЙ — спокойная обстановка", "en": "LOW — calm situation"},
    "index_timeline": {"ru": "Как менялся индекс напряжённости", "en": "How the tension index changed"},
    "index_timeline_desc": {
        "ru": "Цветные зоны на фоне обозначают уровни: зелёный (спокойно) → красный (критично). Жирная красная линия — сглаженный индекс. Вертикальная линия — дата начала операции.",
        "en": "Colored zones indicate levels: green (calm) → red (critical). The bold red line is the smoothed index. The vertical line marks the operation start date.",
    },
    "index_raw": {"ru": "Индекс (точный)", "en": "Index (raw)"},
    "index_smoothed": {"ru": "Индекс (сглаженный)", "en": "Index (smoothed)"},
    "operation_start": {"ru": "Начало операции", "en": "Operation start"},
    "peak_points": {"ru": "Пиковые точки", "en": "Peak points"},
    "tension_index": {"ru": "Индекс напряжённости", "en": "Tension index"},
    "signal_breakdown": {"ru": "Из чего складывается индекс", "en": "What the index consists of"},
    "signal_breakdown_desc": {
        "ru": "Индекс состоит из нескольких компонентов. Здесь видно, какой именно сигнал вносит наибольший вклад в общую картину.",
        "en": "The index consists of several components. Here you can see which signal contributes most to the overall picture.",
    },
    "sig_keyword_freq": {"ru": "Частота ключевых слов", "en": "Keyword frequency"},
    "sig_keyword_accel": {"ru": "Ускорение роста упоминаний", "en": "Mention growth acceleration"},
    "sig_sentiment": {"ru": "Негативный тон новостей", "en": "Negative news tone"},
    "sig_military": {"ru": "Военные действия", "en": "Military actions"},
    "sig_casualties": {"ru": "Жертвы и разрушения", "en": "Casualties & damage"},
    "sig_diplomatic": {"ru": "Дипломатия и политика", "en": "Diplomacy & politics"},
    "sig_missiles": {"ru": "Ракеты и ПВО", "en": "Missiles & air defense"},
    "sig_regional": {"ru": "Расширение на регион", "en": "Regional spread"},
    "retrospective": {"ru": "Ретроспективный анализ", "en": "Retrospective analysis"},
    "retrospective_desc": {
        "ru": "Оглядываясь назад: какие сигналы были видны **до** начала операции? Можно ли было предсказать событие по данным из Telegram?",
        "en": "Looking back: what signals were visible **before** the operation started? Could the event have been predicted from Telegram data?",
    },
    "index_day_before": {"ru": "Индекс накануне", "en": "Index day before"},
    "avg_week_before": {"ru": "Среднее за неделю до", "en": "Average week before"},
    "avg_month_before": {"ru": "Среднее за месяц до", "en": "Average month before"},
    "peak_month": {"ru": "Пиковое значение за месяц", "en": "Peak value in month"},
    "trend_week": {"ru": "Тренд за неделю до", "en": "Trend week before"},
    "trend_rising": {"ru": "Рост", "en": "Rising"},
    "trend_falling": {"ru": "Падение", "en": "Falling"},
    "trend_mixed": {"ru": "Нестабильно", "en": "Unstable"},
    "strongest_signals": {
        "ru": "Какие сигналы были самыми сильными:",
        "en": "Which signals were the strongest:",
    },
    "signal_name": {"ru": "Сигнал", "en": "Signal"},
    "contribution": {"ru": "Вклад в индекс", "en": "Index contribution"},
    "per_week": {"ru": "За неделю", "en": "Per week"},
    "per_month": {"ru": "За месяц", "en": "Per month"},
    "lead_time_title": {
        "ru": "За сколько дней можно было заметить сигнал?",
        "en": "How many days in advance was the signal visible?",
    },
    "lead_time_desc": {
        "ru": "При разных порогах чувствительности — когда индекс впервые достиг этого уровня.",
        "en": "At different sensitivity thresholds — when the index first reached this level.",
    },
    "lead_time_found": {
        "ru": "Порог **{}**: сигнал появился за **{} дней** до события ({})",
        "en": "Threshold **{}**: signal appeared **{} days** before the event ({})",
    },
    "lead_time_sustained": {"ru": "и оставался высоким", "en": "and stayed high"},
    "lead_time_dropped": {"ru": "но потом снижался", "en": "but then dropped"},
    "lead_time_not_reached": {
        "ru": "Порог **{}**: индекс не достигал этого уровня до события",
        "en": "Threshold **{}**: index did not reach this level before the event",
    },

    # === Prediction (page 5) ===
    "predict_title": {"ru": "Можно ли было предсказать?", "en": "Could it have been predicted?"},
    "predict_desc": {
        "ru": "Здесь мы проверяем гипотезу: **содержали ли новости достаточно сигналов, чтобы заранее спрогнозировать эскалацию?** Для этого обучаем модель машинного обучения на исторических данных и смотрим, насколько хорошо она предсказывает периоды высокой напряжённости.",
        "en": "Here we test the hypothesis: **did the news contain enough signals to predict escalation in advance?** We train a machine learning model on historical data and see how well it predicts periods of high tension.",
    },
    "model_params": {"ru": "Параметры модели", "en": "Model parameters"},
    "observation_window": {"ru": "Окно наблюдения (дни)", "en": "Observation window (days)"},
    "forecast_horizon": {"ru": "Горизонт прогноза (дни)", "en": "Forecast horizon (days)"},
    "escalation_threshold": {"ru": "Что считать эскалацией", "en": "What counts as escalation"},
    "step1": {"ru": "Шаг 1: Подготовка данных", "en": "Step 1: Data preparation"},
    "step1_desc": {
        "ru": "Модель смотрит на **{} дней** назад и пытается понять: произойдёт ли эскалация (индекс > {}) в ближайшие **{} дней**? Для этого мы считаем средние, максимумы и тренды каждого сигнала.",
        "en": "The model looks **{} days** back and tries to determine: will escalation (index > {}) occur in the next **{} days**? We calculate averages, maximums, and trends for each signal.",
    },
    "features": {"ru": "Признаков у модели", "en": "Model features"},
    "training_days": {"ru": "Дней для обучения", "en": "Training days"},
    "escalation_days_info": {
        "ru": "В данных **{}** дней ({}%) были помечены как «эскалация».",
        "en": "In the data, **{}** days ({}%) were marked as 'escalation'.",
    },
    "step2": {"ru": "Шаг 2: Обучение и проверка модели", "en": "Step 2: Model training & validation"},
    "step2_desc": {
        "ru": "Модель обучается на ранних данных и проверяется на более поздних — это имитирует реальный прогноз. Метрика **AUC** показывает качество: 1.0 = идеальный прогноз, 0.5 = случайное угадывание.",
        "en": "The model trains on earlier data and is tested on later data — simulating real forecasting. **AUC** measures quality: 1.0 = perfect prediction, 0.5 = random guessing.",
    },
    "auc_good": {
        "ru": "Качество модели: **AUC = {:.3f}** — модель хорошо различает периоды эскалации.",
        "en": "Model quality: **AUC = {:.3f}** — the model distinguishes escalation periods well.",
    },
    "auc_ok": {
        "ru": "Качество модели: **AUC = {:.3f}** — модель видит некоторые закономерности.",
        "en": "Model quality: **AUC = {:.3f}** — the model detects some patterns.",
    },
    "auc_weak": {
        "ru": "Качество модели: **AUC = {:.3f}** — модель слабо различает сигналы.",
        "en": "Model quality: **AUC = {:.3f}** — the model weakly distinguishes signals.",
    },
    "step3": {"ru": "Шаг 3: Что важнее всего для прогноза", "en": "Step 3: Most important factors"},
    "step3_desc": {
        "ru": "Какие факторы модель считает наиболее полезными для предсказания. Длинная полоска = этот фактор больше всего влияет на прогноз.",
        "en": "Which factors the model considers most useful for prediction. Longer bar = more influence on the forecast.",
    },
    "importance": {"ru": "Важность", "en": "Importance"},
    "step4": {"ru": "Шаг 4: Как бы выглядел прогноз", "en": "Step 4: What the forecast would look like"},
    "step4_desc": {
        "ru": "Красная линия показывает **вероятность эскалации** в ближайшие {} дней, как её оценивает модель. Чем выше линия, тем больше модель «тревожилась».",
        "en": "The red line shows the **probability of escalation** in the next {} days as estimated by the model. The higher the line, the more the model 'worried'.",
    },
    "escalation_probability": {"ru": "Вероятность эскалации", "en": "Escalation probability"},
    "event": {"ru": "Событие", "en": "Event"},
    "conclusions": {"ru": "Выводы", "en": "Conclusions"},
    "conclusions_text": {
        "ru": """**Что мы проверили:**
- Модель смотрела на {} дней назад и пыталась предсказать эскалацию на {} дней вперёд
- Порог эскалации: индекс >= {}

**Важно понимать:**
- Это **ретроспективный** анализ — мы проверяем, были ли сигналы *в прошлом*, а не прогнозируем будущее
- Для реального прогнозирования нужна валидация на независимых данных
- Telegram-каналы отражают уже произошедшее — настоящие разведданные недоступны
- Тем не менее, **рост частоты и негативности новостей** — объективный сигнал обострения""",
        "en": """**What we tested:**
- The model looked {} days back and tried to predict escalation {} days ahead
- Escalation threshold: index >= {}

**Important to understand:**
- This is a **retrospective** analysis — we check if signals existed *in the past*, not predict the future
- Real forecasting requires validation on independent data
- Telegram channels reflect events that already happened — real intelligence data is not available
- Nevertheless, **rising frequency and negativity of news** is an objective signal of escalation""",
    },

    # Feature names
    "feat_composite": {"ru": "Общий индекс", "en": "Composite index"},
    "feat_kw_freq": {"ru": "Частота ключевых слов", "en": "Keyword frequency"},
    "feat_kw_accel": {"ru": "Ускорение упоминаний", "en": "Mention acceleration"},
    "feat_sentiment": {"ru": "Негативный тон", "en": "Negative tone"},
    "feat_military": {"ru": "Военные действия", "en": "Military actions"},
    "feat_casualties": {"ru": "Жертвы/разрушения", "en": "Casualties/damage"},
    "feat_diplomatic": {"ru": "Дипломатия", "en": "Diplomacy"},
    "feat_missiles": {"ru": "Ракеты/ПВО", "en": "Missiles/air defense"},
    "feat_regional": {"ru": "Региональная эскалация", "en": "Regional escalation"},
    "feat_mean": {"ru": "среднее", "en": "average"},
    "feat_max": {"ru": "максимум", "en": "maximum"},
    "feat_std": {"ru": "разброс", "en": "spread"},
    "feat_trend": {"ru": "тренд", "en": "trend"},
    "feat_accel": {"ru": "ускорение", "en": "acceleration"},
}


def get_lang() -> str:
    """Get current language from session state."""
    return st.session_state.get("lang", "en")


def t(key: str) -> str:
    """Translate a key to the current language."""
    lang = get_lang()
    entry = TRANSLATIONS.get(key, {})
    return entry.get(lang, entry.get("en", key))


def render_sidebar_nav():
    """Render sidebar navigation with translated page names (used when client.showSidebarNavigation = false)."""
    st.subheader(t("nav_sections"))
    try:
        st.page_link("app.py", label=t("nav_home"), icon="🌍")
        st.page_link("pages/01_📊_Частотный_анализ.py", label=t("freq_title"), icon="📊")
        st.page_link("pages/02_🗺️_Геоаналитика.py", label=t("geo_title"), icon="🗺️")
        st.page_link("pages/03_😤_Тональность.py", label=t("sentiment_title"), icon="😤")
        st.page_link("pages/04_⚠️_Сигналы_эскалации.py", label=t("signals_title"), icon="⚠️")
        st.page_link("pages/05_🔮_Прогнозирование.py", label=t("predict_title"), icon="🔮")
    except Exception:
        st.caption("Use the sidebar pages below.")


def init_language():
    """Initialize language selector and nav in sidebar. Call once from each page."""
    if "lang" not in st.session_state:
        st.session_state["lang"] = "en"

    with st.sidebar:
        lang = st.radio(
            "🌐",
            ["en", "ru"],
            index=["en", "ru"].index(st.session_state["lang"]),
            format_func=lambda x: {"en": "English", "ru": "Русский"}[x],
            horizontal=True,
        )
        if lang != st.session_state["lang"]:
            st.session_state["lang"] = lang
            st.rerun()
        st.divider()
        render_sidebar_nav()


FREQ_LABELS = {
    "1h": lambda: t("hourly"),
    "3h": lambda: t("3h"),
    "6h": lambda: t("6h"),
    "D": lambda: t("daily"),
    "W": lambda: t("weekly"),
}
