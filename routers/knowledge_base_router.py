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
    获取所有可用知识库的列表和详细信息。
    
    **返回信息：**
    - 知识库名称和描述
    - 创建时间
    - 文档数量统计
    - 知识图谱节点和边数量
    - 存储大小
    - 当前状态
    - 支持的语言
    
    **知识库状态：**
    - ready: 知识库就绪，可正常使用
    - building: 知识库正在构建中
    - incomplete: 知识库数据不完整
    - error: 知识库存在错误
    
    **返回数据：**
    - knowledge_bases: 知识库信息列表
    - total_count: 知识库总数
    - current_kb: 当前使用的知识库
    
    **使用场景：**
    - 知识库管理界面
    - 知识库选择和切换
    - 系统状态监控
    """
)
async def list_knowledge_bases():
    """获取知识库列表"""
    return await kb_api.list_knowledge_bases()


@router.post(
    "/knowledge-bases",
    response_model=BaseResponse,
    summary="创建新知识库",
    description="""
    创建一个新的知识库。
    
    **参数说明：**
    - name: 知识库名称（必填，1-50字符，只能包含字母、数字、下划线和连字符）
    - description: 知识库描述（可选，最多500字符）
    - language: 默认语言（可选，默认"中文"）
    - config: 自定义配置（可选）
    
    **命名规则：**
    - 长度：1-50个字符
    - 字符：字母、数字、下划线(_)、连字符(-)
    - 不能与现有知识库重名
    - 不能使用系统保留名称
    
    **配置选项：**
    - chunk_size: 文档分块大小（默认1024）
    - chunk_overlap: 分块重叠大小（默认50）
    - enable_auto_update: 是否启用自动更新（默认true）
    
    **返回结果：**
    - 新创建的知识库详细信息
    - 知识库路径
    - 初始化状态
    
    **使用示例：**
    ```json
    {
        "name": "ai_research",
        "description": "人工智能研究知识库",
        "language": "中文",
        "config": {
            "chunk_size": 1024,
            "chunk_overlap": 50,
            "enable_auto_update": true
        }
    }
    ```
    """
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


# 导出路由器
__all__ = ["router"]
