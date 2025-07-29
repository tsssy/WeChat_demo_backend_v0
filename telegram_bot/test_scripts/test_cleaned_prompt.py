#!/usr/bin/env python3
"""
测试清理后的系统提示词
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from matchmaker_bot import MatchmakerBot, safe_encode_string

def test_cleaned_prompt():
    """测试清理后的系统提示词"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return
    
    bot = MatchmakerBot(api_key, gender="female")
    original_prompt = bot._get_system_prompt()
    cleaned_prompt = safe_encode_string(original_prompt)
    
    print(f"原始提示词长度: {len(original_prompt)}")
    print(f"清理后提示词长度: {len(cleaned_prompt)}")
    
    # 测试编码
    try:
        cleaned_prompt.encode('ascii')
        print("✅ 清理后的提示词可以编码为ASCII")
    except UnicodeEncodeError as e:
        print(f"❌ 清理后的提示词仍然有编码问题: {e}")
        return False
    
    # 检查是否有非ASCII字符
    non_ascii_chars = [char for char in cleaned_prompt if ord(char) >= 128]
    if non_ascii_chars:
        print(f"⚠️ 清理后仍有 {len(non_ascii_chars)} 个非ASCII字符")
        for i, char in enumerate(non_ascii_chars[:10]):  # 只显示前10个
            print(f"  字符 {i+1}: '{char}' (Unicode: {ord(char)})")
    else:
        print("✅ 清理后没有非ASCII字符")
    
    return True

if __name__ == "__main__":
    test_cleaned_prompt() 