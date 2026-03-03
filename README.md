# EchoMap Analytics

Аналитическая платформа для анализа новостных сигналов из Telegram и прогнозирования геополитических событий.

## Возможности

- **Частотный анализ** — отслеживание упоминаний ключевых слов по времени, обнаружение аномальных всплесков
- **Анализ тональности** — мультиязычный sentiment-анализ (RU/EN/HE) на базе XLM-RoBERTa
- **Извлечение сущностей (NER)** — персоны, локации, организации с мультиязычной моделью
- **Категоризация эскалации** — классификация сообщений по типам (военное наращивание, дипломатический провал, прямые угрозы и др.)
- **Композитный индекс эскалации** — объединение всех сигналов в единый индекс с уровнями тревоги
- **Предиктивная модель** — Gradient Boosting для ретроспективного анализа предсказуемости событий

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка подключения к БД

```bash
cp .env.example .env
# Отредактируйте .env — укажите параметры PostgreSQL
```

### 3. Экспорт данных (опционально)

```bash
# Посмотреть схему БД
python scripts/export_from_pg.py --schema-only

# Экспортировать в CSV
python scripts/export_from_pg.py --output data/messages.csv
```

### 4. Запуск дашборда

```bash
streamlit run dashboard/app.py
```

### 5. Запуск полного анализа (без дашборда)

```bash
python scripts/run_analysis.py
```

## Структура проекта

```
EchoMapAnalytics/
├── config.py                     # Конфигурация, ключевые слова, модели
├── requirements.txt
├── .env.example
├── src/
│   ├── data_loader.py            # Загрузка из PostgreSQL / CSV
│   ├── preprocessor.py           # Очистка текста, определение языка
│   ├── frequency_analyzer.py     # Частотный анализ, аномалии, крещендо
│   ├── nlp_analyzer.py           # Sentiment, NER (transformers)
│   └── signal_scorer.py          # Композитный индекс, прогнозирование
├── dashboard/
│   ├── app.py                    # Главная страница Streamlit
│   └── pages/
│       ├── 01_Частотный_анализ    # Графики частот и аномалий
│       ├── 02_Тональность        # Sentiment-анализ
│       ├── 03_Сущности           # NER-анализ
│       ├── 04_Сигналы_эскалации  # Композитный индекс
│       └── 05_Прогнозирование    # ML-модель
├── scripts/
│   ├── export_from_pg.py         # Экспорт из PostgreSQL
│   └── run_analysis.py           # Полный пайплайн
└── data/                         # Данные и результаты
```

## Формат данных

Минимально необходимые поля в БД/CSV:

| Поле | Тип | Описание |
|------|-----|----------|
| `text` | string | Текст сообщения |
| `date` | datetime | Дата/время |

Желательные дополнительные поля:

| Поле | Тип | Описание |
|------|-----|----------|
| `channel` | string | Название канала/источника |
| `views` | int | Количество просмотров |
| `id` | int | ID сообщения |

Система автоматически распознаёт различные названия колонок (message/content/body, timestamp/created_at и т.д.)

## Технологии

- **pandas** — обработка данных
- **transformers** (HuggingFace) — мультиязычный NLP
- **scikit-learn** — ML-модели
- **Streamlit** — интерактивный дашборд
- **Plotly** — визуализации
- **PostgreSQL / SQLAlchemy** — работа с БД

## Деплой (CapRover)

Образ собирается с **CPU-only PyTorch** (без CUDA/Triton), чтобы не занимать лишние гигабайты на сервере.

### Если деплой падает с «no space left on device»

На сервере закончилось место. Подключись по SSH и освободи диск:

```bash
# Сколько занято
df -h

# Удалить неиспользуемые образы, контейнеры, build-кэш Docker
docker system prune -a -f
docker builder prune -a -f

# Проверить снова
df -h
```

После этого повтори деплой в CapRover. Если места всё равно мало — удали старые образы приложения в CapRover или увеличь диск сервера.

### Контейнер постоянно перезапускается («Stopping» в логах)

Нужно понять, **кто** останавливает контейнер. Подключись по SSH к серверу CapRover и выполни по очереди.

**1. Логи приложения (подставь имя своего приложения):**
```bash
# Streamlit-дашборд в CapRover обычно называется echomap-analytics (с суффиксом)
docker service logs srv-captain--echomap-analytics --since 60m --timestamps

# Если у тебя одно приложение без суффикса — будет srv-captain--echomap и т.п.
# Узнать все сервисы: docker service ls | grep -i echo

# Следить в реальном времени (запусти и открой дашборд в браузере)
docker service logs srv-captain--echomap-analytics --timestamps --follow
```

**2. События Docker (кто и когда убил контейнер):**
```bash
# Запусти в одном терминале и оставь работать; в другом сделай деплой или открой дашборд
docker events --filter 'type=container' --filter 'event=die' --filter 'event=destroy' --since 5m
```
В выводе будет видно, какой контейнер завершился и (при OOM) причина.

**3. OOM Killer (закончилась память):**
```bash
dmesg -T | grep -i "out of memory\|oom\|killed process"
# или
journalctl -k | grep -i oom
```

**4. Логи preload-кэша внутри контейнера:**
```bash
CONTAINER=$(docker ps -q -f name=srv-captain--echomap-analytics)
docker exec $CONTAINER cat /var/log/preload.log
```

**5. Логи nginx (если 502 / таймаут со стороны прокси):**
```bash
docker service logs captain-nginx --since 30m --timestamps
```

По результатам: если в `docker events` видно `oom` или в dmesg — контейнер режут по памяти. Если контейнер падает с **exitCode=0** через несколько минут (например, ровно через ~5 минут) — платформа шлёт SIGTERM: чаще всего из‑за **failed health check**. В Dockerfile уже задан HEALTHCHECK по адресу **`/_stcore/health`** (лёгкий endpoint Streamlit), так что проверка не грузит главную страницу. После деплоя контейнер должен оставаться в статусе healthy. В CapRover отдельной настройки пути для health check нет — используется только HEALTHCHECK из Dockerfile.
