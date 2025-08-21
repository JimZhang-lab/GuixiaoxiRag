"""
知识库管理路由
处理知识库的创建、删除、切换、配置等功能
"""
from fastapi import APIRouter, HTTPException

from model import (
    BaseResponse, CreateKnowledgeBaseRequest, SwitchKnowledgeBaseRequest,
    KnowledgeBaseConfigRequest, KnowledgeBaseInfo, KnowledgeBaseListResponse
)
from api.knowledge_base_api import KnowledgeBaseAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["知识库管理"])

# 创建API处理器实例
kb_api = KnowledgeBaseAPI()


@router.get(
    "/knowledge-bases",
    response_model=BaseResponse,
    summary="获取知识库列表",
    description="""
    获取系统中所有可用知识库的完整列表和详细统计信息。

    **📚 返回信息：**
    - 📝 知识库名称、描述和元数据
    - 📅 创建时间和最后更新时间
    - 📊 文档数量和内容统计
    - 🕸️ 知识图谱节点和边数量
    - 💾 存储大小和磁盘使用情况
    - 🔄 当前状态和健康度
    - 🌐 支持的语言和配置信息
    - 🎯 使用频率和性能指标

    **📈 知识库状态：**
    - **ready**: 🟢 知识库就绪，可正常使用
    - **building**: 🟡 知识库正在构建或更新中
    - **incomplete**: 🟠 知识库数据不完整，部分功能受限
    - **error**: 🔴 知识库存在错误，需要修复
    - **maintenance**: 🔵 知识库正在维护中
    - **archived**: ⚫ 知识库已归档，只读状态

    **📋 返回数据结构：**
    - knowledge_bases: 知识库信息列表
    - total_count: 知识库总数
    - current_kb: 当前激活的知识库
    - storage_summary: 存储使用摘要
    - health_summary: 整体健康状态摘要

    **🎯 使用场景：**
    - 📊 知识库管理控制台
    - 🔄 知识库选择和切换界面
    - 📈 系统状态监控和报告
    - 🔍 知识库搜索和筛选
    - 📋 容量规划和资源管理

    **⚡ 性能特点：**
    - 支持分页查询大量知识库
    - 缓存机制提升响应速度
    - 异步加载详细统计信息
    """,
    responses={
        200: {
            "description": "成功获取知识库列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "成功获取知识库列表",
                        "data": {
                            "knowledge_bases": [
                                {
                                    "name": "ai_research",
                                    "description": "人工智能研究知识库",
                                    "status": "ready",
                                    "created_at": "2024-01-01T10:00:00Z",
                                    "updated_at": "2024-01-15T14:30:00Z",
                                    "document_count": 1250,
                                    "node_count": 5680,
                                    "edge_count": 12340,
                                    "storage_size": "2.5GB",
                                    "language": "中文",
                                    "is_current": True,
                                    "health_score": 0.95
                                },
                                {
                                    "name": "tech_docs",
                                    "description": "技术文档知识库",
                                    "status": "building",
                                    "created_at": "2024-01-10T09:00:00Z",
                                    "document_count": 850,
                                    "storage_size": "1.8GB",
                                    "language": "English",
                                    "is_current": False,
                                    "build_progress": 0.75
                                }
                            ],
                            "total_count": 2,
                            "current_kb": "ai_research",
                            "storage_summary": {
                                "total_size": "4.3GB",
                                "available_space": "45.7GB"
                            },
                            "health_summary": {
                                "healthy_count": 1,
                                "building_count": 1,
                                "error_count": 0
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "获取知识库列表失败",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "无法访问知识库目录"
                    }
                }
            }
        }
    }
)
async def list_knowledge_bases():
    """获取知识库列表"""
    return await kb_api.list_knowledge_bases()


