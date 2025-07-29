#!/usr/bin/env python3
"""
编码测试脚本
用于验证Gemini API调用的编码问题是否已修复
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from matchmaker_bot import MatchmakerBot, safe_encode_string

def test_safe_encode_string():
    """测试安全编码函数"""
    print("测试安全编码函数...")
    
    # 测试各种输入
    test_cases = [
        "Hello World",  # 普通英文
        "你好世界",      # 中文
        "Hello 你好",    # 混合
        "",             # 空字符串
        None,           # None
        b"Hello World", # bytes
        "Hello\x00World", # 包含null字符
    ]
    
    for i, test_input in enumerate(test_cases):
        try:
            result = safe_encode_string(test_input)
            print(f"测试 {i+1}: {repr(test_input)} -> {repr(result)}")
        except Exception as e:
            print(f"测试 {i+1}: {repr(test_input)} -> 错误: {e}")

def test_bot_initialization():
    """测试机器人初始化"""
    print("\n测试机器人初始化...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        # 测试不同性别的初始化
        for gender in ["male", "female", "neutral"]:
            print(f"测试 {gender} 性别初始化...")
            bot = MatchmakerBot(api_key, gender=gender)
            print(f"✅ {gender} 初始化成功")
            
            # 测试系统提示词
            system_prompt = bot._get_system_prompt()
            print(f"系统提示词长度: {len(system_prompt)} 字符")
            
            # 测试编码
            try:
                system_prompt.encode('ascii')
                print(f"✅ {gender} 系统提示词编码正常")
            except UnicodeEncodeError as e:
                print(f"⚠️ {gender} 系统提示词包含非ASCII字符: {e}")
            
    except Exception as e:
        print(f"❌ 机器人初始化失败: {e}")
        return False
    
    return True

def test_simple_message():
    """测试简单消息发送"""
    print("\n测试简单消息发送...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        bot = MatchmakerBot(api_key, gender="female")
        
        # 测试空消息
        print("测试空消息...")
        response = bot.send_message("")
        print(f"空消息响应: {response[:100]}...")
        
        # 测试英文消息
        print("测试英文消息...")
        response = bot.send_message("Hello")
        print(f"英文消息响应: {response[:100]}...")
        
        # 测试中文消息
        print("测试中文消息...")
        response = bot.send_message("你好")
        print(f"中文消息响应: {response[:100]}...")
        
        print("✅ 消息发送测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 消息发送测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("编码修复验证测试")
    print("=" * 50)
    
    # 测试安全编码函数
    test_safe_encode_string()
    
    # 测试机器人初始化
    if test_bot_initialization():
        # 测试消息发送
        test_simple_message()
    
    print("=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main() 