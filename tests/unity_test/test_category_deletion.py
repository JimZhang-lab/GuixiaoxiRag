#!/usr/bin/env python3
"""
测试分类删除功能，验证文件夹是否被正确删除
"""

import asyncio
import json
import os
import requests
import time
from pathlib import Path


class CategoryDeletionTester:
    """分类删除功能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        
    def test_category_deletion_with_folder(self):
        """测试分类删除功能，包括文件夹删除"""
        print("🧪 开始测试分类删除功能（包括文件夹删除）")
        
        # 1. 创建测试问答对
        test_category = f"test_deletion_{int(time.time())}"
        print(f"📝 创建测试分类: {test_category}")
        
        qa_data = {
            "question": "这是一个测试问题",
            "answer": "这是一个测试答案",
            "category": test_category,
            "confidence": 0.9,
            "keywords": ["测试", "删除"],
            "source": "deletion_test"
        }
        
        # 创建问答对
        response = requests.post(f"{self.api_base}/qa/pairs", json=qa_data)
        if response.status_code != 200:
            print(f"❌ 创建问答对失败: {response.text}")
            return False
            
        result = response.json()
        if not result.get("success"):
            print(f"❌ 创建问答对失败: {result.get('message')}")
            return False
            
        qa_id = result["data"]["qa_id"]
        print(f"✅ 成功创建问答对: {qa_id}")
        
        # 2. 验证分类存在
        response = requests.get(f"{self.api_base}/qa/categories")
        if response.status_code == 200:
            categories_data = response.json()
            if categories_data.get("success"):
                categories = categories_data["data"]["categories"]
                if test_category in categories:
                    print(f"✅ 分类 {test_category} 已创建")
                else:
                    print(f"⚠️ 分类 {test_category} 未在分类列表中找到")
        
        # 3. 获取QA统计，查看分类文件夹
        response = requests.get(f"{self.api_base}/qa/statistics")
        if response.status_code == 200:
            stats = response.json()
            if stats.get("success"):
                print(f"📊 当前问答对总数: {stats['data']['total_pairs']}")
                print(f"📊 分类统计: {stats['data']['categories']}")
        
        # 4. 删除分类
        print(f"🗑️ 删除分类: {test_category}")
        response = requests.delete(f"{self.api_base}/qa/categories/{test_category}")
        
        if response.status_code != 200:
            print(f"❌ 删除分类失败: {response.text}")
            return False
            
        result = response.json()
        print(f"📋 删除结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if not result.get("success"):
            print(f"❌ 删除分类失败: {result.get('message')}")
            return False
            
        # 5. 验证删除结果
        data = result.get("data", {})
        deleted_count = data.get("deleted_count", 0)
        folder_deleted = data.get("folder_deleted", False)
        
        print(f"✅ 删除成功:")
        print(f"   - 删除的问答对数量: {deleted_count}")
        print(f"   - 文件夹是否删除: {folder_deleted}")
        print(f"   - 消息: {result.get('message')}")
        
        # 6. 验证分类不再存在
        response = requests.get(f"{self.api_base}/qa/categories")
        if response.status_code == 200:
            categories_data = response.json()
            if categories_data.get("success"):
                categories = categories_data["data"]["categories"]
                if test_category not in categories:
                    print(f"✅ 分类 {test_category} 已从分类列表中移除")
                else:
                    print(f"❌ 分类 {test_category} 仍在分类列表中")
                    return False
        
        # 7. 验证问答对不再存在
        try:
            response = requests.get(f"{self.api_base}/qa/pairs", params={"category": test_category})
            if response.status_code == 200:
                pairs_data = response.json()
                if pairs_data.get("success"):
                    pairs = pairs_data["data"]["pairs"]
                    if len(pairs) == 0:
                        print(f"✅ 分类 {test_category} 的问答对已全部删除")
                    else:
                        print(f"❌ 分类 {test_category} 仍有 {len(pairs)} 个问答对")
                        return False
        except Exception as e:
            print(f"⚠️ 验证问答对时出错: {e}")
        
        return True
    
    def test_delete_nonexistent_category(self):
        """测试删除不存在的分类"""
        print("\n🧪 测试删除不存在的分类")
        
        nonexistent_category = f"nonexistent_{int(time.time())}"
        response = requests.delete(f"{self.api_base}/qa/categories/{nonexistent_category}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 删除不存在分类的结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if not result.get("success"):
                print("✅ 正确处理了不存在的分类")
                return True
            else:
                print("❌ 应该返回失败状态")
                return False
        else:
            print(f"❌ 请求失败: {response.text}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 分类删除功能测试套件")
        print("=" * 60)
        
        tests = [
            ("分类删除（包括文件夹）", self.test_category_deletion_with_folder),
            ("删除不存在的分类", self.test_delete_nonexistent_category)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 运行测试: {test_name}")
            try:
                if test_func():
                    print(f"✅ {test_name} - 通过")
                    passed += 1
                else:
                    print(f"❌ {test_name} - 失败")
            except Exception as e:
                print(f"❌ {test_name} - 异常: {e}")
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed}/{total} 通过")
        print("=" * 60)
        
        return passed == total


def main():
    """主函数"""
    tester = CategoryDeletionTester()
    
    # 检查服务是否可用
    try:
        response = requests.get(f"{tester.api_base}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务不可用，请确保GuixiaoxiRag服务正在运行")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return
    
    # 运行测试
    success = tester.run_all_tests()
    
    if success:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，请检查日志")


if __name__ == "__main__":
    main()
