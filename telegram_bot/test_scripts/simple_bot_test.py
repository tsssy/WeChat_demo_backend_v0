#!/usr/bin/env python3
"""
简单机器人测试
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from matchmaker_bot import MatchmakerBot

def test_bot():
    """测试机器人"""
    print("测试机器人初始化...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return
    
    try:
        # 初始化机器人
        bot = MatchmakerBot(api_key, gender="female")
        print("✅ 机器人初始化成功")
        
        # 测试空消息
        print("测试空消息...")
        response = bot.send_message("")
        print(f"响应: {response[:200]}...")
        
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_bot() 