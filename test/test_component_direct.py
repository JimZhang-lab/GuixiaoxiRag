#!/usr/bin/env python3
"""
直接测试组件函数
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_client_methods():
    """测试API客户端方法"""
    print("🔍 测试API客户端方法...")
    
    try:
        from streamlit_app.api_client import StreamlitAPIClient
        
        # 创建客户端
        client = StreamlitAPIClient("http://localhost:8002")
        
        print("\n1. 测试list_knowledge_bases...")
        try:
            kb_list = client.list_knowledge_bases()
            print(f"   返回类型: {type(kb_list)}")
            print(f"   返回值: {kb_list}")
            
            if kb_list:
                print(f"   列表长度: {len(kb_list)}")
                for i, kb in enumerate(kb_list):
                    print(f"   [{i}] 类型: {type(kb)}, 值: {kb}")
                    if isinstance(kb, dict) and "name" in kb:
                        print(f"       名称: {kb['name']}")
            
            # 测试列表推导式
            if kb_list and isinstance(kb_list, list):
                try:
                    kb_names = [kb["name"] for kb in kb_list if isinstance(kb, dict) and "name" in kb]
                    print(f"   提取的名称: {kb_names}")
                except Exception as e:
                    print(f"   ❌ 列表推导式失败: {e}")
                    
        except Exception as e:
            print(f"   ❌ list_knowledge_bases失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n2. 测试list_graph_files...")
        try:
            files_data = client.list_graph_files()
            print(f"   返回类型: {type(files_data)}")
            print(f"   返回值: {files_data}")
            
            if files_data:
                files = files_data.get("files", [])
                print(f"   files类型: {type(files)}")
                print(f"   files内容: {files}")
                
                if files:
                    print(f"   files长度: {len(files)}")
                    for i, f in enumerate(files):
                        print(f"   [{i}] 类型: {type(f)}, 值: {f}")
                
                # 测试列表推导式
                if files and isinstance(files, list):
                    try:
                        graphml_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "GraphML"])
                        print(f"   GraphML文件数: {graphml_count}")
                    except Exception as e:
                        print(f"   ❌ 文件统计失败: {e}")
                        
        except Exception as e:
            print(f"   ❌ list_graph_files失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n3. 测试get_graph_data...")
        try:
            graph_data = client.get_graph_data()
            print(f"   返回类型: {type(graph_data)}")
            
            if graph_data:
                print(f"   数据键: {list(graph_data.keys())}")
                
                nodes = graph_data.get("nodes", [])
                edges = graph_data.get("edges", [])
                
                print(f"   nodes类型: {type(nodes)}, 长度: {len(nodes)}")
                print(f"   edges类型: {type(edges)}, 长度: {len(edges)}")
                
                if nodes:
                    print(f"   第一个节点: {nodes[0]}")
                if edges:
                    print(f"   第一个边: {edges[0]}")
                    
        except Exception as e:
            print(f"   ❌ get_graph_data失败: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ API客户端测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_mock_data():
    """测试模拟数据"""
    print("\n🧪 测试模拟数据处理...")
    
    # 模拟API返回的数据
    mock_kb_list = [
        {"name": "default", "path": "./knowledgeBase/default"},
        {"name": "demo_ai", "path": "./knowledgeBase/demo_ai"}
    ]
    
    mock_files_data = {
        "knowledge_base": "default",
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
    
    print("1. 测试知识库列表处理...")
    try:
        kb_names = [kb["name"] for kb in mock_kb_list if isinstance(kb, dict) and "name" in kb]
        print(f"   ✅ 知识库名称提取成功: {kb_names}")
    except Exception as e:
        print(f"   ❌ 知识库名称提取失败: {e}")
    
    print("\n2. 测试文件列表处理...")
    try:
        files = mock_files_data.get("files", [])
        print(f"   files类型: {type(files)}")
        print(f"   files长度: {len(files)}")
        
        # 测试文件统计
        graphml_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "GraphML"])
        json_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "JSON"])
        html_count = len([f for f in files if isinstance(f, dict) and f.get("type") == "HTML"])
        total_size = sum(f.get("size", 0) for f in files if isinstance(f, dict)) / (1024 * 1024)
        
        print(f"   ✅ 文件统计成功:")
        print(f"      GraphML: {graphml_count}")
        print(f"      JSON: {json_count}")
        print(f"      HTML: {html_count}")
        print(f"      总大小: {total_size:.2f} MB")
        
    except Exception as e:
        print(f"   ❌ 文件列表处理失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试函数"""
    print("🔍 直接测试组件函数")
    print("=" * 60)
    
    # 测试模拟数据
    test_mock_data()
    
    # 测试API客户端（需要API服务运行）
    print("\n" + "=" * 60)
    print("⚠️ 以下测试需要API服务运行在 http://localhost:8002")
    input("按Enter键继续API测试，或Ctrl+C取消...")
    
    test_api_client_methods()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成")

if __name__ == "__main__":
    main()
