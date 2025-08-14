"""
意图识别API模块
"""

import sys
from pathlib import Path

# 添加父目录到路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from api.server import create_intent_app
from api.models import (
    IntentAnalysisRequest,
    IntentAnalysisResponse,
    BaseResponse
)

__all__ = [
    "create_intent_app",
    "IntentAnalysisRequest", 
    "IntentAnalysisResponse",
    "BaseResponse"
]
