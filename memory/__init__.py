import os
from typing import Optional, Dict

from .sqlite_graph import ConversationMemory
from .vector_db import VectorDB


def get_memory(config: Optional[Dict] = None):
    """Return memory backend based on config or env."""
    config = config or {}
    mode = config.get("mode", os.getenv("MEMORY_MODE", "sqlite"))
    if mode == "vector":
        dim = int(config.get("dim", os.getenv("VECTOR_DIM", "768")))
        return VectorDB(dim)
    path = config.get("path", os.getenv("MEMORY_PATH", "openoperator.db"))
    return ConversationMemory(path)
