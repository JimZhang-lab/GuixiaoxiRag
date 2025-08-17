"""
文件处理工具函数
"""
import os
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
import docx2txt
import textract
from fastapi import UploadFile, HTTPException

from .config import settings
from .constants import SUPPORTED_FILE_TYPES, FILE_TYPE_DESCRIPTIONS
from .logging_utils import get_logger

logger = get_logger(__name__)


def is_docx(file_path: str) -> bool:
    """检查文件是否为docx格式"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            return True
    except zipfile.BadZipFile:
        return False


def extract_text_from_file(file_path: str) -> str:
    """从文件中提取文本内容"""
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.txt':
            return _extract_text_file(file_path)
        elif file_extension == '.pdf':
            return _extract_pdf_file(file_path)
        elif file_extension == '.docx':
            return _extract_docx_file(file_path)
        elif file_extension == '.doc':
            return _extract_doc_file(file_path)
        elif file_extension == '.md':
            return _extract_markdown_file(file_path)
        elif file_extension == '.json':
            return _extract_json_file(file_path)
        elif file_extension == '.xml':
            return _extract_xml_file(file_path)
        elif file_extension == '.csv':
            return _extract_csv_file(file_path)
        elif file_extension in ['.py', '.js', '.java', '.cpp', '.c', '.h']:
            return _extract_code_file(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    except Exception as e:
        logger.error(f"文件内容提取失败: {file_path}, 错误: {str(e)}")
        raise ValueError(f"文件内容提取失败: {str(e)}")


def _extract_text_file(file_path: str) -> str:
    """提取纯文本文件内容"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"无法解码文本文件: {file_path}")


def _extract_pdf_file(file_path: str) -> str:
    """提取PDF文件内容"""
    try:
        text_content = textract.process(str(file_path))
        return text_content.decode('utf-8')
    except Exception as e:
        raise ValueError(f"PDF文件处理失败: {str(e)}")


def _extract_docx_file(file_path: str) -> str:
    """提取DOCX文件内容"""
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        raise ValueError(f"DOCX文件处理失败: {str(e)}")


def _extract_doc_file(file_path: str) -> str:
    """提取DOC文件内容"""
    try:
        # 首先尝试用textract处理
        text_content = textract.process(str(file_path))
        return text_content.decode('utf-8')
    except Exception:
        # 如果textract失败，检查文件是否是docx格式
        if is_docx(file_path):
            return docx2txt.process(file_path)
        else:
            raise ValueError(f"无法处理.doc文件: {file_path}")


def _extract_markdown_file(file_path: str) -> str:
    """提取Markdown文件内容"""
    return _extract_text_file(file_path)


def _extract_json_file(file_path: str) -> str:
    """提取JSON文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        raise ValueError(f"JSON文件处理失败: {str(e)}")


def _extract_xml_file(file_path: str) -> str:
    """提取XML文件内容"""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return ET.tostring(root, encoding='unicode')
    except Exception as e:
        raise ValueError(f"XML文件处理失败: {str(e)}")


def _extract_csv_file(file_path: str) -> str:
    """提取CSV文件内容"""
    try:
        import pandas as pd
        df = pd.read_csv(file_path)
        return df.to_string()
    except ImportError:
        # 如果没有pandas，使用基础方法
        return _extract_text_file(file_path)
    except Exception as e:
        raise ValueError(f"CSV文件处理失败: {str(e)}")


def _extract_code_file(file_path: str) -> str:
    """提取代码文件内容"""
    return _extract_text_file(file_path)


async def process_uploaded_file(file: UploadFile) -> Dict[str, Any]:
    """处理上传的文件"""
    # 检查文件大小
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件大小超过限制 ({settings.max_file_size} bytes)"
        )
    
    # 检查文件类型
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}"
        )
    
    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    import uuid
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    try:
        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 提取文本内容
        text_content = extract_text_from_file(file_path)
        
        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "content": text_content,
            "file_type": file_extension,
            "file_type_description": FILE_TYPE_DESCRIPTIONS.get(file_extension, "未知类型")
        }
    
    except Exception as e:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")


def get_file_contents(directory_path: str) -> List[str]:
    """获取目录中所有支持文件的内容"""
    contents = []
    directory = Path(directory_path)
    
    if not directory.exists():
        raise ValueError(f"目录不存在: {directory_path}")
    
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FILE_TYPES:
            try:
                content = extract_text_from_file(str(file_path))
                contents.append(content)
                logger.info(f"成功提取文件内容: {file_path}")
            except Exception as e:
                logger.warning(f"跳过文件 {file_path}: {str(e)}")
                continue
    
    return contents


def validate_file_type(filename: str) -> bool:
    """验证文件类型是否支持"""
    file_extension = Path(filename).suffix.lower()
    return file_extension in SUPPORTED_FILE_TYPES


def get_file_info(file_path: str) -> Dict[str, Any]:
    """获取文件信息"""
    path = Path(file_path)
    
    if not path.exists():
        raise ValueError(f"文件不存在: {file_path}")
    
    stat = path.stat()
    
    return {
        "filename": path.name,
        "file_path": str(path.absolute()),
        "file_size": stat.st_size,
        "file_extension": path.suffix.lower(),
        "created_time": stat.st_ctime,
        "modified_time": stat.st_mtime,
        "is_supported": validate_file_type(path.name)
    }


def clean_temp_files(directory: str = None, max_age_hours: int = 24):
    """清理临时文件"""
    import time
    
    if directory is None:
        directory = settings.upload_dir
    
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    logger.info(f"清理临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"清理文件失败 {file_path}: {str(e)}")


def ensure_directory(directory: str):
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)


def safe_filename(filename: str) -> str:
    """生成安全的文件名"""
    import re
    # 移除或替换不安全的字符
    safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
    return safe_name


# 导出函数
__all__ = [
    "extract_text_from_file",
    "process_uploaded_file",
    "get_file_contents",
    "validate_file_type",
    "get_file_info",
    "clean_temp_files",
    "ensure_directory",
    "safe_filename",
    "is_docx"
]
