"""
工具函数
"""
import os
import logging
import zipfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional
import docx2txt
import textract
from fastapi import UploadFile, HTTPException

from .config import settings


def setup_logging():
    """设置日志配置"""
    # 确保日志目录存在
    os.makedirs(settings.log_dir, exist_ok=True)
    
    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler(
                os.path.join(settings.log_dir, "guixiaoxiRagirag_service.log"),
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )


def is_docx(file_path: str) -> bool:
    """检查文件是否为docx格式"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            return True
    except zipfile.BadZipFile:
        return False


def extract_text_from_file(file_path: str) -> str:
    """从文件中提取文本内容"""
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif file_extension == '.pdf':
            text_content = textract.process(str(file_path))
            return text_content.decode('utf-8')
        
        elif file_extension == '.docx':
            return docx2txt.process(file_path)
        
        elif file_extension == '.doc':
            try:
                # 首先尝试用textract处理
                text_content = textract.process(str(file_path))
                return text_content.decode('utf-8')
            except Exception:
                # 如果textract失败，检查文件是否是docx格式
                if is_docx(file_path):
                    return docx2txt.process(file_path)
                else:
                    raise ValueError(f"无法处理.doc文件: {file_path}")
        
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    except Exception as e:
        raise ValueError(f"文件内容提取失败: {str(e)}")


async def process_uploaded_file(file: UploadFile) -> Dict[str, Any]:
    """处理上传的文件"""
    # 检查文件大小
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"文件大小超过限制 ({settings.max_file_size} bytes)"
        )
    
    # 检查文件类型
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in settings.allowed_file_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_extension}"
        )
    
    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(settings.upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 提取文本内容
        text_content = extract_text_from_file(file_path)
        
        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "content": text_content
        }
    
    except Exception as e:
        # 如果处理失败，删除已保存的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


def get_file_contents(dir_name: str) -> list:
    """从目录中获取所有支持文件的内容"""
    contents = []
    current_dir = Path(__file__).parent.parent
    files_dir = current_dir / dir_name
    
    if not files_dir.exists():
        return contents
    
    # 处理txt文件
    for file_path in files_dir.glob("*.txt"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            contents.append(content)
        except Exception as e:
            logging.error(f"读取txt文件失败 {file_path}: {e}")
    
    # 处理pdf文件
    for file_path in files_dir.glob("*.pdf"):
        try:
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            logging.error(f"处理PDF文件失败 {file_path}: {e}")
    
    # 处理docx文件
    for file_path in files_dir.glob("*.docx"):
        try:
            text_content = docx2txt.process(file_path)
            contents.append(text_content)
        except Exception as e:
            logging.error(f"处理DOCX文件失败 {file_path}: {e}")
    
    # 处理doc文件
    for file_path in files_dir.glob("*.doc"):
        try:
            # 首先尝试用textract处理
            text_content = textract.process(str(file_path))
            contents.append(text_content.decode('utf-8'))
        except Exception as e:
            logging.error(f"用textract处理DOC文件失败 {file_path}: {e}")
            # 如果textract失败，检查文件是否是docx格式
            if is_docx(str(file_path)):
                try:
                    text_content = docx2txt.process(file_path)
                    contents.append(text_content)
                    logging.info(f"成功将{file_path}作为DOCX文件处理")
                except Exception as e2:
                    logging.error(f"将DOC文件作为DOCX处理失败 {file_path}: {e2}")
            else:
                logging.error(f"跳过文件 {file_path}，既不是DOC也不是有效的DOCX")
    
    return contents


def validate_query_mode(mode: str) -> bool:
    """验证查询模式是否有效"""
    valid_modes = ["local", "global", "hybrid", "naive", "mix", "bypass"]
    return mode in valid_modes


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    import re
    # 移除路径分隔符和其他不安全字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename


def xml_to_json(xml_file: str) -> Optional[Dict[str, Any]]:
    """
    将GraphML XML文件转换为JSON格式的知识图谱数据

    Args:
        xml_file: GraphML XML文件路径

    Returns:
        包含nodes和edges的字典，如果转换失败则返回None
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        logging.info(f"解析XML文件: {xml_file}")
        logging.info(f"根元素: {root.tag}")
        logging.info(f"根属性: {root.attrib}")

        data = {"nodes": [], "edges": []}

        # 使用GraphML命名空间
        namespace = {"": "http://graphml.graphdrawing.org/xmlns"}

        # 解析节点
        for node in root.findall(".//node", namespace):
            node_data = {
                "id": node.get("id").strip('"') if node.get("id") else "",
                "entity_type": (
                    node.find("./data[@key='d1']", namespace).text.strip('"')
                    if node.find("./data[@key='d1']", namespace) is not None
                    else ""
                ),
                "description": (
                    node.find("./data[@key='d2']", namespace).text
                    if node.find("./data[@key='d2']", namespace) is not None
                    else ""
                ),
                "source_id": (
                    node.find("./data[@key='d3']", namespace).text
                    if node.find("./data[@key='d3']", namespace) is not None
                    else ""
                ),
            }
            data["nodes"].append(node_data)

        # 解析边
        for edge in root.findall(".//edge", namespace):
            edge_data = {
                "source": edge.get("source").strip('"') if edge.get("source") else "",
                "target": edge.get("target").strip('"') if edge.get("target") else "",
                "weight": (
                    float(edge.find("./data[@key='d5']", namespace).text)
                    if edge.find("./data[@key='d5']", namespace) is not None
                    else 0.0
                ),
                "description": (
                    edge.find("./data[@key='d6']", namespace).text
                    if edge.find("./data[@key='d6']", namespace) is not None
                    else ""
                ),
                "keywords": (
                    edge.find("./data[@key='d7']", namespace).text
                    if edge.find("./data[@key='d7']", namespace) is not None
                    else ""
                ),
                "source_id": (
                    edge.find("./data[@key='d8']", namespace).text
                    if edge.find("./data[@key='d8']", namespace) is not None
                    else ""
                ),
            }
            data["edges"].append(edge_data)

        logging.info(f"成功解析 {len(data['nodes'])} 个节点和 {len(data['edges'])} 条边")
        return data

    except ET.ParseError as e:
        logging.error(f"XML解析错误: {e}")
        return None
    except Exception as e:
        logging.error(f"转换过程中发生错误: {e}")
        return None


