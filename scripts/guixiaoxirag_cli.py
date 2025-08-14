#!/usr/bin/env python3
"""
GuiXiaoXiRag FastAPI 命令行工具
提供便捷的命令行接口
"""
import asyncio
import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from examples.api_client import GuiXiaoXiRagClient


async def cmd_health(args):
    """健康检查命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.health_check()


async def cmd_status(args):
    """系统状态命令"""
    client = GuiXiaoXiRagClient(args.url)
    status = await client.get_system_status()
    if status:
        print(f"服务名称: {status['service_name']}")
        print(f"版本: {status['version']}")
        print(f"初始化状态: {status['initialized']}")
        print(f"工作目录: {status['working_dir']}")
        print(f"运行时间: {status['uptime']:.1f}秒")


async def cmd_insert(args):
    """插入文档命令"""
    client = GuiXiaoXiRagClient(args.url)

    if args.file:
        # 上传文件
        track_id = await client.upload_file(args.file)
        if track_id:
            print(f"文件上传成功，跟踪ID: {track_id}")
    elif args.text:
        # 插入文本
        track_id = await client.insert_text(
            args.text,
            args.doc_id,
            knowledge_base=args.knowledge_base,
            language=args.language
        )
        if track_id:
            print(f"文本插入成功，跟踪ID: {track_id}")
    else:
        print("请提供 --text 或 --file 参数")


async def cmd_query(args):
    """查询命令"""
    client = GuiXiaoXiRagClient(args.url)

    if args.optimized:
        result = await client.optimized_query(
            args.query,
            args.mode,
            args.performance_level
        )
    else:
        result = await client.query(
            args.query,
            args.mode,
            top_k=args.top_k,
            knowledge_base=args.knowledge_base,
            language=args.language
        )

    if result:
        print(f"\n查询结果:")
        print("=" * 50)
        print(result)
        print("=" * 50)


async def cmd_kb_list(args):
    """列出知识库命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.list_knowledge_bases()


async def cmd_kb_create(args):
    """创建知识库命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.create_knowledge_base(args.name, args.description or "")


async def cmd_kb_switch(args):
    """切换知识库命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.switch_knowledge_base(args.name)


