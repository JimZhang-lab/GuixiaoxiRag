"""
清理管理器
负责清理测试过程中生成的文件和目录
"""

import os
import shutil
import glob
from pathlib import Path
from typing import List, Set, Dict
import logging

logger = logging.getLogger(__name__)


class CleanupManager:
    """清理管理器类"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        
        # 需要清理的文件模式
        self.cleanup_patterns = [
            "logs/*.log",
            "logs/*.json", 
            "logs/*.md",
            "temp/*",
            "test_data/*",
            "__pycache__/*",
            "**/__pycache__/*",
            "*.pyc",
            "**/*.pyc",
            ".pytest_cache/*",
            "**/.pytest_cache/*"
        ]
        
        # 需要清理的目录（如果为空）
        self.cleanup_dirs = [
            "logs",
            "temp", 
            "test_data",
            "__pycache__",
            ".pytest_cache"
        ]
        
        # 保护的目录（不会被删除）
        self.protected_dirs = {
            "config",
            "fixtures",
            "tests", 
            "utils",
            "runners"
        }
        
        # 保护的文件（不会被删除）
        self.protected_files = {
            "main.py",
            "README.md",
            "requirements.txt",
            ".gitignore"
        }
    
    def find_files_to_clean(self) -> List[Path]:
        """查找需要清理的文件"""
        files_to_clean = []
        
        for pattern in self.cleanup_patterns:
            pattern_path = self.base_dir / pattern
            
            # 使用glob查找匹配的文件
            for file_path in glob.glob(str(pattern_path), recursive=True):
                file_path = Path(file_path)
                
                # 检查是否为保护文件
                if file_path.name in self.protected_files:
                    continue
                
                # 检查是否在保护目录中
                if any(protected_dir in file_path.parts for protected_dir in self.protected_dirs):
                    # 如果在保护目录中，只清理特定类型的文件
                    if file_path.suffix in ['.pyc', '.log', '.json']:
                        files_to_clean.append(file_path)
                else:
                    files_to_clean.append(file_path)
        
        return files_to_clean
    
    def find_dirs_to_clean(self) -> List[Path]:
        """查找需要清理的空目录"""
        dirs_to_clean = []
        
        for dir_name in self.cleanup_dirs:
            dir_path = self.base_dir / dir_name
            
            if dir_path.exists() and dir_path.is_dir():
                # 检查目录是否为空或只包含可清理的文件
                if self._is_dir_cleanable(dir_path):
                    dirs_to_clean.append(dir_path)
        
        return dirs_to_clean
    
    def _is_dir_cleanable(self, dir_path: Path) -> bool:
        """检查目录是否可以清理"""
        if not dir_path.exists():
            return False
        
        # 如果是保护目录，不清理
        if dir_path.name in self.protected_dirs:
            return False
        
        try:
            # 检查目录内容
            contents = list(dir_path.iterdir())
            
            # 如果目录为空，可以清理
            if not contents:
                return True
            
            # 如果只包含可清理的文件，也可以清理
            for item in contents:
                if item.is_file():
                    # 检查文件是否可清理
                    if not self._is_file_cleanable(item):
                        return False
                elif item.is_dir():
                    # 递归检查子目录
                    if not self._is_dir_cleanable(item):
                        return False
            
            return True
            
        except PermissionError:
            logger.warning(f"无法访问目录: {dir_path}")
            return False
    
    def _is_file_cleanable(self, file_path: Path) -> bool:
        """检查文件是否可以清理"""
        # 保护文件不清理
        if file_path.name in self.protected_files:
            return False
        
        # 检查文件扩展名
        cleanable_extensions = {'.pyc', '.log', '.json', '.md', '.tmp', '.temp'}
        if file_path.suffix in cleanable_extensions:
            return True
        
        # 检查文件是否在临时目录中
        temp_dirs = {'logs', 'temp', 'test_data', '__pycache__', '.pytest_cache'}
        if any(temp_dir in file_path.parts for temp_dir in temp_dirs):
            return True
        
        return False
    
    def clean_files(self, files: List[Path]) -> List[Path]:
        """清理指定的文件"""
        cleaned_files = []
        
        for file_path in files:
            try:
                if file_path.exists() and file_path.is_file():
                    file_path.unlink()
                    cleaned_files.append(file_path)
                    logger.debug(f"删除文件: {file_path}")
            except Exception as e:
                logger.warning(f"无法删除文件 {file_path}: {e}")
        
        return cleaned_files
    
    def clean_dirs(self, dirs: List[Path]) -> List[Path]:
        """清理指定的目录"""
        cleaned_dirs = []
        
        for dir_path in dirs:
            try:
                if dir_path.exists() and dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    cleaned_dirs.append(dir_path)
                    logger.debug(f"删除目录: {dir_path}")
            except Exception as e:
                logger.warning(f"无法删除目录 {dir_path}: {e}")
        
        return cleaned_dirs
    
    def clean_all(self) -> List[Path]:
        """清理所有生成的文件和目录"""
        logger.info("开始清理测试生成的文件...")
        
        all_cleaned = []
        
        # 清理文件
        files_to_clean = self.find_files_to_clean()
        cleaned_files = self.clean_files(files_to_clean)
        all_cleaned.extend(cleaned_files)
        
        # 清理空目录
        dirs_to_clean = self.find_dirs_to_clean()
        cleaned_dirs = self.clean_dirs(dirs_to_clean)
        all_cleaned.extend(cleaned_dirs)
        
        logger.info(f"清理完成，共删除 {len(all_cleaned)} 个文件/目录")
        
        return all_cleaned
    
    def preview_cleanup(self) -> Dict[str, List[Path]]:
        """预览将要清理的文件和目录"""
        files_to_clean = self.find_files_to_clean()
        dirs_to_clean = self.find_dirs_to_clean()
        
        return {
            "files": files_to_clean,
            "directories": dirs_to_clean,
            "total": len(files_to_clean) + len(dirs_to_clean)
        }
    
    def clean_logs_only(self) -> List[Path]:
        """只清理日志文件"""
        log_patterns = [
            "logs/*.log",
            "logs/*.json",
            "logs/*.md"
        ]
        
        files_to_clean = []
        for pattern in log_patterns:
            pattern_path = self.base_dir / pattern
            for file_path in glob.glob(str(pattern_path)):
                files_to_clean.append(Path(file_path))
        
        return self.clean_files(files_to_clean)
    
    def clean_temp_only(self) -> List[Path]:
        """只清理临时文件"""
        temp_patterns = [
            "temp/*",
            "test_data/*",
            "__pycache__/*",
            "**/__pycache__/*",
            "*.pyc",
            "**/*.pyc"
        ]
        
        files_to_clean = []
        for pattern in temp_patterns:
            pattern_path = self.base_dir / pattern
            for file_path in glob.glob(str(pattern_path), recursive=True):
                files_to_clean.append(Path(file_path))
        
        return self.clean_files(files_to_clean)
