#!/usr/bin/env python3
"""
问答库文件导入示例脚本
演示如何使用不同格式的文件导入问答数据
"""

import requests
import json
import os
from pathlib import Path


class QAImporter:
    """问答库导入器"""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/qa"
    
    def import_file(self, file_path, category=None, skip_duplicate_check=False, duplicate_threshold=0.98):
        """
        导入文件到问答库
        
        Args:
            file_path: 文件路径
            category: 默认分类
            skip_duplicate_check: 是否跳过重复检查
            duplicate_threshold: 重复检查阈值
        """
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return None
        
        print(f"📁 导入文件: {file_path}")
        
        # 准备请求数据
        files = {'file': open(file_path, 'rb')}
        data = {}
        
        if category:
            data['category'] = category
        if skip_duplicate_check:
            data['skip_duplicate_check'] = 'true'
        if duplicate_threshold != 0.98:
            data['duplicate_threshold'] = str(duplicate_threshold)
        
        try:
            # 发送导入请求
            response = requests.post(
                f"{self.api_url}/import",
                files=files,
                data=data,
                timeout=300
            )
            
            files['file'].close()
            
            if response.status_code == 200:
                result = response.json()
                self._print_import_result(result)
                return result
            else:
                print(f"❌ 导入失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 导入异常: {e}")
            return None
    
    def _print_import_result(self, result):
        """打印导入结果"""
        print(f"✅ 导入完成")
        print(f"   总处理数: {result.get('total_processed', 0)}")
        print(f"   成功导入: {result.get('successful_imports', 0)}")
        print(f"   导入失败: {result.get('failed_imports', 0)}")
        print(f"   跳过重复: {result.get('duplicate_skipped', 0)}")
        
        # 显示分类统计
        summary = result.get('import_summary', {})
        categories = summary.get('categories', {})
        if categories:
            print(f"   分类统计: {categories}")
        
        # 显示失败记录
        failed_records = result.get('failed_records', [])
        if failed_records:
            print(f"   失败记录:")
            for record in failed_records[:3]:  # 只显示前3个
                print(f"     行 {record.get('row')}: {record.get('error')}")
            if len(failed_records) > 3:
                print(f"     ... 还有 {len(failed_records) - 3} 个失败记录")
    
    def test_connection(self):
        """测试连接"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=10)
            if response.status_code == 200:
                print("✅ 连接正常")
                return True
            else:
                print(f"❌ 连接失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接异常: {e}")
            return False


def main():
    """主函数"""
    print("🔧 问答库文件导入示例")
    print("=" * 50)
    
    # 创建导入器
    importer = QAImporter()
    
    # 测试连接
    print("🔍 测试API连接...")
    if not importer.test_connection():
        print("❌ 无法连接到问答系统API，请确保服务器正在运行")
        return
    
    # 获取当前目录下的示例文件
    current_dir = Path(".")
    example_files = [
        ("qa_example.json", "technology"),
        ("qa_example.csv", "general"),
        ("qa_example.xlsx", "mixed")
    ]
    
    print(f"\n📋 可用的示例文件:")
    available_files = []
    for i, (filename, category) in enumerate(example_files, 1):
        file_path = current_dir / filename
        if file_path.exists():
            print(f"   {i}. {filename} (默认分类: {category})")
            available_files.append((filename, category))
        else:
            print(f"   {i}. {filename} (文件不存在)")
    
    if not available_files:
        print("❌ 没有找到示例文件")
        return
    
    # 交互式选择文件导入
    print(f"\n💡 导入示例:")
    print("   选择要导入的文件编号，或输入 'all' 导入所有文件")
    
    try:
        choice = input("请选择 (1-3 或 'all'): ").strip()
        
        if choice.lower() == 'all':
            # 导入所有文件
            for filename, category in available_files:
                print(f"\n📤 导入 {filename}...")
                result = importer.import_file(
                    filename, 
                    category=category,
                    skip_duplicate_check=False,
                    duplicate_threshold=0.98
                )
                if result:
                    print("✅ 导入成功")
                else:
                    print("❌ 导入失败")
        
        elif choice.isdigit():
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_files):
                filename, category = available_files[choice_idx]
                print(f"\n📤 导入 {filename}...")
                result = importer.import_file(
                    filename,
                    category=category,
                    skip_duplicate_check=False,
                    duplicate_threshold=0.98
                )
                if result:
                    print("✅ 导入成功")
                else:
                    print("❌ 导入失败")
            else:
                print("❌ 无效的选择")
        else:
            print("❌ 无效的输入")
    
    except KeyboardInterrupt:
        print("\n\n👋 导入已取消")
    except Exception as e:
        print(f"❌ 导入过程中出错: {e}")
    
    print(f"\n🎉 导入示例完成！")
    print(f"\n💡 您可以通过以下方式验证导入结果:")
    print(f"   1. 访问 http://localhost:8002/docs 查看API文档")
    print(f"   2. 使用查询API测试问答功能")
    print(f"   3. 查看问答库统计信息")


def demo_api_usage():
    """演示API使用方法"""
    print("\n📚 API使用示例:")
    
    # JSON文件导入示例
    json_example = '''
# JSON文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@qa_example.json" \\
  -F "category=technology" \\
  -F "skip_duplicate_check=false"
'''
    
    # CSV文件导入示例
    csv_example = '''
# CSV文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@qa_example.csv" \\
  -F "category=general" \\
  -F "duplicate_threshold=0.95"
'''
    
    # Excel文件导入示例
    excel_example = '''
# Excel文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \\
  -H "Content-Type: multipart/form-data" \\
  -F "file=@qa_example.xlsx" \\
  -F "category=mixed"
'''
    
    print(json_example)
    print(csv_example)
    print(excel_example)


if __name__ == "__main__":
    main()
    demo_api_usage()
