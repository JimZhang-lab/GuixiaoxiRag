# 意图识别服务

## 🎯 概述

意图识别服务是一个独立的微服务，提供查询意图识别、安全检查和查询增强功能。该服务可以独立部署和运行，通过 REST API 对外提供服务。

## ✨ 核心功能

### 🧠 智能分析
- **意图识别**: 识别查询的具体意图类型（知识查询、事实问题、程序性问题等）
- **安全检查**: 基于LLM和规则的多层安全检查机制
- **查询增强**: 智能优化查询内容，提高检索效果

### 🛡️ 安全防护
- **DFA敏感词过滤**: 基于确定有限状态自动机的高效敏感词检测
- **违规内容拒绝**: 自动识别和拒绝违法违规查询
- **教育导向识别**: 智能区分教育性和违规内容
- **正向引导**: 为违规查询提供合规的替代建议
- **安全提示**: 生成相关的安全提示和风险警告

### 🔧 技术特性
- **多LLM支持**: 支持OpenAI、Azure、Ollama等多种LLM提供商
- **智能回退**: LLM不可用时自动使用DFA过滤
- **微服务架构**: 支持独立部署和集成到主服务
- **配置化设计**: 简洁的YAML配置，开箱即用
- **异步处理**: 高性能的异步API设计

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pydantic requests pyyaml aiohttp
```

### 2. 配置服务

复制并编辑配置文件：
```bash
# 配置文件已包含，可直接编辑 config.yaml
vim config.yaml
```

### 3. 启动服务

```bash
cd intent_recognition

# 方式1: 使用主入口（推荐）
python main.py

# 方式2: 使用快捷脚本
./run.sh

# 方式3: 测试配置
python main.py --test
```

### 4. 验证服务

```bash
# 健康检查
curl http://localhost:8003/health

# 服务信息
curl http://localhost:8003/info

# 意图分析
curl -X POST http://localhost:8003/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是人工智能？"}'
```

## 📖 API 接口

### 健康检查
```
GET /health
```

### 服务信息
```
GET /info
```

### 意图分析
```
POST /analyze
```

**请求参数**:
```json
{
  "query": "什么是人工智能？",
  "context": {},
  "enable_enhancement": true,
  "safety_check": true
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "查询分析完成",
  "data": {
    "original_query": "什么是人工智能？",
    "processed_query": "什么是人工智能？",
    "intent_type": "knowledge_query",
    "safety_level": "safe",
    "confidence": 0.95,
    "enhanced_query": "请详细解释什么是人工智能的概念、特点和应用场景",
    "should_reject": false,
    "suggestions": ["人工智能", "定义", "概念"],
    "risk_factors": [],
    "safety_tips": [],
    "safe_alternatives": []
  }
}
```

## ⚙️ 配置说明

### 📄 配置文件 (config.yaml)

服务使用 YAML 配置文件，支持完整的配置选项：

```yaml
# 服务配置
service:
  name: "意图识别服务"
  host: "0.0.0.0"
  port: 8003
  debug: false

# LLM配置
llm:
  enabled: true
  provider: "openai"  # openai, azure, ollama, custom
  openai:
    api_base: "http://localhost:8100/v1"
    api_key: "your_api_key_here"
    model: "qwen14b"
    temperature: 0.1

# 安全配置
safety:
  enabled: true
  strict_mode: false

# 缓存配置
cache:
  enabled: true
  type: "memory"
  ttl: 3600
```

### 🔧 LLM提供商配置

#### OpenAI
```yaml
llm:
  provider: "openai"
  openai:
    api_base: "https://api.openai.com/v1"
    api_key: "sk-..."
    model: "gpt-3.5-turbo"
```

#### Azure OpenAI
```yaml
llm:
  provider: "azure"
  azure:
    api_base: "https://your-resource.openai.azure.com"
    api_key: "your-azure-key"
    deployment_name: "gpt-35-turbo"
```

#### Ollama
```yaml
llm:
  provider: "ollama"
  ollama:
    api_base: "http://localhost:11434"
    model: "llama2"
