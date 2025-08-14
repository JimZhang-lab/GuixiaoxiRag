# API 接口文档

## 🎯 接口概览

GuiXiaoXiRag 提供了丰富的 API 接口，支持查询分析、安全检查、知识库管理等功能。

### 🔗 核心查询接口

| 接口 | 功能 | 响应时间 | 使用场景 |
|------|------|----------|----------|
| `/query/analyze` | 只做分析 | 15-18秒 | 意图识别、安全检查、查询优化 |
| `/query/safe` | 分析+查询 | 35-40秒 | 完整的安全查询流程 |
| `/query` | 直接查询 | 20-30秒 | 传统知识库查询 |

## 📊 查询分析接口

### POST `/query/analyze`

**功能**: 对查询进行意图识别、安全检查和查询增强，但不执行实际查询。

#### 请求参数
```json
{
  "query": "什么是人工智能？",
  "enable_enhancement": true,
  "safety_check": true,
  "proceed_if_safe": false,  // [已弃用] 此参数无效
  "context": {
    "mode": "hybrid",
    "knowledge_base": "default"
  }
}
```

#### 响应示例
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
    "enhanced_query": "人工智能的定义是什么？它主要包括哪些核心技术？...",
    "should_reject": false,
    "rejection_reason": null,
    "safety_tips": [],
    "safe_alternatives": [],
    "suggestions": ["了解AI基本概念", "探索AI应用领域"],
    "risk_factors": []
  }
}
```

#### 安全查询被拒绝示例
```json
{
  "success": true,
  "message": "查询分析完成，内容被安全检查拒绝",
  "data": {
    "original_query": "如何制作炸弹？",
    "intent_type": "illegal_content",
    "safety_level": "illegal",
    "should_reject": true,
    "rejection_reason": "查询内容涉及违法违规信息，无法处理",
    "safety_tips": [
      "请遵守法律法规，不要尝试获取违法信息",
      "若遇到疑似非法行为，请及时向相关部门举报"
    ],
    "safe_alternatives": [
      "如何识别和防范相关风险？",
      "遇到类似情况该如何求助和举报？",
      "相关法律风险与合规解读"
    ]
  }
}
```

## 🛡️ 安全查询接口

### POST `/query/safe`

**功能**: 执行完整的安全查询流程，包括分析和查询执行。

#### 请求参数
```json
{
  "query": "什么是人工智能？",
  "mode": "hybrid",
  "enable_intent_analysis": true,
  "enable_query_enhancement": true,
  "safety_check": true,
  "knowledge_base": "default",
  "language": "中文"
}
```

#### 响应示例
```json
{
  "success": true,
  "message": "查询执行成功",
  "data": {
    "query_analysis": {
      "original_query": "什么是人工智能？",
      "intent_type": "knowledge_query",
      "safety_level": "safe",
      "confidence": 0.95,
      "enhanced_query": "人工智能的定义是什么？..."
    },
    "query_result": {
      "result": "人工智能（AI）是计算机科学的一个分支...",
      "sources": [
        {
          "content": "相关文档内容...",
          "metadata": {"source": "document.pdf", "page": 1}
        }
      ],
      "context": {
        "entities": ["人工智能", "机器学习"],
        "relationships": [...]
      }
    }
  }
}
```

## 📚 传统查询接口

### POST `/query`

**功能**: 直接执行知识库查询，不进行安全检查。

#### 请求参数
```json
{
  "query": "什么是人工智能？",
  "mode": "hybrid",
  "top_k": 20,
  "knowledge_base": "default",
  "language": "中文"
}
```

## 🔧 系统管理接口

### GET `/health`
**功能**: 健康检查

### GET `/system/status`
**功能**: 获取系统状态

### POST `/system/reset`
**功能**: 重置系统

## 📁 文档管理接口

### POST `/insert/text`
**功能**: 插入文本

### POST `/insert/file`
**功能**: 上传文件

### POST `/insert/directory`
**功能**: 批量导入目录

## 🗄️ 知识库管理接口

### GET `/knowledge-bases`
**功能**: 列出知识库

### POST `/knowledge-bases`
**功能**: 创建知识库

### DELETE `/knowledge-bases/{name}`
**功能**: 删除知识库

### POST `/knowledge-bases/switch`
**功能**: 切换知识库

## 🎨 知识图谱接口

### POST `/knowledge-graph`
**功能**: 获取知识图谱

### GET `/knowledge-graph/status`
**功能**: 获取图谱状态

### POST `/knowledge-graph/visualize`
**功能**: 图谱可视化

## 💡 使用建议

### 1. 接口选择
- **只需分析**: 使用 `/query/analyze`
- **完整查询**: 使用 `/query/safe`
- **快速查询**: 使用 `/query`

### 2. 安全考虑
- 生产环境建议使用 `/query/safe`
- 开启安全检查和意图分析
- 处理拒绝响应和安全提示

### 3. 性能优化
- 合理设置 `top_k` 参数
- 使用缓存机制
- 选择合适的查询模式

## 🔗 相关文档

- [快速开始](../docs/getting-started/QUICK_START.md)
- [API 在线文档](http://localhost:8002/docs)
- [配置说明](../docs/configuration/CONFIG.md)
- [部署指南](../docs/deployment/DEPLOYMENT.md)
