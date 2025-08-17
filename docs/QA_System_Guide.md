# GuiXiaoXiRag 问答系统使用指南

## 概述

GuiXiaoXiRag 问答系统是一个基于向量相似度的智能问答模块，集成在主系统中，提供快速、准确的问答服务。系统支持问答对的管理、智能查询、批量处理等功能。

## 主要特性

### 🚀 核心功能
- **智能问答**: 基于向量相似度的智能匹配
- **问答对管理**: 支持增删改查操作
- **批量处理**: 支持批量导入导出和查询
- **分类管理**: 支持问答对分类组织
- **统计分析**: 提供详细的统计信息
- **数据备份**: 支持数据备份和恢复

### 🛠️ 技术特性
- **向量化检索**: 使用embedding模型进行语义理解
- **相似度匹配**: 基于余弦相似度的精确匹配
- **多格式支持**: 支持JSON、CSV、Excel等格式
- **实时更新**: 支持动态添加和更新问答对
- **性能监控**: 提供详细的性能指标

## 快速开始

### 1. 系统初始化

问答系统会在服务启动时自动初始化，并加载默认的问答对。

```bash
# 启动服务
python main.py

# 检查问答系统状态
curl http://localhost:8002/api/v1/qa/health
```

### 2. 基础使用

#### 创建问答对
```bash
curl -X POST "http://localhost:8002/api/v1/qa/pairs" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是人工智能？",
    "answer": "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。",
    "category": "ai",
    "confidence": 0.95,
    "keywords": ["人工智能", "AI"],
    "source": "manual"
  }'
```

#### 查询问答
```bash
curl -X POST "http://localhost:8002/api/v1/qa/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "AI是什么？",
    "top_k": 3,
    "min_similarity": 0.7
  }'
```

#### 获取问答对列表
```bash
curl "http://localhost:8002/api/v1/qa/pairs?page=1&page_size=10&category=ai"
```

## API 接口详解

### 1. 健康检查

**端点**: `GET /api/v1/qa/health`

**描述**: 检查问答系统的健康状态

**响应示例**:
```json
{
  "success": true,
  "message": "健康检查完成",
  "data": {
    "status": "healthy",
    "qa_storage_status": "ready",
    "embedding_status": "ready",
    "total_qa_pairs": 15,
    "avg_response_time": 0.25,
    "error_rate": 0.0
  }
}
```

### 2. 问答对管理

#### 2.1 创建问答对

**端点**: `POST /api/v1/qa/pairs`

**请求体**:
```json
{
  "question": "问题文本",
  "answer": "答案文本",
  "category": "分类",
  "confidence": 0.95,
  "keywords": ["关键词1", "关键词2"],
  "source": "来源"
}
```

#### 2.2 批量创建问答对

**端点**: `POST /api/v1/qa/pairs/batch`

**请求体**:
```json
{
  "qa_pairs": [
    {
      "question": "问题1",
      "answer": "答案1",
      "category": "分类1"
    },
    {
      "question": "问题2",
      "answer": "答案2",
      "category": "分类2"
    }
  ]
}
```

#### 2.3 获取问答对列表

**端点**: `GET /api/v1/qa/pairs`

**查询参数**:
- `category`: 分类过滤
- `min_confidence`: 最小置信度
- `page`: 页码
- `page_size`: 每页数量
- `keyword`: 关键词搜索

### 3. 问答查询

#### 3.1 单个查询

**端点**: `POST /api/v1/qa/query`

**请求体**:
```json
{
  "question": "查询问题",
  "top_k": 3,
  "min_similarity": 0.7,
  "category": "分类过滤"
}
```

**响应示例**:
```json
{
  "success": true,
  "found": true,
  "answer": "匹配的答案",
  "question": "匹配的问题",
  "similarity": 0.92,
  "confidence": 0.95,
  "category": "ai",
  "qa_id": "qa_123",
  "response_time": 0.15,
  "all_results": [
    {
      "qa_pair": {
        "id": "qa_123",
        "question": "匹配的问题",
        "answer": "匹配的答案",
        "category": "ai",
        "confidence": 0.95
      },
      "similarity": 0.92,
      "rank": 1
    }
  ]
}
```

