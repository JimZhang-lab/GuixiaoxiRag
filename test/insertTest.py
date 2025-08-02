import os
from pathlib import Path
import shutil
import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
import time

import docx2txt
from guixiaoxiRag import GuiXiaoXiRag, QueryParam
from guixiaoxiRag.llm.openai import openai_embed, openai_complete_if_cache
from guixiaoxiRag.kg.shared_storage import initialize_pipeline_status
from guixiaoxiRag.utils import setup_logger, EmbeddingFunc
import numpy as np
import json
import xml.etree.ElementTree as ET
import textract
import zipfile

def is_docx(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            return True
    except zipfile.BadZipFile:
        return False

setup_logger("guixiaoxiRag", level="INFO")

WORKING_DIR = "./knowledgeBase/cs_college"
if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)
    
OPENAI_API_BASE = "http://localhost:8100/v1"
OPENAI_EMBEDDING_API_BASE = "http://localhost:8200/v1"
OPENAI_CHAT_API_KEY = "sk-gdXw028PJ6JtobnBLeQiArQLnmqahdXUQSjIbyFgAhJdHb1Q"
OPENAI_CHAT_MODEL = "qwen14b"
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
            embedding_dim=2056,
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


# contents = []
# current_dir = Path(__file__).parent
# # 指定文件目录
# files_dir = current_dir / "files/inputs"
# for file_path in files_dir.glob("*.txt"):
#     with open(file_path, "r", encoding="utf-8") as file:
#         content = file.read()
#     contents.append(content)
    
# rag.insert(contents)
# print("构建索引完成")
def xml_to_json(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Print the root element's tag and attributes to confirm the file has been correctly loaded
        print(f"Root element: {root.tag}")
        print(f"Root attributes: {root.attrib}")

        data = {"nodes": [], "edges": []}

        # Use namespace
        namespace = {"": "http://graphml.graphdrawing.org/xmlns"}

        for node in root.findall(".//node", namespace):
            node_data = {
                "id": node.get("id").strip('"'),
                "entity_type": node.find("./data[@key='d1']", namespace).text.strip('"')
                if node.find("./data[@key='d1']", namespace) is not None
                else "",
                "description": node.find("./data[@key='d2']", namespace).text
                if node.find("./data[@key='d2']", namespace) is not None
                else "",
                "source_id": node.find("./data[@key='d3']", namespace).text
                if node.find("./data[@key='d3']", namespace) is not None
                else "",
            }
            data["nodes"].append(node_data)

        for edge in root.findall(".//edge", namespace):
            edge_data = {
                "source": edge.get("source").strip('"'),
                "target": edge.get("target").strip('"'),
                "weight": float(edge.find("./data[@key='d5']", namespace).text)
                if edge.find("./data[@key='d5']", namespace) is not None
                else 0.0,
                "description": edge.find("./data[@key='d6']", namespace).text
                if edge.find("./data[@key='d6']", namespace) is not None
                else "",
                "keywords": edge.find("./data[@key='d7']", namespace).text
                if edge.find("./data[@key='d7']", namespace) is not None
                else "",
                "source_id": edge.find("./data[@key='d8']", namespace).text
                if edge.find("./data[@key='d8']", namespace) is not None
                else "",
            }
            data["edges"].append(edge_data)

        # Print the number of nodes and edges found
        print(f"Found {len(data['nodes'])} nodes and {len(data['edges'])} edges")

        return data
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def convert_xml_to_json(xml_path, output_path):
    """Converts XML file to JSON and saves the output."""
    if not os.path.exists(xml_path):
        print(f"Error: File not found - {xml_path}")
        return None

    json_data = xml_to_json(xml_path)
    if json_data:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"JSON file created: {output_path}")
        return json_data
    else:
        print("Failed to create JSON data")
        return None
    
