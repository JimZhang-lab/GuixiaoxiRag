#!/usr/bin/env python3
"""
配置管理工具
用于验证、生成和管理项目配置文件
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from server.config import settings, validate_config, get_config_summary
    from streamlit_app.config import streamlit_settings, validate_streamlit_config, get_streamlit_config_summary
except ImportError as e:
    print(f"❌ 导入配置模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


def check_env_file():
    """检查 .env 文件是否存在"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env 文件不存在")
            print(f"📋 请复制 {env_example} 为 {env_file} 并修改配置")
            return False
        else:
            print("❌ .env 和 .env.example 文件都不存在")
            return False
    
    print("✅ .env 文件存在")
    return True


def validate_all_configs():
    """验证所有配置"""
    print("🔍 验证配置文件...")
    
    # 检查 .env 文件
    env_exists = check_env_file()
    
    # 验证服务器配置
    print("\n📊 验证服务器配置:")
    server_valid = validate_config()
    
    # 验证 Streamlit 配置
    print("\n🎨 验证 Streamlit 配置:")
    streamlit_valid = validate_streamlit_config()
    
    # 总结
    print("\n" + "="*50)
    if env_exists and server_valid and streamlit_valid:
        print("✅ 所有配置验证通过")
        return True
    else:
        print("❌ 配置验证失败，请检查上述警告")
        return False


def show_config_summary():
    """显示配置摘要"""
    print("📋 配置摘要:")
    print("\n🚀 服务器配置:")
    server_config = get_config_summary()
    for key, value in server_config.items():
        print(f"   {key}: {value}")
    
    print("\n🎨 Streamlit 配置:")
    streamlit_config = get_streamlit_config_summary()
    for key, value in streamlit_config.items():
        print(f"   {key}: {value}")


def generate_env_file():
    """生成 .env 文件"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if env_file.exists():
        response = input("⚠️  .env 文件已存在，是否覆盖？(y/N): ")
        if response.lower() != 'y':
            print("❌ 操作取消")
            return False
    
    if not env_example.exists():
        print("❌ .env.example 文件不存在，无法生成 .env 文件")
        return False
    
    try:
        # 复制 .env.example 到 .env
        with open(env_example, 'r', encoding='utf-8') as src:
            content = src.read()
        
        with open(env_file, 'w', encoding='utf-8') as dst:
            dst.write(content)
        
        print(f"✅ 成功生成 {env_file}")
        print("📝 请根据实际情况修改配置")
        return True
    
    except Exception as e:
        print(f"❌ 生成 .env 文件失败: {e}")
        return False


def check_required_env_vars():
    """检查必需的环境变量"""
    required_vars = [
        "OPENAI_API_BASE",
        "OPENAI_EMBEDDING_API_BASE",
        "OPENAI_CHAT_API_KEY",
        "OPENAI_CHAT_MODEL",
        "OPENAI_EMBEDDING_MODEL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var) == "your_api_key_here":
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  以下必需的环境变量未设置或使用默认值:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ 所有必需的环境变量已设置")
    return True


def test_api_connectivity():
    """测试API连接性"""
    import requests
    
    print("🔗 测试API连接性...")
    
    # 测试LLM服务
    try:
        llm_url = settings.openai_api_base.rstrip('/') + '/models'
        response = requests.get(llm_url, timeout=5)
        if response.status_code == 200:
            print("✅ LLM服务连接正常")
        else:
            print(f"⚠️  LLM服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ LLM服务连接失败: {e}")
    
    # 测试Embedding服务
    try:
        embed_url = settings.openai_embedding_api_base.rstrip('/') + '/models'
        response = requests.get(embed_url, timeout=5)
        if response.status_code == 200:
            print("✅ Embedding服务连接正常")
        else:
            print(f"⚠️  Embedding服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ Embedding服务连接失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GuiXiaoXiRag 配置管理工具")
    parser.add_argument("--validate", action="store_true", help="验证配置")
    parser.add_argument("--summary", action="store_true", help="显示配置摘要")
    parser.add_argument("--generate", action="store_true", help="生成 .env 文件")
    parser.add_argument("--check-env", action="store_true", help="检查环境变量")
    parser.add_argument("--test-api", action="store_true", help="测试API连接")
    parser.add_argument("--all", action="store_true", help="执行所有检查")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🔧 GuiXiaoXiRag 配置管理工具")
    print("="*50)
    
    if args.generate or args.all:
        generate_env_file()
        print()
    
    if args.validate or args.all:
        validate_all_configs()
        print()
    
    if args.check_env or args.all:
        check_required_env_vars()
        print()
    
    if args.test_api or args.all:
        test_api_connectivity()
        print()
    
    if args.summary or args.all:
        show_config_summary()
        print()
    
    print("🎉 配置管理完成")


if __name__ == "__main__":
    main()
