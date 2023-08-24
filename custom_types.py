from typing import Dict, List

from pydantic import BaseModel, Field


class TextChunk(BaseModel):
    text: str = Field(...)
    source: str = Field(...)
    metadata: Dict = Field(default_factory=dict)


class Product(BaseModel):
    name: str = Field(...)
    keywords: List[str] = Field(default_factory=list)
    related_texts: List[TextChunk] = Field(default_factory=list)


class ProductsResponse(BaseModel):
    products: List[Product] = Field(default_factory=list)
