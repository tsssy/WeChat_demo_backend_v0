#!/usr/bin/env python3
"""
使用 requests 库直接调用 Gemini API
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_requests_api():
    """使用 requests 直接调用 Gemini API"""
    print("开始 requests 直接调用测试...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    try:
        # 直接调用 Gemini API
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CustomBot/1.0"
        }
        
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": "Hello, how are you?"
                        }
                    ]
                }
            ]
        }
        
        print("✅ 请求数据准备完成")
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ API 调用成功！响应: {text[:100]}...")
                return True
            else:
                print(f"❌ API 响应格式异常: {result}")
                return False
        else:
            print(f"❌ API 调用失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_requests_api() 