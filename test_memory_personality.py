#!/usr/bin/env python3
"""
性格测试内存优先模式验证脚本
测试内存操作和定期同步功能
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
ROOT_PATH = Path(__file__).resolve().parent
sys.path.append(str(ROOT_PATH))

from app.services.https.PersonalityTestManager import PersonalityTestManager
from app.core.database import Database
from app.utils.my_logger import MyLogger

# 创建logger实例
logger = MyLogger("test_memory_personality")

async def test_memory_operations():
    """测试内存操作"""
    print("🧪 测试性格测试内存优先模式...")
    print("=" * 60)
    
    try:
        # 连接数据库
        await Database.connect()
        
        # 初始化PersonalityTestManager
        print("📦 初始化PersonalityTestManager...")
        manager = PersonalityTestManager()
        await manager.initialize_from_database()
        
        # 检查内存数据加载情况
        print(f"✅ 题目加载: {len(manager.questions)}/16")
        print(f"✅ 卡片加载: {len(manager.cards)}/8")
        print(f"✅ 测试会话: {len(manager.test_sessions)}")
        print(f"✅ 用户历史: {len(manager.user_histories)}")
        
        # 测试开始新测试（纯内存操作）
        print("\n🚀 测试开始新测试...")
        user_id = 88888
        start_result = await manager.start_new_test(user_id)
        
        if start_result:
            session_id = start_result["session_id"]
            print(f"✅ 测试会话创建成功: {session_id}")
            print(f"✅ 第一题: {start_result['first_question']['question_text']}")
            
            # 测试内存中的会话数据
            session_data = manager.test_sessions.get(session_id)
            if session_data:
                print(f"✅ 内存中会话状态: 已创建，用户ID: {session_data['user_id']}")
            
            # 模拟回答几道题目
            print("\n📝 测试答题流程...")
            answers = ["A", "B", "C", "D", "A"]  # 前5题的答案
            
            current_question_id = "Q1"
            for i, answer in enumerate(answers):
                print(f"答题: {current_question_id} -> {answer}")
                
                submit_result = await manager.submit_answer(session_id, current_question_id, answer)
                
                if submit_result:
                    if submit_result.get("is_completed"):
                        print("✅ 测试完成！")
                        break
                    else:
                        next_question = submit_result.get("next_question", {})
                        current_question_id = next_question.get("question_id")
                        progress = submit_result.get("progress", {})
                        print(f"进度: {progress['current']}/{progress['total']}")
                else:
                    print("❌ 提交答案失败")
                    break
            
            # 检查内存中的答案记录
            session_data = manager.test_sessions.get(session_id)
            if session_data:
                answers_count = len(session_data.get("answers", []))
                print(f"✅ 内存中答案记录: {answers_count} 条")
            
            # 测试系统统计（从内存读取）
            print("\n📊 测试系统统计...")
            stats = await manager.get_system_stats()
            print(f"系统状态: {stats}")
            
            # 测试保存到数据库
            print("\n💾 测试保存到数据库...")
            save_success = await manager.save_to_database(session_id)
            if save_success:
                print("✅ 数据库保存成功")
            else:
                print("❌ 数据库保存失败")
            
            # 验证数据库中的数据
            print("\n🔍 验证数据库同步...")
            db_session = await Database.find_one("personality_test_records", {"session_id": session_id})
            if db_session:
                print(f"✅ 数据库中找到会话: {db_session['session_id']}")
                print(f"✅ 数据库答案数量: {len(db_session.get('answers', []))}")
            else:
                print("❌ 数据库中未找到会话")
            
        else:
            print("❌ 创建测试会话失败")
        
        print("\n🎉 内存优先模式测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

async def test_multiple_instances():
    """测试单例模式"""
    print("\n🔄 测试单例模式...")
    
    # 创建多个实例，应该是同一个对象
    manager1 = PersonalityTestManager()
    manager2 = PersonalityTestManager()
    
    if manager1 is manager2:
        print("✅ 单例模式工作正常")
    else:
        print("❌ 单例模式失效")
    
    # 测试内存数据共享
    if len(manager1.questions) == len(manager2.questions):
        print("✅ 内存数据共享正常")
    else:
        print("❌ 内存数据不一致")

async def main():
    """主函数"""
    print("🎮 性格测试内存优先模式验证")
    print("请确保已运行数据初始化脚本")
    print("=" * 60)
    
    await test_memory_operations()
    await test_multiple_instances()
    
    print("\n🏁 所有测试完成！")

if __name__ == "__main__":
    asyncio.run(main()) 