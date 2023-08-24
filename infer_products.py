from typing import Iterable, List

from transcripts.custom_types import Product, TextChunk


def infer_products(texts: Iterable[TextChunk]) -> List[Product]:
    return []


def infer_youtube(texts: Iterable[TextChunk]) -> Product:
    return Product(name="YouTube", related_texts=list(texts))
