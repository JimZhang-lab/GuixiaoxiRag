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
    插入单个文本文档到指定知识库，支持自动分块和向量化。

    **功能特性：**
    - 自动文本分块处理
    - 向量化存储
    - 支持多种语言
    - 自动生成文档ID和跟踪ID

    **参数说明：**
    - text: 要插入的文本内容（必填，1-100000字符）
    - doc_id: 文档ID（可选，系统自动生成UUID）
    - file_path: 文件路径（可选，用于标识文档来源）
    - track_id: 跟踪ID（可选，用于批量操作跟踪）
    - working_dir: 自定义知识库路径（可选）
    - knowledge_base: 知识库名称（可选，默认使用当前知识库）
    - language: 处理语言（可选，支持"中文"、"English"等）

    **处理流程：**
    1. 文本内容验证
    2. 自动分块处理
    3. 向量化计算
    4. 存储到知识库
    5. 返回处理结果

    **文本分块：**
    - 智能分块算法
    - 保持语义完整性
    - 支持重叠分块
    - 可配置分块大小
    """,
    responses={
        200: {
            "description": "插入成功",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "插入成功",
                            "value": {
                                "success": True,
                                "message": "文本文档插入成功",
                                "data": {
                                    "track_id": "track_12345678",
                                    "doc_id": "doc_87654321",
                                    "chunks_count": 3,
                                    "total_tokens": 256
                                }
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "参数验证失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "text"],
                                "msg": "文本内容不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文档插入失败: 知识库未初始化"
                    }
                }
            }
        }
    }
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
    上传单个文件并将其内容解析后插入到指定知识库。

    **支持的文件格式：**
    - 📄 文本文件：.txt, .md, .markdown
    - 📋 文档文件：.pdf, .docx, .doc, .rtf
    - 📊 数据文件：.json, .xml, .csv, .xlsx
    - 💻 代码文件：.py, .js, .java, .cpp, .c, .h, .html, .css
    - 🌐 网页文件：.html, .htm

    **文件处理特性：**
    - 智能格式识别
    - 自动内容提取
    - 元数据解析
    - 编码自动检测
    - 结构化内容处理

    **参数说明：**
    - file: 上传的文件（必填，multipart/form-data）
    - knowledge_base: 目标知识库名称（可选）
    - language: 处理语言（可选，影响分词和处理策略）
    - track_id: 跟踪ID（可选，用于批量操作关联）
    - extract_metadata: 是否提取元数据（可选，默认true）

    **文件限制：**
    - 最大文件大小：50MB
    - 支持UTF-8、GBK等常见编码
    - 文件名支持中文

    **元数据提取：**
    - 文件基本信息（大小、创建时间等）
    - 文档属性（作者、标题等）
    - 内容统计（字符数、段落数等）

    **处理流程：**
    1. 文件上传验证
    2. 格式识别和解析
    3. 内容提取和清理
    4. 元数据提取（可选）
    5. 文本分块处理
    6. 向量化存储
    """,
    responses={
        200: {
            "description": "文件上传和插入成功",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {
                            "summary": "处理成功",
                            "value": {
                                "success": True,
                                "message": "文件上传并插入成功",
                                "data": {
                                    "track_id": "track_12345678",
                                    "file_info": {
                                        "filename": "document.pdf",
                                        "size": 1024000,
                                        "format": "pdf",
                                        "pages": 10
                                    },
                                    "processing_result": {
                                        "chunks_count": 15,
                                        "total_tokens": 2048,
                                        "extracted_text_length": 8192
                                    },
                                    "metadata": {
                                        "title": "示例文档",
                                        "author": "作者名称",
                                        "creation_date": "2024-01-01"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        413: {
            "description": "文件过大",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文件大小超过限制（50MB）"
                    }
                }
            }
        },
        415: {
            "description": "不支持的文件格式",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "不支持的文件格式: .exe"
                    }
                }
            }
        },
        422: {
            "description": "文件处理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文件解析失败: PDF文件损坏"
                    }
                }
            }
        }
    }
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