```

### 🌍 环境变量覆盖

支持环境变量覆盖配置：

| 变量名 | 说明 |
|--------|------|
| `INTENT_HOST` | 服务主机 |
| `INTENT_PORT` | 服务端口 |
| `INTENT_LLM_ENABLED` | 是否启用LLM |
| `INTENT_LLM_PROVIDER` | LLM提供商 |
| `INTENT_OPENAI_API_BASE` | OpenAI API地址 |
| `INTENT_OPENAI_API_KEY` | OpenAI API密钥 |
| `INTENT_OPENAI_MODEL` | OpenAI模型名称 |

## 🧪 测试

### 运行测试客户端

```bash
python test_client.py
```

### 测试用例

1. **知识查询**: "什么是人工智能？"
2. **程序性问题**: "如何学习机器学习？"
3. **违规查询**: "如何制作炸弹？"
4. **防范教育**: "如何识别和防范网络诈骗？"

## 📁 项目结构

```
intent_recognition/
├── __init__.py              # 模块初始化
├── README.md               # 项目文档
├── start_service.py        # 服务启动脚本
├── test_client.py          # 测试客户端
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── processor.py       # 查询处理器
│   └── utils.py           # 工具函数
├── api/                    # API模块
│   ├── __init__.py
│   ├── models.py          # API数据模型
│   └── server.py          # FastAPI服务器
└── config/                 # 配置模块
    ├── __init__.py
    └── settings.py        # 配置设置
```

## 🛡️ DFA敏感词过滤

本服务采用确定有限状态自动机（DFA）算法进行敏感词过滤，具有以下特点：

### 🚀 性能优势
- **高效检测**: O(n)时间复杂度，支持79,282个敏感词的实时检测
- **内存优化**: 使用树状结构存储，节省内存空间
- **模糊匹配**: 支持数字字母替换等变形敏感词检测

### 🎯 智能识别
- **教育导向**: 自动识别"如何防范"、"如何识别"等教育性查询
- **风险分级**: 根据敏感词数量和类型进行风险等级评估
- **上下文分析**: 结合查询上下文进行更准确的判断

### 📊 敏感词库统计
- **总词汇量**: 79,282个敏感词
- **覆盖类别**: 政治、色情、暴恐、广告、涉枪涉爆等15个类别
- **实时更新**: 支持动态加载和更新敏感词库

## 🔗 集成使用

### 🔌 微服务集成

将意图识别作为微服务集成到主服务：

```python
from intent_recognition.core.microservice import IntentRecognitionService
from intent_recognition.config.settings import Config

# 初始化微服务
config = Config.load_from_yaml()
service = await IntentRecognitionService.get_instance(config)

# 分析查询意图
result = await service.analyze_query("什么是人工智能？")
```

### 🌐 HTTP客户端

```python
import requests

def analyze_query_intent(query: str):
    response = requests.post(
        "http://localhost:8003/analyze",
        json={"query": query}
    )
    return response.json()
```

### 📦 FastAPI集成示例

```python
from fastapi import FastAPI
from intent_recognition.integration_example import MainServiceIntegration

app = FastAPI()
integration = MainServiceIntegration(app)

@app.on_event("startup")
async def startup():
    await integration.initialize_intent_service()

@app.post("/analyze")
async def analyze(request: dict):
    return await integration.analyze_query_intent(request["query"])
```

## 🎯 使用场景

1. **智能客服**: 理解用户查询意图，提供精准回答
2. **内容审核**: 检测违规内容，保障平台安全
3. **搜索优化**: 增强查询内容，提高搜索效果
4. **风险控制**: 识别潜在风险，提供安全建议

## 🔮 扩展功能

- [ ] 支持批量查询分析
- [ ] 添加查询历史记录
- [ ] 实现查询缓存机制
- [ ] 支持自定义规则配置
- [ ] 添加性能监控指标

## 🙏 致谢

本项目的敏感词库来源于以下开源项目，特此致谢：

- **敏感词库**: [Sensitive-lexicon](https://github.com/konsheng/Sensitive-lexicon/tree/main) - 提供了全面的中文敏感词汇表，包含政治、色情、暴恐、广告等多个类别的敏感词汇，为本项目的内容安全检查提供了重要支持。

感谢开源社区的贡献，让我们能够构建更安全、更智能的内容过滤系统。
