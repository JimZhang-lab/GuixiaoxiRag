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
        "知识图谱可视化",
        "知识库管理",
        "语言设置",
        "服务配置",
        "缓存管理",
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
                    result = api_client.upload_file_with_kb(
                        file_content=file_content,
                        filename=uploaded_file.name,
                        knowledge_base=knowledge_base if knowledge_base != "默认" else None,
                        language=language
                    )
                    if result:
                        st.success(f"✅ 文件上传成功！")
                        st.info(f"文件名: {result.get('filename', uploaded_file.name)}")
                        st.info(f"文件大小: {result.get('file_size', len(file_content))} 字节")
                        st.info(f"知识库: {result.get('knowledge_base', '默认')}")
                        st.info(f"语言: {result.get('language', '中文')}")
                        st.info(f"跟踪ID: {result.get('track_id', 'N/A')}")
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 基础查询", "⚡ 优化查询", "📊 批量查询", "🔧 查询模式", "🛡️ 安全查询"])

    with tab1:
        st.subheader("🔍 基础查询")

        # 获取知识库和查询模式
        knowledge_bases = get_knowledge_base_options(api_client)
        # 动态获取查询模式（回退到默认列表）
        modes_info = api_client.get_query_modes() or {}
        modes = list((modes_info.get("modes") or {}).keys())
        default_mode = modes_info.get("default", "hybrid")
        if not modes:
            modes = ["hybrid", "local", "global", "naive", "mix", "bypass"]
        query_modes = modes

        with st.form("basic_query_form"):
            query_text = st.text_area(
                "查询内容",
                height=100,
                placeholder="请输入您的问题..."
            )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                # 使用后端推荐的默认模式作为初始选中
                default_index = 0
                if default_mode in query_modes:
                    default_index = query_modes.index(default_mode)
                mode = st.selectbox("查询模式", query_modes, index=default_index)
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
                # 使用后端默认模式
                opt_default_index = 0
                if default_mode in query_modes:
                    opt_default_index = query_modes.index(default_mode)
                mode = st.selectbox("查询模式", query_modes, key="opt_mode", index=opt_default_index)
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
                # 使用后端默认模式
                batch_default_index = 0
                if default_mode in query_modes:
                    batch_default_index = query_modes.index(default_mode)
                mode = st.selectbox("查询模式", query_modes, key="batch_mode", index=batch_default_index)
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

    with tab5:
        st.subheader("🛡️ 安全查询与意图分析")
        st.info("🔒 此功能包含内容安全检查和意图分析，可自动过滤违法违规内容")

        # 创建子标签页
        subtab1, subtab2 = st.tabs(["🛡️ 安全查询", "🧠 意图分析"])

        with subtab1:
            st.markdown("### 🛡️ 安全智能查询")

            knowledge_bases = get_knowledge_base_options(api_client)

            with st.form("safe_query_form"):
                safe_query = st.text_area(
                    "输入查询内容",
                    placeholder="请输入您的问题...",
                    height=100,
                    key="safe_query_input"
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    # 动态获取查询模式
                    safe_modes_info = api_client.get_query_modes() or {}
                    safe_modes = list((safe_modes_info.get("modes") or {}).keys())
                    if not safe_modes:
                        safe_modes = ["hybrid", "local", "global", "naive", "mix", "bypass"]
                    safe_mode = st.selectbox("查询模式", safe_modes, key="safe_mode")
                with col2:
                    safe_knowledge_base = st.selectbox("知识库", knowledge_bases, key="safe_kb")
                with col3:
                    safe_language = st.selectbox("查询语言", get_language_options(), key="safe_lang")

                # 安全选项
                with st.expander("🔧 安全选项"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        enable_intent_analysis = st.checkbox("启用意图分析", value=True)
                        enable_query_enhancement = st.checkbox("启用查询增强", value=True)
                    with col_b:
                        safety_check = st.checkbox("启用安全检查", value=True)

                safe_submitted = st.form_submit_button("🛡️ 安全查询")

                if safe_submitted and safe_query:
                    with st.spinner("安全查询中..."):
                        try:
                            result = api_client.safe_query(
                                query=safe_query,
                                mode=safe_mode,
                                knowledge_base=safe_knowledge_base if safe_knowledge_base != "默认" else None,
                                language=safe_language,
                                enable_intent_analysis=enable_intent_analysis,
                                enable_query_enhancement=enable_query_enhancement,
                                safety_check=safety_check
                            )

                            if result:
                                st.success("✅ 安全查询完成！")

                                # 显示查询分析结果
                                if "query_analysis" in result:
                                    analysis = result["query_analysis"]
                                    st.markdown("### 🧠 查询分析")

                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("意图类型", analysis.get("intent_type", "未知"))
                                    with col2:
                                        st.metric("安全级别", analysis.get("safety_level", "未知"))
                                    with col3:
                                        st.metric("置信度", f"{analysis.get('confidence', 0):.2%}")

                                    if analysis.get("enhanced_query"):
                                        st.markdown("**增强后的查询:**")
                                        st.info(analysis["enhanced_query"])

                                    if analysis.get("suggestions"):
                                        st.markdown("**改进建议:**")
                                        for suggestion in analysis["suggestions"]:
                                            st.write(f"• {suggestion}")

                                    # 安全提示与替代问法
                                    if analysis.get("safety_tips") or analysis.get("safe_alternatives"):
                                        st.markdown("**安全与合规提示:**")
                                        for tip in (analysis.get("safety_tips") or []):
                                            st.info(f"⚠️ {tip}")
                                        if analysis.get("safe_alternatives"):
                                            st.markdown("**建议改写:**")
                                            for alt in analysis["safe_alternatives"]:
                                                st.write(f"• {alt}")

                                # 显示查询结果
                                if "query_result" in result:
                                    query_result = result["query_result"]
                                    st.markdown("### 📝 查询结果")
                                    st.write(query_result.get("result", ""))

                                    if "sources" in query_result:
                                        st.markdown("### 📚 参考来源")
                                        for i, source in enumerate(query_result["sources"], 1):
                                            st.write(f"{i}. {source}")
                            else:
                                st.error("❌ 安全查询失败")

                        except Exception as e:
                            if "403" in str(e) or "查询内容" in str(e):
                                st.error("🚫 查询被拒绝：内容可能涉及违法违规信息")
                                st.warning("请重新表述您的问题，避免涉及敏感内容")
                            else:
                                st.error(f"❌ 查询失败: {str(e)}")

        with subtab2:
            st.markdown("### 🧠 查询意图分析")
            st.info("🔍 基于大模型的智能意图分析，检查内容安全性，并提供优化建议")

            with st.form("intent_analysis_form"):
                analysis_query = st.text_area(
                    "输入要分析的查询",
                    placeholder="请输入您想要分析的查询内容...",
                    height=100,
                    key="analysis_query_input"
                )

                # 分析选项
                col1, col2 = st.columns(2)
                with col1:
                    enable_enhancement = st.checkbox("启用查询增强", value=True, key="enable_enhancement")
                    safety_check = st.checkbox("启用安全检查", value=True, key="safety_check")
                with col2:
                    proceed_if_safe = st.checkbox("安全时直接执行查询", value=True, key="proceed_if_safe")
                    # 上下文设置
                    with st.expander("🔧 查询上下文"):
                        ctx_mode = st.selectbox("查询模式", ["hybrid", "local", "global", "naive"], key="ctx_mode")
                        ctx_kb = st.text_input("知识库", placeholder="可选", key="ctx_kb")
                        ctx_lang = st.selectbox("语言", ["中文", "English"], key="ctx_lang")

                analysis_submitted = st.form_submit_button("🧠 智能分析")

                if analysis_submitted and analysis_query:
                    with st.spinner("🧠 大模型智能分析中..."):
                        # 构建上下文
                        context = {}
                        if ctx_mode != "hybrid":
                            context["mode"] = ctx_mode
                        if ctx_kb:
                            context["knowledge_base"] = ctx_kb
                        if ctx_lang != "中文":
                            context["language"] = ctx_lang

                        # 调用分析接口
                        import requests
                        try:
                            response = requests.post(
                                f"{api_client.base_url}/query/analyze",
                                json={
                                    "query": analysis_query,
                                    "context": context if context else None,
                                    "enable_enhancement": enable_enhancement,
                                    "safety_check": safety_check,
                                    "proceed_if_safe": proceed_if_safe
                                }
                            )

                            if response.status_code == 200:
                                result = response.json()
                                if result.get("success"):
                                    analysis_result = result.get("data")
                                else:
                                    st.error(f"❌ 分析失败: {result.get('message', '未知错误')}")
                                    analysis_result = None
                            else:
                                st.error(f"❌ 请求失败: HTTP {response.status_code}")
                                analysis_result = None
                        except Exception as e:
                            st.error(f"❌ 分析失败: {str(e)}")
                            analysis_result = None

                        if analysis_result:
                            # 检查是否包含查询结果（proceed_if_safe=True时）
                            if "query_result" in analysis_result:
                                st.success("✅ 智能分析完成并已执行查询！")

                                # 显示查询结果
                                st.markdown("### 📝 查询结果")
                                query_result = analysis_result["query_result"]
                                st.write(query_result.get("result", ""))

                                if "sources" in query_result:
                                    st.markdown("### 📚 参考来源")
                                    for i, source in enumerate(query_result["sources"], 1):
                                        st.write(f"{i}. {source}")

                                # 显示分析信息（折叠）
                                with st.expander("🧠 详细分析信息"):
                                    analysis_data = analysis_result.get("query_analysis", analysis_result)
                                    self._render_analysis_details(analysis_data)
                            else:
                                st.success("✅ 智能分析完成！")
                                self._render_analysis_details(analysis_result)
                        else:
                            st.error("❌ 智能分析失败")

    def _render_analysis_details(self, analysis_result):
        """渲染分析详情"""
        # 基本信息
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**原始查询:**")
            st.code(analysis_result.get("original_query", ""))

            st.markdown("**处理后查询:**")
            st.code(analysis_result.get("processed_query", ""))

        with col2:
            st.metric("意图类型", analysis_result.get("intent_type", "未知"))
            st.metric("安全级别", analysis_result.get("safety_level", "未知"))
            st.metric("置信度", f"{analysis_result.get('confidence', 0):.2%}")

        # 增强查询
        if analysis_result.get("enhanced_query"):
            st.markdown("### ✨ 大模型增强查询")
            st.success(analysis_result["enhanced_query"])

        # 建议和风险因素
        col1, col2 = st.columns(2)

        with col1:
            if analysis_result.get("suggestions"):
                st.markdown("### 💡 智能建议")
                for suggestion in analysis_result["suggestions"]:
                    st.write(f"• {suggestion}")

            # 安全提示与替代问法
            if analysis_result.get("safety_tips") or analysis_result.get("safe_alternatives"):
                st.markdown("### 🛡️ 安全与合规提示")
                for tip in (analysis_result.get("safety_tips") or []):
                    st.info(f"⚠️ {tip}")
                if analysis_result.get("safe_alternatives"):
                    st.markdown("**大模型建议改写:**")
                    for alt in analysis_result["safe_alternatives"]:
                        st.write(f"• {alt}")

        with col2:
            if analysis_result.get("risk_factors"):
                st.markdown("### ⚠️ 风险因素")
                for risk in analysis_result["risk_factors"]:
                    st.warning(f"⚠️ {risk}")

        # 拒绝信息
        if analysis_result.get("should_reject"):
            st.error("🚫 查询被拒绝")
            if analysis_result.get("rejection_reason"):
                st.error(f"拒绝原因: {analysis_result['rejection_reason']}")


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


def render_knowledge_graph_visualization(api_client):
    """渲染知识图谱可视化界面"""
    st.subheader("🕸️ 知识图谱可视化")

    # 知识库选择
    col1, col2 = st.columns([2, 1])

    with col1:
        knowledge_bases = api_client.list_knowledge_bases()

        # 调试信息
        if st.checkbox("显示调试信息", value=False):
            st.write(f"🔍 知识库调试信息:")
            st.write(f"knowledge_bases类型: {type(knowledge_bases)}")
            st.write(f"knowledge_bases内容: {knowledge_bases}")

        if knowledge_bases:
            try:
                # knowledge_bases 是知识库列表
                if isinstance(knowledge_bases, list) and len(knowledge_bases) > 0:
                    if isinstance(knowledge_bases[0], dict):
                        kb_names = [kb["name"] for kb in knowledge_bases if isinstance(kb, dict) and "name" in kb]
                    else:
                        st.error(f"❌ 知识库数据格式错误，期望字典列表，实际得到: {type(knowledge_bases[0])}")
                        kb_names = []
                else:
                    kb_names = []

                selected_kb = st.selectbox(
                    "选择知识库",
                    ["default"] + kb_names,
                    help="选择要可视化的知识库"
                )
            except Exception as e:
                st.error(f"❌ 处理知识库列表时出错: {e}")
                selected_kb = st.text_input("知识库名称", value="default")
        else:
            selected_kb = st.text_input("知识库名称", value="default")

    with col2:
        if st.button("🔄 刷新状态"):
            st.rerun()

    # 获取图谱状态
    with st.spinner("检查图谱状态..."):
        try:
            graph_status = api_client.get_graph_status(selected_kb if selected_kb != "default" else None)
        except Exception as e:
            st.error(f"❌ 获取图谱状态时出错: {e}")
            return

    if not graph_status:
        st.error("❌ 无法获取图谱状态")
        return

    # 显示状态信息
    st.markdown("### 📊 图谱状态")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "XML文件",
            "存在" if graph_status["xml_file_exists"] else "不存在",
            f"{graph_status['xml_file_size']} bytes" if graph_status["xml_file_exists"] else None
        )

    with col2:
        st.metric(
            "JSON文件",
            "存在" if graph_status["json_file_exists"] else "不存在",
            f"{graph_status['json_file_size']} bytes" if graph_status["json_file_exists"] else None
        )

    with col3:
        status_color = {
            "up_to_date": "🟢",
            "json_missing": "🟡",
            "json_outdated": "🟠",
            "xml_missing": "🔴",
            "error": "🔴"
        }
        st.metric(
            "状态",
            f"{status_color.get(graph_status['status'], '❓')} {graph_status['status']}"
        )

    # 如果没有XML文件，显示提示
    if not graph_status["xml_file_exists"]:
        st.warning("⚠️ 该知识库还没有生成知识图谱，请先插入一些文档。")
        return

    # 可视化参数设置
    st.markdown("### ⚙️ 可视化设置")

    col1, col2, col3 = st.columns(3)

    with col1:
        max_nodes = st.slider("最大节点数", 10, 500, 100, help="限制显示的节点数量以提高性能")

    with col2:
        layout = st.selectbox(
            "布局算法",
            ["spring", "circular", "random", "shell"],
            help="选择图谱布局算法"
        )

    with col3:
        node_size_field = st.selectbox(
            "节点大小依据",
            ["degree", "betweenness", "closeness", "fixed"],
            help="节点大小的计算依据"
        )

    # 转换和可视化按钮
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 转换到JSON", help="将GraphML文件转换为JSON格式"):
            with st.spinner("转换中..."):
                try:
                    result = api_client.convert_graph_to_json(selected_kb if selected_kb != "default" else None)
                    if result:
                        st.success("✅ 转换成功！")
                        st.rerun()
                    else:
                        st.error("❌ 转换失败")
                except Exception as e:
                    st.error(f"❌ 转换时出错: {e}")

    with col2:
        if st.button("📊 获取图谱数据", help="获取图谱的节点和边数据"):
            with st.spinner("获取数据中..."):
                try:
                    graph_data = api_client.get_graph_data(selected_kb if selected_kb != "default" else None)
                    if graph_data:
                        st.session_state.graph_data = graph_data
                        st.success(f"✅ 获取成功！节点: {graph_data.get('node_count', 0)}, 边: {graph_data.get('edge_count', 0)}")
                    else:
                        st.error("❌ 获取数据失败")
                except Exception as e:
                    st.error(f"❌ 获取数据时出错: {e}")

    with col3:
        if st.button("🎨 生成可视化", help="生成交互式图谱可视化"):
            with st.spinner("生成可视化中..."):
                try:
                    viz_result = api_client.visualize_knowledge_graph(
                        knowledge_base=selected_kb if selected_kb != "default" else None,
                        max_nodes=max_nodes,
                        layout=layout,
                        node_size_field=node_size_field
                    )
                    if viz_result:
                        st.session_state.graph_visualization = viz_result
                        st.success("✅ 可视化生成成功！")
                    else:
                        st.error("❌ 可视化生成失败")
                except Exception as e:
                    st.error(f"❌ 生成可视化时出错: {e}")
                    import traceback
                    st.code(traceback.format_exc())

    # 显示图谱数据
    if 'graph_data' in st.session_state:
        st.markdown("### 📋 图谱数据")

        graph_data = st.session_state.graph_data

        tab1, tab2, tab3 = st.tabs(["📊 统计", "🔵 节点", "🔗 边"])

        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("节点总数", graph_data["node_count"])
            with col2:
                st.metric("边总数", graph_data["edge_count"])
            with col3:
                st.metric("知识库", graph_data["knowledge_base"])
            with col4:
                st.metric("数据来源", graph_data["data_source"])

        with tab2:
            if graph_data["nodes"]:
                nodes_df = pd.DataFrame(graph_data["nodes"])
                st.dataframe(nodes_df, use_container_width=True)

                # 节点类型分布
                if "entity_type" in nodes_df.columns:
                    type_counts = nodes_df["entity_type"].value_counts()
                    fig = px.pie(
                        values=type_counts.values,
                        names=type_counts.index,
                        title="节点类型分布"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("没有节点数据")

        with tab3:
            if graph_data["edges"]:
                edges_df = pd.DataFrame(graph_data["edges"])
                st.dataframe(edges_df, use_container_width=True)

                # 边权重分布
                if "weight" in edges_df.columns:
                    fig = px.histogram(
                        edges_df,
                        x="weight",
                        title="边权重分布",
                        nbins=20
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("没有边数据")

    # 显示可视化
    if 'graph_visualization' in st.session_state:
        st.markdown("### 🎨 交互式图谱可视化")

        viz_data = st.session_state.graph_visualization

        # 显示可视化统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📊 节点数: {viz_data.get('node_count', 'N/A')}")
        with col2:
            st.info(f"🔗 边数: {viz_data.get('edge_count', 'N/A')}")
        with col3:
            if "html_file_path" in viz_data:
                st.info(f"📁 文件: {viz_data['html_file_path'].split('/')[-1]}")
            else:
                st.info("📁 文件: N/A")

        # 显示HTML可视化
        if "html_content" in viz_data:
            st.components.v1.html(
                viz_data["html_content"],
                height=600,
                scrolling=True
            )
        else:
            st.error("❌ 可视化内容不可用")

        # 下载和文件信息
        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 下载可视化HTML"):
                st.download_button(
                    label="下载HTML文件",
                    data=viz_data["html_content"],
                    file_name=f"knowledge_graph_{selected_kb}_{int(time.time())}.html",
                    mime="text/html"
                )

        with col2:
            if "html_file_path" in viz_data:
                st.info(f"💡 HTML文件已保存到知识库目录:\n`{viz_data['html_file_path']}`")
            else:
                st.info("💡 HTML文件将保存到知识库目录")

    # 显示知识库文件列表
    st.markdown("### 📁 知识库文件")

    if st.button("🔄 刷新文件列表"):
        st.rerun()

    with st.spinner("获取文件列表..."):
        try:
            files_data = api_client.list_graph_files(selected_kb if selected_kb != "default" else None)
        except Exception as e:
            st.error(f"❌ 获取文件列表时出错: {e}")
            files_data = None

    if files_data:
        files = files_data.get("files", [])

        # 调试信息
        st.write(f"🔍 调试信息:")
        st.write(f"files_data类型: {type(files_data)}")
        st.write(f"files类型: {type(files)}")
        if files:
            st.write(f"files长度: {len(files)}")
            st.write(f"第一个文件类型: {type(files[0])}")
            st.write(f"第一个文件内容: {files[0]}")

        if files and len(files) > 0:
            # 检查文件数据格式
            if isinstance(files[0], dict):
                # 创建文件表格
                import datetime

                file_rows = []
                for file_info in files:
                    try:
                        modified_time = datetime.datetime.fromtimestamp(file_info["modified"]).strftime("%Y-%m-%d %H:%M:%S")
                        size_mb = file_info["size"] / (1024 * 1024)

                        file_rows.append({
                            "文件名": file_info["name"],
                            "类型": file_info["type"],
                            "大小(MB)": f"{size_mb:.2f}",
                            "修改时间": modified_time,
                            "相对路径": file_info["relative_path"]
                        })
                    except Exception as e:
                        st.error(f"处理文件信息时出错: {e}")
                        st.write(f"问题文件: {file_info}")

                if file_rows:
                    files_df = pd.DataFrame(file_rows)
                    st.dataframe(files_df, use_container_width=True)

                    # 文件统计
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        try:
                            graphml_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "GraphML"])
                            st.metric("GraphML文件", graphml_count)
                        except Exception as e:
                            st.error(f"统计GraphML文件时出错: {e}")
                    with col2:
                        try:
                            json_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "JSON"])
                            st.metric("JSON文件", json_count)
                        except Exception as e:
                            st.error(f"统计JSON文件时出错: {e}")
                    with col3:
                        try:
                            html_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "HTML"])
                            st.metric("HTML文件", html_count)
                        except Exception as e:
                            st.error(f"统计HTML文件时出错: {e}")
                    with col4:
                        try:
                            total_size = sum(f.get("size", 0) for f in files if isinstance(f, dict)) / (1024 * 1024)
                            st.metric("总大小(MB)", f"{total_size:.2f}")
                        except Exception as e:
                            st.error(f"计算总大小时出错: {e}")
            else:
                st.error(f"❌ 文件数据格式错误，期望字典列表，实际得到: {type(files[0])}")
        else:
            st.info("📂 该知识库中暂无图谱文件")
    else:
        st.error("❌ 无法获取文件列表")


