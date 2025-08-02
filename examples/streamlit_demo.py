#!/usr/bin/env python3
"""
Streamlit 界面演示脚本
展示如何使用可视化界面的各种功能
"""
import time
import webbrowser
import subprocess
import sys
from pathlib import Path

def main():
    """主演示函数"""
    print("🎨 GuiXiaoXiRag FastAPI Streamlit 界面演示")
    print("=" * 60)
    
    # 检查依赖
    print("1. 检查依赖...")
    try:
        import streamlit
        import plotly
        import pandas
        import numpy
        print(f"   ✅ Streamlit: {streamlit.__version__}")
        print(f"   ✅ Plotly: {plotly.__version__}")
        print(f"   ✅ Pandas: {pandas.__version__}")
        print(f"   ✅ Numpy: {numpy.__version__}")
    except ImportError as e:
        print(f"   ❌ 缺少依赖: {e}")
        print("   请运行: pip install streamlit plotly pandas numpy")
        return
    
    print("\n2. 启动说明...")
    print("   📋 启动方式:")
    print("   • python start_streamlit.py")
    print("   • streamlit run start_streamlit.py")
    print("   • streamlit run start_streamlit.py --server.port 8501")
    
    print("\n3. 界面功能:")
    features = [
        ("🏠 欢迎页面", "功能概览和快速导航"),
        ("📊 系统状态", "健康检查和系统信息"),
        ("📝 文档管理", "插入、上传、批量处理文档"),
        ("🔍 智能查询", "交互式查询界面"),
        ("🗄️ 知识库管理", "创建、切换、管理知识库"),
        ("🌍 语言设置", "多语言配置管理"),
        ("⚙️ 服务配置", "性能优化和配置管理"),
        ("📈 监控面板", "实时监控和数据可视化")
    ]
    
    for feature, description in features:
        print(f"   {feature}: {description}")
    
    print("\n4. 使用流程:")
    workflow = [
        "启动GuiXiaoXiRag FastAPI服务 (python main.py)",
        "启动Streamlit界面 (python start_streamlit.py)",
        "在浏览器中访问 http://localhost:8501",
        "使用界面进行文档管理和查询操作"
    ]
    
    for i, step in enumerate(workflow, 1):
        print(f"   {i}. {step}")
    
    print("\n5. 界面特性:")
    features = [
        "🎨 响应式设计，支持不同屏幕尺寸",
        "📊 交互式图表和数据可视化",
        "🔄 实时数据更新和自动刷新",
        "📁 文件拖拽上传支持",
        "📥 数据导出和下载功能",
        "🔍 智能搜索和过滤",
        "⚙️ 灵活的配置管理",
        "📈 实时性能监控"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n6. 最佳实践:")
    practices = [
        "确保GuiXiaoXiRag FastAPI服务正在运行",
        "使用Chrome或Firefox浏览器以获得最佳体验",
        "在稳定的网络环境下使用",
        "定期备份重要的知识库数据",
        "谨慎使用删除和重置功能"
    ]
    
    for practice in practices:
        print(f"   • {practice}")
    
    print("\n7. 故障排除:")
    troubleshooting = [
        ("界面无法启动", "检查依赖安装: pip install streamlit plotly pandas numpy"),
        ("无法连接API", "确保API服务运行: python main.py status"),
        ("界面显示异常", "清除浏览器缓存并刷新页面"),
        ("数据加载缓慢", "检查网络连接，减少查询数据量")
    ]
    
    for problem, solution in troubleshooting:
        print(f"   • {problem}: {solution}")
    
    print("\n🎉 演示完成！")
    print("📖 详细文档: docs/STREAMLIT_INTERFACE_GUIDE.md")
    print("🚀 立即体验: python start_streamlit.py")

if __name__ == "__main__":
    main()
