# 意图识别系统使用指南

## 概述

意图识别系统是GuiXiaoXiRag的核心组件之一，提供智能查询意图分析和内容安全检查功能。系统采用模块化设计，分为核心功能和配置管理两个主要部分。

## 系统架构

### 核心模块
- **处理器** (`core/intent_recognition/processor.py`): 核心意图识别处理器
- **模型** (`core/intent_recognition/models.py`): 数据模型定义
- **配置管理器** (`core/intent_recognition/config_manager.py`): 配置管理器
- **DFA过滤器** (`core/intent_recognition/dfa_filter.py`): 敏感词过滤器
- **工具函数** (`core/intent_recognition/utils.py`): 工具函数

### API层
- **核心API** (`api/intent_recogition_api.py`): 意图识别核心业务逻辑
- **配置API** (`api/intent_config_api.py`): 配置管理业务逻辑

### 路由层
- **核心路由** (`routers/intent_recogition_router.py`): `/api/v1/intent` 路由
- **配置路由** (`routers/intent_config_router.py`): `/api/v1/intent-config` 路由

## 功能特性

### 1. 意图分析
- 支持多种意图类型识别（知识查询、事实性问题、分析性问题等）
- 基于大模型的智能分析，失败时自动回退到规则分析
- 可配置的置信度阈值
- 支持自定义意图类型

### 2. 安全检查
- 多层次安全检查（安全、可疑、不安全、非法）
- DFA敏感词过滤
- 教育导向和实施导向的区分
- 自定义安全规则

### 3. 查询增强
- 基于意图类型的查询优化
- 智能查询扩展和重写
- 上下文感知的增强建议

### 4. 配置管理
- 动态配置更新，无需重启服务
- 配置验证和导入导出
- 热更新支持
- 配置文件监听（可选）

## 使用示例

### 基础意图分析

```python
import requests

# 意图分析
response = requests.post("http://localhost:8002/api/v1/intent/analyze", json={
    "query": "什么是人工智能？",
    "context": {"domain": "technology"}
})

result = response.json()
print(f"意图类型: {result['data']['intent_type']}")
print(f"安全级别: {result['data']['safety_level']}")
print(f"置信度: {result['data']['confidence']}")
```

### 安全检查

```python
# 内容安全检查
response = requests.post("http://localhost:8002/api/v1/intent/safety-check", json={
    "content": "需要检查的内容",
    "check_type": "comprehensive"
})

result = response.json()
print(f"是否安全: {result['data']['is_safe']}")
print(f"风险因素: {result['data']['risk_factors']}")
```

### 配置管理

```python
# 获取当前配置
response = requests.get("http://localhost:8002/api/v1/intent-config/current")
config = response.json()

# 添加自定义意图类型
response = requests.post("http://localhost:8002/api/v1/intent-config/intent-types", json={
    "intent_type": "product_inquiry",
    "display_name": "产品咨询",
    "priority": 80,
    "category": "business"
})

# 更新提示词
response = requests.post("http://localhost:8002/api/v1/intent-config/prompts", json={
    "prompt_type": "custom_analysis",
    "prompt_content": "请分析以下查询的商业价值：\n\n查询：\"{query}\""
})
```

## 配置说明

### 环境变量配置

在 `.env` 文件中设置以下配置：

```bash
# 意图识别配置
INTENT_CONFIDENCE_THRESHOLD=0.7
INTENT_ENABLE_LLM=true
INTENT_ENABLE_DFA_FILTER=true
INTENT_ENABLE_QUERY_ENHANCEMENT=true
INTENT_SENSITIVE_VOCABULARY_PATH=core/intent_recognition/sensitive_vocabulary
INTENT_CONFIG_PATH=./data/custom_intents
```

### 配置文件结构

配置文件位于 `data/custom_intents/processor_config.json`：

```json
{
  "base": {
    "confidence_threshold": 0.7,
    "enable_llm": true,
    "enable_dfa_filter": true,
    "enable_query_enhancement": true
  },
  "intent_types": {
    "intent_types": {
      "knowledge_query": "知识查询",
      "factual_question": "事实性问题"
    },
    "custom_intent_types": {
      "business_inquiry": "商业咨询"
    },
    "intent_priorities": {
      "business_inquiry": 85
    }
  },
  "llm_prompts": {
    "safety_check_prompt": "...",
    "intent_analysis_prompt": "...",
    "query_enhancement_prompt": "...",
    "custom_prompts": {}
  },
  "safety": {
    "safety_levels": {
      "safe": "安全",
      "suspicious": "可疑",
      "unsafe": "不安全",
      "illegal": "非法"
    },
    "risk_keywords": ["赌博", "毒品", "色情"],
    "educational_patterns": ["如何防范", "如何识别"],
    "instructive_patterns": ["如何实施", "如何制作"],
    "custom_safety_rules": {}
  }
}
```

## API接口详情

### 核心功能接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/intent/health` | GET | 健康检查 |
| `/api/v1/intent/analyze` | POST | 意图分析 |
| `/api/v1/intent/safety-check` | POST | 安全检查 |
| `/api/v1/intent/status` | GET | 处理器状态 |

### 配置管理接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/intent-config/current` | GET | 获取当前配置 |
| `/api/v1/intent-config/update` | POST | 更新配置 |
| `/api/v1/intent-config/reload` | POST | 重新加载配置 |
| `/api/v1/intent-config/intent-types` | GET/POST | 意图类型管理 |
| `/api/v1/intent-config/prompts` | GET/POST | 提示词管理 |
| `/api/v1/intent-config/safety` | GET/POST | 安全配置管理 |
| `/api/v1/intent-config/validate` | POST | 配置验证 |
| `/api/v1/intent-config/export` | GET | 导出配置 |
| `/api/v1/intent-config/import` | POST | 导入配置 |

## 最佳实践

### 1. 意图类型设计
- 使用清晰的命名约定
- 设置合理的优先级
- 按业务领域分类管理

### 2. 安全配置
- 定期更新敏感词库
- 设置合适的安全阈值
- 区分教育和实施导向

### 3. 性能优化
- 合理设置置信度阈值
- 启用缓存机制
- 监控处理器状态

### 4. 配置管理
- 定期备份配置文件
- 使用版本控制管理配置变更
- 在生产环境中谨慎使用热更新

## 故障排除

### 常见问题

1. **意图识别准确率低**
   - 检查置信度阈值设置
   - 优化提示词内容
   - 增加训练样本

2. **安全检查误报**
   - 调整安全规则配置
   - 更新敏感词库
   - 优化教育模式识别

3. **配置更新失败**
   - 检查配置文件格式
   - 验证配置数据有效性
   - 查看错误日志

### 日志查看

```bash
# 查看意图识别相关日志
tail -f logs/guixiaoxirag_service.log | grep intent
```

## 更新历史

### v0.1.0
- 重构意图识别系统架构
- 分离核心功能和配置管理
- 清理重复接口，优化代码结构
- 支持动态配置管理和热更新
- 完善文档和使用指南
