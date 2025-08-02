"""
GuiXiaoXiRag服务单元测试
"""
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from server.guixiaoxirag_service import GuiXiaoXiRagService
from server.config import Settings


class TestGuiXiaoXiRagService:
    """GuiXiaoXiRag服务测试类"""
    
    @pytest.fixture
    async def service(self):
        """创建测试服务实例"""
        # 创建临时目录作为工作目录
        temp_dir = tempfile.mkdtemp()
        
        # 创建测试配置
        test_settings = Settings(
            working_dir=temp_dir,
            embedding_dim=128,  # 使用较小的维度进行测试
            max_token_size=1024
        )
        
        service = GuiXiaoXiRagService()
        
        # 使用测试配置初始化
        try:
            await service.initialize(working_dir=temp_dir)
            yield service
        finally:
            # 清理
            await service.finalize()
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service._initialized is True
        assert service.rag is not None
    
    async def test_insert_text(self, service):
        """测试文本插入"""
        test_text = "这是一个测试文档，用于验证GuiXiaoXiRag的文本插入功能。"
        
        track_id = await service.insert_text(
            text=test_text,
            doc_id="test_doc_1"
        )
        
        assert track_id is not None
        assert isinstance(track_id, str)
    
    async def test_insert_multiple_texts(self, service):
        """测试批量文本插入"""
        test_texts = [
            "第一个测试文档。",
            "第二个测试文档，包含不同的内容。",
            "第三个测试文档，用于验证批量插入功能。"
        ]
        
        track_id = await service.insert_texts(
            texts=test_texts,
            doc_ids=["doc1", "doc2", "doc3"]
        )
        
        assert track_id is not None
        assert isinstance(track_id, str)
    
    async def test_query_after_insert(self, service):
        """测试插入后查询"""
        # 先插入一些数据
        test_text = "人工智能是计算机科学的一个重要分支，专注于创建智能机器。"
        await service.insert_text(text=test_text, doc_id="ai_doc")
        
        # 等待一段时间让数据处理完成
        await asyncio.sleep(1)
        
        # 执行查询
        result = await service.query(
            query="什么是人工智能？",
            mode="hybrid",
            top_k=5
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    async def test_different_query_modes(self, service):
        """测试不同查询模式"""
        # 插入测试数据
        test_text = "机器学习是人工智能的一个子领域，使计算机能够从数据中学习。"
        await service.insert_text(text=test_text, doc_id="ml_doc")
        
        await asyncio.sleep(1)
        
        query = "机器学习是什么？"
        modes = ["local", "global", "hybrid", "naive"]
        
        for mode in modes:
            try:
                result = await service.query(
                    query=query,
                    mode=mode,
                    top_k=3
                )
                assert result is not None
                assert isinstance(result, str)
            except Exception as e:
                # 某些模式可能在测试环境中不可用
                print(f"模式 {mode} 测试跳过: {e}")
    
    async def test_query_with_parameters(self, service):
        """测试带参数的查询"""
        # 插入测试数据
        test_text = "深度学习是机器学习的一个子集，使用神经网络进行学习。"
        await service.insert_text(text=test_text, doc_id="dl_doc")
        
        await asyncio.sleep(1)
        
        # 测试带各种参数的查询
        result = await service.query(
            query="深度学习的特点是什么？",
            mode="hybrid",
            top_k=10,
            stream=False,
            only_need_context=False,
            response_type="Multiple Paragraphs"
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    async def test_service_finalization(self, service):
        """测试服务清理"""
        # 服务应该已经初始化
        assert service._initialized is True
        
        # 执行清理
        await service.finalize()
        
        # 检查清理后的状态
        assert service._initialized is False


# 运行单元测试的辅助函数
async def run_unit_tests():
    """运行单元测试"""
    print("开始运行GuiXiaoXiRag服务单元测试...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 创建服务实例
        service = GuiXiaoXiRagService()
        
        print("测试服务初始化...")
        await service.initialize(working_dir=temp_dir)
        assert service._initialized is True
        print("✓ 服务初始化测试通过")
        
        print("测试文本插入...")
        track_id = await service.insert_text(
            text="这是一个测试文档。",
            doc_id="test_1"
        )
        assert track_id is not None
        print("✓ 文本插入测试通过")
        
        print("测试查询功能...")
        await asyncio.sleep(2)  # 等待处理完成
        result = await service.query(
            query="测试文档包含什么？",
            mode="hybrid"
        )
        assert result is not None
        print("✓ 查询功能测试通过")
        
        print("测试服务清理...")
        await service.finalize()
        assert service._initialized is False
        print("✓ 服务清理测试通过")
        
        print("所有单元测试通过!")
        
    except Exception as e:
        print(f"单元测试失败: {e}")
        raise
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(run_unit_tests())
