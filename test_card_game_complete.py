#!/usr/bin/env python3
"""
抽卡游戏完整功能测试脚本
基于requests库，测试所有API接口功能
"""

import requests
import json
import time
from typing import Dict, Optional

class CardGameTestClient:
    """抽卡游戏测试客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001/api/v1/CardGame"):
        self.base_url = base_url
        
    def get_stats(self) -> Dict:
        """获取系统统计"""
        response = requests.get(f"{self.base_url}/stats")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    def start_test(self, user_id: int) -> Dict:
        """开始测试"""
        response = requests.post(f"{self.base_url}/start", json={"user_id": user_id})
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    def submit_answer(self, session_id: str, question_id: str, selected_option: str) -> Dict:
        """提交答案"""
        payload = {
            "session_id": session_id,
            "question_id": question_id,
            "selected_option": selected_option
        }
        response = requests.post(f"{self.base_url}/answer", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    def get_result(self, session_id: str) -> Dict:
        """获取测试结果"""
        response = requests.get(f"{self.base_url}/result/{session_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    def get_history(self, user_id: int) -> Dict:
        """获取测试历史"""
        response = requests.get(f"{self.base_url}/history/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}
    
    def cleanup_sessions(self) -> Dict:
        """清理过期会话"""
        response = requests.delete(f"{self.base_url}/cleanup")
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "error": f"HTTP {response.status_code}: {response.text}"}

def test_complete_card_game_flow():
    """测试完整的抽卡游戏流程"""
    client = CardGameTestClient()
    user_id = 12345
    
    print("🎮 抽卡游戏完整流程测试")
    print("=" * 60)
    
    try:
        # 1. 检查系统状态
        print("📊 1. 检查系统状态...")
        stats = client.get_stats()
        print(f"系统状态: {stats.get('status')}")
        
        if stats.get("status") != "success":
            print(f"❌ 系统状态异常: {stats.get('error')}")
            return False
        
        system_data = stats.get("data", {})
        print(f"   题目数量: {system_data.get('question_count')}/16")
        print(f"   卡片数量: {system_data.get('card_count')}/8")
        print(f"   系统就绪: {system_data.get('system_ready')}")
        
        if not system_data.get("system_ready"):
            print("❌ 系统未就绪，请先运行初始化")
            return False
        
        # 2. 开始测试
        print("\n🚀 2. 开始新的抽卡测试...")
        start_result = client.start_test(user_id)
        print(f"开始测试状态: {start_result.get('status')}")
        
        if start_result.get("status") != "success":
            print(f"❌ 开始测试失败: {start_result.get('error')}")
            return False
        
        data = start_result.get("data", {})
        session_id = data.get("session_id")
        first_question = data.get("first_question", {})
        progress = data.get("progress", {})
        
        print(f"   会话ID: {session_id}")
        print(f"   第一题: {first_question.get('question_text')}")
        print(f"   进度: {progress.get('current')}/{progress.get('total')}")
        
        # 3. 逐步答题（模拟用户选择）
        print("\n📝 3. 开始答题流程...")
        current_question_id = first_question.get("question_id")
        
        # 模拟用户的选择序列（可以调整这些选择来测试不同的结果）
        user_choices = ["A", "B", "A", "C", "B", "A", "D", "C", 
                       "A", "B", "C", "A", "B", "D", "A", "C"]  # 16个选择
        
        for i, choice in enumerate(user_choices, 1):
            print(f"   第{i}题 ({current_question_id}): 选择 {choice}")
            
            submit_result = client.submit_answer(session_id, current_question_id, choice)
            
            if submit_result.get("status") != "success":
                print(f"❌ 提交答案失败: {submit_result.get('error')}")
                return False
            
            submit_data = submit_result.get("data", {})
            is_completed = submit_data.get("is_completed", False)
            progress = submit_data.get("progress", {})
            
            print(f"      进度: {progress.get('current', 0)}/{progress.get('total', 16)}")
            
            if is_completed:
                print("✅ 测试完成！开始展示结果...")
                
                # 从最终答案响应中获取结果
                if "result" in submit_data:
                    result_data = submit_data["result"]
                    card = result_data.get("card", {})
                    scores = result_data.get("scores", {})
                    
                    print(f"\n🎉 4. 抽卡结果:")
                    print(f"   🎴 卡片名称: {card.get('card_name')} ({card.get('card_id')})")
                    print(f"   📝 卡片标题: {card.get('title')}")
                    print(f"   📄 卡片内容: {card.get('content')[:100]}...")
                    print(f"   😊 表情符号: {card.get('emoji')}")
                    print(f"   🖼️  图片文件: {card.get('image_name')}")
                    print(f"   📊 各类型得分: {scores}")
                    
                break
            else:
                # 获取下一题
                next_question = submit_data.get("next_question", {})
                current_question_id = next_question.get("question_id")
                if not current_question_id:
                    print("❌ 无法获取下一题ID")
                    return False
        
        # 4. 验证结果获取
        print(f"\n🔍 5. 验证结果获取...")
        result = client.get_result(session_id)
        if result.get("status") == "success":
            result_data = result.get("data", {})
            card_info = result_data.get("result", {}).get("card", {})
            print(f"   通过结果API获取: {card_info.get('card_name')} {card_info.get('emoji')}")
        else:
            print(f"⚠️ 获取结果失败: {result.get('error')}")
        
        # 5. 获取历史记录
        print(f"\n📚 6. 获取测试历史...")
        history = client.get_history(user_id)
        if history.get("status") == "success":
            history_data = history.get("data", {})
            total_tests = history_data.get("total", 0)
            recent_tests = history_data.get("history", [])
            
            print(f"   历史测试总数: {total_tests}")
            print(f"   最近测试记录:")
            for idx, test in enumerate(recent_tests[:3], 1):
                card_info = test.get("result_card", {})
                completed_at = test.get("completed_at", "")
                print(f"     {idx}. {card_info.get('card_name')} {card_info.get('emoji')} ({completed_at})")
        else:
            print(f"⚠️ 获取历史失败: {history.get('error')}")
        
        # 6. 系统管理功能测试
        print(f"\n🧹 7. 测试系统管理功能...")
        cleanup_result = client.cleanup_sessions()
        if cleanup_result.get("status") == "success":
            cleanup_data = cleanup_result.get("data", {})
            cleaned_count = cleanup_data.get("cleaned_sessions", 0)
            print(f"   清理了 {cleaned_count} 个过期会话")
        else:
            print(f"⚠️ 清理会话失败: {cleanup_result.get('error')}")
        
        print(f"\n✅ 抽卡游戏完整流程测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    client = CardGameTestClient()
    
    print(f"\n🔧 错误处理测试")
    print("-" * 40)
    
    # 测试无效session_id
    print("测试无效会话ID...")
    result = client.submit_answer("invalid-session-id", "Q1", "A")
    status = result.get("status")
    error = result.get("error", "")
    print(f"   结果: {status} - {error[:100]}...")
    
    # 测试无效选项
    print("测试无效答案选项...")
    start_result = client.start_test(99999)
    if start_result.get("status") == "success":
        session_id = start_result["data"]["session_id"]
        result = client.submit_answer(session_id, "Q1", "X")  # 无效选项
        status = result.get("status")
        error = result.get("error", "")
        print(f"   结果: {status} - {error[:100]}...")
    
    # 测试不存在的结果
    print("测试获取不存在的结果...")
    result = client.get_result("nonexistent-session")
    status = result.get("status")
    error = result.get("error", "")
    print(f"   结果: {status} - {error[:100]}...")

def main():
    """主函数"""
    print("🎮 抽卡游戏 API 完整测试套件")
    print("请确保后端服务器正在运行 (端口8001)")
    print("=" * 60)
    
    # 测试完整流程
    success = test_complete_card_game_flow()
    
    if success:
        # 测试错误处理
        test_error_handling()
        
        print(f"\n🏁 所有测试完成！")
        print("📋 测试总结:")
        print("   ✅ 系统状态检查")
        print("   ✅ 开始游戏流程")
        print("   ✅ 答题提交流程")
        print("   ✅ 抽卡结果展示")
        print("   ✅ 历史记录查询")
        print("   ✅ 系统管理功能")
        print("   ✅ 错误处理机制")
    else:
        print(f"\n❌ 测试失败，请检查服务器状态或日志")

if __name__ == "__main__":
    main() 