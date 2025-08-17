"""
通用工具函数
"""
import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
import time
from datetime import datetime

from .config import settings
from .constants import SUPPORTED_QUERY_MODES, QUERY_MODE_DESCRIPTIONS
from .logging_utils import get_logger

logger = get_logger(__name__)


def validate_query_mode(mode: str) -> bool:
    """验证查询模式是否有效"""
    return mode in SUPPORTED_QUERY_MODES


def get_query_mode_info() -> Dict[str, Any]:
    """获取查询模式信息"""
    return {
        "modes": QUERY_MODE_DESCRIPTIONS,
        "default": "hybrid",
        "recommended": ["hybrid", "mix", "local"]
    }


def check_knowledge_graph_files(working_dir: str) -> Dict[str, bool]:
    """检查知识图谱文件是否存在"""
    xml_file = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
    json_file = os.path.join(working_dir, "graph_chunk_entity_relation.json")
    
    return {
        "xml_exists": os.path.exists(xml_file),
        "json_exists": os.path.exists(json_file),
        "xml_path": xml_file,
        "json_path": json_file
    }


def create_or_update_knowledge_graph_json(working_dir: str) -> bool:
    """创建或更新知识图谱JSON文件"""
    try:
        xml_file = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
        json_file = os.path.join(working_dir, "graph_chunk_entity_relation.json")
        
        if not os.path.exists(xml_file):
            logger.warning(f"XML文件不存在: {xml_file}")
            return False
        
        # 检查JSON文件是否需要更新
        if os.path.exists(json_file):
            xml_mtime = os.path.getmtime(xml_file)
            json_mtime = os.path.getmtime(json_file)
            if json_mtime >= xml_mtime:
                logger.info("JSON文件已是最新，无需更新")
                return True
        
        # 解析XML并转换为JSON
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # 提取节点和边信息
            nodes = []
            edges = []
            
            # 解析GraphML格式
            ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}
            
            for node in root.findall('.//graphml:node', ns):
                node_id = node.get('id')
                node_data = {'id': node_id}
                
                for data in node.findall('graphml:data', ns):
                    key = data.get('key')
                    value = data.text
                    if key and value:
                        node_data[key] = value
                
                nodes.append(node_data)
            
            for edge in root.findall('.//graphml:edge', ns):
                edge_data = {
                    'source': edge.get('source'),
                    'target': edge.get('target')
                }
                
                for data in edge.findall('graphml:data', ns):
                    key = data.get('key')
                    value = data.text
                    if key and value:
                        edge_data[key] = value
                
                edges.append(edge_data)
            
            # 保存为JSON
            graph_data = {
                'nodes': nodes,
                'edges': edges,
                'metadata': {
                    'node_count': len(nodes),
                    'edge_count': len(edges),
                    'created_at': datetime.now().isoformat(),
                    'source_file': xml_file
                }
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功创建/更新JSON文件: {json_file}")
            return True
            
        except ET.ParseError as e:
            logger.error(f"XML解析失败: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"创建/更新JSON文件失败: {str(e)}")
        return False


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def format_duration(seconds: float) -> str:
    """格式化时间间隔"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def generate_unique_id() -> str:
    """生成唯一ID"""
    import uuid
    return str(uuid.uuid4())


def generate_track_id(prefix: str = "track") -> str:
    """生成跟踪ID"""
    timestamp = int(time.time() * 1000)  # 毫秒时间戳
    return f"{prefix}_{timestamp}_{generate_unique_id()[:8]}"


def safe_json_loads(json_str: str, default=None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default=None) -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return default or "{}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """清理文本内容"""
    import re
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符（保留基本标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()[\]{}"\'-]', '', text)
    
    return text.strip()


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """提取关键词（简单实现）"""
    import re
    from collections import Counter
    
    # 简单的关键词提取
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 过滤停用词（简化版）
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        '的', '了', '在', '是', '我', '你', '他', '她', '它', '们', '这', '那', '有', '没', '不', '也', '都', '很', '就', '还'
    }
    
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # 统计词频
    word_counts = Counter(words)
    
    # 返回最常见的关键词
    return [word for word, count in word_counts.most_common(max_keywords)]


async def retry_async(func, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """异步重试装饰器"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = delay * (backoff ** attempt)
            logger.warning(f"操作失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            await asyncio.sleep(wait_time)


def measure_time(func):
    """测量函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.debug(f"函数 {func.__name__} 执行时间: {duration:.3f}秒")
        return result
    return wrapper


async def measure_time_async(func):
    """测量异步函数执行时间的装饰器"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.debug(f"异步函数 {func.__name__} 执行时间: {duration:.3f}秒")
        return result
    return wrapper


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import psutil
    
    try:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
        }
    except ImportError:
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "note": "psutil not available for detailed system info"
        }


def validate_json_schema(data: dict, required_fields: List[str]) -> bool:
    """验证JSON数据结构"""
    for field in required_fields:
        if field not in data:
            return False
    return True


def merge_dicts(*dicts) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def ensure_directory(directory: str) -> None:
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def calculate_file_hash(file_path: str) -> str:
    """计算文件哈希值"""
    import hashlib
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    import re
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制文件名长度
    if len(filename) > 255:
        filename = filename[:255]
    return filename


# 导出函数
__all__ = [
    "validate_query_mode",
    "get_query_mode_info",
    "check_knowledge_graph_files",
    "create_or_update_knowledge_graph_json",
    "format_file_size",
    "format_duration",
    "generate_unique_id",
    "generate_track_id",
    "safe_json_loads",
    "safe_json_dumps",
    "truncate_text",
    "clean_text",
    "extract_keywords",
    "retry_async",
    "measure_time",
    "measure_time_async",
    "get_system_info",
    "validate_json_schema",
    "merge_dicts",
    "chunk_list",
    "ensure_directory",
    "calculate_file_hash",
    "sanitize_filename"
]