@router.post(
    "/knowledge-bases",
    response_model=BaseResponse,
    summary="创建新知识库",
    description="""
    创建一个全新的知识库，包含完整的目录结构和配置文件。

    **🚀 创建流程：**
    1. 验证知识库名称和参数
    2. 创建知识库目录结构
    3. 初始化配置文件
    4. 设置向量数据库索引
    5. 创建知识图谱存储
    6. 生成初始元数据

    **📝 参数说明：**
    - **name**: 知识库名称（必填）
      - 长度：1-50个字符
      - 字符：字母、数字、下划线(_)、连字符(-)、中文
      - 不能与现有知识库重名
      - 不能使用系统保留名称（system、temp、cache等）
    - **description**: 知识库描述（可选，最多500字符）
    - **language**: 默认处理语言（可选，默认"中文"）
      - 支持：中文、English等
    - **config**: 自定义配置对象（可选）

    **⚙️ 高级配置选项：**
    - **chunk_size**: 文档分块大小（默认1024，范围256-4096）
    - **chunk_overlap**: 分块重叠大小（默认50，范围0-200）
    - **enable_auto_update**: 启用自动更新（默认true）
    - **vector_dimension**: 向量维度（默认1536）
    - **similarity_threshold**: 相似度阈值（默认0.7）
    - **max_documents**: 最大文档数限制（默认无限制）
    - **enable_knowledge_graph**: 启用知识图谱（默认true）
    - **enable_full_text_search**: 启用全文搜索（默认true）

    **📁 目录结构：**
    ```
    knowledge_base_name/
    ├── documents/          # 原始文档存储
    ├── vectors/           # 向量索引文件
    ├── knowledge_graph/   # 知识图谱数据
    ├── cache/            # 缓存文件
    ├── config.json       # 配置文件
    └── metadata.json     # 元数据文件
    ```

    **🎯 使用场景：**
    - 🏢 企业知识管理系统
    - 📚 学术研究项目
    - 🔬 专业领域知识库
    - 🤖 AI训练数据集
    - 📖 个人知识整理

    **💡 最佳实践：**
    - 使用描述性的知识库名称
    - 根据内容类型调整分块大小
    - 为不同语言创建独立知识库
    - 定期备份重要知识库
    """,
    responses={
        201: {
            "description": "知识库创建成功",
            "content": {
                "application/json": {
                    "examples": {
                        "basic_creation": {
                            "summary": "基础创建",
                            "value": {
                                "success": True,
                                "message": "知识库创建成功",
                                "data": {
                                    "name": "ai_research",
                                    "description": "人工智能研究知识库",
                                    "path": "/data/knowledge_bases/ai_research",
                                    "language": "中文",
                                    "status": "ready",
                                    "created_at": "2024-01-01T12:00:00Z",
                                    "config": {
                                        "chunk_size": 1024,
                                        "chunk_overlap": 50,
                                        "enable_auto_update": True,
                                        "vector_dimension": 1536
                                    },
                                    "storage_info": {
                                        "total_size": "0MB",
                                        "document_count": 0,
                                        "vector_count": 0
                                    }
                                }
                            }
                        },
                        "advanced_creation": {
                            "summary": "高级配置创建",
                            "value": {
                                "success": True,
                                "message": "知识库创建成功（自定义配置）",
                                "data": {
                                    "name": "tech_docs",
                                    "description": "技术文档知识库",
                                    "language": "English",
                                    "config": {
                                        "chunk_size": 2048,
                                        "chunk_overlap": 100,
                                        "enable_knowledge_graph": True,
                                        "similarity_threshold": 0.8
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "创建参数错误",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_name": {
                            "summary": "名称无效",
                            "value": {
                                "detail": "知识库名称包含无效字符"
                            }
                        },
                        "name_exists": {
                            "summary": "名称已存在",
                            "value": {
                                "detail": "知识库名称 'ai_research' 已存在"
                            }
                        },
                        "invalid_config": {
                            "summary": "配置无效",
                            "value": {
                                "detail": "chunk_size 必须在 256-4096 范围内"
                            }
                        }
                    }
                }
            }
        },
        507: {
            "description": "存储空间不足",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "磁盘空间不足，无法创建知识库"
                    }
                }
            }
        }
    }
)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """创建新知识库"""
    return await kb_api.create_knowledge_base(request)


