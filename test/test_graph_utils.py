#!/usr/bin/env python3
"""
测试知识图谱工具函数
"""
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_graph_utils():
    """测试图谱工具函数"""
    print("🧪 测试知识图谱工具函数...")
    
    try:
        from server.utils import (
            check_knowledge_graph_files, 
            create_or_update_knowledge_graph_json,
            xml_to_json
        )
        
        # 测试工作目录
        working_dir = "./knowledgeBase/default"
        
        print(f"\n1. 测试检查文件状态 - {working_dir}")
        status = check_knowledge_graph_files(working_dir)
        print(f"   工作目录存在: {status['working_dir_exists']}")
        print(f"   XML文件存在: {status['xml_file_exists']}")
        print(f"   JSON文件存在: {status['json_file_exists']}")
        print(f"   状态: {status['status']}")
        
        if status['xml_file_exists']:
            print(f"   XML文件大小: {status['xml_file_size']} bytes")
            print(f"   XML文件路径: {status['xml_file_path']}")
            
            print(f"\n2. 测试XML到JSON转换")
            xml_file = status['xml_file_path']
            json_data = xml_to_json(xml_file)
            
            if json_data:
                print(f"   ✅ XML解析成功")
                print(f"   节点数: {len(json_data.get('nodes', []))}")
                print(f"   边数: {len(json_data.get('edges', []))}")
                
                # 显示节点信息
                nodes = json_data.get('nodes', [])
                if nodes:
                    print(f"   节点示例:")
                    for i, node in enumerate(nodes[:3]):
                        print(f"     {i+1}. ID: {node.get('id', 'N/A')}")
                        print(f"        类型: {node.get('entity_type', 'N/A')}")
                        print(f"        描述: {node.get('description', 'N/A')[:50]}...")
                
                # 显示边信息
                edges = json_data.get('edges', [])
                if edges:
                    print(f"   边示例:")
                    for i, edge in enumerate(edges[:3]):
                        print(f"     {i+1}. {edge.get('source', 'N/A')} -> {edge.get('target', 'N/A')}")
                        print(f"        权重: {edge.get('weight', 'N/A')}")
                        print(f"        描述: {edge.get('description', 'N/A')}")
            else:
                print(f"   ❌ XML解析失败")
            
            print(f"\n3. 测试完整转换流程")
            success = create_or_update_knowledge_graph_json(working_dir)
            if success:
                print(f"   ✅ 转换成功")
                
                # 检查生成的JSON文件
                json_file = os.path.join(working_dir, "graph_data.json")
                if os.path.exists(json_file):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                    print(f"   JSON文件大小: {os.path.getsize(json_file)} bytes")
                    print(f"   保存的节点数: {len(saved_data.get('nodes', []))}")
                    print(f"   保存的边数: {len(saved_data.get('edges', []))}")
            else:
                print(f"   ❌ 转换失败")
        else:
            print(f"   ⚠️ XML文件不存在，跳过转换测试")
        
        print(f"\n✅ 工具函数测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_generation():
    """测试可视化生成"""
    print("\n🧪 测试可视化生成...")
    
    try:
        # 检查依赖
        try:
            import pipmaster as pm
            if not pm.is_installed("pyvis"):
                print("   安装pyvis...")
                pm.install("pyvis")
            if not pm.is_installed("networkx"):
                print("   安装networkx...")
                pm.install("networkx")
        except:
            print("   ⚠️ pipmaster不可用，假设依赖已安装")
        
        import networkx as nx
        from pyvis.network import Network
        import tempfile
        import json
        
        # 读取JSON数据
        working_dir = "./knowledgeBase/default"
        json_file = os.path.join(working_dir, "graph_data.json")
        
        if not os.path.exists(json_file):
            print("   ❌ JSON文件不存在")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])
        
        print(f"   加载数据: {len(nodes)} 个节点, {len(edges)} 条边")
        
        # 创建NetworkX图
        G = nx.Graph()
        
        # 添加节点
        for node in nodes:
            G.add_node(
                node["id"],
                entity_type=node.get("entity_type", ""),
                description=node.get("description", ""),
                source_id=node.get("source_id", "")
            )
        
        # 添加边
        for edge in edges:
            if edge["source"] in G.nodes and edge["target"] in G.nodes:
                G.add_edge(
                    edge["source"],
                    edge["target"],
                    weight=edge.get("weight", 1.0),
                    description=edge.get("description", ""),
                    keywords=edge.get("keywords", "")
                )
        
        print(f"   NetworkX图创建: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")
        
        # 创建Pyvis网络
        net = Network(
            height="600px",
            width="100%",
            bgcolor="#ffffff",
            font_color="black",
            notebook=False
        )
        
        # 从NetworkX转换到Pyvis
        net.from_nx(G)
        
        # 自定义样式
        import random
        for i, node in enumerate(net.nodes):
            node["color"] = "#{:06x}".format(random.randint(0, 0xFFFFFF))

            # 获取节点ID
            node_id = node.get("id", node.get("label", ""))

            # 从原始图数据获取节点属性
            node_data = G.nodes.get(node_id, {})

            title_parts = [f"ID: {node_id}"]
            if "entity_type" in node_data and node_data["entity_type"]:
                title_parts.append(f"类型: {node_data['entity_type']}")
            if "description" in node_data and node_data["description"]:
                title_parts.append(f"描述: {node_data['description']}")
            node["title"] = "\\n".join(title_parts)

            # 设置节点大小
            degree = G.degree(node_id) if node_id in G.nodes else 1
            node["size"] = max(10, min(50, degree * 3))

        for i, edge in enumerate(net.edges):
            # 获取边的源和目标节点
            source = edge.get("from", "")
            target = edge.get("to", "")

            # 从原始图数据获取边属性
            if G.has_edge(source, target):
                edge_data = G.edges[source, target]

                if "description" in edge_data and edge_data["description"]:
                    edge["title"] = edge_data["description"]

                weight = edge_data.get("weight", 1.0)
                edge["width"] = max(1, min(10, weight * 2))
            else:
                edge["width"] = 2
        
        # 生成HTML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            net.save_graph(tmp_file.name)
            
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            print(f"   ✅ HTML生成成功: {len(html_content)} 字符")
            print(f"   临时文件: {tmp_file.name}")

            # 保存到知识库目录
            output_file = os.path.join(working_dir, "knowledge_graph_visualization.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   HTML文件保存到知识库目录: {output_file}")

            # 也保存一份到项目根目录用于测试
            test_output_file = "knowledge_graph_test.html"
            with open(test_output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"   测试HTML文件: {test_output_file}")

            # 清理临时文件
            os.unlink(tmp_file.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试知识图谱功能")
    print("=" * 50)
    
    # 测试工具函数
    utils_ok = test_graph_utils()
    
    # 测试可视化生成
    viz_ok = test_visualization_generation()
    
    print("\n" + "=" * 50)
    if utils_ok and viz_ok:
        print("🎉 所有测试通过！")
        print("\n📝 生成的文件:")
        print("   • knowledge_graph_test.html - 测试用可视化HTML文件")
        print("   • knowledgeBase/default/knowledge_graph_visualization.html - 知识库中的可视化文件")
        print("   • knowledgeBase/default/graph_data.json - 图谱JSON数据")
        print("\n💡 提示:")
        print("   • 在浏览器中打开任一HTML文件查看可视化效果")
        print("   • 可以拖拽节点、缩放、悬停查看详细信息")
        print("   • 知识库目录中的HTML文件会被API自动管理")
    else:
        print("❌ 部分测试失败")
    
    return utils_ok and viz_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
