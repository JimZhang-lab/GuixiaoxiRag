#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI Streamlit 可视化界面启动文件
"""
import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    st.set_page_config(
        page_title="GuiXiaoXiRag FastAPI 管理界面",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 导入并运行主界面
    try:
        from streamlit_app.main_interface import run_main_interface
        run_main_interface()
    except ImportError as e:
        st.error(f"导入错误: {e}")
        st.error("请确保已安装所有依赖: pip install streamlit")
        st.stop()
    except Exception as e:
        st.error(f"启动失败: {e}")
        st.stop()

if __name__ == "__main__":
    main()
