curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "计算机学院院长是谁",
    "knowledge_base": "cs_college",
    "language": "中文",
    "mode": "hybrid",
    "top_k": 50
  }'

curl -X POST "http://localhost:8002/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "陈艳平是谁？",
    "knowledge_base": "cs_college",
    "language": "中文",
    "mode": "hybrid",
    "top_k": 50
  }'


  - `local`: 本地模式 - 专注于上下文相关信息
  - `global`: 全局模式 - 利用全局知识
  - `hybrid`: 混合模式 - 结合本地和全局检索方法（推荐）
  - `naive`: 朴素模式 - 执行基本搜索
  - `mix`: 混合模式 - 整合知识图谱和向量检索
  - `bypass`: 绕过模式 - 直接返回结果