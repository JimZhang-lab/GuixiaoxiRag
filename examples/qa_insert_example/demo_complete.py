#!/usr/bin/env python3
"""
完整的问答库文件导入演示脚本
"""

import requests
import time
import os

def demo_import():
    """演示导入功能"""
    print("🎯 GuiXiaoXiRag 问答库文件导入演示")
    print("=" * 60)
    
    base_url = "http://localhost:8002"
    
    # 测试连接
    print("🔍 测试服务器连接...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code != 200:
            print("❌ 无法连接到服务器")
            return
        print("✅ 服务器连接正常")
    except:
        print("❌ 服务器连接失败")
        return
    
    # 演示文件
    demo_files = [
        ('qa_example.json', 'json', 'demo_json', 'JSON格式示例'),
        ('qa_example.csv', 'csv', 'demo_csv', 'CSV格式示例'),
        ('qa_example.xlsx', 'xlsx', 'demo_excel', 'Excel格式示例')
    ]
    
    print(f"\n📋 准备导入 {len(demo_files)} 个示例文件")
    
    success_count = 0
    
    for i, (file_path, file_type, category, desc) in enumerate(demo_files, 1):
        print(f"\n📁 [{i}/{len(demo_files)}] {desc}: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ 文件不存在")
            continue
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'file_type': file_type,
                    'default_category': category
                }
                
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
                    success_count += 1
                else:
                    print(f"   ❌ 导入失败: {result.get('message')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 导入异常: {e}")
        
        time.sleep(0.5)
    
    print(f"\n🎉 演示完成！成功导入 {success_count}/{len(demo_files)} 个文件")
    
    if success_count > 0:
        print(f"\n💡 您现在可以:")
        print("   1. 通过API查询问答对")
        print("   2. 查看不同分类的问答数据")
        print("   3. 访问 http://localhost:8002/docs 查看完整API文档")

if __name__ == "__main__":
    demo_import()
