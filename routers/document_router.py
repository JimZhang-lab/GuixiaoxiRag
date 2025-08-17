"""
文档管理路由
处理文档上传、插入、批量处理等功能
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from model import (
    BaseResponse, InsertTextRequest, InsertTextsRequest, 
    DirectoryInsertRequest, FileUploadRequest, InsertResponse,
    FileUploadResponse, BatchFileUploadResponse
)
from api.document_api import DocumentAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["文档管理"])

# 创建API处理器实例
document_api = DocumentAPI()


@router.post(
    "/insert/text",
    response_model=BaseResponse,
    summary="插入单个文本文档",
    description="""
    插入单个文本文档到指定知识库。
    
    **参数说明：**
    - text: 要插入的文本内容（必填）
    - doc_id: 文档ID（可选，系统会自动生成）
    - file_path: 文件路径（可选）
    - track_id: 跟踪ID（可选，系统会自动生成）
    - working_dir: 自定义知识库路径（可选）
    - knowledge_base: 知识库名称（可选，默认使用当前知识库）
    - language: 处理语言（可选，默认使用系统设置）
    
    **返回结果：**
    - success: 操作是否成功
    - message: 操作结果消息
    - data: 包含track_id等信息的数据对象
    
    **使用示例：**
    ```json
    {
        "text": "这是一段要插入的文本内容",
        "knowledge_base": "my_kb",
        "language": "中文"
    }
    ```
    """
)
async def insert_text(request: InsertTextRequest):
    """插入单个文本文档"""
    return await document_api.insert_text(request)


@router.post(
    "/insert/texts",
    response_model=BaseResponse,
    summary="批量插入文本文档",
    description="""
    批量插入多个文本文档到指定知识库。
    
    **参数说明：**
    - texts: 要插入的文本列表（必填）
    - doc_ids: 文档ID列表（可选，长度应与texts匹配）
    - file_paths: 文件路径列表（可选）
    - track_id: 跟踪ID（可选，系统会自动生成）
    - knowledge_base: 知识库名称（可选）
    - language: 处理语言（可选）
    
    **返回结果：**
    - success: 操作是否成功
    - message: 操作结果消息
    - data: 包含track_id和处理统计的数据对象
    
    **使用示例：**
    ```json
    {
        "texts": [
            "第一段文本内容",
            "第二段文本内容",
            "第三段文本内容"
        ],
        "knowledge_base": "my_kb",
        "language": "中文"
    }
    ```
    """
)
async def insert_texts(request: InsertTextsRequest):
    """批量插入文本文档"""
    return await document_api.insert_texts(request)


@router.post(
    "/insert/file",
    response_model=BaseResponse,
    summary="上传并插入单个文件",
    description="""
    上传单个文件并将其内容插入到指定知识库。
    
    **支持的文件格式：**
    - 文本文件：.txt, .md
    - 文档文件：.pdf, .docx, .doc
    - 数据文件：.json, .xml, .csv
    - 代码文件：.py, .js, .java, .cpp, .c, .h
    
    **参数说明：**
    - file: 上传的文件（必填）
    - knowledge_base: 目标知识库名称（可选）
    - language: 处理语言（可选）
    - track_id: 跟踪ID（可选）
    - extract_metadata: 是否提取元数据（可选，默认true）
    
    **文件大小限制：**
    - 最大文件大小：50MB
    
    **返回结果：**
    - success: 操作是否成功
    - message: 操作结果消息
    - data: 包含文件信息和处理结果的数据对象
    """
)
async def insert_file(
    file: UploadFile = File(...),
    knowledge_base: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    track_id: Optional[str] = Form(None),
    extract_metadata: bool = Form(True)
):
    """上传并插入单个文件"""
    request = FileUploadRequest(
        knowledge_base=knowledge_base,
        language=language,
        track_id=track_id,
        extract_metadata=extract_metadata
    )
    return await document_api.insert_file(file, request)


@router.post(
    "/insert/files",
    response_model=BaseResponse,
    summary="批量上传并插入文件",
    description="""
    批量上传多个文件并将其内容插入到指定知识库。
    
    **参数说明：**
    - files: 上传的文件列表（必填）
    - knowledge_base: 目标知识库名称（可选）
    - language: 处理语言（可选）
    - extract_metadata: 是否提取元数据（可选）
    
    **处理方式：**
    - 并行处理多个文件以提高效率
    - 单个文件失败不会影响其他文件的处理
    - 返回每个文件的详细处理结果
    
    **返回结果：**
    - success: 整体操作是否成功
    - message: 操作结果消息
    - data: 包含所有文件处理结果的数据对象
    """
)
async def insert_files(
    files: List[UploadFile] = File(...),
    knowledge_base: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    extract_metadata: bool = Form(True)
):
    """批量上传并插入文件"""
    return await document_api.insert_files(files, knowledge_base, language, extract_metadata)


@router.post(
    "/insert/directory",
    response_model=BaseResponse,
    summary="从目录插入文件",
    description="""
    从指定目录读取所有支持的文件并插入到知识库。
    
    **参数说明：**
    - directory_path: 目录路径（必填）
    - knowledge_base: 目标知识库名称（可选）
    - language: 处理语言（可选）
    - recursive: 是否递归处理子目录（可选，默认true）
    - file_patterns: 文件匹配模式列表（可选）
    
    **处理特点：**
    - 自动识别并处理所有支持的文件格式
    - 可以递归处理子目录中的文件
    - 支持文件名模式匹配过滤
    - 批量处理以提高效率
    
    **使用示例：**
    ```json
    {
        "directory_path": "/path/to/documents",
        "knowledge_base": "my_kb",
        "recursive": true,
        "file_patterns": ["*.pdf", "*.txt"]
    }
    ```
    """
)
async def insert_directory(request: DirectoryInsertRequest):
    """从指定目录插入所有支持的文件"""
    return await document_api.insert_directory(request)


# 导出路由器
__all__ = ["router"]
