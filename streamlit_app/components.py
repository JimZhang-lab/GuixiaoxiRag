"""
Streamlit 界面组件
"""
import streamlit as st
import json
import time
from typing import Optional, Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render_sidebar():
    """渲染侧边栏导航"""
    st.sidebar.title("🚀 GuiXiaoXiRag 管理")
    
    # 导航菜单
    pages = [
        "欢迎页面",
        "系统状态", 
        "文档管理",
        "智能查询",
        "知识库管理",
        "语言设置",
        "服务配置",
        "监控面板"
    ]
    
    # 使用session_state来保持页面状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "欢迎页面"
    
    selected_page = st.sidebar.selectbox(
        "选择功能页面",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
    )
    
    # 更新session_state
    st.session_state.current_page = selected_page
    
    st.sidebar.markdown("---")
    
    # 快速操作
    st.sidebar.subheader("🔧 快速操作")
    
    if st.sidebar.button("🔄 刷新页面"):
        st.rerun()
    
    if st.sidebar.button("📊 检查服务状态"):
        st.session_state.current_page = "系统状态"
        st.rerun()
    
    # 服务信息
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ 服务信息")
    
    api_url = st.session_state.get('api_client', {})
    if hasattr(api_url, 'base_url'):
        st.sidebar.text(f"API地址: {api_url.base_url}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**版本**: v1.0.0")
    st.sidebar.markdown("**文档**: [API参考](http://localhost:8002/docs)")
    
    return selected_page

