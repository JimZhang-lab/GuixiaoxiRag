#!/usr/bin/env python3
"""
最小化Streamlit测试
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    st.title("🧪 最小化知识图谱可视化测试")
    
    try:
        from streamlit_app.api_client import StreamlitAPIClient
        
        st.success("✅ API客户端导入成功")
        
        # 创建模拟API客户端
        class MockAPIClient:
            def list_knowledge_bases(self):
                return [
                    {"name": "default", "path": "./knowledgeBase/default"},
                    {"name": "demo_ai", "path": "./knowledgeBase/demo_ai"}
                ]
            
            def get_graph_status(self, kb=None):
                return {
                    "knowledge_base": kb or "default",
                    "xml_file_exists": True,
                    "json_file_exists": True,
                    "xml_file_size": 1024,
                    "json_file_size": 512,
                    "status": "up_to_date"
                }
            
            def get_graph_data(self, kb=None, format="json"):
                return {
                    "nodes": [
                        {"id": "test1", "entity_type": "concept"},
                        {"id": "test2", "entity_type": "technology"}
                    ],
                    "edges": [
                        {"source": "test1", "target": "test2", "weight": 0.8}
                    ],
                    "node_count": 2,
                    "edge_count": 1,
                    "knowledge_base": kb or "default",
                    "data_source": "test"
                }
            
            def convert_graph_to_json(self, kb=None):
                return {"success": True, "message": "转换成功"}
            
            def visualize_knowledge_graph(self, **kwargs):
                return {
                    "html_content": "<html><body><h1>测试可视化</h1></body></html>",
                    "html_file_path": "./test.html",
                    "node_count": 2,
                    "edge_count": 1,
                    "knowledge_base": kwargs.get("knowledge_base", "default")
                }
            
            def list_graph_files(self, kb=None):
                return {
                    "knowledge_base": kb or "default",
                    "files": [
                        {
                            "name": "test.graphml",
                            "type": "GraphML",
                            "size": 1024,
                            "modified": 1234567890,
                            "relative_path": "test.graphml"
                        },
                        {
                            "name": "test.json",
                            "type": "JSON",
                            "size": 512,
                            "modified": 1234567891,
                            "relative_path": "test.json"
                        }
                    ],
                    "total_files": 2
                }
        
        # 使用模拟客户端
        if 'api_client' not in st.session_state:
            st.session_state.api_client = MockAPIClient()
        
        st.info("🔗 使用模拟API客户端")
        
        # 测试知识库选择
        st.markdown("### 📚 知识库选择测试")
        
        try:
            knowledge_bases = st.session_state.api_client.list_knowledge_bases()
            st.write(f"知识库列表类型: {type(knowledge_bases)}")
            st.write(f"知识库列表: {knowledge_bases}")
            
            if knowledge_bases:
                kb_names = [kb["name"] for kb in knowledge_bases if isinstance(kb, dict) and "name" in kb]
                selected_kb = st.selectbox(
                    "选择知识库",
                    ["default"] + kb_names,
                    help="选择要可视化的知识库"
                )
                st.success(f"✅ 选择的知识库: {selected_kb}")
            else:
                st.error("❌ 无法获取知识库列表")
                
        except Exception as e:
            st.error(f"❌ 知识库选择测试失败: {e}")
            st.exception(e)
        
        # 测试图谱状态
        st.markdown("### 📊 图谱状态测试")
        
        if st.button("获取图谱状态"):
            try:
                status = st.session_state.api_client.get_graph_status()
                st.success("✅ 图谱状态获取成功")
                st.json(status)
            except Exception as e:
                st.error(f"❌ 图谱状态测试失败: {e}")
                st.exception(e)
        
        # 测试文件列表
        st.markdown("### 📁 文件列表测试")
        
        if st.button("获取文件列表"):
            try:
                files_data = st.session_state.api_client.list_graph_files()
                st.write(f"文件数据类型: {type(files_data)}")
                st.write(f"文件数据: {files_data}")
                
                if files_data:
                    files = files_data.get("files", [])
                    st.write(f"文件列表类型: {type(files)}")
                    st.write(f"文件列表长度: {len(files)}")
                    
                    if files:
                        # 测试文件统计
                        graphml_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "GraphML"])
                        json_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "JSON"])
                        html_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "HTML"])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("GraphML文件", graphml_count)
                        with col2:
                            st.metric("JSON文件", json_count)
                        with col3:
                            st.metric("HTML文件", html_count)
                        
                        st.success("✅ 文件统计成功")
                    else:
                        st.info("📂 无文件")
                else:
                    st.error("❌ 无法获取文件数据")
                    
            except Exception as e:
                st.error(f"❌ 文件列表测试失败: {e}")
                st.exception(e)
        
        # 测试完整组件
        st.markdown("### 🎨 完整组件测试")
        
        if st.button("测试完整可视化组件"):
            try:
                from streamlit_app.components import render_knowledge_graph_visualization
                
                st.markdown("---")
                render_knowledge_graph_visualization(st.session_state.api_client)
                
            except Exception as e:
                st.error(f"❌ 完整组件测试失败: {e}")
                st.exception(e)
                
                # 显示详细错误信息
                import traceback
                st.code(traceback.format_exc())
        
    except ImportError as e:
        st.error(f"❌ 导入失败: {e}")
        st.exception(e)
    except Exception as e:
        st.error(f"❌ 应用异常: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
