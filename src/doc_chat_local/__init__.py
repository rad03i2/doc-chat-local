"""Doc Chat Local: private local document retrieval."""
from .core import Chunk, DocumentIndex, Hit, chunk_text, read_document, tokenize
__all__ = ["Chunk", "DocumentIndex", "Hit", "chunk_text", "read_document", "tokenize"]
__version__ = "1.0.0"
