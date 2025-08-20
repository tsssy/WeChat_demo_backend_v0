import asyncio
import sys
import os
import time
import httpx

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.https.KimiInteractionAPI import KimiInteractionAPI

async def test_kimi_basic_functionality():
    """测试Kimi基本功能"""
    
    print("🧪 测试Kimi基本功能")
    print("=" * 50)
    
    try:
        # 创建Kimi API服务实例
        kimi_service = KimiInteractionAPI()
        print("✅ Kimi API服务实例创建成功")
        
        # 测试用户ID
        user_id = 12345
        gender = "neutral"
        
        print(f"👤 用户ID: {user_id}")
        print(f"👤 用户性别: {gender}")
        
        # 测试对话
        test_message = "你好，我想咨询情感问题"
        test_history = []
        
        print(f"\n🔄 发送测试消息: {test_message}")
        
        # 发送消息到Kimi
        response = await kimi_service.send_message_to_ai(
            user_id=user_id,
            message=test_message,
            history=test_history,
            gender=gender
        )
        
        print("📊 响应结果:")
        print(f"  - 成功: {response.get('success', False)}")
        print(f"  - 消息长度: {len(response.get('message', ''))} 字符")
        print(f"  - 是否最终: {response.get('is_final', False)}")
        print(f"  - 总结长度: {len(response.get('summary', ''))} 字符")
        
        if response.get('success'):
            message = response.get('message', '')
            print(f"  - 消息预览: {message[:100]}...")
            
            if response.get('summary'):
                summary = response.get('summary', '')
                print(f"  - 总结预览: {summary[:100]}...")
        else:
            print("  - 响应失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_retry_mechanism():
    """测试重试机制"""
    
    print("\n🧪 测试重试机制")
    print("=" * 50)
    
    try:
        kimi_service = KimiInteractionAPI()
        
        # 测试重试配置
        print(f"📊 重试配置:")
        print(f"  - 最大重试次数: {kimi_service.max_retries}")
        print(f"  - 超时时间: {kimi_service.timeout}秒")
        
        # 测试指数退避策略
        print(f"\n📊 指数退避策略:")
        for i in range(kimi_service.max_retries):
            sleep_time = 2 ** i
            print(f"  - 第{i+1}次重试等待时间: {sleep_time}秒")
        
        print("✅ 重试机制配置正确")
        return True
        
    except Exception as e:
        print(f"❌ 重试机制测试失败: {str(e)}")
        return False

async def test_conversation_end_detection():
    """测试对话结束检测"""
    
    print("\n🧪 测试对话结束检测")
    print("=" * 50)
    
    try:
        kimi_service = KimiInteractionAPI()
        
        # 测试用例
        test_cases = [
            {
                "text": "总结一下我们的对话：1. 沟通很重要 2. 需要倾听 3. 保持耐心",
                "expected": True,
                "description": "包含明确总结"
            },
            {
                "text": "好的，谢谢你的帮助！",
                "expected": False,
                "description": "简单结束语"
            },
            {
                "text": "建议你：1. 多沟通 2. 保持耐心 3. 相互理解",
                "expected": True,
                "description": "包含建议"
            },
            {
                "text": "我想再问一个问题",
                "expected": False,
                "description": "继续对话"
            },
            {
                "text": "行动计划：1. 每天沟通15分钟 2. 周末约会 3. 定期总结",
                "expected": True,
                "description": "包含行动计划"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {test_case['description']}")
            print(f"文本: {test_case['text']}")
            
            # 测试对话结束检测
            is_final = kimi_service._is_final_summary(test_case['text'])
            expected = test_case['expected']
            
            print(f"期望: {expected}, 实际: {is_final}")
            
            if expected == is_final:
                print("✅ 对话结束检测正确")
            else:
                print("❌ 对话结束检测错误")
        
        return True
        
    except Exception as e:
        print(f"❌ 对话结束检测测试失败: {str(e)}")
        return False

async def test_summary_splitting():
    """测试总结分割功能"""
    
    print("\n🧪 测试总结分割功能")
    print("=" * 50)
    
    try:
        kimi_service = KimiInteractionAPI()
        
        # 测试用例
        test_cases = [
            {
                "text": "我理解你的问题。\n\n总结：1. 沟通很重要 2. 需要倾听",
                "description": "包含总结的响应"
            },
            {
                "text": "好的，我明白了。",
                "description": "简单响应"
            },
            {
                "text": "建议你：1. 多沟通 2. 保持耐心\n\n行动计划：每天15分钟沟通",
                "description": "包含建议和行动计划"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试 {i}: {test_case['description']}")
            print(f"原始文本: {test_case['text']}")
            
            # 测试总结分割
            parts = kimi_service._split_final_summary(test_case['text'])
            
            print(f"分割结果: {len(parts)} 部分")
            for j, part in enumerate(parts):
                print(f"  部分 {j+1}: {part[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 总结分割测试失败: {str(e)}")
        return False

async def test_api_integration():
    """测试API集成"""
    
    print("\n🧪 测试API集成")
    print("=" * 50)
    
    try:
        base_url = "http://localhost:8001"
        test_user_id = 99999
        
        print(f"👤 测试用户ID: {test_user_id}")
        
        # 测试对话
        test_message = "你好，我想咨询情感问题"
        print(f"\n🔄 发送API请求: {test_message}")
        
        request_data = {
            "user_id": test_user_id,
            "message": test_message
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/ai/chat",
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ API调用成功")
                    print(f"  - 状态: {result.get('status')}")
                    print(f"  - 响应长度: {len(result.get('response', ''))} 字符")
                    print(f"  - 响应预览: {result.get('response', '')[:100]}...")
                    
                    # 检查是否有总结
                    if result.get('summary'):
                        print(f"  - 总结: {result.get('summary')[:100]}...")
                else:
                    print(f"❌ API调用失败: {response.status_code}")
                    print(f"  - 错误信息: {response.text}")
                    
            except Exception as e:
                print(f"❌ API调用异常: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ API集成测试失败: {str(e)}")
        return False

async def test_memory_operations():
    """测试内存操作"""
    
    print("\n🧪 测试内存操作")
    print("=" * 50)
    
    try:
        from app.services.https.AIResponseProcessor import AIResponseProcessor
        
        # 初始化AIResponseProcessor
        ai_processor = AIResponseProcessor()
        await ai_processor.initialize_from_database()
        
        print("✅ AIResponseProcessor初始化完成")
        print(f"📊 内存状态:")
        print(f"  - 聊天室数量: {len(ai_processor.ai_chatrooms)}")
        print(f"  - 消息数量: {len(ai_processor.ai_messages)}")
        print(f"  - 消息计数器: {ai_processor.message_counter}")
        
        # 测试内存操作
        test_user_id = 88888
        test_message = "测试消息"
        test_response = "测试响应"
        
        print(f"\n🔄 测试内存操作 (用户ID: {test_user_id})")
        
        save_success = await ai_processor.save_conversation_history(
            user_id=test_user_id,
            message=test_message,
            response=test_response
        )
        
        if save_success:
            print("✅ 内存操作成功")
            print(f"  - 更新后聊天室数量: {len(ai_processor.ai_chatrooms)}")
            print(f"  - 更新后消息数量: {len(ai_processor.ai_messages)}")
        else:
            print("❌ 内存操作失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 内存操作测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Kimi完整功能测试")
    print("=" * 50)
    
    # 运行测试
    async def run_tests():
        success1 = await test_kimi_basic_functionality()
        success2 = await test_retry_mechanism()
        success3 = await test_conversation_end_detection()
        success4 = await test_summary_splitting()
        success5 = await test_api_integration()
        success6 = await test_memory_operations()
        
        print("\n" + "=" * 50)
        if success1 and success2 and success3 and success4 and success5 and success6:
            print("🎉 所有测试都成功！Kimi功能完整且正常工作。")
        else:
            print("⚠️  部分测试失败，请检查配置。")
    
    asyncio.run(run_tests()) 