#### 3.2 批量查询

**端点**: `POST /api/v1/qa/query/batch`

**请求体**:
```json
{
  "questions": [
    "问题1",
    "问题2",
    "问题3"
  ],
  "top_k": 2,
  "parallel": true,
  "timeout": 300
}
```

### 4. 数据管理

#### 4.1 导入数据

**端点**: `POST /api/v1/qa/import`

**请求**: multipart/form-data
- `file`: 上传的文件
- `file_type`: 文件类型 (json/csv/xlsx)
- `overwrite_existing`: 是否覆盖已存在的问答对
- `default_category`: 默认分类
- `default_source`: 默认来源

#### 4.2 导出数据

**端点**: `GET /api/v1/qa/export`

**查询参数**:
- `format`: 导出格式 (json/csv/xlsx)
- `category`: 分类过滤
- `min_confidence`: 最小置信度
- `include_vectors`: 是否包含向量数据

#### 4.3 数据备份

**端点**: `POST /api/v1/qa/backup`

**请求体**:
```json
{
  "include_vectors": true,
  "compress": true,
  "backup_name": "backup_20240101"
}
```

### 5. 统计信息

**端点**: `GET /api/v1/qa/statistics`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_pairs": 150,
    "categories": {
      "ai": 50,
      "ml": 30,
      "system": 20
    },
    "average_confidence": 0.89,
    "similarity_threshold": 0.85,
    "vector_index_size": 150,
    "embedding_dim": 1024,
    "query_stats": {
      "total_queries": 1000,
      "successful_queries": 950,
      "avg_response_time": 0.25
    }
  }
}
```

## 数据格式规范

### JSON 格式

```json
{
  "metadata": {
    "export_time": 1704067200,
    "total_pairs": 15,
    "version": "1.0"
  },
  "qa_pairs": [
    {
      "id": "qa_001",
      "question": "什么是GuiXiaoXiRag？",
      "answer": "GuiXiaoXiRag是一个基于FastAPI的智能知识问答系统...",
      "category": "system",
      "confidence": 1.0,
      "keywords": ["GuiXiaoXiRag", "系统介绍"],
      "source": "system_default",
      "created_at": 1704067200,
      "updated_at": 1704067200
    }
  ]
}
```

### CSV 格式

```csv
question,answer,category,confidence,keywords,source
"什么是GuiXiaoXiRag？","GuiXiaoXiRag是一个基于FastAPI的智能知识问答系统...","system",1.0,"GuiXiaoXiRag;系统介绍","system_default"
```

## 使用示例

### Python 客户端示例

```python
import requests
import json

class QAClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.api_base = f"{base_url}/api/v1/qa"
        self.session = requests.Session()
    
    def create_qa_pair(self, question, answer, **kwargs):
        """创建问答对"""
        data = {
            "question": question,
            "answer": answer,
            **kwargs
        }
        response = self.session.post(f"{self.api_base}/pairs", json=data)
        return response.json()
    
    def query(self, question, top_k=1):
        """查询问答"""
        data = {
            "question": question,
            "top_k": top_k
        }
        response = self.session.post(f"{self.api_base}/query", json=data)
        return response.json()
    
    def get_statistics(self):
        """获取统计信息"""
        response = self.session.get(f"{self.api_base}/statistics")
        return response.json()

# 使用示例
client = QAClient()

# 创建问答对
result = client.create_qa_pair(
    question="什么是机器学习？",
    answer="机器学习是人工智能的一个子集...",
    category="ml",
    confidence=0.9
)
print(f"创建结果: {result}")

# 查询问答
result = client.query("ML是什么？")
if result.get("found"):
    print(f"答案: {result['answer']}")
    print(f"相似度: {result['similarity']}")
else:
    print("未找到匹配的答案")

