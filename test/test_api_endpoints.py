#!/usr/bin/env python3
"""
测试知识图谱可视化API端点
"""
import os
import sys
import json
import requests
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_endpoints():
    """测试知识图谱可视化API端点"""
    base_url = "http://localhost:8002"
    
    print("🧪 测试知识图谱可视化API端点...")
    
    # 测试健康检查
    print("\n0. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API服务正常运行")
        else:
            print(f"⚠️ API服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到API服务: {e}")
        print("💡 请先启动API服务: python main.py")
        return False
    
    # 测试获取图谱状态
    print("\n1. 测试获取图谱状态...")
    try:
        response = requests.get(f"{base_url}/knowledge-graph/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态获取成功: {data['data']['status']}")
            print(f"   XML文件存在: {data['data']['xml_file_exists']}")
            print(f"   JSON文件存在: {data['data']['json_file_exists']}")
            print(f"   知识库: {data['data']['knowledge_base']}")
        else:
            print(f"❌ 状态获取失败: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 状态获取异常: {e}")
    
    # 测试转换GraphML到JSON
    print("\n2. 测试转换GraphML到JSON...")
    try:
        response = requests.post(f"{base_url}/knowledge-graph/convert", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 转换成功: {data['message']}")
            if 'data' in data:
                print(f"   知识库: {data['data']['knowledge_base']}")
                print(f"   JSON文件大小: {data['data']['json_file_size']} bytes")
        else:
            print(f"⚠️ 转换响应: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 转换失败: {e}")
    
    # 测试获取图谱数据
    print("\n3. 测试获取图谱数据...")
    try:
        payload = {"knowledge_base": None, "format": "json"}
        response = requests.post(f"{base_url}/knowledge-graph/data", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            graph_data = data['data']
            print(f"✅ 数据获取成功:")
            print(f"   节点数: {graph_data['node_count']}")
            print(f"   边数: {graph_data['edge_count']}")
            print(f"   知识库: {graph_data['knowledge_base']}")
            print(f"   数据来源: {graph_data['data_source']}")
        else:
            print(f"⚠️ 数据获取响应: {response.status_code}")
            print(f"   响应: {response.text}")
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
        response = requests.post(f"{base_url}/knowledge-graph/visualize", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            viz_data = data['data']
            print(f"✅ 可视化生成成功:")
            print(f"   HTML内容长度: {len(viz_data.get('html_content', ''))}")
            print(f"   HTML文件路径: {viz_data.get('html_file_path', 'N/A')}")
            print(f"   节点数: {viz_data.get('node_count', 'N/A')}")
            print(f"   边数: {viz_data.get('edge_count', 'N/A')}")
            print(f"   知识库: {viz_data['knowledge_base']}")
        else:
            print(f"⚠️ 可视化生成响应: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
    
    # 测试列出图谱文件
    print("\n5. 测试列出图谱文件...")
    try:
        response = requests.get(f"{base_url}/knowledge-graph/files", timeout=10)
        if response.status_code == 200:
            data = response.json()
            files_data = data['data']
            print(f"✅ 文件列表获取成功:")
            print(f"   知识库: {files_data['knowledge_base']}")
            print(f"   总文件数: {files_data['total_files']}")
            
            for file_info in files_data['files']:
                print(f"   • {file_info['name']} ({file_info['type']}) - {file_info['size']} bytes")
        else:
            print(f"⚠️ 文件列表响应: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 文件列表获取失败: {e}")
    
    return True

def test_with_demo_kb():
    """测试演示知识库"""
    base_url = "http://localhost:8002"
    
    print("\n🎯 测试演示知识库 'demo_ai'...")
    
    # 测试获取demo_ai的状态
    try:
        response = requests.get(f"{base_url}/knowledge-graph/status?knowledge_base=demo_ai", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ demo_ai状态: {data['data']['status']}")
            print(f"   节点数据可用: {data['data']['json_file_exists']}")
        else:
            print(f"⚠️ demo_ai状态获取失败: {response.status_code}")
    except Exception as e:
        print(f"❌ demo_ai状态获取异常: {e}")
    
    # 测试生成demo_ai的可视化
    try:
        payload = {
            "knowledge_base": "demo_ai",
            "max_nodes": 100,
            "layout": "spring",
            "node_size_field": "degree",
            "edge_width_field": "weight"
        }
        response = requests.post(f"{base_url}/knowledge-graph/visualize", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            viz_data = data['data']
            print(f"✅ demo_ai可视化生成成功:")
            print(f"   节点数: {viz_data.get('node_count', 'N/A')}")
            print(f"   边数: {viz_data.get('edge_count', 'N/A')}")
            print(f"   HTML文件: {viz_data.get('html_file_path', 'N/A')}")
        else:
            print(f"⚠️ demo_ai可视化失败: {response.status_code}")
    except Exception as e:
        print(f"❌ demo_ai可视化异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试知识图谱可视化API")
    print("=" * 60)
    
    # 基础API测试
    api_ok = test_api_endpoints()
    
    if api_ok:
        # 演示知识库测试
        test_with_demo_kb()
    
    print("\n" + "=" * 60)
    if api_ok:
        print("🎉 API测试完成！")
        print("\n💡 提示:")
        print("   • 所有API端点都已测试")
        print("   • HTML文件已保存到对应知识库目录")
        print("   • 可以在Streamlit界面中查看可视化效果")
    else:
        print("❌ API测试失败")
        print("\n🔧 解决方案:")
        print("   • 确保API服务正在运行: python main.py")
        print("   • 检查端口8002是否可用")
        print("   • 查看服务日志排查问题")
    
    return api_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
