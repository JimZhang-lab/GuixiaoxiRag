"""
知识图谱API处理器
处理知识图谱相关的业务逻辑
"""
from fastapi import HTTPException

from model import (
    BaseResponse, KnowledgeGraphRequest, GraphVisualizationRequest,
    GraphDataRequest
)
from handler import guixiaoxirag_service
from common.logging_utils import logger_manager


class KnowledgeGraphAPI:
    """知识图谱API处理器"""
    
    def __init__(self):
        self.logger = logger_manager.setup_api_logger()
    
    async def get_knowledge_graph(self, request: KnowledgeGraphRequest) -> BaseResponse:
        """获取知识图谱数据"""
        try:
            self.logger.info(f"获取知识图谱: {request.node_label}")
            
            # 调用服务层
            result = await guixiaoxirag_service.get_knowledge_graph(
                node_label=request.node_label,
                max_depth=request.max_depth,
                max_nodes=request.max_nodes
            )
            
            return BaseResponse(
                success=True,
                message="获取知识图谱成功",
                data=result
            )
            
        except Exception as e:
            self.logger.error(f"获取知识图谱失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取知识图谱失败: {str(e)}")
    
    async def get_knowledge_graph_stats(self) -> BaseResponse:
        """获取知识图谱统计信息"""
        try:
            from common.utils import check_knowledge_graph_files
            from handler import kb_manager

            # 获取当前知识库路径
            current_kb_path = kb_manager.get_current_kb_path()

            # 检查图谱文件状态
            file_status = check_knowledge_graph_files(current_kb_path)

            stats = {
                "knowledge_base": kb_manager.current_kb,
                "working_dir": current_kb_path,
                "xml_file_exists": file_status.get("xml_exists", False),
                "json_file_exists": file_status.get("json_exists", False),
                "node_count": 0,
                "edge_count": 0,
                "file_size": 0
            }

            # 如果XML文件存在，尝试解析统计信息
            if file_status.get("xml_exists"):
                try:
                    import xml.etree.ElementTree as ET
                    import os

                    xml_file = file_status.get("xml_path")
                    if xml_file and os.path.exists(xml_file):
                        tree = ET.parse(xml_file)
                        root = tree.getroot()

                        # 统计节点和边
                        ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}
                        nodes = root.findall('.//graphml:node', ns)
                        edges = root.findall('.//graphml:edge', ns)

                        stats["node_count"] = len(nodes)
                        stats["edge_count"] = len(edges)
                        stats["file_size"] = os.path.getsize(xml_file)

                except Exception as parse_error:
                    self.logger.warning(f"解析GraphML文件失败: {parse_error}")

            return BaseResponse(
                success=True,
                message="获取统计信息成功",
                data=stats
            )

        except Exception as e:
            self.logger.error(f"获取统计信息失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
    
    async def clear_knowledge_graph(self) -> BaseResponse:
        """清空知识图谱数据"""
        try:
            import os
            from handler import kb_manager

            # 获取当前知识库路径
            current_kb_path = kb_manager.get_current_kb_path()

            # 要删除的文件列表
            files_to_delete = [
                "graph_chunk_entity_relation.graphml",
                "graph_chunk_entity_relation.json",
                "graph_data.json"
            ]

            deleted_files = []
            total_size = 0

            for filename in files_to_delete:
                file_path = os.path.join(current_kb_path, filename)
                if os.path.exists(file_path):
                    try:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append(filename)
                        total_size += file_size
                        self.logger.info(f"删除文件: {file_path}")
                    except Exception as e:
                        self.logger.error(f"删除文件失败 {file_path}: {e}")

            return BaseResponse(
                success=True,
                message=f"清空知识图谱成功，删除了 {len(deleted_files)} 个文件",
                data={
                    "deleted_files": deleted_files,
                    "total_size": total_size,
                    "knowledge_base": kb_manager.current_kb
                }
            )

        except Exception as e:
            self.logger.error(f"清空知识图谱失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"清空知识图谱失败: {str(e)}")
    
    async def get_knowledge_graph_status(self) -> BaseResponse:
        """获取知识图谱文件状态"""
        try:
            # 这里应该实现状态检查逻辑
            status = {
                "status": "需要实现状态检查"
            }
            
            return BaseResponse(
                success=True,
                message="获取状态成功",
                data=status
            )
            
        except Exception as e:
            self.logger.error(f"获取状态失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")
    
    async def convert_knowledge_graph(self) -> BaseResponse:
        """转换GraphML到JSON"""
        try:
            from common.utils import create_or_update_knowledge_graph_json
            from handler import kb_manager

            # 获取当前知识库路径
            current_kb_path = kb_manager.get_current_kb_path()

            # 执行转换
            success = create_or_update_knowledge_graph_json(current_kb_path)

            if success:
                import os
                json_file = os.path.join(current_kb_path, "graph_chunk_entity_relation.json")
                file_size = os.path.getsize(json_file) if os.path.exists(json_file) else 0

                return BaseResponse(
                    success=True,
                    message="GraphML转换为JSON成功",
                    data={
                        "json_file": json_file,
                        "file_size": file_size,
                        "knowledge_base": kb_manager.current_kb
                    }
                )
            else:
                raise HTTPException(status_code=500, detail="转换失败，请检查GraphML文件是否存在")

        except Exception as e:
            self.logger.error(f"转换失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")
    
    async def get_knowledge_graph_data(self, request: GraphDataRequest) -> BaseResponse:
        """获取图谱数据"""
        try:
            # 这里应该实现数据获取逻辑
            return BaseResponse(
                success=True,
                message="获取数据成功",
                data={"message": "需要实现数据获取逻辑"}
            )
            
        except Exception as e:
            self.logger.error(f"获取数据失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")
    
    async def visualize_knowledge_graph(self, request: GraphVisualizationRequest) -> BaseResponse:
        """生成知识图谱可视化"""
        try:
            # 这里应该实现可视化逻辑
            return BaseResponse(
                success=True,
                message="生成可视化成功",
                data={"message": "需要实现可视化逻辑"}
            )
            
        except Exception as e:
            self.logger.error(f"生成可视化失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"生成可视化失败: {str(e)}")
    
    async def list_knowledge_graph_files(self) -> BaseResponse:
        """列出知识库中的图谱文件"""
        try:
            # 这里应该实现文件列表逻辑
            return BaseResponse(
                success=True,
                message="获取文件列表成功",
                data={"message": "需要实现文件列表逻辑"}
            )
            
        except Exception as e:
            self.logger.error(f"获取文件列表失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


# 导出API处理器
__all__ = ["KnowledgeGraphAPI"]
