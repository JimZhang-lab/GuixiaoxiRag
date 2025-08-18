# 问答库文件导入示例

本目录包含了从不同格式文件导入问答库的示例和模板文件。

## 支持的文件格式

### 1. Excel文件 (.xlsx)
- **模板文件**: `qa_template.xlsx`
- **示例文件**: `qa_example.xlsx`
- **用途**: 适合批量编辑和管理问答对

### 2. JSON文件 (.json)
- **模板文件**: `qa_template.json`
- **示例文件**: `qa_example.json`
- **用途**: 适合程序化处理和API集成

### 3. CSV文件 (.csv)
- **模板文件**: `qa_template.csv`
- **示例文件**: `qa_example.csv`
- **用途**: 适合简单的数据导入和Excel兼容

## 字段说明

| 字段名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| question | string | ✅ | 问题内容 | "什么是人工智能？" |
| answer | string | ✅ | 答案内容 | "人工智能是..." |
| category | string | ✅ | 分类名称 | "technology" |
| confidence | float | ❌ | 置信度(0.0-1.0) | 0.9 |
| keywords | array/string | ❌ | 关键词列表 | ["AI", "机器学习"] |
| source | string | ❌ | 来源信息 | "官方文档" |

## 使用方法

### 1. 准备数据文件
根据模板文件格式准备您的问答数据。

### 2. 调用导入API
```bash
# Excel文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@qa_example.xlsx" \
  -F "category=technology" \
  -F "skip_duplicate_check=false"

# JSON文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@qa_example.json" \
  -F "category=technology"

# CSV文件导入
curl -X POST "http://localhost:8002/api/v1/qa/import" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@qa_example.csv" \
  -F "category=technology"
```

### 3. 导入参数说明
- `file`: 要导入的文件
- `category`: 默认分类（如果文件中没有指定）
- `skip_duplicate_check`: 是否跳过重复检查（默认false）
- `duplicate_threshold`: 重复检查阈值（默认0.98）

## 注意事项

1. **文件大小限制**: 单个文件不超过10MB
2. **数据量限制**: 单次导入不超过1000条问答对
3. **编码格式**: 
   - CSV文件请使用UTF-8编码
   - Excel文件支持中文内容
4. **重复检查**: 
   - 默认启用，相似度>0.98的问题会被标记为重复
   - 可通过参数控制是否跳过
5. **错误处理**: 
   - 导入失败的记录会在响应中详细说明
   - 部分成功的导入会返回成功和失败的统计

## 批量导入最佳实践

1. **数据准备**:
   - 确保问题表述清晰、准确
   - 答案内容完整、有用
   - 分类命名规范统一

2. **性能优化**:
   - 单次导入建议不超过500条
   - 大量数据可分批导入
   - 避免在高峰期进行大批量导入

3. **质量控制**:
   - 导入前检查数据格式
   - 启用重复检查避免冗余
   - 导入后验证关键问答对

## 错误码说明

- `400`: 文件格式错误或数据验证失败
- `413`: 文件过大
- `422`: 数据格式不符合要求
- `500`: 服务器内部错误

## 示例响应

```json
{
  "success": true,
  "message": "导入完成",
  "total_processed": 10,
  "successful_imports": 8,
  "failed_imports": 2,
  "duplicate_skipped": 1,
  "failed_records": [
    {
      "row": 3,
      "error": "问题内容不能为空",
      "data": {"question": "", "answer": "..."}
    }
  ],
  "import_summary": {
    "categories": {"technology": 5, "general": 3},
    "avg_confidence": 0.85,
    "processing_time": 2.3
  }
}
```
