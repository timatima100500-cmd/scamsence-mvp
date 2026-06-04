# CLAUDE.md — Конституция проекта ScamSence MVP

## Что это?
ScamSence — веб-инструмент для анализа скамов (email, текст, URL, объявления, телефонные скрипты, аудио).
Лёгкий, модульный, freemium, faceless-friendly для YouTube.

## Tech Stack
- **Backend:** Python 3.11+ / FastAPI
- **Frontend:** Streamlit (MVP скорость)
- **Vector DB:** ChromaDB (локально)
- **Database:** SQLite
- **LLM Routing:** заглушки → Ollama (Llama 3.1 8B / Phi-3) → Claude API (для сложных)
- **Voice:** OpenWhisper / Moonshine (Pro only)
- **Rate Limiting:** по IP, 5-10 бесплатных проверок/день

## Архитектура

```
/scamsence_mvp/
├── CLAUDE.md                  # Этот файл — конституция проекта
├── README.md                  # Документация для пользователей
├── requirements.txt           # Зависимости Python
├── main.py                    # Streamlit entry point
├── .env.example               # Шаблон переменных окружения
│
├── backend/                   # FastAPI приложение
│   ├── __init__.py
│   ├── app.py                 # FastAPI app factory
│   ├── routers/               # API endpoints
│   │   ├── __init__.py
│   │   ├── analysis.py        # POST /analyze — главный endpoint
│   │   └── health.py          # GET /health
│   ├── services/              # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   └── rate_limiter.py    # IP-based rate limiting
│   └── models/                # Pydantic schemas
│       ├── __init__.py
│       └── schemas.py         # Request/Response модели
│
├── core/                      # Ядро анализа
│   ├── __init__.py
│   ├── llm_router.py          # Роутинг: заглушка → Ollama → Claude
│   ├── prompts.py             # Промпты для анализа скамов
│   ├── analyzer.py            # Главный класс анализатора
│   └── models.py              # Внутренние модели данных
│
├── knowledge_base/            # База знаний о скамах
│   ├── __init__.py
│   ├── chroma_client.py       # ChromaDB клиент
│   ├── embeddings.py          # Генерация эмбеддингов
│   └── data/                  # Примеры скамов (JSON/CSV)
│       └── scam_examples.json
│
├── voice_analysis/            # Голосовой анализ (Pro)
│   ├── __init__.py
│   ├── transcriber.py         # Whisper транскрипция
│   └── voice_analyzer.py      # Анализ голосовых паттернов
│
├── frontend/                  # Streamlit UI
│   ├── __init__.py
│   ├── pages/                 # Многостраничное Streamlit приложение
│   │   ├── __init__.py
│   │   ├── home.py            # Главная страница
│   │   ├── email_check.py     # Проверка email
│   │   ├── url_check.py       # Проверка URL
│   │   ├── text_check.py      # Проверка текста
│   │   └── voice_check.py     # Проверка голоса (Pro)
│   └── components/            # Переиспользуемые компоненты
│       ├── __init__.py
│       ├── result_card.py     # Карточка результата анализа
│       └── sidebar.py         # Боковая панель
│
├── tests/                     # Тесты
│   ├── __init__.py
│   ├── test_analyzer.py       # Тесты анализатора
│   ├── test_api.py            # Тесты API endpoints
│   └── test_rate_limiter.py   # Тесты rate limiter
│
├── deployment/                # Деплой конфиги
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
└── agents/                    # Будущие sub-agents
    └── __init__.py
```

## Coding Standards

### Python
- **Стиль:** PEP 8, максимальная длина строки 100 символов
- **Типизация:** type hints везде (def func(text: str) -> dict:)
- **Комментарии:** ОБЯЗАТЕЛЬНО на русском, объясняем ЗАЧЕМ, а не ЧТО
- **Docstrings:** для каждой функции и класса
- **Именование:** snake_case для функций/переменных, PascalCase для классов

### Комментарии — правила
```python
# ✅ Хорошо — объясняет ЗАЧЕМ
# Проверяем urgency-слова, потому что 90% скамов давят на срочность
if has_urgency_words(text):

# ❌ Плохо — объясняет ЧТО (и так видно из кода)
# Проверяем есть ли urgency слова
if has_urgency_words(text):
```

### Git
- Коммиты на английском, формат: `type: description`
- Типы: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- Примеры: `feat: add email analysis endpoint`, `fix: rate limiter bypass`

