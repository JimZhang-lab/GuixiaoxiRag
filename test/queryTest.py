import os
from pathlib import Path
import shutil
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import time
from guixiaoxiRag import GuiXiaoXiRag, QueryParam
from guixiaoxiRag.llm.openai import openai_embed, openai_complete_if_cache
from guixiaoxiRag.kg.shared_storage import initialize_pipeline_status
from guixiaoxiRag.utils import setup_logger, EmbeddingFunc
import numpy as np
import json
import xml.etree.ElementTree as ET

setup_logger("guixiaoxiRag", level="INFO")

WORKING_DIR = "./knowledgeBase/cs_college"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)
    
OPENAI_API_BASE = "http://localhost:8100/v1"
OPENAI_EMBEDDING_API_BASE = "http://localhost:8200/v1"
OPENAI_CHAT_API_KEY = "sk-gdXw028PJ6JtobnBLeQiArQLnmqahdXUQSjIbyFgAhJdHb1Q"
OPENAI_CHAT_MODEL = "qwen"
OPENAI_EMBEDDING_MODEL = "embedding_qwen"

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    return await openai_complete_if_cache(
        OPENAI_CHAT_MODEL,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=OPENAI_CHAT_API_KEY,
        base_url=OPENAI_API_BASE,
        **kwargs
    )

async def embedding_func(texts: list[str]) -> np.ndarray:
    return await openai_embed(
        texts,
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_EMBEDDING_API_BASE,
        base_url=OPENAI_EMBEDDING_API_BASE
    )

async def initialize_rag():
    rag = GuiXiaoXiRag(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=2560,
            max_token_size=8192,
            func=embedding_func
        ),
        addon_params={
        "language": "中文"
        }
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag

# async def main():
#     rag = await asyncio.run(initialize_rag())
    
#     print(
#         await rag.aquery(
#             query = """找到文本中的'同学'关系，返回示例("relationship"<|><source_entity><|><target_entity><|><relationship_description><|><relationship_type><|><relationship_strength>)""", 
#             param = QueryParam(mode="local")
#         )
#     )

import time

if __name__ == "__main__":
    
    start_time = time.time()
    async def main():
        rag = await initialize_rag()
        # []
        result = await rag.aquery(
            query = """
             硕博连读硕士期间发的论文是否可以当作博士的毕业条件
            """, 
            param = QueryParam(
                mode="hybrid",
                top_k = 20,)
        )
        print(result)
    
    asyncio.run(main())
    
    end_time = time.time()
    
    print("Time taken:", round(end_time - start_time, 2), "seconds")