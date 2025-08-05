#!/usr/bin/env python3
"""
测试知识图谱可视化功能
"""
import os
import sys
import json
import requests
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_endpoints():
    """测试知识图谱可视化API端点"""
    base_url = "http://localhost:8002"
    
    print("🧪 测试知识图谱可视化API端点...")
    
    # 测试获取图谱状态
    print("\n1. 测试获取图谱状态...")
    try:
        response = requests.get(f"{base_url}/knowledge-graph/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态获取成功: {data['data']['status']}")
            print(f"   XML文件存在: {data['data']['xml_file_exists']}")
            print(f"   JSON文件存在: {data['data']['json_file_exists']}")
        else:
            print(f"❌ 状态获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 测试转换GraphML到JSON
    print("\n2. 测试转换GraphML到JSON...")
    try:
        response = requests.post(f"{base_url}/knowledge-graph/convert")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 转换成功: {data['message']}")
        else:
            print(f"⚠️ 转换响应: {response.status_code} - 可能是文件不存在")
    except Exception as e:
        print(f"❌ 转换失败: {e}")
    
    # 测试获取图谱数据
    print("\n3. 测试获取图谱数据...")
    try:
        payload = {"knowledge_base": None, "format": "json"}
        response = requests.post(f"{base_url}/knowledge-graph/data", json=payload)
        if response.status_code == 200:
            data = response.json()
            graph_data = data['data']
            print(f"✅ 数据获取成功:")
            print(f"   节点数: {graph_data['node_count']}")
            print(f"   边数: {graph_data['edge_count']}")
            print(f"   知识库: {graph_data['knowledge_base']}")
        else:
            print(f"⚠️ 数据获取响应: {response.status_code}")
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
    
    # 测试生成可视化
    print("\n4. 测试生成可视化...")
    try:
        payload = {
            "knowledge_base": None,
            "max_nodes": 50,
            "layout": "spring",
            "node_size_field": "degree",
            "edge_width_field": "weight"
        }
        response = requests.post(f"{base_url}/knowledge-graph/visualize", json=payload)
        if response.status_code == 200:
            data = response.json()
            viz_data = data['data']
            print(f"✅ 可视化生成成功:")
            print(f"   HTML内容长度: {len(viz_data.get('html_content', ''))}")
            print(f"   知识库: {viz_data['knowledge_base']}")
            
            # 保存HTML文件用于测试
            html_content = viz_data.get('html_content', '')
            if html_content:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                    f.write(html_content)
                    print(f"   HTML文件保存到: {f.name}")
        else:
            print(f"⚠️ 可视化生成响应: {response.status_code}")
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
    
    return True

def test_utils_functions():
    """测试工具函数"""
    print("\n🧪 测试工具函数...")
    
    try:
        from server.utils import check_knowledge_graph_files, create_or_update_knowledge_graph_json
        
        # 测试检查文件状态
        print("\n1. 测试检查文件状态...")
        working_dir = "./knowledgeBase/default"
        status = check_knowledge_graph_files(working_dir)
        print(f"✅ 文件状态检查完成:")
        print(f"   工作目录存在: {status['working_dir_exists']}")
        print(f"   XML文件存在: {status['xml_file_exists']}")
        print(f"   JSON文件存在: {status['json_file_exists']}")
        print(f"   状态: {status['status']}")
        
        # 如果XML文件存在，测试转换
        if status['xml_file_exists']:
            print("\n2. 测试XML到JSON转换...")
            success = create_or_update_knowledge_graph_json(working_dir)
            if success:
                print("✅ 转换成功")
            else:
                print("❌ 转换失败")
        else:
            print("\n⚠️ 跳过转换测试 - XML文件不存在")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def create_sample_data():
    """创建示例数据用于测试"""
    print("\n🧪 创建示例数据...")
    
    try:
        # 确保知识库目录存在
        kb_dir = Path("./knowledgeBase/default")
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建示例GraphML文件
        sample_graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d1" for="node" attr.name="entity_type" attr.type="string"/>
  <key id="d2" for="node" attr.name="description" attr.type="string"/>
  <key id="d3" for="node" attr.name="source_id" attr.type="string"/>
  <key id="d5" for="edge" attr.name="weight" attr.type="double"/>
  <key id="d6" for="edge" attr.name="description" attr.type="string"/>
  <key id="d7" for="edge" attr.name="keywords" attr.type="string"/>
  <key id="d8" for="edge" attr.name="source_id" attr.type="string"/>
  <graph id="G" edgedefault="undirected">
    <node id="人工智能">
      <data key="d1">概念</data>
      <data key="d2">计算机科学的一个分支</data>
      <data key="d3">doc1</data>
    </node>
    <node id="机器学习">
      <data key="d1">技术</data>
      <data key="d2">人工智能的一个子领域</data>
      <data key="d3">doc1</data>
    </node>
    <node id="深度学习">
      <data key="d1">技术</data>
      <data key="d2">机器学习的一个分支</data>
      <data key="d3">doc1</data>
    </node>
    <edge source="人工智能" target="机器学习">
      <data key="d5">0.8</data>
      <data key="d6">包含关系</data>
      <data key="d7">AI,ML</data>
      <data key="d8">doc1</data>
    </edge>
    <edge source="机器学习" target="深度学习">
      <data key="d5">0.9</data>
      <data key="d6">包含关系</data>
      <data key="d7">ML,DL</data>
      <data key="d8">doc1</data>
    </edge>
  </graph>
</graphml>"""
        
        graphml_file = kb_dir / "graph_chunk_entity_relation.graphml"
        with open(graphml_file, 'w', encoding='utf-8') as f:
            f.write(sample_graphml)
        
        print(f"✅ 示例GraphML文件创建: {graphml_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试知识图谱可视化功能")
    print("=" * 50)
    
    # 创建示例数据
    if not create_sample_data():
        print("❌ 示例数据创建失败，跳过部分测试")
    
    # 测试工具函数
    test_utils_functions()
    
    # 测试API端点
    print("\n" + "=" * 50)
    print("⚠️ 请确保API服务正在运行 (python main.py)")
    input("按Enter键继续API测试...")
    
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n📝 使用说明:")
    print("1. 启动API服务: python main.py")
    print("2. 启动Streamlit界面: streamlit run start_streamlit.py")
    print("3. 在浏览器中访问知识图谱可视化页面")
    print("4. 选择知识库，检查状态，生成可视化")

if __name__ == "__main__":
    main()
