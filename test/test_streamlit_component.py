#!/usr/bin/env python3
"""
测试Streamlit知识图谱可视化组件
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    st.title("🧪 知识图谱可视化组件测试")
    
    try:
        from streamlit_app.api_client import StreamlitAPIClient
        from streamlit_app.components import render_knowledge_graph_visualization
        
        st.success("✅ 模块导入成功")
        
        # 创建API客户端
        if 'api_client' not in st.session_state:
            api_base_url = st.text_input(
                "API服务地址", 
                value="http://localhost:8002",
                help="GuiXiaoXiRag FastAPI服务的地址"
            )
            st.session_state.api_client = StreamlitAPIClient(api_base_url)
        
        st.info("🔗 API客户端已创建")
        
        # 测试API连接
        if st.button("🔍 测试API连接"):
            try:
                # 测试健康检查
                health = st.session_state.api_client.request_sync("GET", "/health")
                if health:
                    st.success("✅ API连接正常")
                    st.json(health)
                else:
                    st.error("❌ API连接失败")
            except Exception as e:
                st.error(f"❌ API连接异常: {e}")
                st.exception(e)
        
        # 测试知识库列表
        if st.button("📚 测试知识库列表"):
            try:
                kb_list = st.session_state.api_client.list_knowledge_bases()
                st.write(f"返回类型: {type(kb_list)}")
                st.write(f"返回值: {kb_list}")
                
                if kb_list:
                    st.success(f"✅ 获取到 {len(kb_list)} 个知识库")
                    for i, kb in enumerate(kb_list):
                        st.write(f"{i+1}. {kb}")
                        if isinstance(kb, dict) and "name" in kb:
                            st.write(f"   名称: {kb['name']}")
                else:
                    st.warning("⚠️ 未获取到知识库列表")
            except Exception as e:
                st.error(f"❌ 知识库列表获取异常: {e}")
                st.exception(e)
        
        # 测试图谱状态
        if st.button("📊 测试图谱状态"):
            try:
                status = st.session_state.api_client.get_graph_status()
                st.write(f"返回类型: {type(status)}")
                st.write(f"返回值: {status}")
                
                if status:
                    st.success("✅ 图谱状态获取成功")
                    st.json(status)
                else:
                    st.warning("⚠️ 未获取到图谱状态")
            except Exception as e:
                st.error(f"❌ 图谱状态获取异常: {e}")
                st.exception(e)
        
        # 分隔线
        st.markdown("---")
        
        # 测试完整组件
        if st.button("🎨 测试完整可视化组件"):
            try:
                st.markdown("### 🕸️ 知识图谱可视化组件")
                render_knowledge_graph_visualization(st.session_state.api_client)
            except Exception as e:
                st.error(f"❌ 可视化组件异常: {e}")
                st.exception(e)
                
                # 显示详细的错误信息
                import traceback
                st.code(traceback.format_exc())
        
    except ImportError as e:
        st.error(f"❌ 模块导入失败: {e}")
        st.exception(e)
    except Exception as e:
        st.error(f"❌ 应用异常: {e}")
        st.exception(e)

if __name__ == "__main__":
    main()
