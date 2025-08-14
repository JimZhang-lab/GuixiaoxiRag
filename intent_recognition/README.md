# 意图识别服务

## 🎯 概述

意图识别服务是一个独立的微服务，提供查询意图识别、安全检查和查询增强功能。该服务可以独立部署和运行，通过 REST API 对外提供服务。

## ✨ 核心功能

### 🧠 智能分析
- **意图识别**: 识别查询的具体意图类型（知识查询、事实问题、程序性问题等）
- **安全检查**: 基于LLM和规则的多层安全检查机制
- **查询增强**: 智能优化查询内容，提高检索效果

### 🛡️ 安全防护
- **违规内容拒绝**: 自动识别和拒绝违法违规查询
- **正向引导**: 为违规查询提供合规的替代建议
- **安全提示**: 生成相关的安全提示和风险警告

### 🔧 技术特性
- **LLM集成**: 支持大模型进行语义级分析
- **规则回退**: LLM不可用时自动使用规则检查
- **Think标签处理**: 自动过滤大模型思考过程
- **异步处理**: 高性能的异步API设计

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pydantic requests
```

### 2. 启动服务

```bash
cd intent_recognition
python start_service.py
```

### 3. 验证服务

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

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `INTENT_HOST` | `0.0.0.0` | 服务主机 |
| `INTENT_PORT` | `8003` | 服务端口 |
| `INTENT_LOG_LEVEL` | `INFO` | 日志级别 |
| `INTENT_LLM_ENABLED` | `false` | 是否启用LLM |
| `INTENT_LLM_API_URL` | - | LLM API地址 |
| `INTENT_LLM_API_KEY` | - | LLM API密钥 |

### 配置文件

创建 `.env` 文件：
```env
INTENT_HOST=0.0.0.0
INTENT_PORT=8003
INTENT_LOG_LEVEL=INFO
INTENT_LLM_ENABLED=false
```

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

## 🔗 集成使用

### Python客户端

```python
from intent_recognition.test_client import IntentRecognitionClient

client = IntentRecognitionClient("http://localhost:8003")

# 分析查询意图
result = client.analyze_intent("什么是人工智能？")
print(result)
```

### 与主服务集成

```python
import requests

def analyze_query_intent(query: str):
    response = requests.post(
        "http://localhost:8003/analyze",
        json={"query": query}
    )
    return response.json()
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

## 📞 技术支持

- **API文档**: http://localhost:8003/docs
- **健康检查**: http://localhost:8003/health
- **服务信息**: http://localhost:8003/info
