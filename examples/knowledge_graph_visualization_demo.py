#!/usr/bin/env python3
"""
知识图谱可视化功能演示
"""
import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_demo_knowledge_base():
    """创建演示用的知识库"""
    print("🏗️ 创建演示知识库...")
    
    kb_name = "demo_ai"
    kb_dir = Path(f"./knowledgeBase/{kb_name}")
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建更丰富的示例GraphML文件
    demo_graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="d1" for="node" attr.name="entity_type" attr.type="string"/>
  <key id="d2" for="node" attr.name="description" attr.type="string"/>
  <key id="d3" for="node" attr.name="source_id" attr.type="string"/>
  <key id="d5" for="edge" attr.name="weight" attr.type="double"/>
  <key id="d6" for="edge" attr.name="description" attr.type="string"/>
  <key id="d7" for="edge" attr.name="keywords" attr.type="string"/>
  <key id="d8" for="edge" attr.name="source_id" attr.type="string"/>
  <graph id="G" edgedefault="undirected">
    <!-- AI领域核心概念 -->
    <node id="人工智能">
      <data key="d1">领域</data>
      <data key="d2">计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统</data>
      <data key="d3">ai_overview</data>
    </node>
    <node id="机器学习">
      <data key="d1">技术</data>
      <data key="d2">人工智能的一个子领域，使计算机能够在没有明确编程的情况下学习</data>
      <data key="d3">ml_intro</data>
    </node>
    <node id="深度学习">
      <data key="d1">技术</data>
      <data key="d2">机器学习的一个分支，使用多层神经网络来模拟人脑的工作方式</data>
      <data key="d3">dl_basics</data>
    </node>
    <node id="神经网络">
      <data key="d1">模型</data>
      <data key="d2">受生物神经网络启发的计算模型，由相互连接的节点组成</data>
      <data key="d3">nn_structure</data>
    </node>
    <node id="自然语言处理">
      <data key="d1">应用</data>
      <data key="d2">人工智能的一个分支，专注于计算机与人类语言之间的交互</data>
      <data key="d3">nlp_overview</data>
    </node>
    <node id="计算机视觉">
      <data key="d1">应用</data>
      <data key="d2">人工智能的一个分支，使计算机能够理解和解释视觉信息</data>
      <data key="d3">cv_intro</data>
    </node>
    <node id="强化学习">
      <data key="d1">技术</data>
      <data key="d2">机器学习的一个分支，通过与环境交互来学习最优行为</data>
      <data key="d3">rl_basics</data>
    </node>
    <node id="大语言模型">
      <data key="d1">模型</data>
      <data key="d2">基于深度学习的语言模型，能够理解和生成人类语言</data>
      <data key="d3">llm_overview</data>
    </node>
    
    <!-- 关系定义 -->
    <edge source="人工智能" target="机器学习">
      <data key="d5">0.9</data>
      <data key="d6">包含关系</data>
      <data key="d7">AI,ML,子领域</data>
      <data key="d8">ai_overview</data>
    </edge>
    <edge source="机器学习" target="深度学习">
      <data key="d5">0.8</data>
      <data key="d6">包含关系</data>
      <data key="d7">ML,DL,神经网络</data>
      <data key="d8">ml_intro</data>
    </edge>
    <edge source="深度学习" target="神经网络">
      <data key="d5">0.9</data>
      <data key="d6">基于关系</data>
      <data key="d7">DL,NN,架构</data>
      <data key="d8">dl_basics</data>
    </edge>
    <edge source="人工智能" target="自然语言处理">
      <data key="d5">0.7</data>
      <data key="d6">应用领域</data>
      <data key="d7">AI,NLP,语言</data>
      <data key="d8">nlp_overview</data>
    </edge>
    <edge source="人工智能" target="计算机视觉">
      <data key="d5">0.7</data>
      <data key="d6">应用领域</data>
      <data key="d7">AI,CV,视觉</data>
      <data key="d8">cv_intro</data>
    </edge>
    <edge source="机器学习" target="强化学习">
      <data key="d5">0.6</data>
      <data key="d6">包含关系</data>
      <data key="d7">ML,RL,学习</data>
      <data key="d8">rl_basics</data>
    </edge>
    <edge source="深度学习" target="大语言模型">
      <data key="d5">0.8</data>
      <data key="d6">技术基础</data>
      <data key="d7">DL,LLM,语言模型</data>
      <data key="d8">llm_overview</data>
    </edge>
    <edge source="自然语言处理" target="大语言模型">
      <data key="d5">0.9</data>
      <data key="d6">应用实现</data>
      <data key="d7">NLP,LLM,语言理解</data>
      <data key="d8">llm_overview</data>
    </edge>
  </graph>
