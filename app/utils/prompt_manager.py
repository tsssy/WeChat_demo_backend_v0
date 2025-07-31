import os
from pathlib import Path
from typing import Dict, List, Optional

class PromptManager:
    """
    提示词管理器，负责读取和组合prompt文件
    """
    
    def __init__(self):
        """初始化提示词管理器"""
        # 获取prompts文件夹路径
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self._cache = {}  # 缓存读取的文件内容
    
    def _read_prompt_file(self, filename: str) -> str:
        """
        读取指定的prompt文件
        
        Args:
            filename: 文件名（如 'role.md'）
            
        Returns:
            str: 文件内容
        """
        if filename in self._cache:
            return self._cache[filename]
        
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self._cache[filename] = content
                return content
        except Exception as e:
            print(f"读取prompt文件 {filename} 失败: {e}")
            return ""
    
    def get_core_prompts(self) -> str:
        """
        获取核心提示词内容
        
        Returns:
            str: 组合后的核心提示词
        """
        core_files = ['role.md', 'object.md', 'skill.md', 'constraint.md', 'workflow.md']
        prompts = []
        
        for filename in core_files:
            content = self._read_prompt_file(filename)
            if content:
                prompts.append(content)
        
        return "\n\n".join(prompts)
    
    def get_gender_specific_prompt(self, gender: str = "neutral") -> str:
        """
        根据性别获取特定的提示词
        
        Args:
            gender: 性别 ('male', 'female', 'neutral')
            
        Returns:
            str: 性别特定的提示词内容
        """
        gender_map = {
            "male": "male.md",
            "female": "female.md",
            "neutral": "neutral.md"
        }
        
        filename = gender_map.get(gender.lower(), "neutral.md")
        return self._read_prompt_file(filename)
    
    def get_complete_prompt(self, gender: str = "neutral") -> str:
        """
        获取完整的系统提示词
        
        Args:
            gender: 性别 ('male', 'female', 'neutral')
            
        Returns:
            str: 完整的系统提示词
        """
        core_prompts = self.get_core_prompts()
        gender_prompt = self.get_gender_specific_prompt(gender)
        
        if gender_prompt:
            return f"{core_prompts}\n\n{gender_prompt}"
        else:
            return core_prompts
    
    def get_available_genders(self) -> List[str]:
        """
        获取可用的性别选项
        
        Returns:
            List[str]: 可用的性别列表
        """
        return ["male", "female", "neutral"]
    
    def get_prompt_info(self) -> Dict[str, str]:
        """
        获取所有prompt文件的信息
        
        Returns:
            Dict[str, str]: 文件名和内容的字典
        """
        info = {}
        for file_path in self.prompts_dir.glob("*.md"):
            if file_path.name != "README.md":
                content = self._read_prompt_file(file_path.name)
                info[file_path.name] = content
        return info
    
    def validate_prompts(self) -> Dict[str, bool]:
        """
        验证所有prompt文件是否存在且可读
        
        Returns:
            Dict[str, bool]: 文件名和验证结果的字典
        """
        validation = {}
        expected_files = [
            'role.md', 'object.md', 'skill.md', 'constraint.md', 
            'workflow.md', 'male.md', 'female.md', 'neutral.md'
        ]
        
        for filename in expected_files:
            content = self._read_prompt_file(filename)
            validation[filename] = bool(content)
        
        return validation

# 创建全局实例
prompt_manager = PromptManager() 