#!/usr/bin/env python3
"""
极简的 Gemini API 测试
只用英文内容，测试是否能正常工作
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 加载环境变量
load_dotenv()

def test_minimal_gemini():
    """测试极简的 Gemini API 调用"""
    print("开始极简 Gemini API 测试...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        # 创建客户端
        client = genai.Client(api_key=api_key)
        print("✅ 客户端创建成功")
        
        # 创建极简内容
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello, how are you?")]
            )
        ]
        
        print("✅ 内容创建成功")
        
        # 配置生成参数
        config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        
        print("✅ 配置创建成功")
        
        # 调用 API
        print("正在调用 Gemini API...")
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=config,
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
    test_minimal_gemini() 