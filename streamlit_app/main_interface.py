"""
GuiXiaoXiRag FastAPI Streamlit 主界面
"""
import streamlit as st
import asyncio
import httpx
import json
import time
from typing import Optional, Dict, Any

# 导入各个功能模块
from .api_client import StreamlitAPIClient
from .components import (
    render_sidebar,
    render_system_status,
    render_document_management,
    render_query_interface,
    render_knowledge_base_management,
    render_language_settings,
    render_monitoring_dashboard,
    render_service_config
)

def run_main_interface():
    """运行主界面"""
    
    # 页面标题
    st.title("🚀 GuiXiaoXiRag FastAPI 管理界面")
    st.markdown("---")
    
    # 初始化API客户端
    if 'api_client' not in st.session_state:
        api_base_url = st.sidebar.text_input(
            "API服务地址", 
            value="http://localhost:8002",
            help="GuiXiaoXiRag FastAPI服务的地址"
        )
        st.session_state.api_client = StreamlitAPIClient(api_base_url)
    
    # 侧边栏导航
    page = render_sidebar()
    
    # 根据选择的页面渲染对应界面
    if page == "系统状态":
        render_system_status_page()
    elif page == "文档管理":
        render_document_management_page()
    elif page == "智能查询":
        render_query_interface_page()
    elif page == "知识库管理":
        render_knowledge_base_management_page()
    elif page == "语言设置":
        render_language_settings_page()
    elif page == "服务配置":
        render_service_config_page()
    elif page == "监控面板":
        render_monitoring_dashboard_page()
    else:
        render_welcome_page()

def render_welcome_page():
    """渲染欢迎页面"""
    st.header("🎉 欢迎使用 GuiXiaoXiRag FastAPI 管理界面")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 系统状态")
        st.write("查看服务健康状态、运行时间和基本配置信息")
        if st.button("查看系统状态", key="welcome_status"):
            st.session_state.current_page = "系统状态"
            st.rerun()
    
    with col2:
        st.subheader("📝 文档管理")
        st.write("插入文档、上传文件、批量处理等文档管理功能")
        if st.button("管理文档", key="welcome_docs"):
            st.session_state.current_page = "文档管理"
            st.rerun()
    
    with col3:
        st.subheader("🔍 智能查询")
        st.write("执行智能查询、选择查询模式、优化查询参数")
        if st.button("开始查询", key="welcome_query"):
            st.session_state.current_page = "智能查询"
            st.rerun()
    
    st.markdown("---")
    
    # 功能特性展示
    st.subheader("✨ 主要功能特性")
    
    features = [
        ("🗄️ 多知识库管理", "支持创建、切换、管理多个独立的知识库"),
        ("🌍 多语言支持", "支持中文和英文回答，可灵活切换"),
        ("📊 实时监控", "查看系统性能指标、知识图谱统计"),
        ("🔧 灵活配置", "支持性能优化、服务配置管理"),
        ("📖 完整API", "28个API端点，覆盖所有功能"),
        ("🛠️ 易用工具", "提供命令行工具和Python客户端")
    ]
    
    for i in range(0, len(features), 2):
        col1, col2 = st.columns(2)
        with col1:
            if i < len(features):
                title, desc = features[i]
                st.write(f"**{title}**")
                st.write(desc)
        with col2:
            if i + 1 < len(features):
                title, desc = features[i + 1]
                st.write(f"**{title}**")
                st.write(desc)
    
    st.markdown("---")
    
    # 快速开始指南
    st.subheader("🚀 快速开始")
    
    with st.expander("1. 检查系统状态"):
        st.code("""
# 确保GuiXiaoXiRag FastAPI服务正在运行
python main.py status

# 或启动服务
python main.py
        """)
    
    with st.expander("2. 插入第一个文档"):
        st.code("""
# 在文档管理页面插入文档
文本内容: "人工智能是计算机科学的一个分支"
知识库: default
语言: 中文
        """)
    
    with st.expander("3. 执行第一次查询"):
        st.code("""
# 在智能查询页面执行查询
查询内容: "什么是人工智能？"
查询模式: hybrid
知识库: default
回答语言: 中文
        """)

def render_system_status_page():
    """渲染系统状态页面"""
    st.header("📊 系统状态")
    render_system_status(st.session_state.api_client)

def render_document_management_page():
    """渲染文档管理页面"""
    st.header("📝 文档管理")
    render_document_management(st.session_state.api_client)

def render_query_interface_page():
    """渲染查询界面页面"""
    st.header("🔍 智能查询")
    render_query_interface(st.session_state.api_client)

def render_knowledge_base_management_page():
    """渲染知识库管理页面"""
    st.header("🗄️ 知识库管理")
    render_knowledge_base_management(st.session_state.api_client)

def render_language_settings_page():
    """渲染语言设置页面"""
    st.header("🌍 语言设置")
    render_language_settings(st.session_state.api_client)

def render_service_config_page():
    """渲染服务配置页面"""
    st.header("⚙️ 服务配置")
    render_service_config(st.session_state.api_client)

def render_monitoring_dashboard_page():
    """渲染监控面板页面"""
    st.header("📈 监控面板")
    render_monitoring_dashboard(st.session_state.api_client)
