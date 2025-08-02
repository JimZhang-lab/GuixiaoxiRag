"""
工具函数
"""
import os
import logging
import zipfile
from pathlib import Path
from typing import Dict, Any
import docx2txt
import textract
from fastapi import UploadFile, HTTPException

from .config import settings


def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(
                os.path.join(settings.log_dir, "guixiaoxiRagirag_service.log"),
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )


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
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_extension == '.pdf':
            text_content = textract.process(str(file_path))
            return text_content.decode('utf-8')
        
        elif file_extension == '.docx':
            return docx2txt.process(file_path)
        
        elif file_extension == '.doc':
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
        
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    except Exception as e:
        raise ValueError(f"文件内容提取失败: {str(e)}")


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
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}"
        )
    
    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 提取文本内容
        text_content = extract_text_from_file(file_path)
        
        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "content": text_content
        }
    
    except Exception as e:
        # 如果处理失败，删除已保存的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


def get_file_contents(dir_name: str) -> list:
    """从目录中获取所有支持文件的内容"""
    contents = []
    current_dir = Path(__file__).parent.parent
    files_dir = current_dir / dir_name
    
    if not files_dir.exists():
        return contents
    
    # 处理txt文件
    for file_path in files_dir.glob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            contents.append(content)
        except Exception as e:
            logging.error(f"读取txt文件失败 {file_path}: {e}")
    
    # 处理pdf文件
    for file_path in files_dir.glob("*.pdf"):
        try:
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            logging.error(f"处理PDF文件失败 {file_path}: {e}")
    
    # 处理docx文件
    for file_path in files_dir.glob("*.docx"):
        try:
            text_content = docx2txt.process(file_path)
            contents.append(text_content)
        except Exception as e:
            logging.error(f"处理DOCX文件失败 {file_path}: {e}")
    
    # 处理doc文件
    for file_path in files_dir.glob("*.doc"):
        try:
            # 首先尝试用textract处理
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            logging.error(f"用textract处理DOC文件失败 {file_path}: {e}")
            # 如果textract失败，检查文件是否是docx格式
            if is_docx(str(file_path)):
                try:
                    text_content = docx2txt.process(file_path)
                    contents.append(text_content)
                    logging.info(f"成功将{file_path}作为DOCX文件处理")
                except Exception as e2:
                    logging.error(f"将DOC文件作为DOCX处理失败 {file_path}: {e2}")
            else:
                logging.error(f"跳过文件 {file_path}，既不是DOC也不是有效的DOCX")
    
    return contents


def validate_query_mode(mode: str) -> bool:
    """验证查询模式是否有效"""
    valid_modes = ["local", "global", "hybrid", "naive", "mix", "bypass"]
    return mode in valid_modes


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    import re
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename
