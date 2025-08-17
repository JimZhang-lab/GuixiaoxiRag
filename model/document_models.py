"""
文档相关数据模型定义
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_models import SupportedLanguage, TimestampModel, MetadataModel


class DocumentInfo(BaseModel):
    """文档信息模型"""
    doc_id: str = Field(..., description="文档ID")
    title: Optional[str] = Field(None, description="文档标题")
    content: str = Field(..., description="文档内容")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_type: Optional[str] = Field(None, description="文件类型")
    file_size: Optional[int] = Field(None, description="文件大小")
    language: SupportedLanguage = Field(default="中文", description="文档语言")
    knowledge_base: str = Field(..., description="所属知识库")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")
    tags: List[str] = Field(default_factory=list, description="文档标签")
    status: str = Field(default="active", description="文档状态")


class DocumentChunk(BaseModel):
    """文档块模型"""
    chunk_id: str = Field(..., description="块ID")
    doc_id: str = Field(..., description="所属文档ID")
    content: str = Field(..., description="块内容")
    chunk_index: int = Field(..., description="块索引")
    start_position: int = Field(..., description="开始位置")
    end_position: int = Field(..., description="结束位置")
    token_count: int = Field(..., description="token数量")
    embedding: Optional[List[float]] = Field(None, description="向量嵌入")
    metadata: Optional[Dict[str, Any]] = Field(None, description="块元数据")


class DocumentProcessingStatus(BaseModel):
    """文档处理状态模型"""
    track_id: str = Field(..., description="跟踪ID")
    doc_id: Optional[str] = Field(None, description="文档ID")
    status: str = Field(..., description="处理状态")
    progress: float = Field(default=0.0, description="处理进度(0-1)")
    current_step: str = Field(..., description="当前步骤")
    total_steps: int = Field(..., description="总步骤数")
    completed_steps: int = Field(default=0, description="已完成步骤数")
    start_time: str = Field(..., description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    result: Optional[Dict[str, Any]] = Field(None, description="处理结果")


class DocumentStatistics(BaseModel):
    """文档统计模型"""
    total_documents: int = Field(..., description="文档总数")
    total_chunks: int = Field(..., description="块总数")
    total_tokens: int = Field(..., description="token总数")
    average_doc_length: float = Field(..., description="平均文档长度")
    language_distribution: Dict[str, int] = Field(..., description="语言分布")
    file_type_distribution: Dict[str, int] = Field(..., description="文件类型分布")
    size_distribution: Dict[str, int] = Field(..., description="大小分布")
    processing_status_distribution: Dict[str, int] = Field(..., description="处理状态分布")


class DocumentSearchResult(BaseModel):
    """文档搜索结果模型"""
    doc_id: str = Field(..., description="文档ID")
    title: Optional[str] = Field(None, description="文档标题")
    content_snippet: str = Field(..., description="内容片段")
    relevance_score: float = Field(..., description="相关性分数")
    file_path: Optional[str] = Field(None, description="文件路径")
    knowledge_base: str = Field(..., description="所属知识库")
    matched_chunks: List[str] = Field(default_factory=list, description="匹配的块ID")
    highlights: List[str] = Field(default_factory=list, description="高亮片段")


class DocumentVersion(BaseModel):
    """文档版本模型"""
    version_id: str = Field(..., description="版本ID")
    doc_id: str = Field(..., description="文档ID")
    version_number: int = Field(..., description="版本号")
    content: str = Field(..., description="版本内容")
    changes: Optional[str] = Field(None, description="变更说明")
    created_at: str = Field(..., description="创建时间")
    created_by: Optional[str] = Field(None, description="创建者")
    is_current: bool = Field(default=False, description="是否为当前版本")


class DocumentTemplate(BaseModel):
    """文档模板模型"""
    template_id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    content_template: str = Field(..., description="内容模板")
    metadata_template: Optional[Dict[str, Any]] = Field(None, description="元数据模板")
    language: SupportedLanguage = Field(default="中文", description="模板语言")
    category: Optional[str] = Field(None, description="模板分类")
    tags: List[str] = Field(default_factory=list, description="模板标签")
    is_active: bool = Field(default=True, description="是否激活")


class DocumentAnnotation(BaseModel):
    """文档标注模型"""
    annotation_id: str = Field(..., description="标注ID")
    doc_id: str = Field(..., description="文档ID")
    start_position: int = Field(..., description="开始位置")
    end_position: int = Field(..., description="结束位置")
    annotation_type: str = Field(..., description="标注类型")
    content: str = Field(..., description="标注内容")
    label: Optional[str] = Field(None, description="标注标签")
    confidence: Optional[float] = Field(None, description="置信度")
    created_at: str = Field(..., description="创建时间")
    created_by: Optional[str] = Field(None, description="标注者")


class DocumentRelation(BaseModel):
    """文档关系模型"""
    relation_id: str = Field(..., description="关系ID")
    source_doc_id: str = Field(..., description="源文档ID")
    target_doc_id: str = Field(..., description="目标文档ID")
    relation_type: str = Field(..., description="关系类型")
    strength: float = Field(default=1.0, description="关系强度")
    description: Optional[str] = Field(None, description="关系描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="关系元数据")
    created_at: str = Field(..., description="创建时间")


class DocumentCollection(BaseModel):
    """文档集合模型"""
    collection_id: str = Field(..., description="集合ID")
    name: str = Field(..., description="集合名称")
    description: Optional[str] = Field(None, description="集合描述")
    document_ids: List[str] = Field(..., description="文档ID列表")
    knowledge_base: str = Field(..., description="所属知识库")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="集合标签")
    metadata: Optional[Dict[str, Any]] = Field(None, description="集合元数据")


class DocumentProcessingConfig(BaseModel):
    """文档处理配置模型"""
    chunk_size: int = Field(default=1024, description="块大小")
    chunk_overlap: int = Field(default=50, description="块重叠")
    language: SupportedLanguage = Field(default="中文", description="处理语言")
    extract_metadata: bool = Field(default=True, description="是否提取元数据")
    enable_ocr: bool = Field(default=False, description="是否启用OCR")
    enable_entity_extraction: bool = Field(default=True, description="是否启用实体提取")
    enable_keyword_extraction: bool = Field(default=True, description="是否启用关键词提取")
    custom_processors: List[str] = Field(default_factory=list, description="自定义处理器")
    preprocessing_rules: Optional[Dict[str, Any]] = Field(None, description="预处理规则")


class DocumentQualityMetrics(BaseModel):
    """文档质量指标模型"""
    doc_id: str = Field(..., description="文档ID")
    readability_score: Optional[float] = Field(None, description="可读性分数")
    completeness_score: Optional[float] = Field(None, description="完整性分数")
    accuracy_score: Optional[float] = Field(None, description="准确性分数")
    consistency_score: Optional[float] = Field(None, description="一致性分数")
    overall_quality: Optional[float] = Field(None, description="整体质量分数")
    quality_issues: List[str] = Field(default_factory=list, description="质量问题")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议")
    last_evaluated: str = Field(..., description="最后评估时间")


class DocumentBackup(BaseModel):
    """文档备份模型"""
    backup_id: str = Field(..., description="备份ID")
    doc_id: str = Field(..., description="文档ID")
    backup_type: str = Field(..., description="备份类型")
    backup_path: str = Field(..., description="备份路径")
    backup_size: int = Field(..., description="备份大小")
    created_at: str = Field(..., description="备份时间")
    retention_period: Optional[int] = Field(None, description="保留期限（天）")
    checksum: Optional[str] = Field(None, description="校验和")
    compression: Optional[str] = Field(None, description="压缩方式")


# 导出所有文档相关模型
__all__ = [
    "DocumentInfo",
    "DocumentChunk",
    "DocumentProcessingStatus",
    "DocumentStatistics",
    "DocumentSearchResult",
    "DocumentVersion",
    "DocumentTemplate",
    "DocumentAnnotation",
    "DocumentRelation",
    "DocumentCollection",
    "DocumentProcessingConfig",
    "DocumentQualityMetrics",
    "DocumentBackup"
]
