#!/usr/bin/env python3
"""
测试新服务启动脚本
用于验证重构后的服务是否可以正常启动
"""
import sys
import os
import asyncio
import traceback

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加GuiXiaoXiRag项目根目录到Python路径
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("=== GuiXiaoXiRag服务启动测试 ===")
print(f"Python版本: {sys.version}")
print(f"当前目录: {current_dir}")

# 测试基础依赖
print("\n1. 测试基础依赖...")
try:
    import fastapi
    import uvicorn
    import pydantic
    print("✓ FastAPI相关依赖正常")
except ImportError as e:
    print(f"✗ FastAPI依赖缺失: {e}")
    sys.exit(1)

# 测试GuiXiaoXiRag核心库
print("\n2. 测试GuiXiaoXiRag核心库...")
try:
    from core.rag import GuiXiaoXiRag, QueryParam
    print("✓ GuiXiaoXiRag核心库正常")
except ImportError as e:
    print(f"✗ GuiXiaoXiRag核心库缺失: {e}")
    print("请确保已安装GuiXiaoXiRag库")
    sys.exit(1)

# 测试模块导入
print("\n3. 测试模块导入...")
modules_to_test = [
    ("model", "数据模型"),
    ("middleware", "中间件"),
    ("handler", "业务处理器"),
    ("api", "API处理器"),
    ("routers", "路由模块")
]

failed_imports = []
for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"✓ {description} ({module_name})")
    except ImportError as e:
        print(f"✗ {description} ({module_name}): {e}")
        failed_imports.append((module_name, str(e)))

# 测试common模块（已重命名）
try:
    import importlib
    common_config = importlib.import_module("common.config")
    print("✓ 配置模块 (common.config)")
except ImportError as e:
    print(f"✗ 配置模块 (common.config): {e}")
    failed_imports.append(("common.config", str(e)))

if failed_imports:
    print(f"\n警告: {len(failed_imports)} 个模块导入失败")
    for module_name, error in failed_imports:
        print(f"  - {module_name}: {error}")
    print("这些错误可能在实际运行时通过相对导入解决")

# 测试主应用创建
print("\n4. 测试主应用创建...")
try:
    from main import app
    print("✓ 主应用创建成功")
    print(f"  应用名称: {app.title}")
    print(f"  应用版本: {app.version}")
    print(f"  路由数量: {len(app.routes)}")
except Exception as e:
    print(f"✗ 主应用创建失败: {e}")
    print("详细错误信息:")
    traceback.print_exc()
    sys.exit(1)

# 测试配置加载
print("\n5. 测试配置加载...")
try:
    import importlib
    common_config = importlib.import_module("common.config")
    settings = common_config.settings
    print("✓ 配置加载成功")
    print(f"  应用名称: {settings.app_name}")
    print(f"  版本: {settings.version}")
    print(f"  主机: {settings.host}")
    print(f"  端口: {settings.port}")
except Exception as e:
    print(f"✗ 配置加载失败: {e}")

# 测试服务初始化
print("\n6. 测试服务初始化...")
try:
    handler_module = importlib.import_module("handler.guixiaoxirag_service")
    GuiXiaoXiRagService = handler_module.GuiXiaoXiRagService
    service = GuiXiaoXiRagService()
    print("✓ 服务实例创建成功")
    
    # 异步测试初始化
    async def test_init():
        try:
            await service.initialize()
            print("✓ 服务初始化成功")
            return True
        except Exception as e:
            print(f"✗ 服务初始化失败: {e}")
            return False
    
    # 运行异步测试
    init_success = asyncio.run(test_init())
    if not init_success:
        print("服务初始化失败，但这可能是由于缺少配置文件或依赖")
        
except Exception as e:
    print(f"✗ 服务创建失败: {e}")
    print("详细错误信息:")
    traceback.print_exc()

print("\n=== 测试完成 ===")
print("\n如果上述测试大部分通过，可以尝试启动服务:")
print("python main.py")
print("\n或者使用uvicorn:")
print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