### Формат ответа анализа (СТРОГО)
```
Вердикт: [Scam / Likely Scam / Suspicious / Legitimate] — X% вероятность

Ключевые красные флаги: (3-7 пунктов)

Подробное объяснение:

Рекомендации:
```

## Roadmap — 12 дней

### День 1: Фундамент
- [x] CLAUDE.md, структура папок, Git init, requirements.txt, README

### День 2: Backend + Core (часть 1)
- [ ] FastAPI app factory, health endpoint
- [ ] Pydantic модели (Request/Response)
- [ ] LLM Router с заглушкой (mock response)

### День 3: Core Analysis Engine
- [ ] Промпты для анализа скамов
- [ ] Класс Analyzer — главная логика
- [ ] Паттерны распознавания: urgency, impersonation, too-good-to-be-true

### День 4: Knowledge Base
- [ ] ChromaDB setup
- [ ] Загрузка примеров скамов
- [ ] Similarity search для обогащения анализа

### День 5: Frontend (часть 1)
- [ ] Streamlit main.py + навигация
- [ ] Страница проверки текста
- [ ] Компонент result_card

### День 6: Frontend (часть 2)
- [ ] Email check page
- [ ] URL check page
- [ ] Sidebar с историей проверок

### День 7: Rate Limiting + Security
- [ ] IP-based rate limiter (5-10 проверок/день)
- [ ] Input validation и sanitization
- [ ] Error handling на всех уровнях

### День 8: LLM Integration
- [ ] Подключить Ollama (Llama 3.1 8B)
- [ ] Подключить Claude API (опционально)
- [ ] Роутинг: простые → локальная, сложные → Claude

### День 9: Voice + YouTube Module (Pro)
- [x] Whisper интеграция для аудиофайлов (AudioTranscriber, lazy load)
- [x] Транскрипция аудио → текст → ScamAnalyzer (voice_analyzer.py)
- [x] YouTube transcript extraction через youtube-transcript-api (без yt-dlp!)
- [x] POST /api/v1/analyze/youtube + POST /api/v1/analyze/audio
- [x] GET /api/v1/voice/status — проверка доступности модулей
- [x] frontend/pages/voice_check.py — два таба: YouTube + Audio (Pro)

### День 10: Testing
- [ ] Unit тесты для analyzer
- [ ] Integration тесты для API
- [ ] End-to-end тест полного flow

### День 11: Polish + UI
- [ ] Красивый UI (цвета, иконки)
- [ ] Loading states, error messages
- [ ] Mobile-friendly layout

### День 12: Deployment + Launch
- [ ] Docker setup
- [ ] Deploy (Railway / Render / VPS)
- [ ] Финальное тестирование на продакшене

## Правила анализа скамов (2026)

### Красные флаги (паттерны)
1. **Impersonation** — government, bank, tech support, family member
2. **Urgency/Pressure** — "act now", "limited time", "your account will be closed"
3. **Too Good To Be True** — "you won $1M", "guaranteed 500% returns"
4. **AI Voice Cloning** — неестественные паузы, monotone, артефакты
5. **Pig Butchering** — долгий "прогрев", потом инвестиционная схема
6. **Romance Scams** — быстрые чувства + просьба о деньгах
7. **Professional Fake English** — грамотный, но шаблонный язык
8. **Suspicious Links** — URL shorteners, typosquatting, lookalike домены
9. **Payment Red Flags** — crypto only, gift cards, wire transfer
10. **Data Harvesting** — запрос SSN, паролей, банковских данных

## Интеграции и автоматизация

### YouTube Transcript → ScamAnalyzer
YouTube имеет встроенные транскрипты на большинстве видео (кнопка "Show transcript" под видео).
**Подход:** извлекаем transcript через YouTube Data API или прямой парсинг — без скачивания аудио.

**Способ 1 — python (youtube-transcript-api):**
```python
from youtube_transcript_api import YouTubeTranscriptApi
transcript = YouTubeTranscriptApi.get_transcript(video_id)
text = " ".join([t["text"] for t in transcript])
# → передаём text в POST /api/v1/analyze
```

**Способ 2 — n8n автоматизация (есть локально):**
- Триггер: новое видео на канале (YouTube trigger node)
- HTTP Request node → GET transcript
- HTTP Request node → POST /api/v1/analyze с transcript как content
- Если verdict = Scam → уведомление (email/Telegram)

**Реализация:** День 9, функция `transcribe_youtube(video_id: str) -> str` в `voice_analysis/transcriber.py`
**Зависимость:** `pip install youtube-transcript-api` (добавить в requirements.txt на День 9)
