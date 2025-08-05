"""
测试优化后的插入功能，验证知识图谱JSON文件的自动生成和更新
"""
import os
import sys
import asyncio
import json
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.guixiaoxirag_service import GuiXiaoXiRagService
from server.utils import check_knowledge_graph_files, create_or_update_knowledge_graph_json
from guixiaoxiRag.utils import setup_logger

# 设置日志
setup_logger("test_optimized_insert", level="INFO")

# 测试配置
TEST_WORKING_DIR = "./test_knowledge_base"
TEST_TEXT_1 = """
张三是一名软件工程师，在北京的一家科技公司工作。他专门从事人工智能和机器学习项目的开发。
张三毕业于清华大学计算机科学与技术专业，有5年的工作经验。
他的主要技能包括Python编程、深度学习框架如TensorFlow和PyTorch的使用。
"""

TEST_TEXT_2 = """
李四是张三的同事，也是一名数据科学家。李四负责数据分析和模型优化工作。
李四毕业于北京大学数学系，后来转向了数据科学领域。
他们经常合作开展机器学习项目，共同解决复杂的业务问题。
"""

async def test_insert_and_knowledge_graph_generation():
    """测试插入功能和知识图谱JSON文件生成"""
    print("=" * 60)
    print("开始测试优化后的插入功能")
    print("=" * 60)
    
    # 清理测试目录
    if os.path.exists(TEST_WORKING_DIR):
        shutil.rmtree(TEST_WORKING_DIR)
    
    service = GuiXiaoXiRagService()
    
    try:
        # 1. 初始化服务
        print("\n1. 初始化GuiXiaoXiRag服务...")
        await service.initialize(working_dir=TEST_WORKING_DIR, language="中文")
        print(f"✓ 服务初始化成功，工作目录: {TEST_WORKING_DIR}")
        
        # 2. 检查初始状态
        print("\n2. 检查知识图谱文件初始状态...")
        initial_status = check_knowledge_graph_files(TEST_WORKING_DIR)
        print(f"初始状态: {initial_status['status']}")
        print(f"XML文件存在: {initial_status['xml_file_exists']}")
        print(f"JSON文件存在: {initial_status['json_file_exists']}")
        
        # 3. 插入第一段文本
        print("\n3. 插入第一段文本...")
        track_id_1 = await service.insert_text(
            text=TEST_TEXT_1,
            doc_id="doc_001",
            file_path="test_doc_1.txt"
        )
        print(f"✓ 第一段文本插入成功，track_id: {track_id_1}")
        
        # 4. 检查插入后的状态
        print("\n4. 检查第一次插入后的知识图谱文件状态...")
        status_after_first = check_knowledge_graph_files(TEST_WORKING_DIR)
        print(f"状态: {status_after_first['status']}")
        print(f"XML文件存在: {status_after_first['xml_file_exists']}")
        print(f"XML文件大小: {status_after_first['xml_file_size']} bytes")
        print(f"JSON文件存在: {status_after_first['json_file_exists']}")
        print(f"JSON文件大小: {status_after_first['json_file_size']} bytes")
        
        # 5. 验证JSON文件内容
        if status_after_first['json_file_exists']:
            print("\n5. 验证JSON文件内容...")
            json_file_path = status_after_first['json_file_path']
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                print(f"✓ JSON文件解析成功")
                print(f"节点数量: {len(json_data.get('nodes', []))}")
                print(f"边数量: {len(json_data.get('edges', []))}")
                
                # 显示前几个节点和边的信息
                if json_data.get('nodes'):
                    print("前3个节点:")
                    for i, node in enumerate(json_data['nodes'][:3]):
                        print(f"  节点{i+1}: {node.get('id', 'N/A')} - {node.get('entity_type', 'N/A')}")
                
                if json_data.get('edges'):
                    print("前3条边:")
                    for i, edge in enumerate(json_data['edges'][:3]):
                        print(f"  边{i+1}: {edge.get('source', 'N/A')} -> {edge.get('target', 'N/A')}")
                        
            except Exception as e:
                print(f"✗ JSON文件解析失败: {e}")
        
        # 6. 插入第二段文本
        print("\n6. 插入第二段文本...")
        track_id_2 = await service.insert_text(
            text=TEST_TEXT_2,
            doc_id="doc_002",
            file_path="test_doc_2.txt"
        )
        print(f"✓ 第二段文本插入成功，track_id: {track_id_2}")
        
        # 7. 检查第二次插入后的状态
        print("\n7. 检查第二次插入后的知识图谱文件状态...")
        status_after_second = check_knowledge_graph_files(TEST_WORKING_DIR)
        print(f"状态: {status_after_second['status']}")
        print(f"XML文件大小: {status_after_second['xml_file_size']} bytes")
        print(f"JSON文件大小: {status_after_second['json_file_size']} bytes")
        
        # 8. 验证更新后的JSON文件内容
        if status_after_second['json_file_exists']:
            print("\n8. 验证更新后的JSON文件内容...")
            json_file_path = status_after_second['json_file_path']
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    updated_json_data = json.load(f)
                print(f"✓ 更新后的JSON文件解析成功")
                print(f"更新后节点数量: {len(updated_json_data.get('nodes', []))}")
                print(f"更新后边数量: {len(updated_json_data.get('edges', []))}")
                
                # 比较前后变化
                if status_after_first['json_file_exists']:
                    nodes_diff = len(updated_json_data.get('nodes', [])) - len(json_data.get('nodes', []))
                    edges_diff = len(updated_json_data.get('edges', [])) - len(json_data.get('edges', []))
                    print(f"节点增加: {nodes_diff}")
                    print(f"边增加: {edges_diff}")
                        
            except Exception as e:
                print(f"✗ 更新后的JSON文件解析失败: {e}")
        
        # 9. 测试批量插入
        print("\n9. 测试批量插入功能...")
        batch_texts = [
            "王五是公司的项目经理，负责协调张三和李四的工作。",
            "赵六是公司的技术总监，为团队提供技术指导。"
        ]
        track_id_batch = await service.insert_texts(
            texts=batch_texts,
            doc_ids=["doc_003", "doc_004"],
            file_paths=["test_doc_3.txt", "test_doc_4.txt"]
        )
        print(f"✓ 批量文本插入成功，track_id: {track_id_batch}")
        
        # 10. 最终状态检查
        print("\n10. 检查最终状态...")
        final_status = check_knowledge_graph_files(TEST_WORKING_DIR)
        print(f"最终状态: {final_status['status']}")
        print(f"最终XML文件大小: {final_status['xml_file_size']} bytes")
        print(f"最终JSON文件大小: {final_status['json_file_size']} bytes")
        
        if final_status['json_file_exists']:
            json_file_path = final_status['json_file_path']
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    final_json_data = json.load(f)
                print(f"最终节点数量: {len(final_json_data.get('nodes', []))}")
                print(f"最终边数量: {len(final_json_data.get('edges', []))}")
            except Exception as e:
                print(f"✗ 最终JSON文件解析失败: {e}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        await service.finalize()


async def test_manual_conversion():
    """测试手动转换功能"""
    print("\n" + "=" * 60)
    print("测试手动转换功能")
    print("=" * 60)
    
    if os.path.exists(TEST_WORKING_DIR):
        print(f"测试目录存在: {TEST_WORKING_DIR}")
        
        # 检查文件状态
        status = check_knowledge_graph_files(TEST_WORKING_DIR)
        print(f"文件状态: {status}")
        
        if status['xml_file_exists']:
            print("\n手动执行知识图谱转换...")
            success = create_or_update_knowledge_graph_json(TEST_WORKING_DIR)
            if success:
                print("✓ 手动转换成功")
            else:
                print("✗ 手动转换失败")
        else:
            print("XML文件不存在，无法进行手动转换")
    else:
        print("测试目录不存在，请先运行主测试")


if __name__ == "__main__":
    # 运行主测试
    asyncio.run(test_insert_and_knowledge_graph_generation())
    
    # 运行手动转换测试
    asyncio.run(test_manual_conversion())