</graphml>"""
    
    graphml_file = kb_dir / "graph_chunk_entity_relation.graphml"
    with open(graphml_file, 'w', encoding='utf-8') as f:
        f.write(demo_graphml)
    
    print(f"✅ 演示知识库创建完成: {kb_dir}")
    print(f"   GraphML文件: {graphml_file}")
    return kb_name, str(kb_dir)

def demo_graph_processing():
    """演示图谱处理功能"""
    print("\n🔄 演示图谱处理功能...")
    
    # 创建演示知识库
    kb_name, kb_dir = create_demo_knowledge_base()
    
    try:
        from server.utils import (
            check_knowledge_graph_files,
            create_or_update_knowledge_graph_json
        )
        
        # 检查文件状态
        print(f"\n1. 检查知识库状态: {kb_name}")
        status = check_knowledge_graph_files(kb_dir)
        print(f"   XML文件存在: {status['xml_file_exists']}")
        print(f"   JSON文件存在: {status['json_file_exists']}")
        print(f"   状态: {status['status']}")
        
        # 转换XML到JSON
        print(f"\n2. 转换GraphML到JSON")
        success = create_or_update_knowledge_graph_json(kb_dir)
        if success:
            print(f"   ✅ 转换成功")
            
            # 读取并显示JSON数据
            json_file = os.path.join(kb_dir, "graph_data.json")
            with open(json_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            
            print(f"   节点数: {len(nodes)}")
            print(f"   边数: {len(edges)}")
            
            # 显示节点类型分布
            node_types = {}
            for node in nodes:
                node_type = node.get("entity_type", "未知")
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            print(f"   节点类型分布:")
            for node_type, count in node_types.items():
                print(f"     {node_type}: {count}")
        else:
            print(f"   ❌ 转换失败")
            return False
        
        return True, kb_name, kb_dir
        
    except Exception as e:
        print(f"❌ 图谱处理失败: {e}")
        return False, None, None

def demo_visualization():
    """演示可视化生成"""
    print("\n🎨 演示可视化生成...")
    
    # 先处理图谱
    success, kb_name, kb_dir = demo_graph_processing()
    if not success:
        return False
    
    try:
        # 动态导入依赖
        import pipmaster as pm
        if not pm.is_installed("pyvis"):
            print("   安装pyvis...")
            pm.install("pyvis")
        if not pm.is_installed("networkx"):
            print("   安装networkx...")
            pm.install("networkx")
        
        import networkx as nx
        from pyvis.network import Network
        import json
        
        # 读取JSON数据
        json_file = os.path.join(kb_dir, "graph_data.json")
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
        
        print(f"   NetworkX图: {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")
        
        # 创建Pyvis网络
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#f8f9fa",
            font_color="black",
            notebook=False
        )
        
        # 设置物理引擎选项
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "nodes": {
            "font": {"size": 14},
            "borderWidth": 2,
            "shadow": true
          },
          "edges": {
            "font": {"size": 12},
            "shadow": true,
            "smooth": true
          }
        }
        """)
        
        # 从NetworkX转换到Pyvis
        net.from_nx(G)
        
        # 自定义样式
        import random
        
        # 为不同类型的节点设置不同颜色
        type_colors = {
            "领域": "#FF6B6B",
            "技术": "#4ECDC4", 
            "模型": "#45B7D1",
            "应用": "#96CEB4",
            "未知": "#FECA57"
        }
        
        for i, node in enumerate(net.nodes):
            # 获取节点ID
            node_id = node.get("id", node.get("label", ""))

            # 从原始图数据获取节点属性
            node_data = G.nodes.get(node_id, {})
            entity_type = node_data.get("entity_type", "未知")

            node["color"] = type_colors.get(entity_type, "#FECA57")

            # 设置标题（悬停显示）
            title_parts = [f"🏷️ {node_id}"]
            if entity_type:
                title_parts.append(f"📂 类型: {entity_type}")
            if "description" in node_data and node_data["description"]:
                desc = node_data["description"][:100] + "..." if len(node_data["description"]) > 100 else node_data["description"]
                title_parts.append(f"📝 描述: {desc}")
            node["title"] = "\\n".join(title_parts)

            # 设置节点大小（基于度数）
            degree = G.degree(node_id) if node_id in G.nodes else 1
            node["size"] = max(15, min(60, degree * 8))

            # 设置标签
            node["label"] = node_id

        # 自定义边样式
        for i, edge in enumerate(net.edges):
            # 获取边的源和目标节点
            source = edge.get("from", "")
            target = edge.get("to", "")

            # 从原始图数据获取边属性
            if G.has_edge(source, target):
                edge_data = G.edges[source, target]

                if "description" in edge_data and edge_data["description"]:
                    edge["title"] = f"🔗 {edge_data['description']}"

                # 设置边宽度和颜色
                weight = edge_data.get("weight", 1.0)
                edge["width"] = max(2, min(8, weight * 4))
            else:
                edge["width"] = 2

            edge["color"] = {"color": "#848484", "highlight": "#FF6B6B"}
        
        # 保存HTML文件到知识库目录
        html_file = os.path.join(kb_dir, "knowledge_graph_visualization.html")
        net.save_graph(html_file)
        
        print(f"   ✅ 可视化生成成功")
        print(f"   HTML文件: {html_file}")
        
        # 也生成一个演示文件到项目根目录
        demo_html = f"demo_knowledge_graph_{kb_name}.html"
        net.save_graph(demo_html)
        print(f"   演示文件: {demo_html}")
        
        return True, html_file, demo_html
        
    except Exception as e:
        print(f"   ❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def main():
    """主演示函数"""
    print("🚀 知识图谱可视化功能演示")
    print("=" * 60)
    
    # 演示可视化功能
    success, kb_html, demo_html = demo_visualization()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 演示完成！")
        print(f"\n📝 生成的文件:")
        print(f"   • {kb_html} - 知识库中的可视化文件")
        print(f"   • {demo_html} - 演示用可视化文件")
        print(f"   • knowledgeBase/demo_ai/graph_data.json - 图谱JSON数据")
        
        print(f"\n💡 使用说明:")
        print(f"   1. 在浏览器中打开任一HTML文件查看可视化效果")
        print(f"   2. 可以拖拽节点、缩放、悬停查看详细信息")
        print(f"   3. 不同颜色代表不同的实体类型:")
        print(f"      • 🔴 领域 (红色)")
        print(f"      • 🟢 技术 (青色)")
        print(f"      • 🔵 模型 (蓝色)")
        print(f"      • 🟡 应用 (绿色)")
        print(f"   4. 节点大小表示连接数量（度数）")
        print(f"   5. 边的粗细表示关系权重")
        
        print(f"\n🔧 API使用:")
        print(f"   • 启动API服务: python main.py")
        print(f"   • 访问可视化API: POST /knowledge-graph/visualize")
        print(f"   • 查看API文档: http://localhost:8002/docs")
        
        print(f"\n🖥️ Streamlit界面:")
        print(f"   • 启动界面: streamlit run start_streamlit.py")
        print(f"   • 访问知识图谱可视化页面")
        print(f"   • 选择知识库 'demo_ai' 查看演示效果")
    else:
        print("❌ 演示失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
