# ScamSence MVP

AI-powered scam detection tool. Analyzes emails, texts, URLs, ads, and phone scripts for fraud patterns.

## Quick Start

```bash
# 1. Клонируй репозиторий
git clone <repo_url>
cd scamsence_mvp

# 2. Создай виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Настрой переменные окружения
cp .env.example .env
# Отредактируй .env — добавь свои ключи

# 5. Запусти Backend (FastAPI)
uvicorn backend.app:app --reload --port 8000

# 6. Запусти Frontend (Streamlit) — в другом терминале
streamlit run main.py
```

## Tech Stack

| Компонент | Технология |
|-----------|-----------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | Streamlit |
| Vector DB | ChromaDB |
| Database | SQLite |
| LLM | Ollama (local) + Claude API (complex) |
| Voice | OpenAI Whisper (Pro) |

## Project Structure

```
├── backend/          # FastAPI app, routers, services
├── core/             # Analysis engine, LLM router, prompts
├── knowledge_base/   # ChromaDB + scam examples
├── voice_analysis/   # Whisper integration (Pro)
├── frontend/         # Streamlit pages & components
├── tests/            # Unit + integration tests
├── deployment/       # Docker configs
└── agents/           # Future sub-agents
```

## Analysis Format

Every analysis returns a structured verdict:

- **Verdict:** Scam / Likely Scam / Suspicious / Legitimate — X% confidence
- **Key Red Flags:** 3-7 specific indicators
- **Detailed Explanation:** Why this verdict was reached
- **Recommendations:** What the user should do

## License

MIT
