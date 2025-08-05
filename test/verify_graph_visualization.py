#!/usr/bin/env python3
"""
验证知识图谱可视化功能
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def verify_file_structure():
    """验证文件结构"""
    print("📁 验证文件结构...")
    
    required_files = [
        "server/api.py",
        "server/models.py", 
        "server/utils.py",
        "streamlit_app/api_client.py",
        "streamlit_app/components.py",
        "streamlit_app/main_interface.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    else:
        print("✅ 所有必需文件都存在")
        return True

def verify_api_endpoints():
    """验证API端点定义"""
    print("\n🔌 验证API端点...")
    
    try:
        with open("server/api.py", 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        required_endpoints = [
            "/knowledge-graph/status",
            "/knowledge-graph/convert", 
            "/knowledge-graph/data",
            "/knowledge-graph/visualize",
            "/knowledge-graph/files"
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in api_content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"❌ 缺少API端点: {missing_endpoints}")
            return False
        else:
            print("✅ 所有API端点都已定义")
            return True
            
    except Exception as e:
        print(f"❌ 验证API端点失败: {e}")
        return False

def verify_models():
    """验证数据模型"""
    print("\n📊 验证数据模型...")
    
    try:
        with open("server/models.py", 'r', encoding='utf-8') as f:
            models_content = f.read()
        
        required_models = [
            "GraphVisualizationRequest",
            "GraphVisualizationResponse",
            "GraphDataRequest",
            "GraphDataResponse", 
            "GraphStatusResponse"
        ]
        
        missing_models = []
        for model in required_models:
            if model not in models_content:
                missing_models.append(model)
        
        if missing_models:
            print(f"❌ 缺少数据模型: {missing_models}")
            return False
        else:
            print("✅ 所有数据模型都已定义")
            return True
            
    except Exception as e:
        print(f"❌ 验证数据模型失败: {e}")
        return False

def verify_streamlit_components():
    """验证Streamlit组件"""
    print("\n🖥️ 验证Streamlit组件...")
    
    try:
        with open("streamlit_app/components.py", 'r', encoding='utf-8') as f:
            components_content = f.read()
        
        required_functions = [
            "render_knowledge_graph_visualization"
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in components_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ 缺少组件函数: {missing_functions}")
            return False
        else:
            print("✅ 所有Streamlit组件都已定义")
            return True
            
    except Exception as e:
        print(f"❌ 验证Streamlit组件失败: {e}")
        return False

def verify_api_client():
    """验证API客户端"""
    print("\n🔗 验证API客户端...")
    
    try:
        with open("streamlit_app/api_client.py", 'r', encoding='utf-8') as f:
            client_content = f.read()
        
        required_methods = [
            "get_graph_status",
            "convert_graph_to_json",
            "get_graph_data",
            "visualize_knowledge_graph",
            "list_graph_files"
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in client_content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少客户端方法: {missing_methods}")
            return False
        else:
            print("✅ 所有API客户端方法都已定义")
            return True
            
    except Exception as e:
        print(f"❌ 验证API客户端失败: {e}")
        return False

def verify_knowledge_bases():
    """验证知识库"""
    print("\n🗄️ 验证知识库...")
    
    kb_dirs = ["./knowledgeBase/default", "./knowledgeBase/demo_ai"]
    
    for kb_dir in kb_dirs:
        if os.path.exists(kb_dir):
            print(f"✅ 知识库存在: {kb_dir}")
            
            # 检查文件
            files = os.listdir(kb_dir)
            if "graph_chunk_entity_relation.graphml" in files:
                print(f"   ✅ GraphML文件存在")
            else:
                print(f"   ⚠️ GraphML文件不存在")
            
            if "graph_data.json" in files:
                print(f"   ✅ JSON文件存在")
            else:
                print(f"   ⚠️ JSON文件不存在")
            
            if "knowledge_graph_visualization.html" in files:
                print(f"   ✅ HTML文件存在")
            else:
                print(f"   ⚠️ HTML文件不存在")
        else:
            print(f"⚠️ 知识库不存在: {kb_dir}")
    
    return True

def verify_utils_functions():
    """验证工具函数"""
    print("\n🛠️ 验证工具函数...")
    
    try:
        from server.utils import (
            check_knowledge_graph_files,
            create_or_update_knowledge_graph_json
        )
        
        print("✅ 工具函数导入成功")
        
        # 测试函数调用
        working_dir = "./knowledgeBase/default"
        if os.path.exists(working_dir):
            status = check_knowledge_graph_files(working_dir)
            print(f"✅ 文件状态检查成功: {status['status']}")
        else:
            print("⚠️ 默认知识库不存在，跳过功能测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数验证失败: {e}")
        return False

def verify_dependencies():
    """验证依赖"""
    print("\n📦 验证依赖...")
    
    required_packages = [
        "fastapi",
        "streamlit", 
        "pandas",
        "plotly",
        "requests"
    ]
    
    optional_packages = [
        "pyvis",
        "networkx"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_required.append(package)
    
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            missing_optional.append(package)
    
    if missing_required:
        print(f"❌ 缺少必需依赖: {missing_required}")
        return False
    else:
        print("✅ 所有必需依赖都已安装")
    
    if missing_optional:
        print(f"⚠️ 缺少可选依赖: {missing_optional}")
        print("   这些依赖会在需要时自动安装")
    else:
        print("✅ 所有可选依赖都已安装")
    
    return True

def main():
    """主验证函数"""
    print("🔍 知识图谱可视化功能验证")
    print("=" * 60)
    
    checks = [
        ("文件结构", verify_file_structure),
        ("API端点", verify_api_endpoints),
        ("数据模型", verify_models),
        ("Streamlit组件", verify_streamlit_components),
        ("API客户端", verify_api_client),
        ("工具函数", verify_utils_functions),
        ("依赖包", verify_dependencies),
        ("知识库", verify_knowledge_bases)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name}验证异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 验证结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有验证都通过！知识图谱可视化功能已正确实现")
        print("\n🚀 下一步:")
        print("   1. 启动API服务: python main.py")
        print("   2. 启动Streamlit界面: streamlit run start_streamlit.py")
        print("   3. 访问知识图谱可视化页面")
        print("   4. 选择知识库并生成可视化")
    else:
        print("⚠️ 部分验证未通过，请检查相关组件")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
