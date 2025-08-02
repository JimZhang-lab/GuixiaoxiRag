"""
测试配置
"""
import os
import tempfile
from pathlib import Path

# 测试配置
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "test_working_dir": "./test_data",
    "sample_texts": [
        "这是一个测试文档。它包含了一些基本的信息用于测试GuiXiaoXiRag的功能。",
        "人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。",
        "机器学习是人工智能的一个子领域，它使计算机能够在没有明确编程的情况下学习。"
    ],
    "sample_queries": [
        "什么是人工智能？",
        "机器学习的定义是什么？",
        "测试文档包含什么内容？"
    ]
}

# 创建测试目录
def setup_test_environment():
    """设置测试环境"""
    test_dir = Path(TEST_CONFIG["test_working_dir"])
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试文件
    test_files = {
        "test1.txt": TEST_CONFIG["sample_texts"][0],
        "test2.txt": TEST_CONFIG["sample_texts"][1],
        "test3.txt": TEST_CONFIG["sample_texts"][2]
    }
    
    for filename, content in test_files.items():
        file_path = test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return test_dir

def cleanup_test_environment():
    """清理测试环境"""
    import shutil
    test_dir = Path(TEST_CONFIG["test_working_dir"])
    if test_dir.exists():
        shutil.rmtree(test_dir)

# 测试数据
SAMPLE_DOCUMENT = """
计算机科学是研究算法和计算系统的学科。它涵盖了从理论研究到实际应用的广泛领域。

主要分支包括：
1. 算法与数据结构
2. 计算机系统与架构
3. 软件工程
4. 人工智能
5. 数据库系统
6. 计算机网络
7. 人机交互

人工智能作为计算机科学的重要分支，专注于创建能够执行通常需要人类智能的任务的系统。
机器学习是人工智能的一个子集，它使计算机能够从数据中学习而无需明确编程。
深度学习是机器学习的一个子集，使用神经网络来模拟人脑的学习过程。
"""

SAMPLE_QUERIES = [
    "计算机科学的主要分支有哪些？",
    "什么是人工智能？",
    "机器学习和深度学习的关系是什么？",
    "计算机科学涵盖哪些领域？"
]
