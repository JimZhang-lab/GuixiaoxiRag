#!/usr/bin/env python3
"""
调试Streamlit界面错误
"""
import os
import sys
import traceback
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_client():
    """测试API客户端方法"""
    print("🔍 测试API客户端方法...")
    
    try:
        from streamlit_app.api_client import APIClient
        
        # 创建API客户端
        client = APIClient("http://localhost:8002")
        
        print("\n1. 测试list_knowledge_bases...")
        try:
            kb_list = client.list_knowledge_bases()
            print(f"   返回类型: {type(kb_list)}")
            print(f"   返回值: {kb_list}")
            
            if kb_list:
                print(f"   列表长度: {len(kb_list)}")
                if len(kb_list) > 0:
                    print(f"   第一个元素类型: {type(kb_list[0])}")
                    print(f"   第一个元素: {kb_list[0]}")
                    
                    # 测试访问name字段
                    try:
                        name = kb_list[0]["name"]
                        print(f"   第一个知识库名称: {name}")
                    except Exception as e:
                        print(f"   ❌ 访问name字段失败: {e}")
            else:
                print("   返回空列表或None")
                
        except Exception as e:
            print(f"   ❌ list_knowledge_bases失败: {e}")
            traceback.print_exc()
        
        print("\n2. 测试get_graph_status...")
        try:
            status = client.get_graph_status()
            print(f"   返回类型: {type(status)}")
            print(f"   返回值: {status}")
        except Exception as e:
            print(f"   ❌ get_graph_status失败: {e}")
            traceback.print_exc()
        
        print("\n3. 测试get_graph_data...")
        try:
            data = client.get_graph_data()
            print(f"   返回类型: {type(data)}")
            if data:
                print(f"   数据键: {data.keys()}")
                if "nodes" in data:
                    print(f"   节点类型: {type(data['nodes'])}")
                    print(f"   节点数量: {len(data['nodes'])}")
                if "edges" in data:
                    print(f"   边类型: {type(data['edges'])}")
                    print(f"   边数量: {len(data['edges'])}")
        except Exception as e:
            print(f"   ❌ get_graph_data失败: {e}")
            traceback.print_exc()
        
        print("\n4. 测试list_graph_files...")
        try:
            files = client.list_graph_files()
            print(f"   返回类型: {type(files)}")
            print(f"   返回值: {files}")
            
            if files and "files" in files:
                file_list = files["files"]
                print(f"   文件列表类型: {type(file_list)}")
                print(f"   文件数量: {len(file_list)}")
                if len(file_list) > 0:
                    print(f"   第一个文件: {file_list[0]}")
        except Exception as e:
            print(f"   ❌ list_graph_files失败: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ API客户端测试失败: {e}")
        traceback.print_exc()

def test_component_functions():
    """测试组件函数"""
    print("\n🧪 测试组件函数...")
    
    try:
        # 模拟streamlit环境
        import streamlit as st
        
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
                        }
                    ],
                    "total_files": 1
                }
        
        mock_client = MockAPIClient()
        
        print("\n1. 测试知识库列表处理...")
        try:
            kb_list = mock_client.list_knowledge_bases()
            print(f"   知识库列表: {kb_list}")
            
            # 模拟组件中的处理逻辑
            if kb_list:
                kb_names = [kb["name"] for kb in kb_list]
                print(f"   提取的名称: {kb_names}")
            
        except Exception as e:
            print(f"   ❌ 知识库列表处理失败: {e}")
            traceback.print_exc()
        
        print("\n2. 测试图谱数据处理...")
        try:
            graph_data = mock_client.get_graph_data()
            print(f"   图谱数据: {graph_data}")
            
            # 模拟组件中的处理逻辑
            if graph_data["nodes"]:
                import pandas as pd
                nodes_df = pd.DataFrame(graph_data["nodes"])
                print(f"   节点DataFrame: {nodes_df.shape}")
                
        except Exception as e:
            print(f"   ❌ 图谱数据处理失败: {e}")
            traceback.print_exc()
        
        print("\n3. 测试文件列表处理...")
        try:
            files_data = mock_client.list_graph_files()
            print(f"   文件数据: {files_data}")
            
            # 模拟组件中的处理逻辑
            files = files_data.get("files", [])
            if files:
                import datetime
                
                file_rows = []
                for file_info in files:
                    modified_time = datetime.datetime.fromtimestamp(file_info["modified"]).strftime("%Y-%m-%d %H:%M:%S")
                    size_mb = file_info["size"] / (1024 * 1024)
                    
                    file_rows.append({
                        "文件名": file_info["name"],
                        "类型": file_info["type"],
                        "大小(MB)": f"{size_mb:.2f}",
                        "修改时间": modified_time,
                        "相对路径": file_info["relative_path"]
                    })
                
                print(f"   处理后的文件行: {file_rows}")
                
        except Exception as e:
            print(f"   ❌ 文件列表处理失败: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 组件函数测试失败: {e}")
        traceback.print_exc()

def main():
    """主调试函数"""
    print("🐛 Streamlit界面错误调试")
    print("=" * 60)
    
    # 测试API客户端
    test_api_client()
    
    # 测试组件函数
    test_component_functions()
    
    print("\n" + "=" * 60)
    print("🔍 调试完成")
    print("\n💡 如果发现问题:")
    print("   1. 检查API服务是否正常运行")
    print("   2. 确认返回数据格式是否正确")
    print("   3. 查看具体的错误堆栈信息")
    print("   4. 检查数据类型是否匹配")

if __name__ == "__main__":
    main()
