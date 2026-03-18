from __future__ import annotations


class Embedder:
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class FakeEmbedder(Embedder):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(text)), float(index)] for index, text in enumerate(texts)]