test_doc ="""
报警人称： 在学校军训有一位同学被老师持脚殴打，现同学身体不适头晕，请民警到场酌情联动120，涉校高中。接警后，2024年8月28日13时24分，新州派出所民警韩贵祥，辅警杨华、田建松驾驶贵H2285警车到达黄平县新州镇黄平民族中学警情现场。经查，报警人郑宏圣（男，身份证号码：522725200710082756，户籍地址：贵州省瓮安县猴场镇石板坪村
石板坪组10号，现住址：黄平县新州镇民族中学男生宿舍，联系电话：13885587025，就读于黄平民族中学高二（7）班）于2024年8月28日13时许，在黄平县新州镇黄平民族中学，称有一位同学被老师持脚殴打，现同学身体不适头晕，请求民警帮助。经新州派出所民警核实，系宋移录（男，身份证号码：522622200705260031，户籍地址：贵州省黄平县新州镇飞云社区康平路10号1栋1单元701室，现住址：黄平县新州镇民族中学男生宿舍，联系电话：19351431886，就读于黄平民族中学高二（10）班）2024年8月26日晚上未经过老师吴龙（男，身份证号码：522622199109101514，户籍地址及现住址：贵州省黄平县谷陇镇牛场村五组，联系电话：18386799760）的同意，从吴龙老师的宿舍里面将凉席拿去使用，今天中午老师看见自己的凉席铺在宋移录床上后就用脚踢了宋移录的屁股两下，宋移录未受伤，现宋移录的父亲、学校领导以及教育局的工作人员已到场，双方称先由学校进行调解处理。该警情联动到黄平县新州镇综治中心跟进处理，新州派出所作情况掌握。（师生纠纷）
"""

def delete_files_in_directory(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print(f"Deleted {file_path} Successfully!")
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % ())
            
def is_docx(file_path):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            return True
    except zipfile.BadZipFile:
        return False
def get_file_contents(dir_name):
    extensions = ['*.doc', '*.docx', '*.pdf']
    
    contents = []
    current_dir = Path(__file__).parent
    # 指定文件目录
    files_dir = current_dir / dir_name
    for file_path in files_dir.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        contents.append(content)
        
    # 获取 pdf 文件
    for file_path in files_dir.glob("*.pdf"):
        try:
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            print(f"Error processing PDF file {file_path}: {e}")
        
    # 获取 docx 文件
    for file_path in files_dir.glob("*.docx"):
        try:
            text_content = docx2txt.process(file_path)
            contents.append(text_content)
        except Exception as e:
            print(f"Error processing DOCX file {file_path}: {e}")
    
    # 获取 doc 文件
    for file_path in files_dir.glob("*.doc"):
        try:
            # 首先尝试用 textract 处理
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            print(f"Error processing DOC file {file_path} with textract: {e}")
            # 如果 textract 失败，检查文件是否是 docx 格式
            if is_docx(file_path):
                try:
                    text_content = docx2txt.process(file_path)
                    contents.append(text_content)
                    print(f"Successfully processed {file_path} as DOCX file despite .doc extension")
                except Exception as e2:
                    print(f"Error processing DOC file {file_path} as DOCX: {e2}")
                    print(f"Skipping file {file_path}")
            else:
                print(f"Skipping file {file_path} as it is neither a DOC nor a valid DOCX")
    
    return contents


def main():
    
    # 先删除 ./output 下的所有文件
    delete_files_in_directory("./output")
    
    # try:
        # Initialize RAG instance
    start_time = time.time()
    rag = asyncio.run(initialize_rag())
    # rag.insert(contents)
    # rag.insert(test_doc)
    cwd = os.getcwd()
    contents = get_file_contents("cs_college_data")
    rag.insert(contents)
        # Perform hybrid search
    #     mode = "hybrid"
    #     print(
    #       await rag.query(
    #           "What are the top themes in this story?",
    #           param=QueryParam(mode=mode)
    #       )
    #     )

    # except Exception as e:
    #     print(f"An error occurred: {e}")
    # finally:
    #     if rag:
    #         await rag.finalize_storages()
    xml_file = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")
    json_file = os.path.join(WORKING_DIR, "graph_data.json")

    # Convert XML to JSON
    json_data = convert_xml_to_json(xml_file, json_file)
    
    end_time = time.time()
    
    print("Time taken:", round(end_time - start_time, 2), "seconds")
    if json_data is None:
        return
    
    
if __name__ == "__main__":
    main()