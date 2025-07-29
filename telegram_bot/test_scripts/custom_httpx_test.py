#!/usr/bin/env python3
"""
使用自定义 httpx 客户端的 Gemini API 测试
"""

import os
import httpx
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 加载环境变量
load_dotenv()

def test_custom_httpx():
    """使用自定义 httpx 客户端测试"""
    print("开始自定义 httpx 客户端测试...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        # 创建自定义 httpx 客户端
        custom_client = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "CustomBot/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        print("✅ 自定义 httpx 客户端创建成功")
        
        # 创建 Gemini 客户端
        client = genai.Client(api_key=api_key)
        
        print("✅ Gemini 客户端创建成功")
        
        # 创建极简内容
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello")]
            )
        ]
        
        print("✅ 内容创建成功")
        
        # 调用 API
        print("正在调用 Gemini API...")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
        ):
            if chunk.text:
                response_text += chunk.text
        
        print(f"✅ API 调用成功！响应: {response_text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_custom_httpx() 