# GuiXiaoXiRag FastAPI 知识库和语言功能指南

## 🌍 多语言支持概述

GuiXiaoXiRag FastAPI 提供了强大的多语言支持功能，能够处理不同语言的文档，并根据用户需求以指定语言回答问题。系统支持智能语言识别、跨语言检索和多语言知识库管理。

## 🗄️ 知识库管理

### 知识库概念

知识库是 GuiXiaoXiRag 中用于存储和组织文档的独立空间。每个知识库包含：
- **文档数据**: 原始文档和处理后的文本块
- **向量索引**: 文档的向量化表示
- **知识图谱**: 实体关系和语义网络
- **元数据**: 文档属性和统计信息

### 知识库结构

```
knowledgeBase/
├── default/                    # 默认知识库
│   ├── graph_chunk_entity_relation.graphml  # 知识图谱文件
│   ├── kv_store_full_docs.json             # 完整文档存储
│   ├── kv_store_text_chunks.json           # 文本块存储
│   └── vector_cache/                        # 向量缓存目录
├── knowledge_base_1/           # 自定义知识库1
├── knowledge_base_2/           # 自定义知识库2
└── ...
```

### 知识库操作

#### 1. 查看知识库列表
```bash
# API调用
curl http://localhost:8002/knowledge-bases

# CLI工具
python scripts/guixiaoxirag_cli.py kb list
```

#### 2. 创建新知识库
```bash
# API调用
curl -X POST "http://localhost:8002/knowledge-bases" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_knowledge_base",
    "description": "我的专用知识库",
    "language": "中文"
  }'

# CLI工具
python scripts/guixiaoxirag_cli.py kb create my_knowledge_base --description "我的专用知识库"
```

#### 3. 切换知识库
```bash
# API调用
curl -X POST "http://localhost:8002/knowledge-bases/switch" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_knowledge_base",
    "language": "中文"
  }'

# CLI工具
python scripts/guixiaoxirag_cli.py kb switch my_knowledge_base
```

#### 4. 删除知识库
```bash
# API调用
curl -X DELETE "http://localhost:8002/knowledge-bases/my_knowledge_base"

# CLI工具
python scripts/guixiaoxirag_cli.py kb delete my_knowledge_base
```

#### 5. 导出知识库
```bash
# API调用
curl "http://localhost:8002/knowledge-bases/my_knowledge_base/export" -o backup.json

# CLI工具
python scripts/guixiaoxirag_cli.py kb export my_knowledge_base --output backup.json
```

### 知识库最佳实践

#### 按主题分类
```bash
# 创建不同主题的知识库
python scripts/guixiaoxirag_cli.py kb create tech_docs --description "技术文档"
python scripts/guixiaoxirag_cli.py kb create business_docs --description "业务文档"
python scripts/guixiaoxirag_cli.py kb create legal_docs --description "法律文档"
```

#### 按语言分类
```bash
# 创建不同语言的知识库
python scripts/guixiaoxirag_cli.py kb create chinese_kb --description "中文知识库"
python scripts/guixiaoxirag_cli.py kb create english_kb --description "English Knowledge Base"
```

#### 按项目分类
```bash
# 为不同项目创建独立知识库
python scripts/guixiaoxirag_cli.py kb create project_a --description "项目A文档"
python scripts/guixiaoxirag_cli.py kb create project_b --description "项目B文档"
```

## 🌍 语言功能

### 支持的语言

GuiXiaoXiRag 支持多种语言的文档处理和查询：

#### 主要支持语言
- **中文**: 中文、Chinese、zh、zh-CN、zh-TW
- **英文**: 英文、English、en、en-US、en-GB
- **日文**: 日文、Japanese、ja、ja-JP
- **韩文**: 韩文、Korean、ko、ko-KR
- **法文**: 法文、French、fr、fr-FR
- **德文**: 德文、German、de、de-DE
- **西班牙文**: 西班牙文、Spanish、es、es-ES
- **俄文**: 俄文、Russian、ru、ru-RU

### 语言设置

#### 1. 查看支持的语言
```bash
# API调用
curl http://localhost:8002/languages

# CLI工具
python scripts/guixiaoxirag_cli.py lang list
```

#### 2. 设置默认语言
```bash
# API调用
curl -X POST "http://localhost:8002/languages/set" \
  -H "Content-Type: application/json" \
  -d '{"language": "中文"}'

# CLI工具
python scripts/guixiaoxirag_cli.py lang set 中文
```

#### 3. 查询时指定语言
```bash
# API调用
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "mode": "hybrid",
    "language": "English"
  }'

# CLI工具
python scripts/guixiaoxirag_cli.py query "What is artificial intelligence?" --language English
```

### 语言识别和处理

#### 自动语言识别
系统能够自动识别输入文档和查询的语言：

```python
# 文档插入时自动识别语言
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工智能是计算机科学的一个分支",
    "auto_detect_language": true
  }'
```

#### 跨语言检索
支持用一种语言查询，返回另一种语言的答案：

```python
# 用中文查询，返回英文答案
curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "mode": "hybrid",
    "response_language": "English"
  }'
```

### 多语言文档处理

#### 混合语言文档
系统可以处理包含多种语言的文档：

```bash
# 插入混合语言文档
curl -X POST "http://localhost:8002/insert/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "人工智能 (Artificial Intelligence, AI) 是计算机科学的一个分支。AI systems can perform tasks that typically require human intelligence.",
    "mixed_language": true
  }'
```

#### 语言特定处理
针对不同语言采用优化的处理策略：

- **中文**: 支持分词、实体识别、语义分析
- **英文**: 支持词干提取、命名实体识别、语法分析
- **日文**: 支持假名处理、汉字识别、语法分析
- **其他语言**: 基于Unicode的通用处理

