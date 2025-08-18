"""
优化的问答系统

基于RAG架构的高效问答对存储和检索系统
"""

from .optimized_qa_manager import OptimizedQAManager
from .qa_vector_storage import QAVectorStorage, QAPair

__version__ = "0.1.0"
__author__ = "GuiXiaoXiRag Team"
__description__ = "基于RAG架构的优化问答系统"

__all__ = [
    # 优化的管理器和存储
    "OptimizedQAManager",
    "QAVectorStorage",
    "QAPair",

    # 版本信息
    "__version__",
    "__author__",
    "__description__"
]