async def cmd_metrics(args):
    """性能指标命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.get_metrics()


async def cmd_graph_stats(args):
    """知识图谱统计命令"""
    client = GuiXiaoXiRagClient(args.url)
    await client.get_knowledge_graph_stats()


async def cmd_languages(args):
    """语言管理命令"""
    client = GuiXiaoXiRagClient(args.url)

    if args.lang_command == "list":
        await client.get_supported_languages()
    elif args.lang_command == "set":
        await client.set_language(args.language)
    elif args.lang_command == "current":
        config = await client.get_service_config()
        if config:
            print(f"当前语言: {config['language']}")


async def cmd_service(args):
    """服务管理命令"""
    client = GuiXiaoXiRagClient(args.url)

    if args.service_command == "config":
        await client.get_service_config()
    elif args.service_command == "effective-config":
        await cmd_effective_config(args)
    elif args.service_command == "update-config":
        await cmd_update_config(args)
    elif args.service_command == "switch":
        await client.switch_knowledge_base(args.knowledge_base, args.language)


async def cmd_effective_config(args):
    """获取有效配置命令"""
    client = GuiXiaoXiRagClient(args.url)

    try:
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{args.url}/service/effective-config")

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    config = data["data"]

                    print("🔧 当前有效配置:")
                    print(f"  应用名称: {config['app_name']}")
                    print(f"  版本: {config['version']}")
                    print(f"  服务地址: {config['host']}:{config['port']}")
                    print(f"  调试模式: {config['debug']}")
                    print(f"  工作目录: {config['working_dir']}")
                    print(f"  日志级别: {config['log_level']}")

                    print("\n🧠 LLM配置:")
                    llm = config['llm']
                    print(f"  API地址: {llm['api_base']}")
                    print(f"  API密钥: {llm['api_key']}")
                    print(f"  模型: {llm['model']}")
                    print(f"  提供商: {llm['provider']}")

                    print("\n📊 Embedding配置:")
                    embedding = config['embedding']
                    print(f"  API地址: {embedding['api_base']}")
                    print(f"  API密钥: {embedding['api_key']}")
                    print(f"  模型: {embedding['model']}")
                    print(f"  维度: {embedding['dim']}")
                    print(f"  提供商: {embedding['provider']}")

                    print("\n⚙️ 其他配置:")
                    print(f"  最大文件大小: {config['max_file_size_mb']}MB")
                    print(f"  最大Token数: {config['max_token_size']}")
                    print(f"  Streamlit端口: {config['streamlit_port']}")

                    if 'azure' in config:
                        print("\n☁️ Azure配置:")
                        azure = config['azure']
                        print(f"  API版本: {azure['api_version']}")
                        print(f"  部署名称: {azure['deployment_name']}")

                else:
                    print(f"❌ 获取配置失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 获取有效配置失败: {e}")


async def cmd_update_config(args):
    """更新配置命令"""
    try:
        import httpx

        # 构建配置更新数据
        config_data = {}

        # 从命令行参数构建配置数据
        if hasattr(args, 'llm_model') and args.llm_model:
            config_data['openai_chat_model'] = args.llm_model
        if hasattr(args, 'embedding_model') and args.embedding_model:
            config_data['openai_embedding_model'] = args.embedding_model
        if hasattr(args, 'llm_api_key') and args.llm_api_key:
            config_data['openai_chat_api_key'] = args.llm_api_key
        if hasattr(args, 'embedding_api_key') and args.embedding_api_key:
            config_data['openai_embedding_api_key'] = args.embedding_api_key
        if hasattr(args, 'llm_api_base') and args.llm_api_base:
            config_data['openai_api_base'] = args.llm_api_base
        if hasattr(args, 'embedding_api_base') and args.embedding_api_base:
            config_data['openai_embedding_api_base'] = args.embedding_api_base
        if hasattr(args, 'log_level') and args.log_level:
            config_data['log_level'] = args.log_level
        if hasattr(args, 'embedding_dim') and args.embedding_dim:
            config_data['embedding_dim'] = args.embedding_dim

        if not config_data:
            print("❌ 没有提供要更新的配置项")
            return

        async with httpx.AsyncClient() as http_client:
            response = await http_client.post(
                f"{args.url}/service/config/update",
                json=config_data
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result = data["data"]

                    print("✅ 配置更新成功:")
                    print(f"  更新字段: {', '.join(result['updated_fields'])}")
                    print(f"  需要重启: {'是' if result['restart_required'] else '否'}")

                    if result['restart_required']:
                        print("\n⚠️ 某些配置更改需要重启服务才能完全生效")

                else:
                    print(f"❌ 配置更新失败: {data.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 更新配置失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GuiXiaoXiRag FastAPI 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s health                           # 健康检查
  %(prog)s status                           # 系统状态
  %(prog)s insert --text "测试文档"          # 插入文本
  %(prog)s insert --text "测试" --knowledge-base my_kb --language 中文  # 插入到指定知识库
  %(prog)s insert --file document.txt       # 上传文件
  %(prog)s query "什么是AI？"                # 基础查询
  %(prog)s query "What is AI?" --knowledge-base my_kb --language 英文   # 指定知识库和语言查询
  %(prog)s query "什么是AI？" --optimized    # 优化查询
  %(prog)s kb list                          # 列出知识库
  %(prog)s kb create test_kb                # 创建知识库
  %(prog)s kb switch test_kb                # 切换知识库
  %(prog)s lang list                        # 列出支持的语言
  %(prog)s lang set 英文                    # 设置默认语言
  %(prog)s service config                   # 查看服务配置
  %(prog)s service effective-config         # 查看有效配置（包含默认值）
  %(prog)s service update-config --llm-model gpt-4 --log-level DEBUG  # 更新配置
  %(prog)s service switch my_kb --language 中文  # 切换服务配置
  %(prog)s metrics                          # 性能指标
  %(prog)s graph-stats                      # 图谱统计
        """
    )
    
    parser.add_argument(
        "--url", 
        default="http://localhost:8002",
        help="API服务地址 (默认: http://localhost:8002)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 健康检查
    subparsers.add_parser("health", help="健康检查")
    
    # 系统状态
    subparsers.add_parser("status", help="系统状态")
    
    # 插入文档
    insert_parser = subparsers.add_parser("insert", help="插入文档")
    insert_group = insert_parser.add_mutually_exclusive_group(required=True)
    insert_group.add_argument("--text", help="要插入的文本内容")
    insert_group.add_argument("--file", help="要上传的文件路径")
    insert_parser.add_argument("--doc-id", help="文档ID")
    insert_parser.add_argument("--knowledge-base", help="知识库名称")
    insert_parser.add_argument("--language", help="处理语言")
    
    # 查询
    query_parser = subparsers.add_parser("query", help="执行查询")
    query_parser.add_argument("query", help="查询内容")
    query_parser.add_argument("--mode", default="hybrid",
                             choices=["local", "global", "hybrid", "naive", "mix", "bypass"],
                             help="查询模式 (默认: hybrid)")
    query_parser.add_argument("--top-k", type=int, default=20, help="返回结果数量 (默认: 20)")
    query_parser.add_argument("--optimized", action="store_true", help="使用优化查询")
    query_parser.add_argument("--performance-level", default="balanced",
                             choices=["fast", "balanced", "quality"],
                             help="性能级别 (默认: balanced)")
    query_parser.add_argument("--knowledge-base", help="知识库名称")
    query_parser.add_argument("--language", help="回答语言")
    
    # 知识库管理
    kb_parser = subparsers.add_parser("kb", help="知识库管理")
    kb_subparsers = kb_parser.add_subparsers(dest="kb_command", help="知识库操作")
    
    kb_subparsers.add_parser("list", help="列出知识库")
    
    kb_create_parser = kb_subparsers.add_parser("create", help="创建知识库")
    kb_create_parser.add_argument("name", help="知识库名称")
    kb_create_parser.add_argument("--description", help="知识库描述")
    
    kb_switch_parser = kb_subparsers.add_parser("switch", help="切换知识库")
    kb_switch_parser.add_argument("name", help="知识库名称")

    # 语言管理
    lang_parser = subparsers.add_parser("lang", help="语言管理")
    lang_subparsers = lang_parser.add_subparsers(dest="lang_command", help="语言操作")

    lang_subparsers.add_parser("list", help="列出支持的语言")
    lang_subparsers.add_parser("current", help="查看当前语言")

    lang_set_parser = lang_subparsers.add_parser("set", help="设置语言")
    lang_set_parser.add_argument("language", help="目标语言")

    # 服务管理
    service_parser = subparsers.add_parser("service", help="服务管理")
    service_subparsers = service_parser.add_subparsers(dest="service_command", help="服务操作")

    service_subparsers.add_parser("config", help="查看服务配置")
    service_subparsers.add_parser("effective-config", help="查看有效配置（包含用户自定义和默认值）")

    # 配置更新子命令
    service_update_parser = service_subparsers.add_parser("update-config", help="更新服务配置")
    service_update_parser.add_argument("--llm-model", help="LLM模型名称")
    service_update_parser.add_argument("--embedding-model", help="Embedding模型名称")
    service_update_parser.add_argument("--llm-api-key", help="LLM API密钥")
    service_update_parser.add_argument("--embedding-api-key", help="Embedding API密钥")
    service_update_parser.add_argument("--llm-api-base", help="LLM API基础URL")
    service_update_parser.add_argument("--embedding-api-base", help="Embedding API基础URL")
    service_update_parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="日志级别")
    service_update_parser.add_argument("--embedding-dim", type=int, help="Embedding维度")

    service_switch_parser = service_subparsers.add_parser("switch", help="切换服务配置")
    service_switch_parser.add_argument("knowledge_base", help="知识库名称")
    service_switch_parser.add_argument("--language", help="语言设置")

    # 监控
    subparsers.add_parser("metrics", help="性能指标")
    subparsers.add_parser("graph-stats", help="知识图谱统计")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行命令
    try:
        if args.command == "health":
            asyncio.run(cmd_health(args))
        elif args.command == "status":
            asyncio.run(cmd_status(args))
        elif args.command == "insert":
            asyncio.run(cmd_insert(args))
        elif args.command == "query":
            asyncio.run(cmd_query(args))
        elif args.command == "kb":
            if args.kb_command == "list":
                asyncio.run(cmd_kb_list(args))
            elif args.kb_command == "create":
                asyncio.run(cmd_kb_create(args))
            elif args.kb_command == "switch":
                asyncio.run(cmd_kb_switch(args))
            else:
                kb_parser.print_help()
        elif args.command == "lang":
            if args.lang_command == "list":
                asyncio.run(cmd_languages(args))
            elif args.lang_command == "current":
                asyncio.run(cmd_languages(args))
            elif args.lang_command == "set":
                asyncio.run(cmd_languages(args))
            else:
                lang_parser.print_help()
        elif args.command == "service":
            if args.service_command == "config":
                asyncio.run(cmd_service(args))
            elif args.service_command == "effective-config":
                asyncio.run(cmd_service(args))
            elif args.service_command == "update-config":
                asyncio.run(cmd_service(args))
            elif args.service_command == "switch":
                asyncio.run(cmd_service(args))
            else:
                service_parser.print_help()
        elif args.command == "metrics":
            asyncio.run(cmd_metrics(args))
        elif args.command == "graph-stats":
            asyncio.run(cmd_graph_stats(args))
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    main()
