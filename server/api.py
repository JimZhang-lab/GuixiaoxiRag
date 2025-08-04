"""
GuiXiaoXiRag FastAPI主应用
"""
import os
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .guixiaoxirag_service import guixiaoxirag_service
from .models import *
from .utils import setup_logging, process_uploaded_file
from .middleware import LoggingMiddleware, MetricsMiddleware, SecurityMiddleware, get_metrics
from .performance_config import PerformanceConfig, get_optimized_query_params
from .knowledge_base_manager import kb_manager


# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

# 应用启动时间
start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动GuiXiaoXiRag FastAPI服务...")
    try:
        await guixiaoxirag_service.initialize()
        logger.info("GuiXiaoXiRag服务初始化完成")
    except Exception as e:
        logger.error(f"GuiXiaoXiRag服务初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("正在关闭GuiXiaoXiRag FastAPI服务...")
    try:
        await guixiaoxirag_service.finalize()
        logger.info("GuiXiaoXiRag服务清理完成")
    except Exception as e:
        logger.error(f"GuiXiaoXiRag服务清理失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于GuiXiaoXiRag的知识图谱检索增强生成服务",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(SecurityMiddleware, max_request_size=settings.max_file_size)
app.add_middleware(LoggingMiddleware)

# 添加性能监控中间件
from .middleware import metrics_middleware_instance
metrics_middleware_instance = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)


# 异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="服务器内部错误",
            details={"error": str(exc)}
        ).model_dump()
    )


