"""
knowledge_base/embeddings.py — Генерация эмбеддингов

Преобразует текст в векторы для similarity search в ChromaDB.
Используем ChromaDB built-in embedding function (all-MiniLM-L6-v2):
работает локально, бесплатно, без API ключей.
"""
from __future__ import annotations
from loguru import logger

_embedding_fn = None


def get_embedding_function():
    """
    Возвращает ChromaDB embedding function (singleton).
    Загружается лениво — не замедляет старт сервера.
    all-MiniLM-L6-v2: 384-мерные векторы, EN+RU, тексты до 512 токенов.
    """
    global _embedding_fn
    if _embedding_fn is None:
        try:
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
            _embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            logger.info("Embedding function loaded: all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning("sentence-transformers недоступен, fallback: {}", e)
            _embedding_fn = _FallbackEmbeddingFunction()
    return _embedding_fn


class _FallbackEmbeddingFunction:
    """
    Fallback через ChromaDB default embedding (только chromadb без sentence-transformers).
    Используется если sentence-transformers не установлен — сервер не падает.
    """
    def __call__(self, input: list[str]) -> list[list[float]]:
        try:
            from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
            return DefaultEmbeddingFunction()(input)
        except Exception as e:
            logger.error("Fallback embedding недоступен: {}", e)
            return [[0.0] * 384 for _ in input]
