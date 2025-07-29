#!/usr/bin/env python3
"""
网络连接测试脚本
用于诊断Telegram API连接问题
"""

import asyncio
import httpx
import logging
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_telegram_api_connection():
    """测试Telegram API连接"""
    logging.info("开始测试Telegram API连接...")
    
    # Telegram API基础URL
    base_url = "https://api.telegram.org"
    bot_token = Config.API.TELEGRAM_BOT_TOKEN
    
    # 测试不同的端点
    endpoints = [
        f"https://api.telegram.org/bot{bot_token}/getMe",
        f"https://api.telegram.org/bot{bot_token}/getUpdates",
        "https://core.telegram.org/bots/api"
    ]
    
    async with httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ) as client:
        
        for endpoint in endpoints:
            try:
                logging.info(f"测试端点: {endpoint}")
                response = await client.get(endpoint)
                
                if response.status_code == 200:
                    logging.info(f"✅ 成功连接到 {endpoint}")
                    if "getMe" in endpoint:
                        data = response.json()
                        if data.get("ok"):
                            bot_info = data.get("result", {})
                            logging.info(f"机器人信息: {bot_info.get('first_name', 'Unknown')} (@{bot_info.get('username', 'Unknown')})")
                else:
                    logging.warning(f"⚠️ 端点 {endpoint} 返回状态码: {response.status_code}")
                    
            except httpx.ConnectError as e:
                logging.error(f"❌ 连接错误 {endpoint}: {str(e)}")
            except httpx.TimeoutException as e:
                logging.error(f"❌ 超时错误 {endpoint}: {str(e)}")
            except Exception as e:
                logging.error(f"❌ 其他错误 {endpoint}: {str(e)}")

async def test_network_connectivity():
    """测试基本网络连接"""
    logging.info("测试基本网络连接...")
    
    test_urls = [
        "https://www.google.com",
        "https://api.telegram.org",
        "https://core.telegram.org"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in test_urls:
            try:
                response = await client.get(url)
                logging.info(f"✅ 成功连接到 {url} (状态码: {response.status_code})")
            except Exception as e:
                logging.error(f"❌ 无法连接到 {url}: {str(e)}")

def test_config():
    """测试配置"""
    logging.info("检查配置...")
    
    # 检查Token
    token = Config.API.TELEGRAM_BOT_TOKEN
    if token:
        logging.info(f"✅ Telegram Token已配置: {token[:10]}...")
    else:
        logging.error("❌ Telegram Token未配置")
        return False
    
    # 检查Gemini API Key
    gemini_key = Config.API.GEMINI_API_KEY
    if gemini_key:
        logging.info(f"✅ Gemini API Key已配置: {gemini_key[:10]}...")
    else:
        logging.warning("⚠️ Gemini API Key未配置")
    
    return True

async def main():
    """主函数"""
    logging.info("=" * 50)
    logging.info("网络连接诊断工具")
    logging.info("=" * 50)
    
    # 测试配置
    if not test_config():
        logging.error("配置检查失败，退出")
        return
    
    # 测试基本网络连接
    await test_network_connectivity()
    
    # 测试Telegram API连接
    await test_telegram_api_connection()
    
    logging.info("=" * 50)
    logging.info("诊断完成")
    logging.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 