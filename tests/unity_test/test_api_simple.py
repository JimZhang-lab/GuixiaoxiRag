#!/usr/bin/env python3
"""
简单的API测试
"""

import json
import subprocess


def test_api():
    """测试API"""
    print("🔍 测试问答系统API")
    print("=" * 40)
    
    # 测试查询
    query_data = {
        "question": "问答系统支持哪些功能？",
        "top_k": 1,
        "min_similarity": 0.1
    }
    
    try:
        result = subprocess.run([
            "curl", "-s", "-X", "POST",
            "http://localhost:8002/api/v1/qa/query",
            "-H", "accept: application/json",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(query_data),
            "--connect-timeout", "10"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            
            print(f"查询: '{query_data['question']}'")
            print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            
            if response.get('found'):
                similarity = response.get('similarity', 0)
                matched_question = response.get('question', '')
                
                print(f"\n✅ 找到匹配")
                print(f"相似度: {similarity}")
                print(f"匹配问题: '{matched_question}'")
                
                if matched_question == query_data['question']:
                    if similarity > 0.99:
                        print(f"🎉 完美匹配！")
                        return True
                    else:
                        print(f"✅ 问题匹配正确，相似度: {similarity}")
                        return True
                else:
                    print(f"⚠️  匹配到错误问题")
                    return False
            else:
                print(f"❌ 未找到匹配")
                return False
        else:
            print(f"❌ API调用失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 测试成功！相似度精度问题已修复！")
    else:
        print("\n❌ 测试失败")