def render_system_status(api_client):
    """渲染系统状态"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 健康检查")
        if st.button("检查服务健康状态", key="health_check"):
            with st.spinner("检查中..."):
                health = api_client.health_check()
                if health:
                    st.success("✅ 服务运行正常")
                    st.json(health)
                else:
                    st.error("❌ 服务不可用")
    
    with col2:
        st.subheader("📊 系统详情")
        if st.button("获取系统状态", key="system_status"):
            with st.spinner("获取中..."):
                status = api_client.get_system_status()
                if status:
                    st.success("✅ 获取成功")
                    
                    # 显示关键信息
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("服务名称", status.get('service_name', 'Unknown'))
                        st.metric("版本", status.get('version', 'Unknown'))
                    with col_b:
                        st.metric("运行时间", f"{status.get('uptime', 0):.1f}秒")
                        st.metric("初始化状态", "✅" if status.get('initialized') else "❌")
                    
                    # 显示配置信息
                    if 'config' in status:
                        st.subheader("⚙️ 配置信息")
                        config_df = pd.DataFrame([
                            {"配置项": k, "值": str(v)}
                            for k, v in status['config'].items()
                        ])
                        st.dataframe(config_df, use_container_width=True)
                else:
                    st.error("❌ 获取失败")
    
    st.markdown("---")
    
    # 系统重置
    st.subheader("🔄 系统重置")
    st.warning("⚠️ 此操作将清空所有数据，请谨慎操作！")
    
    if st.button("重置系统", key="reset_system"):
        if st.checkbox("我确认要重置系统", key="confirm_reset"):
            with st.spinner("重置中..."):
                success = api_client.reset_system()
                if success:
                    st.success("✅ 系统重置成功")
                else:
                    st.error("❌ 系统重置失败")

def render_document_management(api_client):
    """渲染文档管理界面"""
    tab1, tab2, tab3, tab4 = st.tabs(["📝 单文档插入", "📚 批量插入", "📁 文件上传", "📂 目录插入"])
    
    with tab1:
        st.subheader("📝 插入单个文档")
        
        # 获取知识库列表
        knowledge_bases = get_knowledge_base_options(api_client)
        
        with st.form("single_text_form"):
            text_content = st.text_area(
                "文档内容", 
                height=200,
                placeholder="请输入要插入的文档内容..."
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                doc_id = st.text_input("文档ID (可选)", placeholder="auto_generated")
            with col2:
                knowledge_base = st.selectbox("知识库", knowledge_bases)
            with col3:
                language = st.selectbox("处理语言", ["中文", "英文", "English", "Chinese"])
            
            submitted = st.form_submit_button("插入文档")
            
            if submitted and text_content:
                with st.spinner("插入中..."):
                    track_id = api_client.insert_text(
                        text=text_content,
                        doc_id=doc_id if doc_id else None,
                        knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                        language=language
                    )
                    if track_id:
                        st.success(f"✅ 文档插入成功！跟踪ID: {track_id}")
                    else:
                        st.error("❌ 文档插入失败")
    
    with tab2:
        st.subheader("📚 批量插入文档")
        
        with st.form("batch_text_form"):
            # 文本输入方式选择
            input_method = st.radio(
                "输入方式",
                ["逐行输入", "JSON格式"]
            )
            
            if input_method == "逐行输入":
                texts_input = st.text_area(
                    "文档内容（每行一个文档）",
                    height=200,
                    placeholder="文档1\n文档2\n文档3"
                )
                texts = [line.strip() for line in texts_input.split('\n') if line.strip()]
                doc_ids = None
            else:
                json_input = st.text_area(
                    "JSON格式输入",
                    height=200,
                    placeholder='[{"text": "文档1", "doc_id": "doc1"}, {"text": "文档2", "doc_id": "doc2"}]'
                )
                try:
                    if json_input:
                        data = json.loads(json_input)
                        texts = [item.get("text", "") for item in data]
                        doc_ids = [item.get("doc_id") for item in data]
                    else:
                        texts = []
                        doc_ids = None
                except json.JSONDecodeError:
                    st.error("JSON格式错误")
                    texts = []
                    doc_ids = None
            
            col1, col2 = st.columns(2)
            with col1:
                knowledge_base = st.selectbox("知识库", knowledge_bases, key="batch_kb")
            with col2:
                language = st.selectbox("处理语言", ["中文", "英文", "English", "Chinese"], key="batch_lang")
            
            submitted = st.form_submit_button("批量插入")
            
            if submitted and texts:
                st.info(f"准备插入 {len(texts)} 个文档")
                with st.spinner("批量插入中..."):
                    track_id = api_client.insert_texts(
                        texts=texts,
                        doc_ids=doc_ids,
                        knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                        language=language
                    )
                    if track_id:
                        st.success(f"✅ 批量插入成功！跟踪ID: {track_id}")
                    else:
                        st.error("❌ 批量插入失败")
    
    with tab3:
        st.subheader("📁 文件上传")
        
        uploaded_file = st.file_uploader(
            "选择文件",
            type=['txt', 'pdf', 'docx', 'doc'],
            help="支持的文件格式: .txt, .pdf, .docx, .doc"
        )
        
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                knowledge_base = st.selectbox("知识库", knowledge_bases, key="file_kb")
            with col2:
                language = st.selectbox("处理语言", ["中文", "英文", "English", "Chinese"], key="file_lang")
            
            if st.button("上传文件"):
                with st.spinner("上传中..."):
                    file_content = uploaded_file.read()
                    track_id = api_client.upload_file(file_content, uploaded_file.name)
                    if track_id:
                        st.success(f"✅ 文件上传成功！跟踪ID: {track_id}")
                        st.info(f"文件名: {uploaded_file.name}")
                        st.info(f"文件大小: {len(file_content)} 字节")
                    else:
                        st.error("❌ 文件上传失败")
    
    with tab4:
        st.subheader("📂 目录文件插入")
        
        with st.form("directory_form"):
            directory_path = st.text_input(
                "目录路径",
                placeholder="/path/to/documents"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                knowledge_base = st.selectbox("知识库", knowledge_bases, key="dir_kb")
            with col2:
                language = st.selectbox("处理语言", ["中文", "英文", "English", "Chinese"], key="dir_lang")
            
            submitted = st.form_submit_button("插入目录文件")
            
            if submitted and directory_path:
                with st.spinner("处理目录文件..."):
                    result = api_client.insert_directory(
                        directory_path=directory_path,
                        knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                        language=language
                    )
                    if result:
                        st.success(f"✅ 目录文件插入成功！")
                        st.info(f"处理文件数: {result.get('file_count', 0)}")
                        st.info(f"跟踪ID: {result.get('track_id', 'N/A')}")
                    else:
                        st.error("❌ 目录文件插入失败")

def get_knowledge_base_options(api_client):
    """获取知识库选项"""
    try:
        kbs = api_client.list_knowledge_bases()
        if kbs:
            return ["默认"] + [kb['name'] for kb in kbs]
        else:
            return ["默认"]
    except:
        return ["默认"]

def get_language_options():
    """获取语言选项"""
    return ["中文", "英文", "English", "Chinese", "zh", "en", "zh-CN", "en-US"]

def render_query_interface(api_client):
    """渲染查询界面"""
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 基础查询", "⚡ 优化查询", "📊 批量查询", "🔧 查询模式"])

    with tab1:
        st.subheader("🔍 基础查询")

        # 获取知识库和查询模式
        knowledge_bases = get_knowledge_base_options(api_client)
        query_modes = ["hybrid", "local", "global", "naive", "mix", "bypass"]

        with st.form("basic_query_form"):
            query_text = st.text_area(
                "查询内容",
                height=100,
                placeholder="请输入您的问题..."
            )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                mode = st.selectbox("查询模式", query_modes)
            with col2:
                knowledge_base = st.selectbox("知识库", knowledge_bases, key="query_kb")
            with col3:
                language = st.selectbox("回答语言", get_language_options(), key="query_lang")
            with col4:
                top_k = st.number_input("返回结果数", min_value=1, max_value=100, value=20)

            # 高级参数
            with st.expander("🔧 高级参数"):
                col_a, col_b = st.columns(2)
                with col_a:
                    max_entity_tokens = st.number_input("最大实体tokens", min_value=100, max_value=10000, value=1000)
                    max_relation_tokens = st.number_input("最大关系tokens", min_value=100, max_value=10000, value=1000)
                with col_b:
                    enable_rerank = st.checkbox("启用重排序", value=True)
                    response_type = st.selectbox("响应类型", ["Multiple Paragraphs", "Single Paragraph", "List"])

            submitted = st.form_submit_button("🔍 执行查询")

            if submitted and query_text:
                with st.spinner("查询中..."):
                    start_time = time.time()
                    result = api_client.query(
                        query=query_text,
                        mode=mode,
                        top_k=top_k,
                        knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                        language=language,
                        max_entity_tokens=max_entity_tokens,
                        max_relation_tokens=max_relation_tokens,
                        enable_rerank=enable_rerank,
                        response_type=response_type
                    )
                    end_time = time.time()

                    if result:
                        st.success(f"✅ 查询成功 (耗时: {end_time - start_time:.2f}秒)")

                        # 显示查询信息
                        col_info1, col_info2, col_info3 = st.columns(3)
                        with col_info1:
                            st.metric("查询模式", result.get('mode', mode))
                        with col_info2:
                            st.metric("知识库", result.get('knowledge_base', '默认'))
                        with col_info3:
                            st.metric("回答语言", result.get('language', language))

                        # 显示查询结果
                        st.subheader("📝 查询结果")
                        st.markdown(result.get('result', '无结果'))

                        # 显示原始查询
                        with st.expander("📋 查询详情"):
                            st.text(f"原始查询: {result.get('query', query_text)}")
                            st.text(f"响应时间: {end_time - start_time:.2f}秒")
                    else:
                        st.error("❌ 查询失败")

    with tab2:
        st.subheader("⚡ 优化查询")

        with st.form("optimized_query_form"):
            query_text = st.text_area(
                "查询内容",
                height=100,
                placeholder="请输入您的问题..."
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                mode = st.selectbox("查询模式", query_modes, key="opt_mode")
            with col2:
                performance_level = st.selectbox(
                    "性能级别",
                    ["fast", "balanced", "quality"],
                    index=1
                )
            with col3:
                st.write("") # 占位

            submitted = st.form_submit_button("⚡ 执行优化查询")

            if submitted and query_text:
                with st.spinner("优化查询中..."):
                    start_time = time.time()
                    result = api_client.optimized_query(
                        query=query_text,
                        mode=mode,
                        performance_level=performance_level
                    )
                    end_time = time.time()

                    if result:
                        st.success(f"✅ 优化查询成功 (耗时: {end_time - start_time:.2f}秒)")

                        # 显示优化参数
                        if 'optimized_params' in result:
                            st.subheader("🔧 优化参数")
                            params_df = pd.DataFrame([
                                {"参数": k, "值": str(v)}
                                for k, v in result['optimized_params'].items()
                            ])
                            st.dataframe(params_df, use_container_width=True)

                        # 显示查询结果
                        st.subheader("📝 查询结果")
                        st.markdown(result.get('result', '无结果'))
                    else:
                        st.error("❌ 优化查询失败")

    with tab3:
        st.subheader("📊 批量查询")

        with st.form("batch_query_form"):
            queries_input = st.text_area(
                "查询列表（每行一个查询）",
                height=150,
                placeholder="查询1\n查询2\n查询3"
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                mode = st.selectbox("查询模式", query_modes, key="batch_mode")
            with col2:
                knowledge_base = st.selectbox("知识库", knowledge_bases, key="batch_kb")
            with col3:
                language = st.selectbox("回答语言", get_language_options(), key="batch_lang")

            submitted = st.form_submit_button("📊 执行批量查询")

            if submitted and queries_input:
                queries = [line.strip() for line in queries_input.split('\n') if line.strip()]
                if queries:
                    st.info(f"准备执行 {len(queries)} 个查询")

                    with st.spinner("批量查询中..."):
                        start_time = time.time()
                        results = api_client.batch_query(
                            queries=queries,
                            mode=mode,
                            knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                            language=language
                        )
                        end_time = time.time()

                        if results:
                            st.success(f"✅ 批量查询成功 (耗时: {end_time - start_time:.2f}秒)")

                            # 显示结果
                            for i, result in enumerate(results, 1):
                                with st.expander(f"查询 {i}: {result.get('query', '')[:50]}..."):
                                    st.markdown(f"**查询**: {result.get('query', '')}")
                                    st.markdown(f"**回答**: {result.get('result', '无结果')}")
                                    st.markdown(f"**模式**: {result.get('mode', mode)}")
                        else:
                            st.error("❌ 批量查询失败")

    with tab4:
        st.subheader("🔧 查询模式说明")

        if st.button("获取查询模式信息"):
            modes_info = api_client.get_query_modes()
            if modes_info:
                st.success("✅ 获取成功")

                modes = modes_info.get('modes', {})
                default_mode = modes_info.get('default', 'hybrid')
                recommended = modes_info.get('recommended', [])

                st.subheader("📋 可用查询模式")
                for mode, description in modes.items():
                    icon = "⭐" if mode in recommended else "🔹"
                    default_tag = " (默认)" if mode == default_mode else ""
                    st.markdown(f"{icon} **{mode}{default_tag}**: {description}")

                # 模式对比表
                st.subheader("📊 模式对比")
                mode_data = []
                for mode, desc in modes.items():
                    mode_data.append({
                        "模式": mode,
                        "描述": desc,
                        "推荐": "✅" if mode in recommended else "❌",
                        "默认": "✅" if mode == default_mode else "❌"
                    })

                df = pd.DataFrame(mode_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.error("❌ 获取失败")

def render_knowledge_base_management(api_client):
    """渲染知识库管理界面"""
    tab1, tab2, tab3, tab4 = st.tabs(["📋 知识库列表", "➕ 创建知识库", "🔄 切换知识库", "📤 导出数据"])

    with tab1:
        st.subheader("📋 知识库列表")

        if st.button("刷新知识库列表", key="refresh_kb_list"):
            with st.spinner("获取知识库列表..."):
                kbs = api_client.list_knowledge_bases()
                if kbs:
                    st.success(f"✅ 找到 {len(kbs)} 个知识库")

                    # 创建表格数据
                    kb_data = []
                    for kb in kbs:
                        kb_data.append({
                            "名称": kb.get('name', 'Unknown'),
                            "文档数": kb.get('document_count', 0),
                            "节点数": kb.get('node_count', 0),
                            "边数": kb.get('edge_count', 0),
                            "大小(MB)": f"{kb.get('size_mb', 0):.2f}",
                            "创建时间": kb.get('created_at', 'Unknown')
                        })

                    df = pd.DataFrame(kb_data)
                    st.dataframe(df, use_container_width=True)

                    # 知识库统计图表
                    if len(kb_data) > 1:
                        st.subheader("📊 知识库统计")

                        col1, col2 = st.columns(2)
                        with col1:
                            # 文档数量对比
                            fig_docs = px.bar(
                                df,
                                x="名称",
                                y="文档数",
                                title="各知识库文档数量"
                            )
                            st.plotly_chart(fig_docs, use_container_width=True)

                        with col2:
                            # 大小对比
                            fig_size = px.pie(
                                df,
                                values="大小(MB)",
                                names="名称",
                                title="知识库大小分布"
                            )
                            st.plotly_chart(fig_size, use_container_width=True)
                else:
                    st.warning("⚠️ 未找到知识库或获取失败")

    with tab2:
        st.subheader("➕ 创建新知识库")

        with st.form("create_kb_form"):
            kb_name = st.text_input(
                "知识库名称",
                placeholder="my_knowledge_base",
                help="只能包含字母、数字、下划线和连字符"
            )

            kb_description = st.text_area(
                "知识库描述",
                placeholder="描述这个知识库的用途...",
                height=100
            )

            submitted = st.form_submit_button("创建知识库")

            if submitted and kb_name:
                # 验证名称格式
                import re
                if re.match(r'^[a-zA-Z0-9_-]+$', kb_name):
                    with st.spinner("创建中..."):
                        success = api_client.create_knowledge_base(kb_name, kb_description)
                        if success:
                            st.success(f"✅ 知识库 '{kb_name}' 创建成功！")
                        else:
                            st.error("❌ 知识库创建失败")
                else:
                    st.error("❌ 知识库名称格式错误，只能包含字母、数字、下划线和连字符")

    with tab3:
        st.subheader("🔄 切换知识库")

        # 获取知识库列表
        kbs = api_client.list_knowledge_bases()
        if kbs:
            kb_names = [kb['name'] for kb in kbs]

            with st.form("switch_kb_form"):
                selected_kb = st.selectbox("选择知识库", kb_names)

                submitted = st.form_submit_button("切换知识库")

                if submitted:
                    with st.spinner("切换中..."):
                        success = api_client.switch_knowledge_base(selected_kb)
                        if success:
                            st.success(f"✅ 已切换到知识库 '{selected_kb}'")
                        else:
                            st.error("❌ 知识库切换失败")
        else:
            st.warning("⚠️ 无可用知识库")

        # 删除知识库
        st.markdown("---")
        st.subheader("🗑️ 删除知识库")
        st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")

        if kbs:
            with st.form("delete_kb_form"):
                kb_to_delete = st.selectbox("选择要删除的知识库", kb_names, key="delete_kb")
                confirm_delete = st.checkbox(f"我确认要删除知识库 '{kb_to_delete}'")

                submitted = st.form_submit_button("删除知识库", type="secondary")

                if submitted and confirm_delete:
                    if kb_to_delete != "default":
                        with st.spinner("删除中..."):
                            success = api_client.delete_knowledge_base(kb_to_delete)
                            if success:
                                st.success(f"✅ 知识库 '{kb_to_delete}' 删除成功")
                            else:
                                st.error("❌ 知识库删除失败")
                    else:
                        st.error("❌ 不能删除默认知识库")

    with tab4:
        st.subheader("📤 导出知识库数据")

        kbs = api_client.list_knowledge_bases()
        if kbs:
            kb_names = [kb['name'] for kb in kbs]

            selected_kb = st.selectbox("选择要导出的知识库", kb_names, key="export_kb")

            if st.button("导出数据"):
                with st.spinner("导出中..."):
                    export_data = api_client.export_knowledge_base(selected_kb)
                    if export_data:
                        st.success(f"✅ 知识库 '{selected_kb}' 导出成功")

                        # 显示导出信息
                        metadata = export_data.get('metadata', {})
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("文档数量", metadata.get('document_count', 0))
                        with col2:
                            st.metric("节点数量", metadata.get('node_count', 0))
                        with col3:
                            st.metric("边数量", metadata.get('edge_count', 0))

                        # 提供下载
                        export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 下载导出数据",
                            data=export_json,
                            file_name=f"{selected_kb}_export_{int(time.time())}.json",
                            mime="application/json"
                        )

                        # 显示部分数据预览
                        with st.expander("📋 数据预览"):
                            st.json(export_data)
                    else:
                        st.error("❌ 导出失败")
        else:
            st.warning("⚠️ 无可用知识库")

def render_language_settings(api_client):
    """渲染语言设置界面"""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 当前语言设置")

        if st.button("获取语言信息", key="get_lang_info"):
            with st.spinner("获取中..."):
                lang_info = api_client.get_supported_languages()
                if lang_info:
                    st.success("✅ 获取成功")

                    current_lang = lang_info.get('current_language', 'Unknown')
                    supported_langs = lang_info.get('supported_languages', [])

                    st.metric("当前语言", current_lang)

                    st.subheader("📋 支持的语言")
                    for lang in supported_langs:
                        st.write(f"• {lang}")
                else:
                    st.error("❌ 获取失败")

    with col2:
        st.subheader("⚙️ 设置默认语言")

        with st.form("set_language_form"):
            new_language = st.selectbox(
                "选择语言",
                get_language_options()
            )

            submitted = st.form_submit_button("设置语言")

            if submitted:
                with st.spinner("设置中..."):
                    success = api_client.set_language(new_language)
                    if success:
                        st.success(f"✅ 语言已设置为: {new_language}")
                    else:
                        st.error("❌ 语言设置失败")

    st.markdown("---")

    # 语言使用说明
    st.subheader("📖 语言设置说明")

    st.markdown("""
    **语言设置的作用**:
    - 🔍 **查询回答**: 影响AI回答的语言
    - 📝 **文档处理**: 影响文档的处理方式
    - 🔧 **系统提示**: 影响系统内部的语言指令

    **支持的语言标识**:
    - 中文: `中文`, `Chinese`, `zh`, `zh-CN`
    - 英文: `英文`, `English`, `en`, `en-US`

    **使用建议**:
    - 为不同项目设置合适的语言
    - 可以在每次查询时临时指定语言
    - 服务级别的语言设置作为默认值
    """)

def render_service_config(api_client):
    """渲染服务配置界面"""
    tab1, tab2, tab3 = st.tabs(["⚙️ 当前配置", "🔄 切换配置", "🚀 性能优化"])

    with tab1:
        st.subheader("⚙️ 当前服务配置")

        if st.button("获取服务配置", key="get_service_config"):
            with st.spinner("获取中..."):
                config = api_client.get_service_config()
                if config:
                    st.success("✅ 获取成功")

                    # 显示配置信息
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("当前知识库", config.get('knowledge_base', 'default'))
                        st.metric("当前语言", config.get('language', 'Unknown'))
                    with col2:
                        st.metric("初始化状态", "✅" if config.get('initialized') else "❌")
                        st.metric("缓存实例数", config.get('cached_instances', 0))

                    # 详细配置
                    st.subheader("📋 详细配置")
                    config_df = pd.DataFrame([
                        {"配置项": k, "值": str(v)}
                        for k, v in config.items()
                    ])
                    st.dataframe(config_df, use_container_width=True)
                else:
                    st.error("❌ 获取失败")

    with tab2:
        st.subheader("🔄 切换服务配置")

        # 获取知识库列表
        kbs = api_client.list_knowledge_bases()
        if kbs:
            kb_names = [kb['name'] for kb in kbs]

            with st.form("switch_service_config"):
                col1, col2 = st.columns(2)
                with col1:
                    new_kb = st.selectbox("知识库", kb_names)
                with col2:
                    new_language = st.selectbox("语言", get_language_options())

                submitted = st.form_submit_button("切换配置")

                if submitted:
                    with st.spinner("切换中..."):
                        success = api_client.switch_service_kb(new_kb, new_language)
                        if success:
                            st.success(f"✅ 服务配置已切换")
                            st.info(f"知识库: {new_kb}")
                            st.info(f"语言: {new_language}")
                        else:
                            st.error("❌ 配置切换失败")
        else:
            st.warning("⚠️ 无可用知识库")

    with tab3:
        st.subheader("🚀 性能优化")

        if st.button("获取性能配置", key="get_perf_config"):
            with st.spinner("获取中..."):
                perf_config = api_client.get_performance_configs()
                if perf_config:
                    st.success("✅ 获取成功")

                    configs = perf_config.get('configs', {})
                    current_settings = perf_config.get('current_settings', {})

                    # 显示当前设置
                    st.subheader("📊 当前性能设置")
                    current_df = pd.DataFrame([
                        {"设置项": k, "值": str(v)}
                        for k, v in current_settings.items()
                    ])
                    st.dataframe(current_df, use_container_width=True)

                    # 显示可用配置
                    st.subheader("🔧 可用性能配置")
                    for config_name, config_data in configs.items():
                        with st.expander(f"📋 {config_name} 配置"):
                            config_df = pd.DataFrame([
                                {"参数": k, "值": str(v)}
                                for k, v in config_data.items()
                            ])
                            st.dataframe(config_df, use_container_width=True)
                else:
                    st.error("❌ 获取失败")

        # 应用性能配置
        st.markdown("---")
        st.subheader("⚡ 应用性能配置")

        with st.form("apply_perf_config"):
            perf_mode = st.selectbox(
                "性能模式",
                ["basic", "high_performance", "fast_test"],
                help="选择适合的性能配置模式"
            )

            submitted = st.form_submit_button("应用配置")

            if submitted:
                with st.spinner("应用中..."):
                    success = api_client.optimize_performance(perf_mode)
                    if success:
                        st.success(f"✅ 性能配置 '{perf_mode}' 应用成功")
                        st.warning("⚠️ 配置更改可能需要重启服务才能生效")
                    else:
                        st.error("❌ 性能配置应用失败")

def render_monitoring_dashboard(api_client):
    """渲染监控面板"""
    tab1, tab2, tab3, tab4 = st.tabs(["📊 性能指标", "🕸️ 知识图谱", "📋 系统日志", "📈 实时监控"])

    with tab1:
        st.subheader("📊 系统性能指标")

        if st.button("获取性能指标", key="get_metrics"):
            with st.spinner("获取中..."):
                metrics = api_client.get_metrics()
                if metrics:
                    st.success("✅ 获取成功")

                    # 关键指标展示
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总请求数", metrics.get('total_requests', 0))
                    with col2:
                        st.metric("错误数", metrics.get('total_errors', 0))
                    with col3:
                        st.metric("平均响应时间", f"{metrics.get('average_response_time', 0):.3f}秒")
                    with col4:
                        error_rate = metrics.get('error_rate', 0)
                        st.metric("错误率", f"{error_rate:.2%}")

                    # 性能图表
                    st.subheader("📈 性能趋势")

                    # 创建示例数据（实际应用中应该从历史数据获取）
                    import numpy as np
                    times = pd.date_range(start='2024-01-01', periods=24, freq='H')
                    requests = np.random.poisson(metrics.get('total_requests', 100) / 24, 24)
                    response_times = np.random.normal(metrics.get('average_response_time', 1), 0.2, 24)

                    col_chart1, col_chart2 = st.columns(2)

                    with col_chart1:
                        # 请求数趋势
                        fig_requests = go.Figure()
                        fig_requests.add_trace(go.Scatter(
                            x=times,
                            y=requests,
                            mode='lines+markers',
                            name='请求数',
                            line=dict(color='blue')
                        ))
                        fig_requests.update_layout(
                            title="24小时请求数趋势",
                            xaxis_title="时间",
                            yaxis_title="请求数"
                        )
                        st.plotly_chart(fig_requests, use_container_width=True)

                    with col_chart2:
                        # 响应时间趋势
                        fig_response = go.Figure()
                        fig_response.add_trace(go.Scatter(
                            x=times,
                            y=response_times,
                            mode='lines+markers',
                            name='响应时间',
                            line=dict(color='red')
                        ))
                        fig_response.update_layout(
                            title="24小时响应时间趋势",
                            xaxis_title="时间",
                            yaxis_title="响应时间(秒)"
                        )
                        st.plotly_chart(fig_response, use_container_width=True)

                    # 详细指标表
                    st.subheader("📋 详细指标")
                    metrics_df = pd.DataFrame([
                        {"指标": k, "值": str(v)}
                        for k, v in metrics.items()
                    ])
                    st.dataframe(metrics_df, use_container_width=True)
                else:
                    st.error("❌ 获取失败")

    with tab2:
        st.subheader("🕸️ 知识图谱统计")

        if st.button("获取图谱统计", key="get_graph_stats"):
            with st.spinner("获取中..."):
                stats = api_client.get_knowledge_graph_stats()
                if stats:
                    st.success("✅ 获取成功")

                    # 图谱统计指标
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("节点总数", stats.get('total_nodes', 0))
                    with col2:
                        st.metric("边总数", stats.get('total_edges', 0))
                    with col3:
                        density = 0
                        nodes = stats.get('total_nodes', 0)
                        edges = stats.get('total_edges', 0)
                        if nodes > 1:
                            density = (2 * edges) / (nodes * (nodes - 1))
                        st.metric("图密度", f"{density:.4f}")

                    # 图谱可视化（简化版）
                    st.subheader("📊 图谱结构分析")

                    # 节点度分布（示例）
                    degrees = np.random.exponential(2, min(stats.get('total_nodes', 100), 1000))
                    fig_degree = px.histogram(
                        x=degrees,
                        nbins=20,
                        title="节点度分布",
                        labels={'x': '度数', 'y': '节点数量'}
                    )
                    st.plotly_chart(fig_degree, use_container_width=True)

                    # 图谱信息表
                    st.subheader("📋 图谱详情")
                    graph_df = pd.DataFrame([
                        {"属性": k, "值": str(v)}
                        for k, v in stats.items()
                    ])
                    st.dataframe(graph_df, use_container_width=True)
                else:
                    st.error("❌ 获取失败")

        # 图谱操作
        st.markdown("---")
        st.subheader("🔧 图谱操作")

        col_op1, col_op2 = st.columns(2)

        with col_op1:
            st.write("**获取特定节点图谱**")
            with st.form("get_node_graph"):
                node_label = st.text_input("节点标签", placeholder="输入节点名称")
                max_depth = st.slider("最大深度", 1, 5, 3)
                max_nodes = st.slider("最大节点数", 10, 500, 100)

                submitted = st.form_submit_button("获取图谱")

                if submitted and node_label:
                    with st.spinner("获取中..."):
                        graph_data = api_client.get_knowledge_graph(node_label, max_depth, max_nodes)
                        if graph_data:
                            st.success("✅ 获取成功")

                            nodes = graph_data.get('nodes', [])
                            edges = graph_data.get('edges', [])

                            st.info(f"找到 {len(nodes)} 个节点，{len(edges)} 条边")

                            # 显示部分数据
                            if nodes:
                                st.subheader("📋 节点预览")
                                nodes_df = pd.DataFrame(nodes[:10])  # 只显示前10个
                                st.dataframe(nodes_df, use_container_width=True)
                        else:
                            st.error("❌ 获取失败")

        with col_op2:
            st.write("**清空图谱**")
            st.warning("⚠️ 此操作将清空所有图谱数据，不可恢复！")

            if st.button("清空知识图谱", key="clear_graph"):
                if st.checkbox("我确认要清空图谱", key="confirm_clear_graph"):
                    with st.spinner("清空中..."):
                        success = api_client.clear_knowledge_graph()
                        if success:
                            st.success("✅ 知识图谱已清空")
                        else:
                            st.error("❌ 清空失败")

    with tab3:
        st.subheader("📋 系统日志")

        col_log1, col_log2 = st.columns([3, 1])

        with col_log2:
            log_lines = st.number_input("日志行数", min_value=10, max_value=1000, value=100)

            if st.button("获取日志", key="get_logs"):
                with st.spinner("获取中..."):
                    logs = api_client.get_logs(log_lines)
                    if logs:
                        st.session_state.current_logs = logs
                    else:
                        st.error("❌ 获取日志失败")

        with col_log1:
            if 'current_logs' in st.session_state:
                st.success(f"✅ 获取到 {len(st.session_state.current_logs)} 条日志")

                # 日志过滤
                log_filter = st.text_input("过滤日志", placeholder="输入关键词过滤...")

                filtered_logs = st.session_state.current_logs
                if log_filter:
                    filtered_logs = [log for log in filtered_logs if log_filter.lower() in log.lower()]

                # 显示日志
                st.subheader(f"📄 日志内容 ({len(filtered_logs)} 条)")

                # 使用代码块显示日志
                log_text = "\n".join(filtered_logs[-50:])  # 只显示最后50条
                st.code(log_text, language="text")

                # 提供下载
                full_log_text = "\n".join(filtered_logs)
                st.download_button(
                    label="📥 下载日志",
                    data=full_log_text,
                    file_name=f"guixiaoxiRag_logs_{int(time.time())}.txt",
                    mime="text/plain"
                )

    with tab4:
        st.subheader("📈 实时监控")

        # 自动刷新控制
        auto_refresh = st.checkbox("启用自动刷新", value=False)
        refresh_interval = st.slider("刷新间隔(秒)", 5, 60, 10)

        if auto_refresh:
            st.info(f"🔄 每 {refresh_interval} 秒自动刷新")
            time.sleep(refresh_interval)
            st.rerun()

        # 实时指标展示
        col_rt1, col_rt2 = st.columns(2)

        with col_rt1:
            if st.button("刷新指标", key="refresh_metrics"):
                with st.spinner("刷新中..."):
                    # 获取系统状态
                    status = api_client.get_system_status()
                    if status:
                        st.metric("服务状态", "🟢 运行中" if status.get('initialized') else "🔴 未初始化")
                        st.metric("运行时间", f"{status.get('uptime', 0):.1f}秒")

                    # 获取性能指标
                    metrics = api_client.get_metrics()
                    if metrics:
                        st.metric("当前请求数", metrics.get('total_requests', 0))
                        st.metric("当前错误率", f"{metrics.get('error_rate', 0):.2%}")

        with col_rt2:
            if st.button("刷新图谱", key="refresh_graph"):
                with st.spinner("刷新中..."):
                    # 获取图谱统计
                    stats = api_client.get_knowledge_graph_stats()
                    if stats:
                        st.metric("图谱节点", stats.get('total_nodes', 0))
                        st.metric("图谱边数", stats.get('total_edges', 0))

                    # 获取知识库信息
                    kbs = api_client.list_knowledge_bases()
                    if kbs:
                        total_docs = sum(kb.get('document_count', 0) for kb in kbs)
                        st.metric("总文档数", total_docs)
                        st.metric("知识库数", len(kbs))

        # 系统健康状态
        st.markdown("---")
        st.subheader("🏥 系统健康检查")

        if st.button("完整健康检查", key="full_health_check"):
            with st.spinner("检查中..."):
                health_status = {}

                # 检查基础服务
                health = api_client.health_check()
                health_status['基础服务'] = "✅ 正常" if health else "❌ 异常"

                # 检查系统状态
                status = api_client.get_system_status()
                health_status['系统状态'] = "✅ 正常" if status and status.get('initialized') else "❌ 异常"

                # 检查知识库
                kbs = api_client.list_knowledge_bases()
                health_status['知识库'] = "✅ 正常" if kbs else "❌ 异常"

                # 检查语言设置
                lang_info = api_client.get_supported_languages()
                health_status['语言设置'] = "✅ 正常" if lang_info else "❌ 异常"

                # 显示健康状态
                st.subheader("🔍 健康检查结果")
                for component, status in health_status.items():
                    st.write(f"**{component}**: {status}")

                # 总体状态
                all_healthy = all("✅" in status for status in health_status.values())
                if all_healthy:
                    st.success("🎉 系统整体运行正常！")
                else:
                    st.error("⚠️ 系统存在异常，请检查相关组件")
