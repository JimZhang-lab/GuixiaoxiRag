"""
向量化问答对存储系统

专注于向量化存储和检索功能的精简实现
"""

from .vectorized_qa_core import VectorizedQAStorage, QAPair, SearchResult
from .embedding_client import EmbeddingClient, MockEmbeddingClient, create_embedding_client
from .qa_manager import QAManager

__version__ = "1.0.0"
__author__ = "Vectorized QA Team"
__description__ = "向量化问答对存储和检索系统"

__all__ = [
    # 核心存储
    "VectorizedQAStorage",
    "QAPair", 
    "SearchResult",
    
    # Embedding客户端
    "EmbeddingClient",
    "MockEmbeddingClient",
    "create_embedding_client",
    
    # 高级管理器
    "QAManager",
    
    # 版本信息
    "__version__",
    "__author__",
    "__description__"
]