# 健康检查
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["系统"],
    summary="系统健康检查",
    description="""
    检查系统运行状态和服务健康情况。

    **功能说明：**
    - 检查服务是否正常运行
    - 返回系统基本信息和运行时间
    - 检查GuiXiaoXiRag服务初始化状态
    - 提供系统配置信息

    **返回信息包括：**
    - 服务名称和版本
    - 运行状态
    - 初始化状态
    - 工作目录
    - 系统运行时间
    """,
    responses={
        200: {
            "description": "系统健康状态正常",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "timestamp": "2024-01-01T12:00:00",
                        "system": {
                            "service_name": "GuiXiaoXiRag API",
                            "version": "1.0.0",
                            "status": "running",
                            "initialized": True,
                            "working_dir": "./knowledgeBase/default",
                            "uptime": 3600.5
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """系统健康检查接口"""
    return HealthResponse(
        timestamp=datetime.now().isoformat(),
        system=SystemStatus(
            service_name=settings.app_name,
            version=settings.app_version,
            status="running",
            initialized=guixiaoxirag_service._initialized,
            working_dir=settings.working_dir,
            uptime=time.time() - start_time
        )
    )


# 根路径
@app.get(
    "/",
    tags=["系统"],
    summary="API服务根路径",
    description="""
    获取API服务的基本信息和导航链接。

    **功能说明：**
    - 提供服务基本信息
    - 返回API文档和健康检查链接
    - 确认服务运行状态

    **适用场景：**
    - 服务发现和状态确认
    - 获取API文档入口
    - 系统集成时的连通性测试
    """,
    responses={
        200: {
            "description": "服务信息获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "service": "GuiXiaoXiRag API",
                        "version": "1.0.0",
                        "status": "running",
                        "docs": "/docs",
                        "health": "/health"
                    }
                }
            }
        }
    }
)
async def root():
    """API服务根路径信息"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# 文档插入API
@app.post(
    "/insert/text",
    response_model=BaseResponse,
    tags=["文档管理"],
    summary="插入单个文本文档",
    description="""
    将单个文本内容插入到指定的知识库中，支持多语言处理。

    **功能特性：**
    - 支持自定义文档ID和文件路径
    - 支持多种语言处理（中文、英文等）
    - 支持知识库切换和自定义工作目录
    - 提供跟踪ID用于后续操作追踪
    - 自动进行文本向量化和知识图谱构建

    **参数说明：**
    - `text`: 必填，要插入的文本内容
    - `doc_id`: 可选，文档唯一标识符
    - `file_path`: 可选，文档来源文件路径
    - `track_id`: 可选，用于跟踪处理进度
    - `knowledge_base`: 可选，目标知识库名称
    - `working_dir`: 可选，自定义工作目录路径
    - `language`: 可选，文本处理语言

    **使用场景：**
    - 单个文档内容导入
    - 实时文本数据添加
    - 知识库内容更新
    - 多语言文档处理
    """,
    responses={
        200: {
            "description": "文本插入成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "track_id": "track_123456",
                            "message": "文本插入成功到知识库 'my_kb'，语言: 中文"
                        }
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文本内容不能为空"
                    }
                }
            }
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "插入文本失败: 数据库连接错误"
                    }
                }
            }
        }
    }
)
async def insert_text(request: InsertTextRequest):
    """插入单个文本文档到知识库"""
    try:
        # 处理知识库路径
        working_dir = None
        if request.knowledge_base:
            working_dir = f"./knowledgeBase/{request.knowledge_base}"
        elif request.working_dir:
            working_dir = request.working_dir

        track_id = await guixiaoxirag_service.insert_text(
            text=request.text,
            doc_id=request.doc_id,
            file_path=request.file_path,
            track_id=request.track_id,
            working_dir=working_dir,
            language=request.language
        )

        kb_name = request.knowledge_base or "default"
        lang = request.language or "中文"
        return BaseResponse(
            data=InsertResponse(
                track_id=track_id,
                message=f"文本插入成功到知识库 '{kb_name}'，语言: {lang}"
            )
        )
    except Exception as e:
        logger.error(f"插入文本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/insert/texts",
    response_model=BaseResponse,
    tags=["文档管理"],
    summary="批量插入文本文档",
    description="""
    批量插入多个文本内容到指定知识库，提高处理效率。

    **功能特性：**
    - 支持一次性插入多个文本文档
    - 支持批量文档ID和文件路径设置
    - 高效的批量处理机制
    - 统一的语言和知识库设置
    - 原子性操作，确保数据一致性

    **参数说明：**
    - `texts`: 必填，文本内容列表
    - `doc_ids`: 可选，文档ID列表（与texts一一对应）
    - `file_paths`: 可选，文件路径列表（与texts一一对应）
    - `track_id`: 可选，批量操作跟踪ID
    - `knowledge_base`: 可选，目标知识库名称
    - `language`: 可选，批量处理语言

    **使用场景：**
    - 大量文档批量导入
    - 数据迁移和同步
    - 批量内容更新
    - 提高插入效率

    **注意事项：**
    - 建议单次批量插入不超过100个文档
    - 确保texts、doc_ids、file_paths长度一致（如果提供）
    - 大批量操作建议分批处理
    """,
    responses={
        200: {
            "description": "批量插入成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "track_id": "batch_track_123456",
                            "message": "批量插入成功到知识库 'my_kb'，语言: 中文"
                        }
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文本列表不能为空或长度不匹配"
                    }
                }
            }
        },
        500: {
            "description": "批量插入失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "批量插入文本失败: 处理超时"
                    }
                }
            }
        }
    }
)
async def insert_texts(request: InsertTextsRequest):
    """批量插入文本文档到知识库"""
    try:
        # 处理知识库路径
        working_dir = None
        if request.knowledge_base:
            working_dir = f"./knowledgeBase/{request.knowledge_base}"

        track_id = await guixiaoxirag_service.insert_texts(
            texts=request.texts,
            doc_ids=request.doc_ids,
            file_paths=request.file_paths,
            track_id=request.track_id,
            working_dir=working_dir,
            language=request.language
        )

        kb_name = request.knowledge_base or "default"
        lang = request.language or "中文"
        return BaseResponse(
            data=InsertResponse(
                track_id=track_id,
                message=f"批量插入成功到知识库 '{kb_name}'，语言: {lang}"
            )
        )
    except Exception as e:
        logger.error(f"批量插入文本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/insert/file",
    response_model=BaseResponse,
    tags=["文档管理"],
    summary="上传并插入单个文件",
    description="""
    上传单个文件并将其内容插入到知识库中。

    **支持的文件格式：**
    - 文本文件：.txt, .md, .rst
    - 文档文件：.pdf, .docx, .doc
    - 代码文件：.py, .js, .java, .cpp, .c, .h
    - 数据文件：.json, .xml, .csv

    **功能特性：**
    - 自动文件格式识别和内容提取
    - 文件大小限制和安全检查
    - 自动生成文件路径和跟踪ID
    - 支持多种编码格式
    - 文件元数据保存

    **处理流程：**
    1. 文件上传和验证
    2. 内容提取和格式转换
    3. 文本预处理和清理
    4. 向量化和知识图谱构建
    5. 返回处理结果

    **使用场景：**
    - 单个文档快速导入
    - 文件内容实时处理
    - 文档格式转换
    - 知识库内容补充

    **注意事项：**
    - 文件大小限制：默认最大50MB
    - 支持的编码：UTF-8, GBK, GB2312
    - PDF文件需要可提取文本内容
    """,
    responses={
        200: {
            "description": "文件上传并插入成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "filename": "document.pdf",
                            "file_path": "/uploads/document.pdf",
                            "file_size": 1024000,
                            "track_id": "file_track_123456"
                        }
                    }
                }
            }
        },
        400: {
            "description": "文件格式不支持或文件损坏",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "不支持的文件格式或文件大小超限"
                    }
                }
            }
        },
        413: {
            "description": "文件大小超过限制",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文件大小超过50MB限制"
                    }
                }
            }
        },
        500: {
            "description": "文件处理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "文件上传插入失败: 内容提取错误"
                    }
                }
            }
        }
    }
)
async def insert_file(file: UploadFile = File(...)):
    """上传并插入单个文件到知识库"""
    try:
        # 处理上传的文件
        file_info = await process_uploaded_file(file)

        # 插入文本内容
        track_id = await guixiaoxirag_service.insert_text(
            text=file_info["content"],
            file_path=file_info["file_path"]
        )

        return BaseResponse(
            data=FileUploadResponse(
                filename=file_info["filename"],
                file_path=file_info["file_path"],
                file_size=file_info["file_size"],
                track_id=track_id
            )
        )
    except Exception as e:
        logger.error(f"文件上传插入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 查询API
@app.post(
    "/query",
    response_model=BaseResponse,
    tags=["查询"],
    summary="智能知识查询",
    description="""
    基于知识图谱和向量检索的智能查询系统，支持多种查询模式。

    **查询模式说明：**
    - `local`: 本地模式 - 专注于上下文相关信息，适合精确查询
    - `global`: 全局模式 - 利用全局知识，适合概念性查询
    - `hybrid`: 混合模式 - 结合本地和全局检索，推荐使用
    - `naive`: 朴素模式 - 基本搜索，不使用高级技术
    - `mix`: 混合模式 - 整合知识图谱和向量检索
    - `bypass`: 绕过模式 - 直接返回结果，用于测试

    **高级参数：**
    - `top_k`: 返回结果数量，影响查询精度和响应时间
    - `stream`: 流式返回，适合长文本生成
    - `max_entity_tokens`: 实体token限制，控制知识图谱使用
    - `max_relation_tokens`: 关系token限制，控制关系推理
    - `max_total_tokens`: 总token限制，控制响应长度
    - `enable_rerank`: 启用重排序，提高结果相关性

    **特殊功能：**
    - `only_need_context`: 仅返回检索上下文，不生成回答
    - `only_need_prompt`: 仅返回构建的提示，用于调试
    - `hl_keywords`: 高级关键词，增强检索精度
    - `ll_keywords`: 低级关键词，扩展检索范围
    - `conversation_history`: 对话历史，支持多轮对话

    **使用场景：**
    - 智能问答系统
    - 文档检索和总结
    - 知识发现和推理
    - 多轮对话支持
    - 专业领域查询
    """,
    responses={
        200: {
            "description": "查询执行成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "result": "根据知识库内容，这是查询的详细回答...",
                            "mode": "hybrid",
                            "query": "什么是人工智能？",
                            "knowledge_base": "ai_kb",
                            "language": "中文"
                        }
                    }
                }
            }
        },
        400: {
            "description": "查询参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询内容不能为空或模式不支持"
                    }
                }
            }
        },
        404: {
            "description": "知识库不存在",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "指定的知识库不存在"
                    }
                }
            }
        },
        500: {
            "description": "查询处理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询失败: 模型服务不可用"
                    }
                }
            }
        }
    }
)
async def query(request: QueryRequest):
    """执行智能知识查询"""
    try:
        # 构建查询参数
        query_kwargs = {}
        if request.max_entity_tokens is not None:
            query_kwargs["max_entity_tokens"] = request.max_entity_tokens
        if request.max_relation_tokens is not None:
            query_kwargs["max_relation_tokens"] = request.max_relation_tokens
        if request.max_total_tokens is not None:
            query_kwargs["max_total_tokens"] = request.max_total_tokens
        if request.hl_keywords:
            query_kwargs["hl_keywords"] = request.hl_keywords
        if request.ll_keywords:
            query_kwargs["ll_keywords"] = request.ll_keywords
        if request.conversation_history:
            query_kwargs["conversation_history"] = request.conversation_history
        if request.user_prompt:
            query_kwargs["user_prompt"] = request.user_prompt

        query_kwargs.update({
            "only_need_context": request.only_need_context,
            "only_need_prompt": request.only_need_prompt,
            "response_type": request.response_type,
            "enable_rerank": request.enable_rerank
        })

        # 处理知识库路径
        working_dir = None
        if request.knowledge_base:
            working_dir = f"./knowledgeBase/{request.knowledge_base}"

        result = await guixiaoxirag_service.query(
            query=request.query,
            mode=request.mode,
            top_k=request.top_k,
            stream=request.stream,
            working_dir=working_dir,
            language=request.language,
            **query_kwargs
        )

        kb_name = request.knowledge_base or "default"
        lang = request.language or "中文"
        return BaseResponse(
            data=QueryResponse(
                result=result,
                mode=request.mode,
                query=request.query,
                knowledge_base=kb_name,
                language=lang
            )
        )
    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/query/modes",
    response_model=BaseResponse,
    tags=["查询"],
    summary="获取查询模式列表",
    description="""
    获取系统支持的所有查询模式及其详细说明。

    **查询模式详解：**

    **1. local（本地模式）**
    - 专注于查询相关的局部上下文
    - 适合精确、具体的问题
    - 响应速度快，资源消耗低
    - 推荐用于事实性查询

    **2. global（全局模式）**
    - 利用整个知识库的全局信息
    - 适合概念性、总结性问题
    - 能够发现远距离关联
    - 推荐用于分析性查询

    **3. hybrid（混合模式）**
    - 结合本地和全局检索优势
    - 平衡精确性和全面性
    - 系统默认推荐模式
    - 适合大多数查询场景

    **4. naive（朴素模式）**
    - 基础的关键词匹配搜索
    - 不使用高级AI技术
    - 响应最快，适合简单查询
    - 用于基准测试和对比

    **5. mix（混合模式）**
    - 深度整合知识图谱和向量检索
    - 最强的推理和关联能力
    - 适合复杂的多步推理
    - 资源消耗较高

    **6. bypass（绕过模式）**
    - 直接返回预设结果
    - 主要用于系统测试
    - 不进行实际查询处理

    **选择建议：**
    - 日常使用：hybrid
    - 精确查询：local
    - 深度分析：mix
    - 快速测试：naive
    """,
    responses={
        200: {
            "description": "查询模式列表获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "modes": {
                                "local": "本地模式 - 专注于上下文相关信息",
                                "global": "全局模式 - 利用全局知识",
                                "hybrid": "混合模式 - 结合本地和全局检索方法",
                                "naive": "朴素模式 - 执行基本搜索，不使用高级技术",
                                "mix": "混合模式 - 整合知识图谱和向量检索",
                                "bypass": "绕过模式 - 直接返回结果"
                            },
                            "default": "hybrid",
                            "recommended": ["hybrid", "mix", "local"]
                        }
                    }
                }
            }
        }
    }
)
async def get_query_modes():
    """获取支持的查询模式列表"""
    modes = {
        "local": "本地模式 - 专注于上下文相关信息",
        "global": "全局模式 - 利用全局知识",
        "hybrid": "混合模式 - 结合本地和全局检索方法",
        "naive": "朴素模式 - 执行基本搜索，不使用高级技术",
        "mix": "混合模式 - 整合知识图谱和向量检索",
        "bypass": "绕过模式 - 直接返回结果"
    }

    return BaseResponse(
        data={
            "modes": modes,
            "default": "hybrid",
            "recommended": ["hybrid", "mix", "local"]
        }
    )


@app.post(
    "/query/batch",
    response_model=BaseResponse,
    tags=["查询"],
    summary="批量查询处理",
    description="""
    一次性处理多个查询请求，提高查询效率和系统吞吐量。

    **功能特性：**
    - 支持同时处理多个查询
    - 统一的查询模式和参数设置
    - 并行处理提高效率
    - 批量结果统一返回
    - 自动错误处理和重试

    **参数说明：**
    - `queries`: 必填，查询文本列表
    - `mode`: 可选，统一的查询模式（默认hybrid）
    - `top_k`: 可选，每个查询返回的结果数量

    **使用场景：**
    - 批量问答处理
    - 数据分析和报告生成
    - 系统性能测试
    - 多问题并行处理
    - API调用优化

    **性能优化：**
    - 建议单次批量不超过50个查询
    - 复杂查询建议减少批量大小
    - 支持异步并行处理
    - 自动负载均衡

    **注意事项：**
    - 所有查询使用相同的模式和参数
    - 单个查询失败不影响其他查询
    - 返回结果保持原始顺序
    - 超时查询会被跳过
    """,
    responses={
        200: {
            "description": "批量查询处理成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "results": [
                                {
                                    "query": "什么是人工智能？",
                                    "result": "人工智能是...",
                                    "mode": "hybrid"
                                },
                                {
                                    "query": "机器学习的应用？",
                                    "result": "机器学习应用于...",
                                    "mode": "hybrid"
                                }
                            ],
                            "total_queries": 2,
                            "mode": "hybrid"
                        }
                    }
                }
            }
        },
        400: {
            "description": "批量查询参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "查询列表不能为空或超过限制"
                    }
                }
            }
        },
        500: {
            "description": "批量查询处理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "批量查询失败: 服务器负载过高"
                    }
                }
            }
        }
    }
)
async def batch_query(queries: List[str], mode: str = "hybrid", top_k: int = 20):
    """批量查询处理接口"""
    try:
        results = []
        for query_text in queries:
            result = await guixiaoxirag_service.query(
                query=query_text,
                mode=mode,
                top_k=top_k
            )
            results.append({
                "query": query_text,
                "result": result,
                "mode": mode
            })

        return BaseResponse(
            data={
                "results": results,
                "total_queries": len(queries),
                "mode": mode
            }
        )
    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/insert/files",
    response_model=BaseResponse,
    tags=["文档管理"],
    summary="批量上传并插入文件",
    description="""
    批量上传多个文件并将其内容插入到知识库中，提高文件处理效率。

    **批量处理特性：**
    - 支持同时上传多个文件
    - 并行文件内容提取
    - 统一的批量插入处理
    - 原子性操作保证
    - 详细的处理结果反馈

    **支持的文件类型：**
    - 文档：PDF, DOCX, DOC, TXT, MD
    - 代码：PY, JS, JAVA, CPP, C, H
    - 数据：JSON, XML, CSV
    - 其他：RTF, ODT等

    **处理流程：**
    1. 验证所有文件格式和大小
    2. 并行提取文件内容
    3. 统一进行文本预处理
    4. 批量向量化和图谱构建
    5. 返回详细处理结果

    **使用场景：**
    - 文档库批量导入
    - 项目文件整体上传
    - 数据迁移和同步
    - 知识库快速构建

    **性能优化：**
    - 建议单次上传不超过20个文件
    - 大文件建议分批处理
    - 支持断点续传（规划中）
    - 自动负载均衡
    """,
    responses={
        200: {
            "description": "批量文件上传成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "track_id": "batch_files_123456",
                            "files": [
                                {
                                    "filename": "document1.pdf",
                                    "file_path": "/uploads/document1.pdf",
                                    "file_size": 1024000
                                },
                                {
                                    "filename": "document2.docx",
                                    "file_path": "/uploads/document2.docx",
                                    "file_size": 512000
                                }
                            ],
                            "total_files": 2
                        }
                    }
                }
            }
        },
        400: {
            "description": "文件格式或大小错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "部分文件格式不支持或超过大小限制"
                    }
                }
            }
        },
        413: {
            "description": "文件总大小超限",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "批量文件总大小超过限制"
                    }
                }
            }
        },
        500: {
            "description": "批量文件处理失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "批量文件上传插入失败: 处理超时"
                    }
                }
            }
        }
    }
)
async def insert_files(files: List[UploadFile] = File(...)):
    """批量上传并插入文件到知识库"""
    try:
        results = []
        texts = []
        file_paths = []

        for file in files:
            # 处理每个上传的文件
            file_info = await process_uploaded_file(file)
            texts.append(file_info["content"])
            file_paths.append(file_info["file_path"])
            results.append({
                "filename": file_info["filename"],
                "file_path": file_info["file_path"],
                "file_size": file_info["file_size"]
            })

        # 批量插入文本内容
        track_id = await guixiaoxirag_service.insert_texts(
            texts=texts,
            file_paths=file_paths
        )

        return BaseResponse(
            data={
                "track_id": track_id,
                "files": results,
                "total_files": len(files)
            }
        )
    except Exception as e:
        logger.error(f"批量文件上传插入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/insert/directory", response_model=BaseResponse, tags=["文档管理"])
async def insert_directory(request: DirectoryInsertRequest):
    """从指定目录插入所有支持的文件到指定知识库"""
    try:
        from .utils import get_file_contents

        # 获取目录中的所有文件内容
        contents = get_file_contents(request.directory_path)

        if not contents:
            raise HTTPException(
                status_code=404,
                detail=f"目录 {request.directory_path} 中没有找到支持的文件"
            )

        # 处理知识库路径
        working_dir = None
        if request.knowledge_base:
            working_dir = f"./knowledgeBase/{request.knowledge_base}"

        # 批量插入内容
        track_id = await guixiaoxirag_service.insert_texts(
            texts=contents,
            working_dir=working_dir,
            language=request.language
        )

        kb_name = request.knowledge_base or "default"
        lang = request.language or "中文"
        return BaseResponse(
            data={
                "track_id": track_id,
                "directory": request.directory_path,
                "file_count": len(contents),
                "knowledge_base": kb_name,
                "language": lang
            }
        )
    except Exception as e:
        logger.error(f"目录文件插入失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 知识图谱API
@app.post(
    "/knowledge-graph",
    response_model=BaseResponse,
    tags=["知识图谱"],
    summary="获取知识图谱数据",
    description="""
    根据指定节点标签获取相关的知识图谱数据，支持深度和节点数量控制。

    **功能特性：**
    - 基于节点标签的图谱检索
    - 可控制的遍历深度
    - 节点数量限制防止过载
    - 完整的节点和边信息
    - 支持图谱可视化数据格式

    **参数说明：**
    - `node_label`: 必填，起始节点的标签或实体名称
    - `max_depth`: 可选，最大遍历深度（默认3层）
    - `max_nodes`: 可选，最大返回节点数量（防止图谱过大）

    **返回数据结构：**
    - `nodes`: 节点列表，包含ID、标签和属性
    - `edges`: 边列表，包含源节点、目标节点、关系标签和属性
    - `node_count`: 节点总数
    - `edge_count`: 边总数

    **使用场景：**
    - 知识图谱可视化
    - 实体关系分析
    - 知识发现和探索
    - 图谱数据导出
    - 关系网络分析

    **性能建议：**
    - 大型图谱建议设置max_nodes限制
    - 深度遍历会增加计算时间
    - 可以分批获取大型图谱数据
    - 建议先查看图谱统计信息

    **数据格式：**
    - 节点包含实体类型、属性等元数据
    - 边包含关系描述、权重等信息
    - 支持多种图谱可视化工具格式
    """,
    responses={
        200: {
            "description": "知识图谱数据获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "nodes": [
                                {
                                    "id": "entity_1",
                                    "label": "Person",
                                    "properties": {
                                        "entity_type": "Person",
                                        "name": "张三",
                                        "description": "软件工程师"
                                    }
                                }
                            ],
                            "edges": [
                                {
                                    "source": "entity_1",
                                    "target": "entity_2",
                                    "label": "works_at",
                                    "properties": {
                                        "description": "在...工作",
                                        "weight": 0.8
                                    }
                                }
                            ],
                            "node_count": 10,
                            "edge_count": 15
                        }
                    }
                }
            }
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "节点标签不能为空或格式错误"
                    }
                }
            }
        },
        404: {
            "description": "节点不存在",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "指定的节点标签在知识图谱中不存在"
                    }
                }
            }
        },
        500: {
            "description": "知识图谱获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取知识图谱失败: 图数据库连接错误"
                    }
                }
            }
        }
    }
)
async def get_knowledge_graph(request: KnowledgeGraphRequest):
    """获取知识图谱数据"""
    try:
        kg = await guixiaoxirag_service.get_knowledge_graph(
            node_label=request.node_label,
            max_depth=request.max_depth,
            max_nodes=request.max_nodes
        )

        # 转换为响应格式
        nodes = [
            GraphNode(
                id=node_id,
                label=node_data.get("entity_type", "Unknown"),
                properties=node_data
            )
            for node_id, node_data in kg.nodes.items()
        ]

        edges = [
            GraphEdge(
                source=edge[0],
                target=edge[1],
                label=edge_data.get("description", ""),
                properties=edge_data
            )
            for edge, edge_data in kg.edges.items()
        ]

        return BaseResponse(
            data=KnowledgeGraphResponse(
                nodes=nodes,
                edges=edges,
                node_count=len(nodes),
                edge_count=len(edges)
            )
        )
    except Exception as e:
        logger.error(f"获取知识图谱失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/knowledge-graph/stats",
    response_model=BaseResponse,
    tags=["知识图谱"],
    summary="获取知识图谱统计信息",
    description="""
    获取当前知识库中知识图谱的详细统计信息和元数据。

    **统计信息包括：**
    - 节点总数：图谱中所有实体的数量
    - 边总数：图谱中所有关系的数量
    - 工作目录：当前知识库路径
    - 图谱类型：底层图数据库类型
    - 存储信息：数据存储相关统计

    **功能用途：**
    - 监控知识图谱规模
    - 评估系统性能需求
    - 数据质量分析
    - 容量规划参考
    - 系统健康检查

    **使用场景：**
    - 系统管理和监控
    - 性能优化决策
    - 数据分析报告
    - 容量规划
    - 故障诊断

    **返回信息：**
    - 实时统计数据
    - 图谱结构信息
    - 存储配置详情
    - 系统状态指标
    """,
    responses={
        200: {
            "description": "知识图谱统计信息获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "total_nodes": 1500,
                            "total_edges": 3200,
                            "working_dir": "./knowledgeBase/default",
                            "graph_type": "NetworkXStorage",
                            "last_updated": "2024-01-01T12:00:00",
                            "storage_size_mb": 25.6
                        }
                    }
                }
            }
        },
        500: {
            "description": "统计信息获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取知识图谱统计失败: 图数据库未初始化"
                    }
                }
            }
        }
    }
)
async def get_knowledge_graph_stats():
    """获取知识图谱统计信息"""
    try:
        if not guixiaoxirag_service._initialized:
            await guixiaoxirag_service.initialize()

        # 获取图谱统计信息
        graph = guixiaoxirag_service.rag.chunk_entity_relation_graph

        # 获取节点和边的数量
        node_count = await graph.node_count() if hasattr(graph, 'node_count') else 0
        edge_count = await graph.edge_count() if hasattr(graph, 'edge_count') else 0

        stats = {
            "total_nodes": node_count,
            "total_edges": edge_count,
            "working_dir": settings.working_dir,
            "graph_type": type(graph).__name__
        }

        return BaseResponse(data=stats)
    except Exception as e:
        logger.error(f"获取知识图谱统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete(
    "/knowledge-graph/clear",
    response_model=BaseResponse,
    tags=["知识图谱"],
    summary="清空知识图谱数据",
    description="""
    清空当前知识库中的所有知识图谱数据，包括节点和边信息。

    **⚠️ 危险操作警告：**
    - 此操作将永久删除所有图谱数据
    - 操作不可逆，请谨慎使用
    - 建议在操作前备份重要数据
    - 不会影响原始文档数据

    **清空范围：**
    - 所有实体节点
    - 所有关系边
    - 图谱索引数据
    - 相关缓存信息

    **保留内容：**
    - 原始文档内容
    - 向量嵌入数据
    - 系统配置信息
    - 知识库结构

    **使用场景：**
    - 重新构建知识图谱
    - 清理错误数据
    - 系统重置
    - 测试环境清理
    - 数据迁移准备

    **操作后果：**
    - 图谱查询将返回空结果
    - 需要重新插入数据来重建图谱
    - 基于图谱的查询模式将受影响
    - 向量检索功能不受影响

    **恢复方法：**
    - 重新插入原始文档
    - 从备份恢复数据
    - 重新运行数据处理流程
    """,
    responses={
        200: {
            "description": "知识图谱清空成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "知识图谱已清空",
                        "data": {
                            "status": "cleared",
                            "timestamp": "2024-01-01T12:00:00",
                            "affected_nodes": 1500,
                            "affected_edges": 3200
                        }
                    }
                }
            }
        },
        403: {
            "description": "操作权限不足",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "清空知识图谱需要管理员权限"
                    }
                }
            }
        },
        500: {
            "description": "清空操作失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "清空知识图谱失败: 数据库锁定中"
                    }
                }
            }
        }
    }
)
async def clear_knowledge_graph():
    """清空知识图谱数据"""
    try:
        if not guixiaoxirag_service._initialized:
            await guixiaoxirag_service.initialize()

        # 清空图谱数据
        await guixiaoxirag_service.rag.chunk_entity_relation_graph.drop()

        return BaseResponse(
            message="知识图谱已清空",
            data={"status": "cleared"}
        )
    except Exception as e:
        logger.error(f"清空知识图谱失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 系统管理API
@app.post(
    "/system/reset",
    response_model=BaseResponse,
    tags=["系统管理"],
    summary="系统重置",
    description="""
    重置整个系统，清空所有数据并重新初始化服务。

    **⚠️ 危险操作警告：**
    - 此操作将清空所有系统数据
    - 包括知识图谱、向量数据、缓存等
    - 操作不可逆，请谨慎使用
    - 建议在操作前备份重要数据

    **重置范围：**
    - 所有知识库数据
    - 知识图谱和向量索引
    - 系统缓存和临时文件
    - 服务实例状态

    **保留内容：**
    - 系统配置文件
    - 日志文件
    - 上传的原始文件（可选）

    **重置流程：**
    1. 停止所有正在进行的操作
    2. 清理内存中的数据结构
    3. 删除存储的数据文件
    4. 重新初始化服务组件
    5. 恢复系统到初始状态

    **使用场景：**
    - 系统故障恢复
    - 开发测试环境重置
    - 数据迁移前清理
    - 性能问题排查
    - 配置更改后重启

    **操作后果：**
    - 所有查询将返回空结果
    - 需要重新导入数据
    - 系统恢复到初始状态
    - 所有缓存被清空

    **恢复建议：**
    - 重新导入备份数据
    - 重新配置知识库
    - 验证系统功能正常
    """,
    responses={
        200: {
            "description": "系统重置成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "系统已重置",
                        "data": {
                            "status": "reset",
                            "initialized": True,
                            "timestamp": "2024-01-01T12:00:00",
                            "reset_duration_seconds": 5.2
                        }
                    }
                }
            }
        },
        403: {
            "description": "操作权限不足",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "系统重置需要管理员权限"
                    }
                }
            }
        },
        500: {
            "description": "系统重置失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "系统重置失败: 服务正在处理其他请求"
                    }
                }
            }
        }
    }
)
async def reset_system():
    """重置系统（清空所有数据）"""
    try:
        if guixiaoxirag_service._initialized:
            await guixiaoxirag_service.finalize()

        # 重新初始化
        await guixiaoxirag_service.initialize()

        return BaseResponse(
            message="系统已重置",
            data={"status": "reset", "initialized": True}
        )
    except Exception as e:
        logger.error(f"系统重置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/system/status",
    response_model=BaseResponse,
    tags=["系统管理"],
    summary="获取系统详细状态",
    description="""
    获取系统的详细运行状态和配置信息，用于监控和诊断。

    **状态信息包括：**

    **基本信息：**
    - 服务名称和版本
    - 初始化状态
    - 当前工作目录
    - 系统运行时间

    **配置信息：**
    - 嵌入向量维度
    - 最大token大小
    - OpenAI模型配置
    - 系统参数设置

    **运行状态：**
    - 服务健康状态
    - 内存使用情况
    - 活跃连接数
    - 处理队列状态

    **性能指标：**
    - 请求处理统计
    - 响应时间分析
    - 错误率统计
    - 资源使用率

    **使用场景：**
    - 系统监控和告警
    - 性能分析和优化
    - 故障诊断和排查
    - 容量规划参考
    - 健康检查自动化

    **监控建议：**
    - 定期检查系统状态
    - 监控关键性能指标
    - 设置异常告警阈值
    - 记录状态变化趋势
    """,
    responses={
        200: {
            "description": "系统状态获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "service_name": "GuiXiaoXiRag API",
                            "version": "1.0.0",
                            "initialized": True,
                            "working_dir": "./knowledgeBase/default",
                            "uptime": 3600.5,
                            "config": {
                                "embedding_dim": 1536,
                                "max_token_size": 8192,
                                "openai_chat_model": "gpt-3.5-turbo",
                                "openai_embedding_model": "text-embedding-ada-002"
                            },
                            "performance": {
                                "total_requests": 1250,
                                "avg_response_time": 0.85,
                                "error_rate": 0.02
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "状态获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取系统状态失败: 内部服务错误"
                    }
                }
            }
        }
    }
)
async def get_system_status():
    """获取系统详细状态信息"""
    try:
        status_info = {
            "service_name": settings.app_name,
            "version": settings.app_version,
            "initialized": guixiaoxirag_service._initialized,
            "working_dir": settings.working_dir,
            "uptime": time.time() - start_time,
            "config": {
                "embedding_dim": settings.embedding_dim,
                "max_token_size": settings.max_token_size,
                "openai_chat_model": settings.openai_chat_model,
                "openai_embedding_model": settings.openai_embedding_model
            }
        }

        return BaseResponse(data=status_info)
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/metrics",
    response_model=BaseResponse,
    tags=["监控"],
    summary="获取系统性能指标",
    description="""
    获取系统的详细性能指标和监控数据，用于性能分析和系统优化。

    **性能指标包括：**

    **请求统计：**
    - 总请求数量
    - 成功/失败请求数
    - 平均响应时间
    - 请求频率分析

    **资源使用：**
    - CPU使用率
    - 内存使用情况
    - 磁盘I/O统计
    - 网络流量统计

    **服务性能：**
    - 查询处理时间
    - 向量检索性能
    - 知识图谱查询效率
    - 缓存命中率

    **错误统计：**
    - 错误类型分布
    - 错误发生频率
    - 异常堆栈统计
    - 超时请求统计

    **使用场景：**
    - 性能监控和告警
    - 系统优化决策
    - 容量规划分析
    - 故障诊断支持
    - SLA监控报告

    **监控建议：**
    - 定期收集性能数据
    - 设置关键指标阈值
    - 建立性能基线
    - 监控趋势变化
    """,
    responses={
        200: {
            "description": "性能指标获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "requests": {
                                "total": 1250,
                                "success": 1225,
                                "failed": 25,
                                "avg_response_time": 0.85,
                                "requests_per_minute": 15.2
                            },
                            "resources": {
                                "cpu_usage": 45.6,
                                "memory_usage": 68.3,
                                "disk_usage": 23.1,
                                "network_io": 1024000
                            },
                            "performance": {
                                "query_avg_time": 1.2,
                                "vector_search_time": 0.3,
                                "graph_query_time": 0.8,
                                "cache_hit_rate": 0.75
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "性能指标获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取系统指标失败: 监控服务不可用"
                    }
                }
            }
        }
    }
)
async def get_system_metrics():
    """获取系统性能指标"""
    try:
        metrics = get_metrics()
        return BaseResponse(data=metrics)
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs", response_model=BaseResponse, tags=["监控"])
async def get_recent_logs(lines: int = 100):
    """获取最近的日志"""
    try:
        import os
        log_file = os.path.join(settings.log_dir, "guixiaoxirag_service.log")

        if not os.path.exists(log_file):
            return BaseResponse(data={"logs": [], "message": "日志文件不存在"})

        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return BaseResponse(data={
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(recent_lines),
            "log_file": log_file
        })
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 性能优化API
@app.post("/performance/optimize", response_model=BaseResponse, tags=["性能优化"])
async def optimize_performance(mode: str = "basic"):
    """应用性能优化配置"""
    try:
        valid_modes = ["basic", "high_performance", "fast_test"]
        if mode not in valid_modes:
            raise HTTPException(
                status_code=400,
                detail=f"无效的模式。支持的模式: {valid_modes}"
            )

        config = PerformanceConfig.apply_config(mode)

        return BaseResponse(
            message=f"性能配置已应用: {mode}",
            data={
                "mode": mode,
                "config": config,
                "restart_required": True
            }
        )
    except Exception as e:
        logger.error(f"应用性能配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/performance/configs", response_model=BaseResponse, tags=["性能优化"])
async def get_performance_configs():
    """获取所有性能配置选项"""
    try:
        configs = {
            "basic": PerformanceConfig.get_config("basic"),
            "high_performance": PerformanceConfig.get_config("high_performance"),
            "fast_test": PerformanceConfig.get_config("fast_test"),
        }

        return BaseResponse(data={
            "configs": configs,
            "current_settings": {
                "embedding_dim": settings.embedding_dim,
                "max_token_size": settings.max_token_size,
            }
        })
    except Exception as e:
        logger.error(f"获取性能配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/optimized", response_model=BaseResponse, tags=["查询"])
async def optimized_query(
    request: dict
):
    """使用优化参数的查询"""
    try:
        query = request.get("query")
        mode = request.get("mode", "hybrid")
        performance_level = request.get("performance_level", "balanced")

        if not query:
            raise HTTPException(status_code=400, detail="查询内容不能为空")

        # 获取优化的查询参数
        optimized_params = get_optimized_query_params(mode, performance_level)

        result = await guixiaoxirag_service.query(
            query=query,
            mode=mode,
            **optimized_params
        )

        return BaseResponse(
            data={
                "result": result,
                "mode": mode,
                "performance_level": performance_level,
                "query": query,
                "optimized_params": optimized_params
            }
        )
    except Exception as e:
        logger.error(f"优化查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 知识库管理API
@app.get(
    "/knowledge-bases",
    response_model=BaseResponse,
    tags=["知识库管理"],
    summary="列出所有知识库",
    description="""
    获取系统中所有可用知识库的列表和详细信息。

    **返回信息包括：**
    - 知识库名称和路径
    - 创建时间和最后更新时间
    - 文档数量和节点统计
    - 存储大小和状态信息
    - 当前活跃的知识库

    **知识库信息：**
    - `name`: 知识库名称
    - `path`: 存储路径
    - `created_at`: 创建时间
    - `document_count`: 文档数量
    - `node_count`: 图谱节点数
    - `edge_count`: 图谱边数
    - `size_mb`: 存储大小（MB）

    **使用场景：**
    - 知识库管理界面
    - 系统资源监控
    - 数据迁移规划
    - 用户权限管理
    - 容量分析报告

    **管理功能：**
    - 查看知识库概览
    - 选择切换目标
    - 监控存储使用
    - 评估数据质量
    """,
    responses={
        200: {
            "description": "知识库列表获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "knowledge_bases": [
                                {
                                    "name": "default",
                                    "path": "./knowledgeBase/default",
                                    "created_at": "2024-01-01T10:00:00",
                                    "document_count": 150,
                                    "node_count": 1200,
                                    "edge_count": 2800,
                                    "size_mb": 45.6
                                },
                                {
                                    "name": "ai_research",
                                    "path": "./knowledgeBase/ai_research",
                                    "created_at": "2024-01-02T14:30:00",
                                    "document_count": 89,
                                    "node_count": 750,
                                    "edge_count": 1650,
                                    "size_mb": 28.3
                                }
                            ],
                            "current": "default",
                            "total": 2
                        }
                    }
                }
            }
        },
        500: {
            "description": "知识库列表获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "列出知识库失败: 文件系统访问错误"
                    }
                }
            }
        }
    }
)
async def list_knowledge_bases():
    """列出所有知识库"""
    try:
        knowledge_bases = kb_manager.list_knowledge_bases()
        return BaseResponse(data={
            "knowledge_bases": knowledge_bases,
            "current": kb_manager.current_kb,
            "total": len(knowledge_bases)
        })
    except Exception as e:
        logger.error(f"列出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/knowledge-bases",
    response_model=BaseResponse,
    tags=["知识库管理"],
    summary="创建新知识库",
    description="""
    创建一个新的知识库，用于存储和管理特定领域的知识数据。

    **创建流程：**
    1. 验证知识库名称的唯一性
    2. 创建知识库目录结构
    3. 初始化存储组件
    4. 设置默认配置
    5. 返回创建结果

    **命名规则：**
    - 只能包含字母、数字、下划线和连字符
    - 长度限制：3-50个字符
    - 不能与现有知识库重名
    - 不能使用系统保留名称

    **目录结构：**
    - 向量存储目录
    - 知识图谱数据目录
    - 配置文件目录
    - 日志和缓存目录

    **使用场景：**
    - 多租户数据隔离
    - 不同项目的知识管理
    - 领域专业知识库
    - 测试和开发环境
    - 数据分类存储

    **注意事项：**
    - 创建后需要导入数据才能使用
    - 建议设置有意义的描述信息
    - 考虑存储空间和性能需求
    - 规划好知识库的用途和范围
    """,
    responses={
        200: {
            "description": "知识库创建成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "知识库 'ai_research' 创建成功",
                        "data": {
                            "name": "ai_research",
                            "path": "./knowledgeBase/ai_research",
                            "created_at": "2024-01-01T12:00:00",
                            "description": "人工智能研究知识库",
                            "document_count": 0,
                            "node_count": 0,
                            "edge_count": 0,
                            "size_mb": 0.0
                        }
                    }
                }
            }
        },
        400: {
            "description": "创建参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "知识库名称已存在或格式不正确"
                    }
                }
            }
        },
        500: {
            "description": "知识库创建失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "创建知识库失败: 磁盘空间不足"
                    }
                }
            }
        }
    }
)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """创建新的知识库"""
    try:
        kb_info = kb_manager.create_knowledge_base(
            name=request.name,
            description=request.description
        )
        return BaseResponse(
            message=f"知识库 '{request.name}' 创建成功",
            data=kb_info
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge-bases/{name}", response_model=BaseResponse, tags=["知识库管理"])
async def delete_knowledge_base(name: str):
    """删除知识库"""
    try:
        kb_manager.delete_knowledge_base(name)
        return BaseResponse(message=f"知识库 '{name}' 删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"删除知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge-bases/switch", response_model=BaseResponse, tags=["知识库管理"])
async def switch_knowledge_base(request: SwitchKnowledgeBaseRequest):
    """切换当前知识库"""
    try:
        kb_path = kb_manager.switch_knowledge_base(request.name)

        # 重新初始化GuiXiaoXiRag服务
        await guixiaoxirag_service.finalize()
        await guixiaoxirag_service.initialize(working_dir=kb_path)

        return BaseResponse(
            message=f"已切换到知识库 '{request.name}'",
            data={
                "current_kb": request.name,
                "kb_path": kb_path,
                "service_reinitialized": True
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"切换知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-bases/{name}/export", response_model=BaseResponse, tags=["知识库管理"])
async def export_knowledge_base(name: str, format: str = "json"):
    """导出知识库"""
    try:
        export_data = kb_manager.export_knowledge_base(name, format)
        return BaseResponse(
            message=f"知识库 '{name}' 导出成功",
            data=export_data
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 语言管理API
@app.get(
    "/languages",
    response_model=BaseResponse,
    tags=["语言管理"],
    summary="获取支持的语言列表",
    description="""
    获取系统支持的所有语言选项和当前语言设置。

    **支持的语言：**
    - 中文：中文、Chinese、zh、zh-CN
    - 英文：英文、English、en、en-US

    **语言功能：**
    - 查询结果语言控制
    - 文档处理语言识别
    - 系统提示语言适配
    - 多语言知识库支持

    **语言设置影响：**
    - 查询回答的语言
    - 实体识别和关系抽取
    - 知识图谱构建
    - 错误信息显示

    **使用场景：**
    - 多语言应用支持
    - 国际化配置
    - 用户偏好设置
    - 语言切换功能

    **配置建议：**
    - 根据主要用户群体选择默认语言
    - 支持动态语言切换
    - 考虑文档内容的主要语言
    - 保持语言设置的一致性
    """,
    responses={
        200: {
            "description": "语言列表获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "current_language": "中文",
                            "supported_languages": [
                                "中文", "英文", "English", "Chinese",
                                "zh", "en", "zh-CN", "en-US"
                            ]
                        }
                    }
                }
            }
        },
        500: {
            "description": "语言列表获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取语言列表失败: 配置文件读取错误"
                    }
                }
            }
        }
    }
)
async def get_supported_languages():
    """获取支持的语言列表"""
    try:
        languages = guixiaoxirag_service.get_supported_languages()
        current_config = guixiaoxirag_service.get_current_config()

        return BaseResponse(
            data=LanguageResponse(
                current_language=current_config["language"],
                supported_languages=languages
            )
        )
    except Exception as e:
        logger.error(f"获取语言列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/languages/set",
    response_model=BaseResponse,
    tags=["语言管理"],
    summary="设置默认回答语言",
    description="""
    设置系统的默认回答语言，影响所有后续的查询和响应。

    **语言设置功能：**
    - 控制查询回答的语言
    - 影响系统提示和错误信息
    - 调整文本处理算法
    - 优化多语言知识库检索

    **支持的语言标识：**
    - 中文：中文、Chinese、zh、zh-CN
    - 英文：英文、English、en、en-US

    **设置影响范围：**
    - 新的查询请求
    - 系统生成的回答
    - 错误和状态信息
    - 知识图谱实体识别

    **语言处理特性：**
    - 自动语言检测
    - 跨语言知识检索
    - 多语言实体对齐
    - 语言特定的优化

    **使用场景：**
    - 用户偏好设置
    - 多语言应用切换
    - 国际化部署
    - 语言特定优化

    **注意事项：**
    - 设置立即生效
    - 不影响已存储的数据
    - 建议重启服务以获得最佳效果
    - 某些功能可能需要对应语言的模型支持
    """,
    responses={
        200: {
            "description": "语言设置成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "语言已设置为: 中文",
                        "data": {
                            "language": "中文",
                            "previous_language": "英文",
                            "effective_immediately": True
                        }
                    }
                }
            }
        },
        400: {
            "description": "语言设置失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "不支持的语言类型或语言设置失败"
                    }
                }
            }
        },
        500: {
            "description": "语言设置错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "设置语言失败: 配置更新错误"
                    }
                }
            }
        }
    }
)
async def set_language(request: LanguageRequest):
    """设置默认回答语言"""
    try:
        success = guixiaoxirag_service.set_language(request.language)
        if success:
            return BaseResponse(
                message=f"语言已设置为: {request.language}",
                data={"language": request.language}
            )
        else:
            raise HTTPException(status_code=400, detail="语言设置失败")
    except Exception as e:
        logger.error(f"设置语言失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 服务配置API
@app.get(
    "/service/config",
    response_model=BaseResponse,
    tags=["服务管理"],
    summary="获取当前服务配置",
    description="""
    获取当前服务的详细配置信息，包括知识库、语言设置等。

    **配置信息包括：**
    - 当前工作目录路径
    - 活跃知识库名称
    - 默认语言设置
    - 服务初始化状态
    - 缓存实例数量

    **使用场景：**
    - 服务状态检查
    - 配置信息确认
    - 系统集成验证
    - 故障诊断支持
    - 管理界面显示

    **返回信息用途：**
    - 确认当前配置
    - 验证服务状态
    - 支持配置管理
    - 提供系统信息
    """,
    responses={
        200: {
            "description": "服务配置获取成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "操作成功",
                        "data": {
                            "working_dir": "./knowledgeBase/default",
                            "knowledge_base": "default",
                            "language": "中文",
                            "initialized": True,
                            "cached_instances": 2
                        }
                    }
                }
            }
        },
        500: {
            "description": "配置获取失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "获取服务配置失败: 配置文件读取错误"
                    }
                }
            }
        }
    }
)
async def get_service_config():
    """获取当前服务配置信息"""
    try:
        config = guixiaoxirag_service.get_current_config()
        kb_name = None
        if config["working_dir"]:
            from pathlib import Path
            kb_name = Path(config["working_dir"]).name

        return BaseResponse(
            data=ServiceConfigResponse(
                working_dir=config["working_dir"],
                knowledge_base=kb_name,
                language=config["language"],
                initialized=config["initialized"],
                cached_instances=config["cached_instances"]
            )
        )
    except Exception as e:
        logger.error(f"获取服务配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/service/switch-kb",
    response_model=BaseResponse,
    tags=["服务管理"],
    summary="切换服务知识库",
    description="""
    切换服务使用的知识库和语言设置，支持动态切换不同的知识库。

    **切换功能：**
    - 动态切换知识库
    - 同时设置语言偏好
    - 保持服务连续性
    - 自动重新初始化

    **切换流程：**
    1. 验证目标知识库存在
    2. 保存当前状态
    3. 清理旧的服务实例
    4. 初始化新的知识库
    5. 应用语言设置

    **参数说明：**
    - `knowledge_base`: 必填，目标知识库名称
    - `language`: 可选，语言设置

    **使用场景：**
    - 多租户环境切换
    - 不同项目间切换
    - 测试环境配置
    - 动态配置管理
    - 用户偏好应用

    **注意事项：**
    - 切换会中断当前操作
    - 建议在空闲时进行切换
    - 确保目标知识库已存在
    - 切换后需要重新验证功能
    """,
    responses={
        200: {
            "description": "知识库切换成功",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "已切换到知识库 'ai_research'",
                        "data": {
                            "knowledge_base": "ai_research",
                            "language": "中文",
                            "switch_time": "2024-01-01T12:00:00",
                            "previous_kb": "default"
                        }
                    }
                }
            }
        },
        400: {
            "description": "切换参数错误",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "知识库不存在或切换失败"
                    }
                }
            }
        },
        500: {
            "description": "知识库切换失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "切换知识库失败: 服务初始化错误"
                    }
                }
            }
        }
    }
)
async def switch_service_knowledge_base(request: KnowledgeBaseRequest):
    """切换服务使用的知识库和语言"""
    try:
        working_dir = f"./knowledgeBase/{request.knowledge_base}"
        success = await guixiaoxirag_service.switch_knowledge_base(
            working_dir=working_dir,
            language=request.language
        )

        if success:
            return BaseResponse(
                message=f"已切换到知识库 '{request.knowledge_base}'",
                data={
                    "knowledge_base": request.knowledge_base,
                    "language": request.language or guixiaoxirag_service._current_language
                }
            )
        else:
            raise HTTPException(status_code=400, detail="知识库切换失败")
    except Exception as e:
        logger.error(f"切换知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
