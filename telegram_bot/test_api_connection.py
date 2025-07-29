#!/usr/bin/env python3
"""
测试API连接脚本
用于验证本地后端API是否正常工作
"""

import asyncio
import httpx
import logging
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API配置
API_BASE_URL = Config.API.API_BASE_URL

async def test_api_connection():
    """测试API连接"""
    try:
        async with httpx.AsyncClient() as client:
            # 测试API是否可访问（远端API可能没有/docs端点，先测试根路径）
            response = await client.get(f"{API_BASE_URL}/", timeout=10.0)
            if response.status_code == 200:
                logging.info(f"✅ API连接成功！响应: {response.text}")
                return True
            else:
                logging.error(f"❌ API返回错误状态码: {response.status_code}")
                return False
    except Exception as e:
        logging.error(f"❌ API连接失败: {str(e)}")
        return False

async def test_create_user():
    """测试创建用户API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/UserManagement/create_new_user",
                json={
                    "telegram_user_id": 123456789,
                    "telegram_user_name": "test_user",
                    "gender": 1
                },
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ 创建用户成功: {result}")
                return result.get('user_id')
            else:
                logging.error(f"❌ 创建用户失败: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logging.error(f"❌ 创建用户API调用失败: {str(e)}")
        return None

async def test_edit_user_age(user_id: int):
    """测试编辑用户年龄API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/UserManagement/edit_user_age",
                json={
                    "user_id": user_id,
                    "age": 25
                },
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ 编辑用户年龄成功: {result}")
                return result.get('success', False)
            else:
                logging.error(f"❌ 编辑用户年龄失败: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"❌ 编辑用户年龄API调用失败: {str(e)}")
        return False

async def test_edit_target_gender(user_id: int):
    """测试编辑用户目标性别API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/UserManagement/edit_target_gender",
                json={
                    "user_id": user_id,
                    "target_gender": 1
                },
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ 编辑用户目标性别成功: {result}")
                return result.get('success', False)
            else:
                logging.error(f"❌ 编辑用户目标性别失败: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"❌ 编辑用户目标性别API调用失败: {str(e)}")
        return False

async def test_edit_summary(user_id: int):
    """测试编辑用户总结API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/UserManagement/edit_summary",
                json={
                    "user_id": user_id,
                    "summary": "这是一个测试总结"
                },
                timeout=10.0
            )
            if response.status_code == 200:
                result = response.json()
                logging.info(f"✅ 编辑用户总结成功: {result}")
                return result.get('success', False)
            else:
                logging.error(f"❌ 编辑用户总结失败: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        logging.error(f"❌ 编辑用户总结API调用失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    logging.info("开始测试API连接...")
    
    # 测试API连接
    if not await test_api_connection():
        logging.error("API连接失败，请检查后端服务是否启动")
        return
    
    # 测试创建用户
    user_id = await test_create_user()
    if not user_id:
        logging.error("创建用户失败，停止测试")
        return
    
    # 测试编辑用户年龄
    await test_edit_user_age(user_id)
    
    # 测试编辑用户目标性别
    await test_edit_target_gender(user_id)
    
    # 测试编辑用户总结
    await test_edit_summary(user_id)
    
    logging.info("API测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 