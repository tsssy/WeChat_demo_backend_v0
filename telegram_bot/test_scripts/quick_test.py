#!/usr/bin/env python3
"""
快速编码测试
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from matchmaker_bot import safe_encode_string

def test_encoding():
    """测试编码函数"""
    print("测试编码函数...")
    
    # 测试包含特殊字符的文本
    test_text = "Hello 你好 World 世界"
    result = safe_encode_string(test_text)
    print(f"原文: {test_text}")
    print(f"结果: {result}")
    
    # 测试是否可以编码为ASCII
    try:
        result.encode('ascii')
        print("✅ 编码成功")
    except UnicodeEncodeError as e:
        print(f"❌ 编码失败: {e}")

if __name__ == "__main__":
    test_encoding() 