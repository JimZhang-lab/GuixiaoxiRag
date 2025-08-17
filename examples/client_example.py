#!/usr/bin/env python3
"""
GuiXiaoXiRag 客户端示例
演示如何使用API进行查询和文档管理
"""
import requests
import json
import time
from pathlib import Path

class GuiXiaoXiRagClient:
    """GuiXiaoXiRag API 客户端"""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """健康检查"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            return response.status_code == 200
        except:
            return False
    
    def query(self, question, mode="hybrid", stream=False):
        """查询问题"""
        url = f"{self.base_url}/api/v1/query"
        data = {
            "query": question,
            "mode": mode,
            "stream": stream
        }
        
        response = self.session.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"查询失败: {response.status_code} - {response.text}")
            return None
    
    def upload_document(self, file_path, knowledge_base="default"):
        """上传文档"""
        url = f"{self.base_url}/api/v1/documents/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'knowledge_base': knowledge_base}
            
            response = self.session.post(url, files=files, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"上传失败: {response.status_code} - {response.text}")
                return None
    
    def get_knowledge_bases(self):
        """获取知识库列表"""
        url = f"{self.base_url}/api/v1/knowledge-bases"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取知识库失败: {response.status_code}")
            return None
    
    def get_system_status(self):
        """获取系统状态"""
        url = f"{self.base_url}/api/v1/system/status"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取系统状态失败: {response.status_code}")
            return None

def demo_basic_usage():
    """基本使用演示"""
    print("🎯 GuiXiaoXiRag 客户端演示")
    print("=" * 40)
    
    # 创建客户端
    client = GuiXiaoXiRagClient()
    
    # 健康检查
    print("1. 健康检查...")
    if not client.health_check():
        print("❌ 服务不可用，请确保服务已启动")
        return
    print("✅ 服务正常")
    
    # 获取系统状态
    print("\n2. 获取系统状态...")
    status = client.get_system_status()
    if status:
        print(f"✅ 系统状态: {status.get('status', 'unknown')}")
        print(f"   启动时间: {status.get('uptime', 'unknown')}")
    
    # 获取知识库列表
    print("\n3. 获取知识库列表...")
    kbs = client.get_knowledge_bases()
    if kbs:
        print(f"✅ 知识库数量: {len(kbs.get('knowledge_bases', []))}")
        for kb in kbs.get('knowledge_bases', []):
            print(f"   - {kb}")
    
    # 查询示例
    print("\n4. 查询示例...")
    questions = [
        "什么是人工智能？",
        "机器学习的基本概念",
        "深度学习算法"
    ]
    
    for question in questions:
        print(f"\n📝 查询: {question}")
        result = client.query(question, mode="hybrid")
        if result:
            print(f"✅ 回答: {result.get('response', '无回答')[:100]}...")
            print(f"   模式: {result.get('mode', 'unknown')}")
            print(f"   耗时: {result.get('processing_time', 0):.2f}s")
        else:
            print("❌ 查询失败")
        
        time.sleep(1)  # 避免请求过快

def demo_different_modes():
    """不同查询模式演示"""
    print("\n🔍 不同查询模式演示")
    print("=" * 40)
    
    client = GuiXiaoXiRagClient()
    question = "什么是神经网络？"
    modes = ["local", "global", "hybrid", "naive"]
    
    for mode in modes:
        print(f"\n📝 模式: {mode}")
        result = client.query(question, mode=mode)
        if result:
            print(f"✅ 耗时: {result.get('processing_time', 0):.2f}s")
            print(f"   回答长度: {len(result.get('response', ''))}")
        else:
            print("❌ 查询失败")
        
        time.sleep(1)

def main():
    """主函数"""
    try:
        demo_basic_usage()
        demo_different_modes()
        print("\n🎉 演示完成！")
    except KeyboardInterrupt:
        print("\n👋 演示已停止")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")

if __name__ == "__main__":
    main()
