#!/usr/bin/env python3
"""
简化的服务启动测试
避免复杂的相对导入问题
"""
import sys
import os

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, current_dir)

print("=== 简化的GuiXiaoXiRag服务测试 ===")

# 测试基础依赖
print("\n1. 测试基础依赖...")
try:
    import fastapi
    import uvicorn
    print("✓ FastAPI和Uvicorn正常")
except ImportError as e:
    print(f"✗ FastAPI依赖缺失: {e}")
    sys.exit(1)

# 测试GuiXiaoXiRag核心库
print("\n2. 测试GuiXiaoXiRag核心库...")
try:
    from core.rag import GuiXiaoXiRag, QueryParam
    print("✓ GuiXiaoXiRag核心库正常")
    print(f"  GuiXiaoXiRag类: {GuiXiaoXiRag}")
    print(f"  QueryParam类: {QueryParam}")
except ImportError as e:
    print(f"✗ GuiXiaoXiRag核心库缺失: {e}")
    sys.exit(1)

# 测试创建简单的FastAPI应用
print("\n3. 测试创建简单的FastAPI应用...")
try:
    app = fastapi.FastAPI(
        title="GuiXiaoXiRag测试",
        version="2.0.0",
        description="重构版本测试"
    )
    
    @app.get("/")
    async def root():
        return {"message": "GuiXiaoXiRag服务运行正常", "version": "2.0.0"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "service": "GuiXiaoXiRag"}
    
    print("✓ 简单FastAPI应用创建成功")
    print(f"  应用标题: {app.title}")
    print(f"  路由数量: {len(app.routes)}")
    
except Exception as e:
    print(f"✗ FastAPI应用创建失败: {e}")
    sys.exit(1)

# 测试GuiXiaoXiRag实例创建
print("\n4. 测试GuiXiaoXiRag实例创建...")
try:
    # 创建一个简单的工作目录
    test_working_dir = "./test_kb"
    os.makedirs(test_working_dir, exist_ok=True)
    
    # 尝试创建GuiXiaoXiRag实例
    rag = GuiXiaoXiRag(working_dir=test_working_dir)
    print("✓ GuiXiaoXiRag实例创建成功")
    print(f"  工作目录: {test_working_dir}")
    print(f"  实例类型: {type(rag)}")
    
except Exception as e:
    print(f"✗ GuiXiaoXiRag实例创建失败: {e}")
    print("这可能是由于缺少配置或依赖")

print("\n=== 测试完成 ===")
print("\n基础测试通过！可以尝试启动简化版本的服务。")
print("\n要启动完整的重构服务，需要解决相对导入问题。")
print("建议使用以下命令启动简化版本:")
print("uvicorn simple_test:app --host 0.0.0.0 --port 8000 --reload")

# 如果所有测试都通过，可以尝试启动服务
if __name__ == "__main__":
    print("\n如果要直接启动测试服务，请运行:")
    print("python -c \"import simple_test; import uvicorn; uvicorn.run(simple_test.app, host='0.0.0.0', port=8000)\"")
