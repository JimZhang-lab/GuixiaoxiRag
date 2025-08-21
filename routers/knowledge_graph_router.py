"""
知识图谱路由
处理知识图谱查询、可视化、数据导出等功能
"""
from fastapi import APIRouter, HTTPException

from model import (
    BaseResponse, KnowledgeGraphRequest, GraphVisualizationRequest,
    GraphDataRequest, KnowledgeGraphResponse, GraphVisualizationResponse,
    GraphDataResponse, GraphStatusResponse
)
from api.knowledge_graph_api import KnowledgeGraphAPI

# 创建路由器
router = APIRouter(prefix="/api/v1", tags=["知识图谱"])

# 创建API处理器实例
kg_api = KnowledgeGraphAPI()


@router.post(
    "/knowledge-graph",
    response_model=BaseResponse,
    summary="获取知识图谱数据",
    description="""
    基于指定节点标签智能提取知识图谱的子图数据，支持多层关系探索。

    **🕸️ 图谱探索特性：**
    - 🎯 智能节点匹配和扩展
    - 🔍 多层关系深度遍历
    - 📊 动态节点数量控制
    - 🎨 可视化友好的数据格式
    - ⚡ 高性能图谱查询算法

    **🔧 参数说明：**
    - **node_label**: 起始节点标签（必填）
      - 支持精确匹配和模糊匹配
      - 可以是实体名称、概念或关键词
      - 示例："人工智能"、"机器学习"、"深度学习"
    - **max_depth**: 最大遍历深度（可选，默认3）
      - 范围：1-10层
      - 深度越大，返回的关联节点越多
      - 建议：概念探索用3-5层，详细分析用1-2层
    - **max_nodes**: 最大节点数限制（可选，默认100）
      - 范围：10-5000个节点
      - 防止返回数据过大影响性能
      - 建议：可视化用100-500，分析用500-2000
    - **include_metadata**: 包含元数据（可选，默认true）
      - 节点属性、创建时间、权重等
      - 关系强度、置信度等信息
    - **filter_types**: 节点类型过滤（可选）
      - 可指定返回特定类型的节点
      - 如：["Person", "Organization", "Concept"]
    - **min_weight**: 最小关系权重（可选，默认0.1）
      - 过滤弱关系，提高结果质量

    **📊 返回数据结构：**
    - **nodes**: 节点列表
      - id: 唯一标识符
      - label: 节点标签/名称
      - type: 节点类型
      - properties: 节点属性字典
      - weight: 节点重要性权重
      - degree: 节点度数（连接数）
    - **edges**: 边列表
      - source: 源节点ID
      - target: 目标节点ID
      - relation: 关系类型
      - weight: 关系权重
      - properties: 关系属性
    - **statistics**: 图谱统计
      - node_count: 节点数量
      - edge_count: 边数量
      - avg_degree: 平均度数
      - density: 图谱密度
    - **metadata**: 元数据信息
      - query_time: 查询耗时
      - source_kb: 来源知识库
      - algorithm: 使用的算法

    **🎯 应用场景：**
    - 🔍 知识图谱探索和导航
    - 📈 关系网络分析和可视化
    - 🧠 知识发现和智能推理
    - 📚 概念关联分析
    - 🎓 教育知识图谱展示
    - 🏢 企业知识管理

    **💡 使用技巧：**
    - 从核心概念开始探索
    - 根据可视化需求调整节点数量
    - 使用类型过滤聚焦特定领域
    - 调整权重阈值优化结果质量
    """,
    responses={
        200: {
            "description": "成功获取知识图谱数据",
            "content": {
                "application/json": {
                    "examples": {
                        "concept_exploration": {
                            "summary": "概念探索",
                            "value": {
                                "success": True,
                                "message": "成功获取知识图谱数据",
                                "data": {
                                    "nodes": [
                                        {
                                            "id": "ai_001",
                                            "label": "人工智能",
                                            "type": "Concept",
                                            "properties": {
                                                "definition": "模拟人类智能的技术",
                                                "created_at": "2024-01-01"
                                            },
                                            "weight": 0.95,
                                            "degree": 15
                                        },
                                        {
                                            "id": "ml_001",
                                            "label": "机器学习",
                                            "type": "Concept",
                                            "weight": 0.88,
                                            "degree": 12
                                        }
                                    ],
                                    "edges": [
                                        {
                                            "source": "ai_001",
                                            "target": "ml_001",
                                            "relation": "包含",
                                            "weight": 0.9,
                                            "properties": {
                                                "confidence": 0.95
                                            }
                                        }
                                    ],
                                    "statistics": {
                                        "node_count": 25,
                                        "edge_count": 48,
                                        "avg_degree": 3.84,
                                        "density": 0.16
                                    },
                                    "metadata": {
                                        "query_time": 0.15,
                                        "source_kb": "ai_research",
                                        "algorithm": "BFS_weighted"
                                    }
                                }
                            }
                        },
                        "empty_result": {
                            "summary": "无匹配结果",
                            "value": {
                                "success": True,
                                "message": "未找到匹配的节点",
                                "data": {
                                    "nodes": [],
                                    "edges": [],
                                    "statistics": {
                                        "node_count": 0,
                                        "edge_count": 0
                                    },
                                    "suggestions": [
                                        "尝试使用更通用的关键词",
                                        "检查知识库是否包含相关内容"
                                    ]
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
                                "loc": ["body", "node_label"],
                                "msg": "节点标签不能为空",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        404: {
            "description": "知识图谱不存在",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "当前知识库不存在知识图谱数据"
                    }
                }
            }
        }
    }
)
async def get_knowledge_graph(request: KnowledgeGraphRequest):
    """获取知识图谱数据"""
    return await kg_api.get_knowledge_graph(request)


@router.get(
    "/knowledge-graph/stats",
    response_model=BaseResponse,
    summary="获取知识图谱统计信息",
    description="""
    获取当前知识库的知识图谱统计信息。
    
    **统计信息包括：**
    - 总节点数量
    - 总边数量
    - 节点类型分布
    - 关系类型分布
    - 图谱密度
    - 连通性信息
    - 中心性指标
    
    **返回数据：**
    - node_count: 节点总数
    - edge_count: 边总数
    - node_types: 节点类型统计
    - edge_types: 边类型统计
    - density: 图谱密度
    - components: 连通分量数
    - avg_degree: 平均度数
    - max_degree: 最大度数
    
    **使用场景：**
    - 图谱质量评估
    - 数据分析和报告
    - 性能优化参考
    """
)
async def get_knowledge_graph_stats():
    """获取知识图谱统计信息"""
    return await kg_api.get_knowledge_graph_stats()


@router.delete(
    "/knowledge-graph/clear",
    response_model=BaseResponse,
    summary="清空知识图谱数据",
    description="""
    清空当前知识库的知识图谱数据。
    
    **警告：** 此操作不可逆，将删除所有图谱数据！
    
    **清理内容：**
    - GraphML文件
    - JSON格式图谱文件
    - 图谱索引文件
    - 相关缓存数据
    
    **操作结果：**
    - 返回清理的文件数量
    - 释放的存储空间大小
    - 操作执行时间
    
    **使用场景：**
    - 重新构建知识图谱
    - 清理测试数据
    - 释放存储空间
    
    **注意事项：**
    - 建议在操作前备份重要数据
    - 清理后需要重新插入文档来重建图谱
    """
)
async def clear_knowledge_graph():
    """清空知识图谱数据"""
    return await kg_api.clear_knowledge_graph()


@router.get(
    "/knowledge-graph/status",
    response_model=BaseResponse,
    summary="获取知识图谱文件状态",
    description="""
    获取当前知识库的知识图谱文件状态信息。
    
    **检查内容：**
    - GraphML文件是否存在
    - JSON文件是否存在
    - 文件大小信息
    - 最后修改时间
    - 文件完整性状态
    
    **返回信息：**
    - knowledge_base: 知识库名称
    - working_dir: 工作目录
    - xml_file_exists: XML文件是否存在
    - xml_file_size: XML文件大小
    - json_file_exists: JSON文件是否存在
    - json_file_size: JSON文件大小
    - last_xml_modified: XML文件最后修改时间
    - last_json_modified: JSON文件最后修改时间
    - status: 整体状态描述
    
    **状态类型：**
    - ready: 图谱文件完整可用
    - building: 图谱正在构建中
    - incomplete: 图谱文件不完整
    - error: 图谱文件存在错误
    """
)
async def get_knowledge_graph_status():
    """获取知识图谱文件状态"""
    return await kg_api.get_knowledge_graph_status()


@router.post(
    "/knowledge-graph/convert",
    response_model=BaseResponse,
    summary="转换GraphML到JSON",
    description="""
    将GraphML格式的知识图谱文件转换为JSON格式。
    
    **转换特性：**
    - 自动检测GraphML文件更新
    - 增量转换，避免重复处理
    - 保持数据完整性
    - 优化JSON结构便于前端使用
    
    **转换内容：**
    - 节点数据（ID、标签、属性）
    - 边数据（源节点、目标节点、关系）
    - 元数据信息
    - 统计信息
    
    **返回结果：**
    - 转换是否成功
    - JSON文件路径
    - 节点和边数量
    - 转换耗时
    
    **使用场景：**
    - 前端图谱可视化
    - 数据格式转换
    - API数据提供
    """
)
async def convert_knowledge_graph():
    """转换GraphML到JSON"""
    return await kg_api.convert_knowledge_graph()


@router.post(
    "/knowledge-graph/data",
    response_model=BaseResponse,
    summary="获取图谱数据",
    description="""
    获取知识图谱的完整数据，支持多种格式输出。
    
    **参数说明：**
    - knowledge_base: 知识库名称（可选）
    - format: 数据格式（json/xml/csv）
    - include_metadata: 是否包含元数据
    - compress: 是否压缩数据
    
    **支持格式：**
    - json: JSON格式，便于程序处理
    - xml: GraphML格式，保持原始结构
    - csv: CSV格式，便于表格分析
    
    **返回数据：**
    - nodes: 节点数据数组
    - edges: 边数据数组
    - node_count: 节点数量
    - edge_count: 边数量
    - knowledge_base: 知识库名称
    - data_source: 数据来源文件
    - format: 数据格式
    - file_size: 数据文件大小
    
    **使用示例：**
    ```json
    {
        "knowledge_base": "my_kb",
        "format": "json",
        "include_metadata": true,
        "compress": false
    }
    ```
    """
)
async def get_knowledge_graph_data(request: GraphDataRequest):
    """获取图谱数据"""
    return await kg_api.get_knowledge_graph_data(request)


@router.post(
    "/knowledge-graph/visualize",
    response_model=BaseResponse,
    summary="生成知识图谱可视化",
    description="""
    生成知识图谱的交互式可视化HTML页面。
    
    **参数说明：**
    - knowledge_base: 知识库名称（可选）
    - max_nodes: 最大显示节点数（默认100，范围10-1000）
    - layout: 布局算法（spring/force/circular/hierarchical）
    - node_size_field: 节点大小字段（degree/centrality/weight）
    - edge_width_field: 边宽度字段（weight/frequency/strength）
    - filter_nodes: 节点过滤条件
    - filter_edges: 边过滤条件
    
    **布局算法：**
    - spring: 弹簧布局，适合一般图谱
    - force: 力导向布局，适合大型图谱
    - circular: 圆形布局，适合小型图谱
    - hierarchical: 层次布局，适合有向图
    
    **可视化特性：**
    - 交互式节点和边操作
    - 缩放和平移支持
    - 节点详情显示
    - 搜索和过滤功能
    - 导出图片功能
    
    **返回结果：**
    - html_content: 可视化HTML内容
    - html_file_path: HTML文件保存路径
    - node_count: 显示的节点数量
    - edge_count: 显示的边数量
    - layout_algorithm: 使用的布局算法
    """
)
async def visualize_knowledge_graph(request: GraphVisualizationRequest):
    """生成知识图谱可视化"""
    return await kg_api.visualize_knowledge_graph(request)


@router.get(
    "/knowledge-graph/files",
    response_model=BaseResponse,
    summary="列出知识库中的图谱文件",
    description="""
    列出指定知识库中的所有图谱相关文件。
    
    **文件类型：**
    - GraphML文件（.graphml）
    - JSON文件（.json）
    - 索引文件
    - 缓存文件
    - 备份文件
    
    **返回信息：**
    - 文件列表
    - 文件大小
    - 创建时间
    - 修改时间
    - 文件状态
    
    **使用场景：**
    - 文件管理和维护
    - 存储空间分析
    - 备份和恢复
    """
)
async def list_knowledge_graph_files():
    """列出知识库中的图谱文件"""
    return await kg_api.list_knowledge_graph_files()


# 导出路由器
__all__ = ["router"]