@router.delete(
    "/knowledge-bases/{name}",
    response_model=BaseResponse,
    summary="删除知识库",
    description="""
    删除指定的知识库。
    
    **警告：** 此操作将永久删除知识库及其所有数据！
    
    **删除内容：**
    - 所有文档数据
    - 知识图谱数据
    - 向量索引
    - 配置文件
    - 缓存数据
    
    **安全措施：**
    - 默认知识库不能删除（除非使用force参数）
    - 删除前会创建备份
    - 支持强制删除模式
    
    **参数说明：**
    - name: 知识库名称（路径参数）
    - force: 是否强制删除（查询参数，默认false）
    
    **返回结果：**
    - 删除操作结果
    - 备份文件位置
    - 释放的存储空间
    
    **使用场景：**
    - 清理不需要的知识库
    - 释放存储空间
    - 系统维护
    
    **注意事项：**
    - 删除操作不可逆
    - 建议在删除前确认数据已备份
    - 删除大型知识库可能需要较长时间
    """
)
async def delete_knowledge_base(name: str, force: bool = False):
    """删除知识库"""
    return await kb_api.delete_knowledge_base(name, force)


@router.post(
    "/knowledge-bases/switch",
    response_model=BaseResponse,
    summary="切换当前知识库",
    description="""
    切换到指定的知识库作为当前工作知识库。
    
    **参数说明：**
    - name: 要切换到的知识库名称（必填）
    - create_if_not_exists: 如果知识库不存在是否创建（可选，默认false）
    
    **切换效果：**
    - 后续的查询操作将在新知识库中执行
    - 文档插入操作将添加到新知识库
    - 知识图谱操作将针对新知识库
    
    **返回结果：**
    - 切换操作结果
    - 新知识库的详细信息
    - 切换后的工作目录
    
    **使用示例：**
    ```json
    {
        "name": "ai_research",
        "create_if_not_exists": false
    }
    ```
    
    **使用场景：**
    - 多知识库环境下的切换
    - 不同项目或领域的知识管理
    - 测试和生产环境隔离
    
    **注意事项：**
    - 切换知识库会影响所有后续操作
    - 建议在切换前保存当前工作状态
    """
)
async def switch_knowledge_base(request: SwitchKnowledgeBaseRequest):
    """切换当前知识库"""
    return await kb_api.switch_knowledge_base(request)


@router.get(
    "/knowledge-bases/current",
    response_model=BaseResponse,
    summary="获取当前知识库信息",
    description="""
    获取当前正在使用的知识库的详细信息。
    
    **返回信息：**
    - 知识库基本信息（名称、描述、创建时间）
    - 数据统计（文档数、节点数、边数）
    - 存储信息（大小、路径）
    - 配置信息（语言、版本、标签）
    - 状态信息（就绪状态、健康状态）
    
    **使用场景：**
    - 确认当前工作环境
    - 显示知识库状态
    - 系统状态监控
    """
)
async def get_current_knowledge_base():
    """获取当前知识库信息"""
    return await kb_api.get_current_knowledge_base()


@router.get(
    "/knowledge-bases/{name}",
    response_model=BaseResponse,
    summary="获取指定知识库信息",
    description="""
    获取指定知识库的详细信息。
    
    **参数说明：**
    - name: 知识库名称（路径参数）
    
    **返回信息：**
    - 知识库详细信息
    - 数据统计和分析
    - 配置参数
    - 文件状态
    
    **使用场景：**
    - 知识库详情查看
    - 数据分析和报告
    - 系统监控
    """
)
async def get_knowledge_base_info(name: str):
    """获取指定知识库信息"""
    return await kb_api.get_knowledge_base_info(name)