# 获取统计信息
stats = client.get_statistics()
print(f"总问答对数: {stats['data']['total_pairs']}")
```

### JavaScript 客户端示例

```javascript
class QAClient {
    constructor(baseUrl = "http://localhost:8002") {
        this.apiBase = `${baseUrl}/api/v1/qa`;
    }
    
    async createQAPair(question, answer, options = {}) {
        const data = {
            question,
            answer,
            ...options
        };
        
        const response = await fetch(`${this.apiBase}/pairs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
    
    async query(question, topK = 1) {
        const data = {
            question,
            top_k: topK
        };
        
        const response = await fetch(`${this.apiBase}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        return await response.json();
    }
}

// 使用示例
const client = new QAClient();

// 查询问答
client.query("什么是AI？").then(result => {
    if (result.found) {
        console.log(`答案: ${result.answer}`);
        console.log(`相似度: ${result.similarity}`);
    } else {
        console.log("未找到匹配的答案");
    }
});
```

## 配置说明

### 环境变量配置

在 `.env` 文件中添加以下配置：

```bash
# 问答系统配置
QA_SIMILARITY_THRESHOLD=0.85    # 相似度阈值
QA_MAX_RESULTS=10              # 最大返回结果数
QA_STORAGE_DIR=./Q&A_Base      # 存储目录
QA_AUTO_SAVE_INTERVAL=300      # 自动保存间隔(秒)

# Embedding配置
OPENAI_EMBEDDING_API_BASE=http://localhost:8200/v1
OPENAI_EMBEDDING_API_KEY=your_key_here
OPENAI_EMBEDDING_MODEL=embedding_model
```

### 性能调优

#### 相似度阈值设置
- **高精度场景**: 0.9+ (更严格的匹配)
- **平衡场景**: 0.85 (推荐默认值)
- **高召回场景**: 0.7-0.8 (更宽松的匹配)

#### 批量处理优化
- 批量创建: 每批不超过100个问答对
- 批量查询: 每批不超过50个问题
- 并行处理: 启用parallel参数提高性能

## 最佳实践

### 1. 问答对设计
- **问题表述**: 使用清晰、自然的语言
- **答案完整性**: 提供完整、准确的答案
- **关键词标注**: 添加相关关键词提高匹配率
- **分类管理**: 合理使用分类组织问答对

### 2. 性能优化
- **定期维护**: 定期清理低质量问答对
- **阈值调整**: 根据实际效果调整相似度阈值
- **批量操作**: 使用批量接口提高效率
- **缓存利用**: 利用系统缓存机制

### 3. 数据管理
- **定期备份**: 定期备份问答数据
- **版本控制**: 维护问答对的版本历史
- **质量监控**: 监控查询效果和用户反馈
- **持续优化**: 根据使用情况持续优化

## 故障排除

### 常见问题

#### 1. 查询无结果
- 检查相似度阈值设置
- 确认问答对是否存在
- 验证embedding服务状态
- 检查问题表述是否准确

#### 2. 响应时间慢
- 检查embedding服务性能
- 优化问答对数量
- 调整批量处理参数
- 检查系统资源使用

#### 3. 导入失败
- 验证文件格式是否正确
- 检查文件大小限制
- 确认数据格式规范
- 查看错误日志信息

### 调试工具

```bash
# 检查系统状态
curl http://localhost:8002/api/v1/qa/health

# 获取统计信息
curl http://localhost:8002/api/v1/qa/statistics

# 运行测试脚本
python tests/test_qa_system.py
```

## 扩展开发

### 自定义相似度算法

```python
class CustomSimilarityCalculator:
    def calculate_similarity(self, query_vector, qa_vector):
        # 实现自定义相似度计算
        pass
```

### 添加新的数据源

```python
class CustomDataImporter:
    def import_from_source(self, source_config):
        # 实现自定义数据导入
        pass
```

---

*本指南提供了问答系统的完整使用说明，帮助用户充分利用系统功能。*