def render_cache_management():
    """渲染缓存管理界面"""
    st.header("🗑️ 缓存管理")
    st.markdown("管理系统缓存，优化性能和内存使用")

    api_client = st.session_state.get('api_client')
    if not api_client:
        st.error("❌ API客户端未初始化")
        return

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📊 缓存统计", "🗑️ 缓存清理", "⚙️ 缓存设置"])

    with tab1:
        st.subheader("📊 缓存统计信息")

        # 刷新按钮
        if st.button("🔄 刷新统计", key="refresh_cache_stats"):
            st.rerun()

        # 获取缓存统计
        cache_stats = api_client.get_cache_stats()

        if cache_stats:
            # 系统内存信息
            st.subheader("💾 系统内存")
            system_memory = cache_stats.get("system_memory", {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "总内存",
                    f"{system_memory.get('total_mb', 0):.1f} MB"
                )
            with col2:
                st.metric(
                    "可用内存",
                    f"{system_memory.get('available_mb', 0):.1f} MB"
                )
            with col3:
                st.metric(
                    "使用率",
                    f"{system_memory.get('used_percent', 0):.1f}%"
                )

            # 进程内存信息
            st.subheader("🔧 进程内存")
            st.metric("当前进程内存", f"{cache_stats.get('total_memory_mb', 0):.2f} MB")

            # 各类缓存统计
            st.subheader("📦 缓存详情")
            caches = cache_stats.get("caches", {})

            if caches:
                for cache_name, cache_info in caches.items():
                    with st.expander(f"📁 {cache_name.upper()} 缓存"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("项目数量", cache_info.get("item_count", 0))
                        with col2:
                            st.metric("大小", f"{cache_info.get('size_mb', 0):.2f} MB")
                        with col3:
                            st.metric("命中率", f"{cache_info.get('hit_rate', 0):.1%}")
            else:
                st.info("📝 暂无缓存数据")
        else:
            st.error("❌ 无法获取缓存统计信息")

    with tab2:
        st.subheader("🗑️ 缓存清理")

        # 清理所有缓存
        st.markdown("### 🚨 清理所有缓存")
        st.warning("⚠️ 此操作将清理所有缓存数据，可能影响系统性能")

        if st.button("🗑️ 清理所有缓存", type="primary", key="clear_all_cache"):
            with st.spinner("正在清理所有缓存..."):
                result = api_client.clear_all_cache()

                if result:
                    st.success("✅ 所有缓存清理成功！")

                    # 显示清理结果
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("释放内存", f"{result.get('freed_memory_mb', 0):.2f} MB")
                    with col2:
                        st.metric("垃圾回收对象", result.get('gc_collected_objects', 0))

                    # 显示清理的缓存类型
                    cleared_caches = result.get('cleared_caches', [])
                    if cleared_caches:
                        st.write("**清理的缓存类型：**")
                        for cache in cleared_caches:
                            st.write(f"- {cache}")
                else:
                    st.error("❌ 清理缓存失败")

        st.markdown("---")

        # 清理指定类型缓存
        st.markdown("### 🎯 清理指定缓存")

        cache_types = {
            "llm": "🧠 LLM响应缓存",
            "vector": "📊 向量计算缓存",
            "knowledge_graph": "🕸️ 知识图谱缓存",
            "documents": "📄 文档处理缓存",
            "queries": "🔍 查询结果缓存"
        }

        selected_cache_type = st.selectbox(
            "选择要清理的缓存类型",
            options=list(cache_types.keys()),
            format_func=lambda x: cache_types[x],
            key="cache_type_selector"
        )

        if st.button(f"🗑️ 清理 {cache_types[selected_cache_type]}", key="clear_specific_cache"):
            with st.spinner(f"正在清理 {cache_types[selected_cache_type]}..."):
                result = api_client.clear_specific_cache(selected_cache_type)

                if result:
                    st.success(f"✅ {cache_types[selected_cache_type]} 清理成功！")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("清理项目数", result.get('cleared_items', 0))
                    with col2:
                        st.metric("释放内存", f"{result.get('freed_memory_mb', 0):.2f} MB")
                else:
                    st.error(f"❌ 清理 {cache_types[selected_cache_type]} 失败")

    with tab3:
        st.subheader("⚙️ 缓存设置")
        st.info("🚧 缓存设置功能正在开发中...")

        # 未来可以添加缓存配置选项
        st.markdown("""
        **计划中的功能：**
        - 缓存大小限制设置
        - 缓存过期时间配置
        - 自动清理策略
        - 缓存性能监控
        """)


def render_enhanced_service_config():
    """渲染增强的服务配置界面"""
    st.header("⚙️ 服务配置管理")
    st.markdown("动态管理服务配置，支持运行时更新")

    api_client = st.session_state.get('api_client')
    if not api_client:
        st.error("❌ API客户端未初始化")
        return

    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["📋 当前配置", "✏️ 配置更新", "📊 配置历史"])

    with tab1:
        st.subheader("📋 当前有效配置")

        # 刷新按钮
        if st.button("🔄 刷新配置", key="refresh_config"):
            st.rerun()

        # 获取有效配置
        config = api_client.get_effective_config()

        if config:
            # 应用基本信息
            st.subheader("📱 应用信息")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("应用名称", config.get('app_name', 'N/A'))
            with col2:
                st.metric("版本", config.get('version', 'N/A'))
            with col3:
                st.metric("端口", config.get('port', 'N/A'))

            # LLM配置
            st.subheader("🧠 LLM配置")
            llm_config = config.get('llm', {})
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("API地址", value=llm_config.get('api_base', ''), disabled=True)
                st.text_input("模型", value=llm_config.get('model', ''), disabled=True)
            with col2:
                st.text_input("API密钥", value=llm_config.get('api_key', ''), disabled=True, type="password")
                st.text_input("提供商", value=llm_config.get('provider', ''), disabled=True)

            # Embedding配置
            st.subheader("📊 Embedding配置")
            embedding_config = config.get('embedding', {})
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("API地址", value=embedding_config.get('api_base', ''), disabled=True, key="emb_api_base")
                st.text_input("模型", value=embedding_config.get('model', ''), disabled=True, key="emb_model")
            with col2:
                st.text_input("API密钥", value=embedding_config.get('api_key', ''), disabled=True, type="password", key="emb_api_key")
                st.number_input("维度", value=embedding_config.get('dim', 0), disabled=True, key="emb_dim")

            # 其他配置
            st.subheader("🔧 其他配置")
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("工作目录", value=config.get('working_dir', ''), disabled=True)
                st.text_input("日志级别", value=config.get('log_level', ''), disabled=True)
            with col2:
                st.number_input("最大文件大小(MB)", value=config.get('max_file_size_mb', 0), disabled=True)
                st.number_input("最大Token数", value=config.get('max_token_size', 0), disabled=True)
        else:
            st.error("❌ 无法获取配置信息")

    with tab2:
        st.subheader("✏️ 配置更新")
        st.markdown("动态更新服务配置，部分配置可能需要重启服务")

        # 配置更新表单
        with st.form("config_update_form"):
            st.markdown("#### 🧠 LLM配置")
            col1, col2 = st.columns(2)
            with col1:
                llm_api_base = st.text_input("LLM API地址", placeholder="http://localhost:8100/v1")
                llm_model = st.text_input("LLM模型", placeholder="qwen14b")
            with col2:
                llm_api_key = st.text_input("LLM API密钥", type="password", placeholder="your_api_key_here")
                llm_provider = st.selectbox("LLM提供商", ["", "openai", "azure", "ollama", "anthropic"])

            st.markdown("#### 📊 Embedding配置")
            col1, col2 = st.columns(2)
            with col1:
                emb_api_base = st.text_input("Embedding API地址", placeholder="http://localhost:8200/v1")
                emb_model = st.text_input("Embedding模型", placeholder="embedding_qwen")
            with col2:
                emb_api_key = st.text_input("Embedding API密钥", type="password", placeholder="your_api_key_here")
                emb_dim = st.number_input("Embedding维度", min_value=0, max_value=10000, value=0)

            st.markdown("#### 🔧 系统配置")
            col1, col2 = st.columns(2)
            with col1:
                log_level = st.selectbox("日志级别", ["", "DEBUG", "INFO", "WARNING", "ERROR"])
            with col2:
                max_token_size = st.number_input("最大Token数", min_value=0, value=0)

            # 提交按钮
            submitted = st.form_submit_button("🚀 更新配置", type="primary")

            if submitted:
                # 构建更新数据
                config_updates = {}

                if llm_api_base:
                    config_updates["openai_api_base"] = llm_api_base
                if llm_api_key:
                    config_updates["openai_chat_api_key"] = llm_api_key
                if llm_model:
                    config_updates["openai_chat_model"] = llm_model
                if llm_provider:
                    config_updates["custom_llm_provider"] = llm_provider

                if emb_api_base:
                    config_updates["openai_embedding_api_base"] = emb_api_base
                if emb_api_key:
                    config_updates["openai_embedding_api_key"] = emb_api_key
                if emb_model:
                    config_updates["openai_embedding_model"] = emb_model
                if emb_dim > 0:
                    config_updates["embedding_dim"] = emb_dim

                if log_level:
                    config_updates["log_level"] = log_level
                if max_token_size > 0:
                    config_updates["max_token_size"] = max_token_size

                if config_updates:
                    with st.spinner("正在更新配置..."):
                        result = api_client.update_config(config_updates)

                        if result:
                            st.success("✅ 配置更新成功！")

                            # 显示更新结果
                            updated_fields = result.get('updated_fields', [])
                            if updated_fields:
                                st.write("**更新的字段：**")
                                for field in updated_fields:
                                    st.write(f"- {field}")

                            # 重启提示
                            if result.get('restart_required', False):
                                st.warning("⚠️ 某些配置更改需要重启服务才能完全生效")

                            # 自动刷新页面显示新配置
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ 配置更新失败")
                else:
                    st.warning("⚠️ 请至少填写一个配置项")

    with tab3:
        st.subheader("📊 配置历史")
        st.info("🚧 配置历史功能正在开发中...")

        st.markdown("""
        **计划中的功能：**
        - 配置变更历史记录
        - 配置版本管理
        - 配置回滚功能
        - 配置对比工具
        """)