def convert_xml_to_json(xml_path: str, output_path: str) -> Optional[Dict[str, Any]]:
    """
    将XML文件转换为JSON并保存输出

    Args:
        xml_path: 输入的XML文件路径
        output_path: 输出的JSON文件路径

    Returns:
        转换后的JSON数据，如果转换失败则返回None
    """
    if not os.path.exists(xml_path):
        logging.error(f"文件不存在: {xml_path}")
        return None

    json_data = xml_to_json(xml_path)
    if json_data:
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            logging.info(f"JSON文件已创建: {output_path}")
            return json_data
        except Exception as e:
            logging.error(f"保存JSON文件失败: {e}")
            return None
    else:
        logging.error("JSON数据创建失败")
        return None


def create_or_update_knowledge_graph_json(working_dir: str) -> bool:
    """
    为指定工作目录创建或更新知识图谱JSON文件

    Args:
        working_dir: 知识库工作目录

    Returns:
        成功返回True，失败返回False
    """
    try:
        # 检查工作目录是否存在
        if not working_dir or not os.path.exists(working_dir):
            logging.error(f"工作目录不存在: {working_dir}")
            return False

        xml_file = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
        json_file = os.path.join(working_dir, "graph_data.json")

        # 检查XML文件是否存在
        if not os.path.exists(xml_file):
            logging.warning(f"知识图谱XML文件不存在: {xml_file}")
            return False

        # 检查XML文件是否为空
        if os.path.getsize(xml_file) == 0:
            logging.warning(f"知识图谱XML文件为空: {xml_file}")
            return False

        # 检查XML文件是否可读
        if not os.access(xml_file, os.R_OK):
            logging.error(f"知识图谱XML文件无法读取: {xml_file}")
            return False

        # 转换XML到JSON
        json_data = convert_xml_to_json(xml_file, json_file)

        if json_data:
            # 验证JSON数据的有效性
            if not isinstance(json_data, dict) or 'nodes' not in json_data or 'edges' not in json_data:
                logging.error(f"生成的JSON数据格式无效: {json_file}")
                return False

            logging.info(f"知识图谱JSON文件已更新: {json_file}")
            logging.info(f"包含 {len(json_data.get('nodes', []))} 个节点和 {len(json_data.get('edges', []))} 条边")
            return True
        else:
            logging.error(f"知识图谱JSON文件更新失败: {json_file}")
            return False

    except PermissionError as e:
        logging.error(f"权限错误，无法访问文件: {e}")
        return False
    except OSError as e:
        logging.error(f"文件系统错误: {e}")
        return False
    except Exception as e:
        logging.error(f"创建或更新知识图谱JSON文件时发生未知错误: {e}")
        return False


def check_knowledge_graph_files(working_dir: str) -> Dict[str, Any]:
    """
    检查知识图谱相关文件的状态

    Args:
        working_dir: 知识库工作目录

    Returns:
        包含文件状态信息的字典
    """
    result = {
        "working_dir_exists": False,
        "xml_file_exists": False,
        "xml_file_size": 0,
        "json_file_exists": False,
        "json_file_size": 0,
        "xml_file_path": "",
        "json_file_path": "",
        "last_xml_modified": None,
        "last_json_modified": None,
        "status": "unknown"
    }

    try:
        # 检查工作目录
        if working_dir and os.path.exists(working_dir):
            result["working_dir_exists"] = True

            xml_file = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
            json_file = os.path.join(working_dir, "graph_data.json")

            result["xml_file_path"] = xml_file
            result["json_file_path"] = json_file

            # 检查XML文件
            if os.path.exists(xml_file):
                result["xml_file_exists"] = True
                result["xml_file_size"] = os.path.getsize(xml_file)
                result["last_xml_modified"] = os.path.getmtime(xml_file)

            # 检查JSON文件
            if os.path.exists(json_file):
                result["json_file_exists"] = True
                result["json_file_size"] = os.path.getsize(json_file)
                result["last_json_modified"] = os.path.getmtime(json_file)

            # 确定状态
            if result["xml_file_exists"] and result["json_file_exists"]:
                if result["last_xml_modified"] > result["last_json_modified"]:
                    result["status"] = "json_outdated"
                else:
                    result["status"] = "up_to_date"
            elif result["xml_file_exists"]:
                result["status"] = "json_missing"
            else:
                result["status"] = "xml_missing"
        else:
            result["status"] = "working_dir_missing"

    except Exception as e:
        logging.error(f"检查知识图谱文件状态时发生错误: {e}")
        result["status"] = "error"
        result["error"] = str(e)

    return result
