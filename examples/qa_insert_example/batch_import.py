#!/usr/bin/env python3
"""
批量导入问答数据脚本
支持从多个文件批量导入问答对到不同分类
"""

import requests
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any


class BatchQAImporter:
    """批量问答导入器"""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/qa"
        self.import_results = []
    
    def import_batch(self, import_configs: List[Dict[str, Any]]):
        """
        批量导入多个文件
        
        Args:
            import_configs: 导入配置列表，每个配置包含:
                - file_path: 文件路径
                - category: 分类名称
                - skip_duplicate_check: 是否跳过重复检查
                - duplicate_threshold: 重复检查阈值
        """
        print(f"🚀 开始批量导入 {len(import_configs)} 个文件")
        print("=" * 60)
        
        total_success = 0
        total_failed = 0
        total_processed = 0
        
        for i, config in enumerate(import_configs, 1):
            file_path = config['file_path']
            category = config.get('category', 'general')
            
            print(f"\n📁 [{i}/{len(import_configs)}] 导入文件: {file_path}")
            print(f"   分类: {category}")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"   ❌ 文件不存在，跳过")
                continue
            
            # 导入文件
            result = self._import_single_file(config)
            
            if result:
                success_count = result.get('successful_imports', 0)
                failed_count = result.get('failed_imports', 0)
                processed_count = result.get('total_processed', 0)
                
                total_success += success_count
                total_failed += failed_count
                total_processed += processed_count
                
                print(f"   ✅ 成功: {success_count}, 失败: {failed_count}")
                
                # 记录结果
                self.import_results.append({
                    'file_path': file_path,
                    'category': category,
                    'result': result,
                    'success': True
                })
            else:
                print(f"   ❌ 导入失败")
                self.import_results.append({
                    'file_path': file_path,
                    'category': category,
                    'result': None,
                    'success': False
                })
            
            # 短暂延迟，避免过快请求
            time.sleep(0.5)
        
        # 打印总结
        self._print_batch_summary(total_processed, total_success, total_failed)
    
    def _import_single_file(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """导入单个文件"""
        file_path = config['file_path']
        
        # 准备请求数据
        files = {'file': open(file_path, 'rb')}
        data = {}
        
        if config.get('category'):
            data['category'] = config['category']
        if config.get('skip_duplicate_check'):
            data['skip_duplicate_check'] = 'true'
        if config.get('duplicate_threshold'):
            data['duplicate_threshold'] = str(config['duplicate_threshold'])
        
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
                return response.json()
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ 导入异常: {e}")
            return None
    
    def _print_batch_summary(self, total_processed, total_success, total_failed):
        """打印批量导入总结"""
        print("\n" + "=" * 60)
        print("📊 批量导入总结")
        print("=" * 60)
        print(f"总处理记录数: {total_processed}")
        print(f"总成功导入: {total_success}")
        print(f"总失败记录: {total_failed}")
        print(f"成功率: {total_success/total_processed*100:.1f}%" if total_processed > 0 else "成功率: 0%")
        
        # 按分类统计
        category_stats = {}
        for result in self.import_results:
            if result['success'] and result['result']:
                category = result['category']
                success_count = result['result'].get('successful_imports', 0)
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += success_count
        
        if category_stats:
            print(f"\n📋 分类统计:")
            for category, count in category_stats.items():
                print(f"   {category}: {count} 条")
        
        # 失败文件列表
        failed_files = [r for r in self.import_results if not r['success']]
        if failed_files:
            print(f"\n❌ 失败文件:")
            for failed in failed_files:
                print(f"   {failed['file_path']}")
    
    def export_results(self, output_file="import_results.json"):
        """导出导入结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.import_results, f, ensure_ascii=False, indent=2)
            print(f"📄 导入结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


def create_sample_import_config():
    """创建示例导入配置"""
    current_dir = Path(".")
    
    configs = []
    
    # 检查示例文件并创建配置
    sample_files = [
        {
            'file_path': 'qa_example.json',
            'category': 'technology',
            'skip_duplicate_check': False,
            'duplicate_threshold': 0.98
        },
        {
            'file_path': 'qa_example.csv',
            'category': 'general',
            'skip_duplicate_check': False,
            'duplicate_threshold': 0.95
        },
        {
            'file_path': 'qa_example.xlsx',
            'category': 'mixed',
            'skip_duplicate_check': True,  # 跳过重复检查
            'duplicate_threshold': 0.98
        }
    ]
    
    for config in sample_files:
        file_path = current_dir / config['file_path']
        if file_path.exists():
            configs.append(config)
    
    return configs


def main():
    """主函数"""
    print("🔧 批量问答库导入工具")
    print("=" * 50)
    
    # 创建批量导入器
    importer = BatchQAImporter()
    
    # 测试连接
    print("🔍 测试API连接...")
    try:
        response = requests.get(f"{importer.api_url}/stats", timeout=10)
        if response.status_code != 200:
            print("❌ 无法连接到问答系统API，请确保服务器正在运行")
            return
        print("✅ 连接正常")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return
    
    # 创建示例配置
    import_configs = create_sample_import_config()
    
    if not import_configs:
        print("❌ 没有找到可导入的示例文件")
        print("请确保以下文件存在:")
        print("   - qa_example.json")
        print("   - qa_example.csv") 
        print("   - qa_example.xlsx")
        return
    
    print(f"\n📋 找到 {len(import_configs)} 个可导入的文件:")
    for i, config in enumerate(import_configs, 1):
        print(f"   {i}. {config['file_path']} -> {config['category']}")
    
    # 确认导入
    try:
        confirm = input(f"\n是否开始批量导入？(y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("👋 导入已取消")
            return
        
        # 开始批量导入
        importer.import_batch(import_configs)
        
        # 导出结果
        importer.export_results()
        
        print(f"\n🎉 批量导入完成！")
        
    except KeyboardInterrupt:
        print("\n\n👋 导入已取消")
    except Exception as e:
        print(f"❌ 批量导入过程中出错: {e}")


def demo_custom_config():
    """演示自定义配置"""
    print("\n📚 自定义配置示例:")
    
    example_config = '''
# 自定义导入配置示例
import_configs = [
    {
        'file_path': 'tech_qa.json',
        'category': 'technology',
        'skip_duplicate_check': False,
        'duplicate_threshold': 0.98
    },
    {
        'file_path': 'business_qa.csv',
        'category': 'business',
        'skip_duplicate_check': True,
        'duplicate_threshold': 0.95
    },
    {
        'file_path': 'general_qa.xlsx',
        'category': 'general',
        'skip_duplicate_check': False,
        'duplicate_threshold': 0.90
    }
]

# 执行批量导入
importer = BatchQAImporter()
importer.import_batch(import_configs)
'''
    
    print(example_config)


if __name__ == "__main__":
    main()
    demo_custom_config()
