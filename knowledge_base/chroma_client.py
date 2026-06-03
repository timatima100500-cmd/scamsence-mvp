"""
knowledge_base/chroma_client.py — ChromaDB клиент

Локальная векторная БД скамов. Similarity search находит похожие кейсы
для обогащения анализа в LLM router.

Архитектура:
- Одна коллекция "scam_examples" с cosine-distance эмбеддингами
- При старте: загружаем JSON (только если коллекция пустая)
- При анализе: top-3 похожих кейса передаются в LLM router
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loguru import logger

_CHROMA_DB_PATH = Path(__file__).parent / "chroma_db"
_EXAMPLES_PATH = Path(__file__).parent / "data" / "scam_examples.json"
_COLLECTION_NAME = "scam_examples"


class KnowledgeBaseClient:
    """
    Клиент ChromaDB для similarity search по скамам.
    Инициализируется лениво при первом вызове — сервер стартует быстро.
    """

    def __init__(self, persist_directory: Path = _CHROMA_DB_PATH) -> None:
        self._persist_dir = persist_directory
        self._client = None
        self._collection = None
        self._initialized = False

    def _ensure_initialized(self) -> bool:
        """
        Ленивая инициализация ChromaDB.
        Возвращает True если OK, False если chromadb недоступен.
        Не бросает исключения — KB опциональна.
        """
        if self._initialized:
            return self._collection is not None

        self._initialized = True
        try:
            import chromadb
            from knowledge_base.embeddings import get_embedding_function

            self._persist_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self._persist_dir))
            embedding_fn = get_embedding_function()

            # get_or_create — идемпотентно, безопасно при каждом старте
            self._collection = self._client.get_or_create_collection(
                name=_COLLECTION_NAME,
                embedding_function=embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )

            # Заполняем примерами только если коллекция пустая
            if self._collection.count() == 0:
                self._populate_from_json()
            else:
                logger.info("KB из кэша: {} примеров", self._collection.count())

            return True

        except ImportError:
            logger.warning("chromadb не установлен — knowledge base отключена")
            return False
        except Exception as e:
            logger.error("Ошибка инициализации KB: {}", e)
            return False

    def _populate_from_json(self) -> None:
        """Загружает примеры скамов из JSON в ChromaDB (один раз при пустой коллекции)."""
        if not _EXAMPLES_PATH.exists():
            logger.warning("scam_examples.json не найден: {}", _EXAMPLES_PATH)
            return

        with open(_EXAMPLES_PATH, encoding="utf-8") as f:
            examples: list[dict] = json.load(f)

        ids = [ex["id"] for ex in examples]
        documents = [ex["text"] for ex in examples]
        metadatas = [
            {
                "type": ex.get("type", "unknown"),
                "language": ex.get("language", "en"),
                "verdict": ex["verdict"],
                "confidence": str(ex["confidence"]),
                "red_flags": ", ".join(ex.get("red_flags", [])),
            }
            for ex in examples
        ]

        self._collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info("KB заполнена: {} примеров загружено", len(examples))

    def similarity_search(
        self,
        query_text: str,
        n_results: int = 3,
        min_similarity: float = 0.3,
    ) -> list[dict[str, Any]]:
        """
        Ищет top-N похожих кейсов из базы знаний.
        Возвращает пустой список если KB недоступна или ничего не найдено.
        """
        if not self._ensure_initialized():
            return []

        if not self._collection or self._collection.count() == 0:
            return []

        try:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=min(n_results, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            similar_cases = []
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for doc, meta, distance in zip(docs, metas, distances):
                # ChromaDB cosine distance: 0=идентично, 2=противоположно
                # Конвертируем в similarity: 1=идентично, 0=не похоже
                similarity = 1.0 - (distance / 2.0)

                if similarity < min_similarity:
                    continue

                similar_cases.append({
                    "text": doc,
                    "verdict": meta.get("verdict", "Unknown"),
                    "confidence": int(meta.get("confidence", 0)),
                    "red_flags": [
                        f.strip() for f in meta.get("red_flags", "").split(",") if f.strip()
                    ],
                    "type": meta.get("type", "unknown"),
                    "language": meta.get("language", "en"),
                    "similarity": round(similarity, 3),
                })

            logger.debug("KB: {} похожих кейсов (query len={})", len(similar_cases), len(query_text))
            return similar_cases

        except Exception as e:
            logger.error("Ошибка similarity_search: {}", e)
            return []

    def count(self) -> int:
        """Количество примеров в базе знаний."""
        if not self._ensure_initialized() or not self._collection:
            return 0
        return self._collection.count()

    def is_available(self) -> bool:
        """Проверяет доступность ChromaDB."""
        return self._ensure_initialized() and self._collection is not None


_kb_client: KnowledgeBaseClient | None = None


def get_knowledge_base() -> KnowledgeBaseClient:
    """Возвращает singleton KnowledgeBaseClient."""
    global _kb_client
    if _kb_client is None:
        _kb_client = KnowledgeBaseClient()
    return _kb_client
