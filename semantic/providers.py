from __future__ import annotations
import threading
from typing import Optional, Self

import numpy as np
from numpy.typing import NDArray
import torch
from sentence_transformers import SentenceTransformer


class _E5Singleton:
    """
    Thread-safe singleton for intfloat/multilingual-e5-large.
    """
    _instance: Optional[Self] = None
    _lock = threading.RLock()

    model_name: str = 'intfloat/multilingual-e5-large'

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, device: Optional[str] = None) -> None:
        if getattr(self, '_init_done', False):
            return

        self.device = device or self._auto_device()
        self.model: SentenceTransformer = SentenceTransformer(
            self.model_name,
            device=self.device,
            cache_folder='./semantic/ml_models',
        )
        self._init_done = True

    @staticmethod
    def _auto_device() -> str:
        if torch.cuda.is_available():
            return 'cuda'
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():  # type: ignore[attr-defined]
            return 'mps'
        return 'cpu'


class E5Provider:
    def __init__(self, device: Optional[str] = None) -> None:
        singleton = _E5Singleton(device=device)
        self.model = singleton.model
        self.device = singleton.device

    @staticmethod
    def _l2_normalize(x: NDArray[np.float32] | NDArray[np.float64]) -> NDArray[np.float32]:
        x = np.asarray(x, dtype=np.float32)
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
        return (x / norms).astype(np.float32)

    def embed_docs(self, texts: list[str]) -> list[list[float]]:
        inputs = [f'passage: {t or ''}' for t in texts]
        emb = self.model.encode(
            inputs,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=False,
        )
        emb = self._l2_normalize(emb)
        return emb.tolist()

    def embed_query(self, text: str) -> list[float]:
        q = self.model.encode(
            [f'query: {(text or '').strip()}'],
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=False,
        )
        q = self._l2_normalize(q)[0]
        return q.tolist()