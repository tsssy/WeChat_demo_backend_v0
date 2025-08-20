#!/usr/bin/env python3
"""
语音转文字功能测试脚本
测试各个组件是否正常工作
"""

import asyncio
import os
import tempfile
import time
from pathlib import Path

# 添加项目根目录到Python路径
import sys
sys.path.append(str(Path(__file__).parent))

async def test_audio_processor():
    """测试音频处理器"""
    print("=== 测试音频处理器 ===")
    
    try:
        from app.utils.audio_processor import audio_processor
        print("✓ 音频处理器导入成功")
        
        # 检查Whisper模型是否加载
        if audio_processor.whisper_model is not None:
            print("✓ Whisper模型加载成功")
        else:
            print("✗ Whisper模型未加载")
            return False
        
        # 检查支持的格式
        print(f"✓ 支持的音频格式: {audio_processor.supported_formats}")
        print(f"✓ 最大文件大小: {audio_processor.max_file_size / (1024*1024):.1f}MB")
        
        return True
        
    except Exception as e:
        print(f"✗ 音频处理器测试失败: {str(e)}")
        return False

async def test_voice_service():
    """测试语音转文字服务"""
    print("\n=== 测试语音转文字服务 ===")
    
    try:
        from app.services.https.VoiceToTextService import voice_to_text_service
        print("✓ 语音转文字服务导入成功")
        
        # 检查AI服务是否可用
        if voice_to_text_service.ai_service is not None:
            print("✓ AI服务连接成功")
        else:
            print("✗ AI服务连接失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ 语音转文字服务测试失败: {str(e)}")
        return False

async def test_api_routes():
    """测试API路由"""
    print("\n=== 测试API路由 ===")
    
    try:
        from app.api.v1.VoiceToText import router
        print("✓ 语音转文字API路由导入成功")
        
        # 检查路由是否注册
        routes = [route.path for route in router.routes]
        expected_routes = ["/voice/transcribe", "/voice/chat", "/voice/health"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✓ 路由 {route} 注册成功")
            else:
                print(f"✗ 路由 {route} 未找到")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ API路由测试失败: {str(e)}")
        return False

async def test_config():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    try:
        from app.config import settings
        
        print(f"✓ Whisper模型大小: {settings.WHISPER_MODEL_SIZE}")
        print(f"✓ Whisper设备: {settings.WHISPER_DEVICE}")
        print(f"✓ 最大音频文件大小: {settings.MAX_AUDIO_FILE_SIZE / (1024*1024):.1f}MB")
        print(f"✓ 支持的音频格式: {settings.SUPPORTED_AUDIO_FORMATS}")
        print(f"✓ 当前AI服务: {settings.CURRENT_AI_SERVICE}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置测试失败: {str(e)}")
        return False

async def test_whisper_model():
    """测试Whisper模型"""
    print("\n=== 测试Whisper模型 ===")
    
    try:
        import whisper
        
        # 测试模型加载
        model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
        print(f"正在加载Whisper模型: {model_size}")
        
        start_time = time.time()
        model = whisper.load_model(model_size)
        load_time = time.time() - start_time
        
        print(f"✓ Whisper模型 {model_size} 加载成功，耗时: {load_time:.2f}秒")
        
        # 测试模型信息
        print(f"✓ 模型大小: {model_size}")
        print(f"✓ 模型加载成功")
        
        return True
        
    except Exception as e:
        print(f"✗ Whisper模型测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("开始测试语音转文字功能...\n")
    
    tests = [
        test_config,
        test_whisper_model,
        test_audio_processor,
        test_voice_service,
        test_api_routes
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"测试 {test.__name__} 时发生异常: {str(e)}")
            results.append(False)
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！语音转文字功能已准备就绪。")
    else:
        print("⚠️  部分测试失败，请检查相关配置和依赖。")
    
    return passed == total

if __name__ == "__main__":
    # 设置环境变量（如果需要）
    os.environ.setdefault("WHISPER_MODEL_SIZE", "base")
    os.environ.setdefault("WHISPER_DEVICE", "cpu")
    
    # 运行测试
    success = asyncio.run(main())
    exit(0 if success else 1)
