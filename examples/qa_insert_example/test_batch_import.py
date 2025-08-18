#!/usr/bin/env python3
"""
简化的批量导入测试脚本
"""

import requests
import time
import os

def test_batch_import():
    """测试批量导入功能"""
    print("🔧 测试批量问答库导入功能")
    print("=" * 50)
    
    base_url = "http://localhost:8002"
    
    # 测试文件列表
    test_files = [
        {
            'file_path': 'qa_example.json',
            'file_type': 'json',
            'category': 'technology_test'
        },
        {
            'file_path': 'qa_example.csv',
            'file_type': 'csv',
            'category': 'general_test'
        },
        {
            'file_path': 'qa_example.xlsx',
            'file_type': 'xlsx',
            'category': 'mixed_test'
        }
    ]
    
    total_success = 0
    total_failed = 0
    
    for i, config in enumerate(test_files, 1):
        file_path = config['file_path']
        file_type = config['file_type']
        category = config['category']
        
        print(f"\n📁 [{i}/{len(test_files)}] 导入文件: {file_path}")
        print(f"   类型: {file_type}, 分类: {category}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"   ❌ 文件不存在，跳过")
            total_failed += 1
            continue
        
        try:
            # 准备请求
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'file_type': file_type,
                    'default_category': category
                }
                
                # 发送导入请求
                response = requests.post(
                    f"{base_url}/api/v1/qa/import",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"   ✅ 导入成功")
                    total_success += 1
                else:
                    print(f"   ❌ 导入失败: {result.get('message')}")
                    total_failed += 1
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   错误信息: {response.text}")
                total_failed += 1
                
        except Exception as e:
            print(f"   ❌ 导入异常: {e}")
            total_failed += 1
        
        # 短暂延迟
        time.sleep(0.5)
    
    # 打印总结
    print("\n" + "=" * 50)
    print("📊 批量导入总结")
    print("=" * 50)
    print(f"总文件数: {len(test_files)}")
    print(f"成功导入: {total_success}")
    print(f"导入失败: {total_failed}")
    print(f"成功率: {total_success/len(test_files)*100:.1f}%")
    
    if total_success > 0:
        print(f"\n🎉 批量导入测试完成！成功导入了 {total_success} 个文件")
    else:
        print(f"\n❌ 批量导入测试失败，没有成功导入任何文件")

def test_query():
    """测试查询功能"""
    print("\n🔍 测试问答查询功能")
    print("=" * 30)
    
    base_url = "http://localhost:8002"
    
    test_questions = [
        "什么是人工智能？",
        "如何学习编程？",
        "什么是云计算？"
    ]
    
    for question in test_questions:
        print(f"\n❓ 问题: {question}")
        try:
            response = requests.post(
                f"{base_url}/api/v1/qa/query",
                json={
                    "question": question,
                    "top_k": 1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data', {}).get('results'):
                    answer_data = result['data']['results'][0]
                    answer = answer_data.get('qa_pair', {}).get('answer', '未找到答案')
                    similarity = answer_data.get('similarity', 0)
                    print(f"✅ 答案: {answer[:100]}...")
                    print(f"   相似度: {similarity:.3f}")
                else:
                    print("❌ 未找到匹配的答案")
            else:
                print(f"❌ 查询失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")

if __name__ == "__main__":
    test_batch_import()
    test_query()
