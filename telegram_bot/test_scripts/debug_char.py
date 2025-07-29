#!/usr/bin/env python3
"""
调试字符位置
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from matchmaker_bot import MatchmakerBot

def debug_char():
    """调试字符位置"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return
    
    bot = MatchmakerBot(api_key, gender="female")
    system_prompt = bot._get_system_prompt()
    
    print(f"系统提示词长度: {len(system_prompt)}")
    
    # 检查第877个字符
    if len(system_prompt) > 877:
        char_877 = system_prompt[877]
        print(f"第877个字符: '{char_877}' (Unicode: {ord(char_877)})")
        
        # 检查周围的字符
        start = max(0, 877 - 10)
        end = min(len(system_prompt), 877 + 10)
        context = system_prompt[start:end]
        print(f"上下文: {repr(context)}")
    
    # 检查第43-49个字符
    if len(system_prompt) > 49:
        chars_43_49 = system_prompt[43:50]
        print(f"第43-49个字符: {repr(chars_43_49)}")
        for i, char in enumerate(chars_43_49):
            print(f"  位置 {43+i}: '{char}' (Unicode: {ord(char)})")

if __name__ == "__main__":
    debug_char() 