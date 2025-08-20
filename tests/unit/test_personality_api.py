#!/usr/bin/env python3
"""
性格测试API功能验证脚本
测试完整的性格测试流程
"""

import httpx
import asyncio
import json
from typing import Dict

# API基础URL（需要根据实际运行端口调整） - 更新为新的CardGame路由
BASE_URL = "http://127.0.0.1:8001/api/v1/CardGame"

class PersonalityTestClient:
    """性格测试API客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        
    async def start_test(self, user_id: int) -> Dict:
        """开始测试"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/start",
                json={"user_id": user_id}
            )
            return response.json()
    
    async def submit_answer(self, session_id: str, question_id: str, selected_option: str) -> Dict:
        """提交答案"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/answer",
                json={
                    "session_id": session_id,
                    "question_id": question_id, 
                    "selected_option": selected_option
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    async def get_result(self, session_id: str) -> Dict:
        """获取结果"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/result/{session_id}")
            return response.json()
    
    async def get_history(self, user_id: int) -> Dict:
        """获取历史"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/history/{user_id}")
            return response.json()
    
    async def get_stats(self) -> Dict:
        """获取系统统计"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/stats")
            print(f"Status: {response.status_code}, Content: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

async def test_complete_flow():
    """测试完整的性格测试流程"""
    client = PersonalityTestClient()
    user_id = 12345
    
    print("🧪 开始测试性格测试API...")
    print("=" * 60)
    
    try:
        # 1. 检查系统状态
        print("📊 检查系统状态...")
        stats = await client.get_stats()
        print(f"系统统计: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        if not stats.get("data", {}).get("system_ready", False):
            print("❌ 系统未就绪，请先运行初始化脚本")
            return
        
        # 2. 开始测试
        print("\n🚀 开始新测试...")
        start_result = await client.start_test(user_id)
        print(f"开始测试结果: {start_result.get('status')}")
        
        if start_result.get("status") != "success":
            print(f"❌ 开始测试失败: {start_result.get('error')}")
            return
        
        session_id = start_result["data"]["session_id"]
        first_question = start_result["data"]["first_question"]
        print(f"会话ID: {session_id}")
        print(f"第一题: {first_question['question_text']}")
        
        # 3. 模拟回答16道题目（选择随机答案）
        print("\n📝 开始答题...")
        answers = ["A", "B", "C", "D", "A", "B", "C", "D", 
                  "A", "B", "C", "D", "A", "B", "C", "D"]  # 16个答案
        
        current_question_id = first_question["question_id"]
        
        for i, answer in enumerate(answers, 1):
            print(f"答题进度: {i}/16 - 题目: {current_question_id}, 选择: {answer}")
            
            submit_result = await client.submit_answer(session_id, current_question_id, answer)
            
            if submit_result.get("status") != "success":
                print(f"❌ 提交答案失败: {submit_result.get('error')}")
                return
            
            # 检查是否完成
            if submit_result["data"].get("is_completed"):
                print("✅ 测试完成！")
                break
            else:
                # 获取下一题ID
                next_question = submit_result["data"].get("next_question", {})
                current_question_id = next_question.get("question_id")
                if not current_question_id:
                    print("❌ 无法获取下一题")
                    return
        
        # 4. 获取测试结果
        print("\n🎯 获取测试结果...")
        result = await client.get_result(session_id)
        
        if result.get("status") != "success":
            print(f"❌ 获取结果失败: {result.get('error')}")
            return
        
        result_data = result["data"]["result"]
        result_card = result_data["card"]
        scores = result_data["scores"]
        
        print("🎉 测试结果:")
        print(f"人格卡片: {result_card['card_name']} ({result_card['card_id']})")
        print(f"卡片标题: {result_card['title']}")
        print(f"详细内容: {result_card['content']}")
        print(f"图片文件: {result_card['image_name']}")
        print(f"表情符号: {result_card['emoji']}")
        print(f"各类型得分: {scores}")
        
        # 5. 获取用户历史
        print("\n📚 获取测试历史...")
        history = await client.get_history(user_id)
        
        if history.get("status") == "success":
            history_data = history["data"]["history"]
            total_tests = history["data"]["total"]
            print(f"历史测试次数: {total_tests}")
            if history_data:
                print("最近测试:")
                for test in history_data[:3]:  # 显示最近3次
                    card_info = test["result_card"]
                    print(f"  - {card_info['card_name']} {card_info['emoji']} ({test['completed_at']})")
        
        print("\n✅ 完整流程测试成功！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")

async def test_api_validation():
    """测试API参数验证"""
    client = PersonalityTestClient()
    
    print("\n🔍 测试API参数验证...")
    print("-" * 40)
    
    # 测试无效的session_id
    print("测试无效session_id...")
    result = await client.submit_answer("invalid-session", "Q1", "A")
    print(f"结果: {result.get('status')} - {result.get('error', 'OK')}")
    
    # 测试无效的选项
    print("测试无效选项...")
    start_result = await client.start_test(99999)
    if start_result.get("status") == "success":
        session_id = start_result["data"]["session_id"]
        result = await client.submit_answer(session_id, "Q1", "X")  # 无效选项
        print(f"结果: {result.get('status')} - {result.get('error', 'OK')}")

async def main():
    """主函数"""
    print("🎮 性格测试API测试脚本")
    print("请确保后端服务器正在运行 (端口8001)")
    print("=" * 60)
    
    # 测试完整流程
    await test_complete_flow()
    
    # 测试参数验证
    await test_api_validation()
    
    print("\n🏁 测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 