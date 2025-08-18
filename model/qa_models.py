"""
问答系统数据模型
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import time


class QAPairBase(BaseModel):
    """问答对基础模型"""
    question: str = Field(..., description="问题文本", min_length=1, max_length=2000)
    answer: str = Field(..., description="答案文本", min_length=1, max_length=10000)
    category: str = Field(default="general", description="分类", max_length=100)
    confidence: float = Field(default=1.0, description="置信度", ge=0.0, le=1.0)
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    source: str = Field(default="manual", description="来源", max_length=200)

    @validator('question', 'answer')
    def validate_text_not_empty(cls, v):
        if not v.strip():
            raise ValueError('文本内容不能为空')
        return v.strip()

    @validator('keywords')
    def validate_keywords(cls, v):
        if v is None:
            return []
        return [keyword.strip() for keyword in v if keyword.strip()]


class QAPairCreate(QAPairBase):
    """创建问答对请求模型"""
    skip_duplicate_check: bool = Field(default=False, description="是否跳过重复检查")
    duplicate_threshold: float = Field(default=0.98, description="重复检查阈值", ge=0.0, le=1.0)


class QAPairUpdate(BaseModel):
    """更新问答对请求模型"""
    question: Optional[str] = Field(None, description="问题文本", min_length=1, max_length=2000)
    answer: Optional[str] = Field(None, description="答案文本", min_length=1, max_length=10000)
    category: Optional[str] = Field(None, description="分类", max_length=100)
    confidence: Optional[float] = Field(None, description="置信度", ge=0.0, le=1.0)
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    source: Optional[str] = Field(None, description="来源", max_length=200)

    @validator('question', 'answer')
    def validate_text_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('文本内容不能为空')
        return v.strip() if v else v


class QAPairResponse(QAPairBase):
    """问答对响应模型"""
    id: str = Field(..., description="问答对ID")
    created_at: float = Field(..., description="创建时间戳")
    updated_at: float = Field(..., description="更新时间戳")
    
    class Config:
        from_attributes = True


class QAPairBatchCreate(BaseModel):
    """批量创建问答对请求模型"""
    qa_pairs: List[QAPairCreate] = Field(..., description="问答对列表", min_items=1, max_items=100)
    
    @validator('qa_pairs')
    def validate_qa_pairs_not_empty(cls, v):
        if not v:
            raise ValueError('问答对列表不能为空')
        return v


class QAQueryRequest(BaseModel):
    """问答查询请求模型"""
    question: str = Field(..., description="查询问题", min_length=1, max_length=2000)
    top_k: int = Field(default=1, description="返回结果数量", ge=1, le=20)
    min_similarity: Optional[float] = Field(None, description="最小相似度阈值", ge=0.0, le=1.0)
    category: Optional[str] = Field(None, description="分类过滤", max_length=100)
    
    @validator('question')
    def validate_question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('查询问题不能为空')
        return v.strip()


class QASearchResult(BaseModel):
    """问答搜索结果模型"""
    qa_pair: QAPairResponse = Field(..., description="问答对")
    similarity: float = Field(..., description="相似度分数", ge=0.0, le=1.0)
    rank: int = Field(..., description="排名", ge=1)


class QAQueryResponse(BaseModel):
    """问答查询响应模型"""
    success: bool = Field(..., description="查询是否成功")
    found: bool = Field(default=False, description="是否找到匹配结果")
    answer: Optional[str] = Field(None, description="最佳答案")
    question: Optional[str] = Field(None, description="匹配的问题")
    similarity: Optional[float] = Field(None, description="相似度分数")
    confidence: Optional[float] = Field(None, description="置信度")
    category: Optional[str] = Field(None, description="分类")
    qa_id: Optional[str] = Field(None, description="问答对ID")
    response_time: float = Field(..., description="响应时间(秒)")
    all_results: List[QASearchResult] = Field(default_factory=list, description="所有搜索结果")
    message: Optional[str] = Field(None, description="消息")
    error: Optional[str] = Field(None, description="错误信息")


class QAListRequest(BaseModel):
    """问答对列表请求模型"""
    category: Optional[str] = Field(None, description="分类过滤", max_length=100)
    min_confidence: Optional[float] = Field(None, description="最小置信度", ge=0.0, le=1.0)
    page: int = Field(default=1, description="页码", ge=1)
    page_size: int = Field(default=20, description="每页数量", ge=1, le=100)
    keyword: Optional[str] = Field(None, description="关键词搜索", max_length=200)


class QAListResponse(BaseModel):
    """问答对列表响应模型"""
    qa_pairs: List[QAPairResponse] = Field(..., description="问答对列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


class QAImportRequest(BaseModel):
    """问答对导入请求模型"""
    file_type: str = Field(..., description="文件类型", pattern="^(json|csv|xlsx)$")
    overwrite_existing: bool = Field(default=False, description="是否覆盖已存在的问答对")
    default_category: str = Field(default="imported", description="默认分类", max_length=100)
    default_source: str = Field(default="file_import", description="默认来源", max_length=200)


class QAImportResponse(BaseModel):
    """问答对导入响应模型"""
    success: bool = Field(..., description="导入是否成功")
    imported_count: int = Field(..., description="成功导入数量")
    skipped_count: int = Field(..., description="跳过数量")
    error_count: int = Field(..., description="错误数量")
    total_count: int = Field(..., description="总数量")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    message: str = Field(..., description="导入结果消息")


class QAExportRequest(BaseModel):
    """问答对导出请求模型"""
    format: str = Field(..., description="导出格式", pattern="^(json|csv|xlsx)$")
    category: Optional[str] = Field(None, description="分类过滤", max_length=100)
    min_confidence: Optional[float] = Field(None, description="最小置信度", ge=0.0, le=1.0)
    include_vectors: bool = Field(default=False, description="是否包含向量数据")


class QAStatistics(BaseModel):
    """问答系统统计信息模型"""
    total_pairs: int = Field(..., description="总问答对数量")
    categories: Dict[str, int] = Field(..., description="分类统计")
    average_confidence: float = Field(..., description="平均置信度")
    similarity_threshold: float = Field(..., description="相似度阈值")
    vector_index_size: int = Field(..., description="向量索引大小")
    embedding_dim: int = Field(..., description="向量维度")
    query_stats: Dict[str, Any] = Field(..., description="查询统计")


class QAHealthCheck(BaseModel):
    """问答系统健康检查模型"""
    status: str = Field(..., description="状态")
    qa_storage_status: str = Field(..., description="问答存储状态")
    embedding_status: str = Field(..., description="向量化服务状态")
    total_qa_pairs: int = Field(..., description="总问答对数量")
    last_query_time: Optional[float] = Field(None, description="最后查询时间")
    avg_response_time: float = Field(..., description="平均响应时间")
    error_rate: float = Field(..., description="错误率")


class QAConfigUpdate(BaseModel):
    """问答系统配置更新模型"""
    similarity_threshold: Optional[float] = Field(None, description="相似度阈值", ge=0.0, le=1.0)
    max_results: Optional[int] = Field(None, description="最大返回结果数", ge=1, le=100)
    enable_auto_save: Optional[bool] = Field(None, description="是否启用自动保存")
    auto_save_interval: Optional[int] = Field(None, description="自动保存间隔(秒)", ge=60, le=3600)


class QABatchQueryRequest(BaseModel):
    """批量问答查询请求模型"""
    questions: List[str] = Field(..., description="问题列表", min_items=1, max_items=50)
    top_k: int = Field(default=1, description="每个问题返回结果数量", ge=1, le=10)
    min_similarity: Optional[float] = Field(None, description="最小相似度阈值", ge=0.0, le=1.0)
    parallel: bool = Field(default=True, description="是否并行处理")
    timeout: int = Field(default=300, description="超时时间(秒)", ge=10, le=600)
    
    @validator('questions')
    def validate_questions_not_empty(cls, v):
        if not v:
            raise ValueError('问题列表不能为空')
        cleaned_questions = []
        for question in v:
            if question and question.strip():
                cleaned_questions.append(question.strip())
        if not cleaned_questions:
            raise ValueError('问题列表中没有有效的问题')
        return cleaned_questions


class QABatchQueryResponse(BaseModel):
    """批量问答查询响应模型"""
    success: bool = Field(..., description="批量查询是否成功")
    results: List[QAQueryResponse] = Field(..., description="查询结果列表")
    total_queries: int = Field(..., description="总查询数量")
    successful_queries: int = Field(..., description="成功查询数量")
    failed_queries: int = Field(..., description="失败查询数量")
    total_time: float = Field(..., description="总处理时间(秒)")
    average_time: float = Field(..., description="平均处理时间(秒)")


class QABackupRequest(BaseModel):
    """问答系统备份请求模型"""
    include_vectors: bool = Field(default=True, description="是否包含向量数据")
    compress: bool = Field(default=True, description="是否压缩备份文件")
    backup_name: Optional[str] = Field(None, description="备份文件名", max_length=200)


class QABackupResponse(BaseModel):
    """问答系统备份响应模型"""
    success: bool = Field(..., description="备份是否成功")
    backup_file: str = Field(..., description="备份文件路径")
    backup_size: int = Field(..., description="备份文件大小(字节)")
    qa_pairs_count: int = Field(..., description="备份的问答对数量")
    created_at: float = Field(..., description="备份创建时间戳")
    message: str = Field(..., description="备份结果消息")


class QARestoreRequest(BaseModel):
    """问答系统恢复请求模型"""
    backup_file: str = Field(..., description="备份文件路径", max_length=500)
    overwrite_existing: bool = Field(default=False, description="是否覆盖现有数据")
    validate_data: bool = Field(default=True, description="是否验证数据完整性")


class QARestoreResponse(BaseModel):
    """问答系统恢复响应模型"""
    success: bool = Field(..., description="恢复是否成功")
    restored_count: int = Field(..., description="恢复的问答对数量")
    skipped_count: int = Field(..., description="跳过的问答对数量")
    error_count: int = Field(..., description="错误的问答对数量")
    total_count: int = Field(..., description="总数量")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    message: str = Field(..., description="恢复结果消息")
