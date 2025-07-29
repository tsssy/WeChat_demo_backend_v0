#!/usr/bin/env python3
"""
测试远端API连接脚本
专门用于测试 https://lovetapoversea.xyz:4433 的API连接
"""

import asyncio
import httpx
import logging
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API配置
API_BASE_URL = Config.API.API_BASE_URL

async def test_remote_api_connection():
    """测试远端API连接"""
    logging.info(f"正在测试远端API连接: {API_BASE_URL}")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试根路径
            response = await client.get(f"{API_BASE_URL}/", timeout=10.0)
            logging.info(f"根路径响应状态码: {response.status_code}")
            logging.info(f"根路径响应内容: {response.text}")
            
            if response.status_code == 200:
                logging.info("✅ 远端API连接成功！")
                return True
            else:
                logging.error(f"❌ 远端API返回错误状态码: {response.status_code}")
                return False
    except Exception as e:
        logging.error(f"❌ 远端API连接失败: {str(e)}")
        return False

async def test_remote_api_endpoints():
    """测试远端API的具体端点"""
    logging.info("正在测试远端API端点...")
    
    try:
        async with httpx.AsyncClient() as client:
            # 测试创建用户端点
            test_data = {
                "telegram_user_id": 999999999,
                "telegram_user_name": "test_remote_user",
                "gender": 1
            }
            
            response = await client.post(
                f"{API_BASE_URL}/api/v1/UserManagement/create_new_user",
                json=test_data,
                timeout=15.0
            )
            
            logging.info(f"创建用户端点响应状态码: {response.status_code}")
            logging.info(f"创建用户端点响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                user_id = result.get('user_id')
                logging.info(f"✅ 远端API创建用户成功！用户ID: {user_id}")
                
                # 测试编辑年龄端点
                age_data = {
                    "user_id": user_id,
                    "age": 25
                }
                
                age_response = await client.post(
                    f"{API_BASE_URL}/api/v1/UserManagement/edit_user_age",
                    json=age_data,
                    timeout=15.0
                )
                
                logging.info(f"编辑年龄端点响应状态码: {age_response.status_code}")
                logging.info(f"编辑年龄端点响应内容: {age_response.text}")
                
                if age_response.status_code == 200:
                    logging.info("✅ 远端API编辑年龄成功！")
                else:
                    logging.error("❌ 远端API编辑年龄失败！")
                
                return True
            else:
                logging.error("❌ 远端API创建用户失败！")
                return False
                
    except Exception as e:
        logging.error(f"❌ 远端API端点测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    logging.info("开始测试远端API...")
    
    # 测试API连接
    if not await test_remote_api_connection():
        logging.error("远端API连接失败，请检查网络连接和API地址")
        return
    
    # 测试API端点
    await test_remote_api_endpoints()
    
    logging.info("远端API测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 