## 🔧 高级功能

### 语言模型配置

#### 多语言模型支持
```env
# 配置不同语言的模型
OPENAI_CHAT_MODEL_ZH=qwen14b-chat-zh
OPENAI_CHAT_MODEL_EN=qwen14b-chat-en
OPENAI_EMBEDDING_MODEL_ZH=embedding_qwen_zh
OPENAI_EMBEDDING_MODEL_EN=embedding_qwen_en
```

#### 语言特定配置
```bash
# 为不同语言设置不同的处理参数
curl -X POST "http://localhost:8002/languages/config" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "中文",
    "chunk_size": 500,
    "overlap": 50,
    "embedding_model": "embedding_qwen_zh"
  }'
```

### 知识图谱多语言支持

#### 多语言实体识别
```bash
# 获取多语言知识图谱
curl -X POST "http://localhost:8002/knowledge-graph" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能",
    "languages": ["中文", "English"],
    "max_depth": 2
  }'
```

#### 跨语言关系映射
系统能够识别和映射不同语言中的相同概念：

```json
{
  "entities": [
    {
      "name": "人工智能",
      "language": "中文",
      "aliases": ["AI", "Artificial Intelligence"],
      "cross_language_refs": ["Artificial Intelligence@en"]
    }
  ]
}
```

## 🎯 使用场景

### 多语言企业知识库

#### 场景描述
跨国企业需要管理多种语言的文档，员工可能用不同语言查询。

#### 解决方案
```bash
# 1. 创建语言特定的知识库
python scripts/guixiaoxirag_cli.py kb create chinese_docs --description "中文文档库"
python scripts/guixiaoxirag_cli.py kb create english_docs --description "English Documents"

# 2. 插入不同语言的文档
python scripts/guixiaoxirag_cli.py insert "公司政策文档内容" --kb chinese_docs
python scripts/guixiaoxirag_cli.py insert "Company policy content" --kb english_docs

# 3. 跨语言查询
python scripts/guixiaoxirag_cli.py query "公司休假政策" --language English --kb chinese_docs
```

### 学术研究文献管理

#### 场景描述
研究人员需要管理多种语言的学术文献，进行跨语言的文献检索。

#### 解决方案
```bash
# 1. 创建学科特定的知识库
python scripts/guixiaoxirag_cli.py kb create ai_research --description "AI研究文献"

# 2. 插入多语言文献
python scripts/guixiaoxirag_cli.py insert-file paper_zh.pdf --kb ai_research
python scripts/guixiaoxirag_cli.py insert-file paper_en.pdf --kb ai_research

# 3. 多语言检索
python scripts/guixiaoxirag_cli.py query "深度学习最新进展" --language English --kb ai_research
```

### 客户服务系统

#### 场景描述
国际化的客户服务需要支持多种语言的问答。

#### 解决方案
```bash
# 1. 创建客服知识库
python scripts/guixiaoxirag_cli.py kb create customer_service --description "客服知识库"

# 2. 插入多语言FAQ
python scripts/guixiaoxirag_cli.py insert "常见问题解答..." --kb customer_service
python scripts/guixiaoxirag_cli.py insert "Frequently Asked Questions..." --kb customer_service

# 3. 智能客服查询
python scripts/guixiaoxirag_cli.py query "如何退款？" --language English --kb customer_service
```

## 🔧 配置和优化

### 语言处理配置

#### 分词器配置
```env
# 中文分词器
CHINESE_TOKENIZER=jieba
CHINESE_DICT_PATH=./dicts/chinese.dict

# 英文分词器
ENGLISH_TOKENIZER=nltk
ENGLISH_STOPWORDS=./dicts/english_stopwords.txt
```

#### 语言模型配置
```env
# 语言检测模型
LANGUAGE_DETECTION_MODEL=langdetect
LANGUAGE_DETECTION_THRESHOLD=0.8

# 翻译模型（可选）
TRANSLATION_MODEL=google_translate
TRANSLATION_API_KEY=your_api_key
```

### 性能优化

#### 语言特定缓存
```bash
# 启用语言特定的缓存
curl -X POST "http://localhost:8002/performance/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "enable_language_cache": true,
    "cache_by_language": true
  }'
```

#### 并行处理
```bash
# 启用多语言并行处理
curl -X POST "http://localhost:8002/performance/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "parallel_language_processing": true,
    "max_language_workers": 4
  }'
```

## 🔍 监控和统计

### 语言使用统计
```bash
# 获取语言使用统计
curl http://localhost:8002/metrics/languages

# 获取知识库统计
curl http://localhost:8002/knowledge-bases/stats
```

### 多语言性能监控
```bash
# 获取各语言的查询性能
curl http://localhost:8002/metrics/performance?group_by=language

# 获取跨语言查询统计
curl http://localhost:8002/metrics/cross-language-queries
```

## 🔗 相关文档

- [快速开始指南](../getting-started/QUICK_START.md)
- [API参考文档](../api/API_REFERENCE.md)
- [配置指南](../getting-started/CONFIGURATION_GUIDE.md)
- [Streamlit界面指南](STREAMLIT_INTERFACE_GUIDE.md)
- [项目架构](../project/PROJECT_ARCHITECTURE.md)

## 💡 最佳实践

1. **知识库规划**: 根据业务需求合理规划知识库结构
2. **语言设置**: 为不同用户群体设置合适的默认语言
3. **文档组织**: 按语言或主题组织文档，便于管理
4. **性能优化**: 根据使用情况调整语言处理参数
5. **监控维护**: 定期监控多语言功能的使用情况和性能