@router.put(
    "/knowledge-bases/{name}/config",
    response_model=BaseResponse,
    summary="更新知识库配置",
    description="""
    更新指定知识库的配置参数。
    
    **可更新配置：**
    - 描述信息
    - 语言设置
    - 分块参数
    - 处理选项
    - 自定义标签
    
    **参数说明：**
    - name: 知识库名称（路径参数）
    - config: 配置参数对象（请求体）
    
    **配置选项：**
    - description: 知识库描述
    - language: 默认语言
    - chunk_size: 分块大小
    - chunk_overlap: 分块重叠
    - enable_auto_update: 自动更新
    - tags: 标签列表
    
    **返回结果：**
    - 更新操作结果
    - 更新后的配置信息
    - 影响的配置项列表
    
    **使用示例：**
    ```json
    {
        "knowledge_base": "ai_research",
        "config": {
            "description": "更新后的描述",
            "chunk_size": 2048,
            "tags": ["AI", "研究", "机器学习"]
        }
    }
    ```
    """
)
async def update_knowledge_base_config(name: str, request: KnowledgeBaseConfigRequest):
    """更新知识库配置"""
    request.knowledge_base = name
    return await kb_api.update_knowledge_base_config(request)


@router.post(
    "/knowledge-bases/{name}/backup",
    response_model=BaseResponse,
    summary="备份知识库",
    description="""
    创建指定知识库的完整备份。
    
    **备份内容：**
    - 所有文档数据
    - 知识图谱文件
    - 向量索引
    - 配置文件
    - 元数据信息
    
    **备份格式：**
    - 压缩包格式（.zip）
    - 包含完整目录结构
    - 支持增量备份
    
    **参数说明：**
    - name: 知识库名称（路径参数）
    - compress: 是否压缩（查询参数，默认true）
    - include_vectors: 是否包含向量数据（查询参数，默认false）
    
    **返回结果：**
    - 备份文件路径
    - 备份文件大小
    - 备份创建时间
    - 备份内容摘要
    
    **使用场景：**
    - 数据安全保护
    - 系统迁移准备
    - 版本管理
    """
)
async def backup_knowledge_base(name: str, compress: bool = True, include_vectors: bool = False):
    """备份知识库"""
    return await kb_api.backup_knowledge_base(name, compress, include_vectors)


@router.post(
    "/knowledge-bases/{name}/restore",
    response_model=BaseResponse,
    summary="恢复知识库",
    description="""
    从备份文件恢复知识库。
    
    **恢复选项：**
    - 完全恢复：替换所有数据
    - 增量恢复：仅恢复缺失数据
    - 选择性恢复：恢复指定类型数据
    
    **参数说明：**
    - name: 知识库名称（路径参数）
    - backup_file: 备份文件路径
    - restore_mode: 恢复模式（full/incremental/selective）
    - overwrite: 是否覆盖现有数据
    
    **返回结果：**
    - 恢复操作结果
    - 恢复的数据统计
    - 操作耗时
    
    **注意事项：**
    - 恢复操作可能需要较长时间
    - 建议在恢复前备份当前数据
    """
)
async def restore_knowledge_base(name: str, backup_file: str, restore_mode: str = "full", overwrite: bool = False):
    """恢复知识库"""
    return await kb_api.restore_knowledge_base(name, backup_file, restore_mode, overwrite)


@router.post(
    "/reload-config",
    response_model=BaseResponse,
    summary="重新加载配置",
    description="""
    重新加载知识库配置，包括：

    **重新加载内容：**
    - 从环境变量重新读取配置
    - 根据WORKING_DIR自动切换当前知识库
    - 更新知识库管理器状态

    **返回信息：**
    - 更新后的配置信息
    - 当前知识库信息
    - 路径配置详情

    **使用场景：**
    - 修改.env文件后需要重新加载配置
    - 切换知识库后需要更新状态
    - 配置调试和验证
    """
)
async def reload_config():
    """重新加载配置"""
    return await kb_api.reload_config()


@router.get(
    "/config-info",
    response_model=BaseResponse,
    summary="获取配置信息",
    description="""
    获取当前知识库管理器的配置信息。

    **返回信息：**
    - 知识库基础目录
    - 当前知识库名称
    - 当前知识库路径
    - 配置文件中的路径设置

    **用途：**
    - 调试配置问题
    - 验证路径设置
    - 检查当前状态
    """
)
async def get_config_info():
    """获取配置信息"""
    return await kb_api.get_config_info()


# 导出路由器
__all__ = ["router"]
