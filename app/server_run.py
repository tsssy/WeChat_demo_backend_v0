#Daniel 到此一游

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from contextlib import asynccontextmanager
import sys
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件
import json
import time
import asyncio
from fastapi.websockets import WebSocketDisconnect # 导入 WebSocketDisconnect

ROOT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_PATH))

from app.api.v1.api import api_router
from app.ws import all_ws_routers
from app.config import settings
from app.core.database import Database
from app.utils.my_logger import MyLogger
from app.utils.singleton_status import SingletonStatusReporter
from app.services.https.UserManagement import UserManagement
from app.services.https.MatchManager import MatchManager
from app.services.https.ChatroomManager import ChatroomManager
from app.services.https.N8nWebhookManager import N8nWebhookManager
from app.services.https.DataIntegrity import DataIntegrity
from app.services.https.AIResponseProcessor import AIResponseProcessor

logger = MyLogger("server")

# ===== 性格测试数据初始化相关 - 新增抽卡游戏数据 =====
from datetime import datetime

# 16道性格测试题目数据 - 抽卡游戏题库
PERSONALITY_QUESTIONS = [
    {
        "question_id": "Q1",
        "question_text": "如果周末一个人待着，你最想做的是？",
        "options": [
            {"option": "A", "text": "开启一场即兴小旅行", "personality_type": "A1"},
            {"option": "B", "text": "实践一个一直想做的点子项目", "personality_type": "A2"},
            {"option": "C", "text": "去熟悉的地方静静坐一下午", "personality_type": "A3"},
            {"option": "D", "text": "躺在床上听歌，想象不可能的恋爱剧情", "personality_type": "A4"}
        ]
    },
    {
        "question_id": "Q2",
        "question_text": "面对新关系，你最自然的状态是？",
        "options": [
            {"option": "A", "text": "自然而然地交流，不主动也不抗拒", "personality_type": "A3"},
            {"option": "B", "text": "一旦确定好感就会主动出击", "personality_type": "A2"},
            {"option": "C", "text": "暗暗观察，等自己确认安全再靠近", "personality_type": "A6"},
            {"option": "D", "text": "如果对方像阳光一样有吸引力，我会靠近", "personality_type": "A8"}
        ]
    },
    {
        "question_id": "Q3",
        "question_text": "在你理想的感情中，对方最重要的特质是？",
        "options": [
            {"option": "A", "text": "能理解我不需要被拯救", "personality_type": "A1"},
            {"option": "B", "text": "愿意陪我一起变得更好", "personality_type": "A8"},
            {"option": "C", "text": "踏实可靠，稳定长期", "personality_type": "A5"},
            {"option": "D", "text": "懂得共情，不需要出口的情结", "personality_type": "A6"}
        ]
    },
    {
        "question_id": "Q4",
        "question_text": "你面对陌生社交场合时，最常见的反应是？",
        "options": [
            {"option": "A", "text": "带着礼貌微笑，但保持一定距离", "personality_type": "A3"},
            {"option": "B", "text": "主动寒暄，迅速破冰", "personality_type": "A2"},
            {"option": "C", "text": "选择角落，静静观察人群", "personality_type": "A7"},
            {"option": "D", "text": "观察细节，寻找有深度的人交流", "personality_type": "A6"}
        ]
    },
    {
        "question_id": "Q5",
        "question_text": "如果你送喜欢的人一份礼物，你更可能选：",
        "options": [
            {"option": "A", "text": "一起共同回忆的记录，比如手写信或拼图", "personality_type": "A6"},
            {"option": "B", "text": "一个她旅行中提过却没买的纪念品", "personality_type": "A1"},
            {"option": "C", "text": "一张照片，画面是很久下的绘景", "personality_type": "A4"},
            {"option": "D", "text": "一把保温壶或护手霜，实用又贴心", "personality_type": "A5"}
        ]
    },
    {
        "question_id": "Q6",
        "question_text": "爱情对你来说，更像什么？",
        "options": [
            {"option": "A", "text": "一场自由灵魂之间的同步舞蹈", "personality_type": "A1"},
            {"option": "B", "text": "彼此照亮和扶持的成长旅程", "personality_type": "A8"},
            {"option": "C", "text": "安全、稳定、温暖的家园", "personality_type": "A5"},
            {"option": "D", "text": "静静陪伴的老友关系，不用太多话", "personality_type": "A3"}
        ]
    },
    {
        "question_id": "Q7",
        "question_text": "你眼中的爱情信念是：",
        "options": [
            {"option": "A", "text": "我们彼此点燃，不互相消耗", "personality_type": "A2"},
            {"option": "B", "text": "彼此能一起创造浪漫，哪怕有点不现实", "personality_type": "A4"},
            {"option": "C", "text": "最动人的感情藏在日常细节里", "personality_type": "A5"},
            {"option": "D", "text": "爱是要先学会与自己和平共处", "personality_type": "A7"}
        ]
    },
    {
        "question_id": "Q8",
        "question_text": "你面对情绪冲突时，通常会？",
        "options": [
            {"option": "A", "text": "主动沟通，不希望误会留太久", "personality_type": "A2"},
            {"option": "B", "text": "暂时独处，等自己冷静", "personality_type": "A7"},
            {"option": "C", "text": "一口沉默，但会用文字或行动表达", "personality_type": "A3"},
            {"option": "D", "text": "理性分析，摸索情绪背后的原因", "personality_type": "A6"}
        ]
    },
    {
        "question_id": "Q9",
        "question_text": "以下哪个描述最接近你？",
        "options": [
            {"option": "A", "text": "思维跳跃，喜欢新奇", "personality_type": "A1"},
            {"option": "B", "text": "热血积极，有点容易着急", "personality_type": "A2"},
            {"option": "C", "text": "情绪细腻，有些慢热", "personality_type": "A3"},
            {"option": "D", "text": "梦想丰富，常常发呆", "personality_type": "A4"}
        ]
    },
    {
        "question_id": "Q10",
        "question_text": "你与人互动中，最在意的是什么？",
        "options": [
            {"option": "A", "text": "能不能一起做很多有趣的事", "personality_type": "A1"},
            {"option": "B", "text": "对方是否真诚，直接", "personality_type": "A2"},
            {"option": "C", "text": "安不安全，值不值得信任", "personality_type": "A5"},
            {"option": "D", "text": "对方能不能引发你内心的话题", "personality_type": "A4"}
        ]
    },
    {
        "question_id": "Q11",
        "question_text": "你更喜欢哪种生活方式？",
        "options": [
            {"option": "A", "text": "每天有计划，有节奏", "personality_type": "A5"},
            {"option": "B", "text": "边走边看，不被框住", "personality_type": "A1"},
            {"option": "C", "text": "清晨阳光，晚上自我反思", "personality_type": "A8"},
            {"option": "D", "text": "自然社交，晚上独处", "personality_type": "A7"}
        ]
    },
    {
        "question_id": "Q12",
        "question_text": "如果你写一本关于自己的书，更倾像？",
        "options": [
            {"option": "A", "text": "一本旅行日记，风景是主角", "personality_type": "A1"},
            {"option": "B", "text": "一本热血成长故事", "personality_type": "A2"},
            {"option": "C", "text": "一本散文诗集", "personality_type": "A4"},
            {"option": "D", "text": "一本慢慢读懂的心事集", "personality_type": "A6"}
        ]
    },
    {
        "question_id": "Q13",
        "question_text": "你在恋爱中最害怕什么？",
        "options": [
            {"option": "A", "text": "被控制，失去空间", "personality_type": "A1"},
            {"option": "B", "text": "对方冷漠或被彻底回应", "personality_type": "A2"},
            {"option": "C", "text": "太快的热情后迅速流远", "personality_type": "A5"},
            {"option": "D", "text": "对方无法理解你的情绪语言", "personality_type": "A6"}
        ]
    },
    {
        "question_id": "Q14",
        "question_text": "如果生活变得一成不变，你会？",
        "options": [
            {"option": "A", "text": "制造变化，主动突破", "personality_type": "A8"},
            {"option": "B", "text": "暂时接受，寻找内部成长", "personality_type": "A5"},
            {"option": "C", "text": "逃到别的地方换个节奏", "personality_type": "A1"},
            {"option": "D", "text": "用创想和创作丰富内部现实", "personality_type": "A4"}
        ]
    },
    {
        "question_id": "Q15",
        "question_text": "你如何描述你自己？",
        "options": [
            {"option": "A", "text": "乐观积极，喜欢阳光", "personality_type": "A8"},
            {"option": "B", "text": "稳重踏实，值得依靠", "personality_type": "A5"},
            {"option": "C", "text": "想法很多，不喜欢平庸", "personality_type": "A4"},
            {"option": "D", "text": "有点神秘，不容易被理解", "personality_type": "A7"}
        ]
    },
    {
        "question_id": "Q16",
        "question_text": "如果必须选择一个角色，你更愿做？",
        "options": [
            {"option": "A", "text": "追风的流浪者", "personality_type": "A1"},
            {"option": "B", "text": "持剑前行的行动者", "personality_type": "A2"},
            {"option": "C", "text": "倾听与守护的伴侣", "personality_type": "A5"},
            {"option": "D", "text": "写信给宇宙的梦中人", "personality_type": "A6"}
        ]
    }
]

# 8张人格卡片数据 - 抽卡游戏卡池
PERSONALITY_CARDS = [
    {
        "card_id": "A1",
        "card_name": "风之旅人",
        "title": "你是风的旅人，自由、不羁，像山谷中穿梭的灵魂。",
        "content": "你热爱思考，也擅长沟通。你讨厌束缚与黏腻，追求独立灵魂的双向靠近。你要找的人，是那个愿意与你同行，而不是牵绊你步伐的人。",
        "emoji": "🌀",
        "image_name": "a1.jpg",
        "visual_style": {
            "keywords": ["青年", "山谷中迎风站立", "风蚀衣角", "手持折扇或纸鹤"],
            "style": "极简线条 + 淡蓝调 + 透明感插画"
        }
    },
    {
        "card_id": "A2",
        "card_name": "烈焰信徒",
        "title": "你是烈焰中的信徒，热情如火，却带着敬意。",
        "content": "你用行动表达情意，坦率而专注，不撒娇哄骗，更不会玩暧昧。你在寻找那个能直接你全部热度的人。",
        "emoji": "🔥",
        "image_name": "a2.jpg",
        "visual_style": {
            "keywords": ["男性斗篷", "夜色中独行", "背后火光"],
            "style": "深红与橘调"
        }
    },
    {
        "card_id": "A3",
        "card_name": "静水之眼",
        "title": "你是深水的眼眸，表面平静，心却波澜壮阔。",
        "content": "你不善表达，却极具深情。你在沉默中等待那个能懂你跳频率的人。真正的连接，不必多言。",
        "emoji": "💧",
        "image_name": "a3.jpg",
        "visual_style": {
            "keywords": ["码头边沉思的青年", "星空湖水", "倒影成双"],
            "style": "夜蓝调，安静细腻，冷暖光影对比"
        }
    },
    {
        "card_id": "A4",
        "card_name": "星尘拾梦人",
        "title": "你是拾捡星星的人，怀擅浪漫，也有真实。",
        "content": "你相信奇迹，相信值得，相信某种\"只属于彼此的瞬间\"。你是现实中的梦中人，你寻找的，是那个愿意与你共建星辰宇宙的人。",
        "emoji": "⭐",
        "image_name": "a4.jpg",
        "visual_style": {
            "keywords": ["仰望星空的青年", "手中漂浮星点", "粉蓝调"],
            "style": "梦幻粒子感，星云背景，童话式笔触"
        }
    },
    {
        "card_id": "A5",
        "card_name": "原野守望者",
        "title": "你是原野的守望者，不多言，却深情如山。",
        "content": "你不急不躁，慢慢靠近，也慢慢扎根。你把信任看得比热情更珍贵，你愿意陪一个人走很久很远的路。",
        "emoji": "🌾",
        "image_name": "a5.jpg",
        "visual_style": {
            "keywords": ["立于黄昏草原的青年", "望远姿态", "逆光"],
            "style": "暖色调写实插画，层次分明，秋意氛围"
        }
    },
    {
        "card_id": "A6",
        "card_name": "沉思诗者",
        "title": "你是沉思的记录者，在细节中感受宇宙的倒影。",
        "content": "你习惯用沉默表达复杂的思绪，善于感知却不擅易懂。你希望深度的灵魂对话，不需要被打扰的共鸣，是无需翻译的语言。",
        "emoji": "📖",
        "image_name": "a6.jpg",
        "visual_style": {
            "keywords": ["烛光下写字的男人", "古书", "墨迹笔触"],
            "style": "复古油画风，黄色暖调，带有书卷气息"
        }
    },
    {
        "card_id": "A7",
        "card_name": "月下旅者",
        "title": "你是月影下的独行者，安静但不孤单。",
        "content": "你不是怕亲密，只是怕失真。你在等待那个能与自己并肩而不侵入的人。那个人要先懂得与你共享宁静。",
        "emoji": "🌙",
        "image_name": "a7.jpg",
        "visual_style": {
            "keywords": ["黑夜街巷中缓步的青年", "月光投影"],
            "style": "黑白灰主调，一抹银光，细腻手绘风"
        }
    },
    {
        "card_id": "A8",
        "card_name": "晨光梦想家",
        "title": "你是晨光中的梦想家，带着理想的光芒前行。",
        "content": "你相信爱是共同成长的旅程，也相信乐观和探索本身就值得被爱。你寻找的，是那个愿意陪你走向更好未来的人。",
        "emoji": "⭐",
        "image_name": "a8.jpg",
        "visual_style": {
            "keywords": ["清晨跑步的青年", "向日美日", "刘海"],
            "style": "明亮黄调，治愈系漫画风格或极简风"
        }
    }
]

async def init_personality_data():
    """
    初始化性格测试数据到数据库
    包含16道测试题目和8张人格卡片
    - 这是新增的抽卡游戏功能的基础数据
    """
    try:
        logger.info("🎮 开始初始化性格测试数据（抽卡游戏数据）...")
        
        # 检查数据完整性 - 避免重复插入同时确保数据完整
        existing_questions = await Database.get_collection("personality_questions").count_documents({})
        existing_cards = await Database.get_collection("personality_cards").count_documents({})
        
        logger.info(f"🎮 现有题目数量: {existing_questions}, 现有卡片数量: {existing_cards}")
        
        # 精确检查题目数据完整性 - 检查是否有完整的16道题目
        if existing_questions != 16:
            if existing_questions > 0:
                logger.warning(f"🎮 发现不完整的题目数据({existing_questions}/16)，将清理后重新导入")
                # 清理不完整的数据
                await Database.get_collection("personality_questions").delete_many({})
                logger.info("🎮 已清理不完整的题目数据")
            else:
                logger.info("🎮 未发现题目数据，开始全新导入")
            logger.info("🎮 开始导入16道测试题目...")
            try:
                # 创建题目数据副本并添加创建时间戳（避免修改原始数据）
                questions_to_insert = []
                for question in PERSONALITY_QUESTIONS:
                    question_copy = question.copy()
                    question_copy["created_at"] = datetime.now()
                    questions_to_insert.append(question_copy)
                
                # 批量插入题目数据到MongoDB
                result = await Database.insert_many("personality_questions", questions_to_insert)
                if len(result) == len(PERSONALITY_QUESTIONS):
                    logger.info("✅ 题目数据导入成功")
                else:
                    logger.error("❌ 题目数据导入不完整")
                    return False
            except Exception as e:
                logger.error(f"❌ 题目数据导入失败: {e}")
                return False
        else:
            logger.info("🎮 题目数据完整(16/16)，跳过导入")
        
        # 精确检查卡片数据完整性 - 检查是否有完整的8张卡片
        if existing_cards != 8:
            if existing_cards > 0:
                logger.warning(f"🎮 发现不完整的卡片数据({existing_cards}/8)，将清理后重新导入")
                # 清理不完整的数据
                await Database.get_collection("personality_cards").delete_many({})
                logger.info("🎮 已清理不完整的卡片数据")
            else:
                logger.info("🎮 未发现卡片数据，开始全新导入")
            logger.info("🎮 开始导入8张人格卡片...")
            try:
                # 创建卡片数据副本并添加创建时间戳（避免修改原始数据）
                cards_to_insert = []
                for card in PERSONALITY_CARDS:
                    card_copy = card.copy()
                    # 深拷贝visual_style字典
                    if "visual_style" in card_copy:
                        card_copy["visual_style"] = card_copy["visual_style"].copy()
                    card_copy["created_at"] = datetime.now()
                    cards_to_insert.append(card_copy)
                
                # 批量插入卡片数据到MongoDB
                result = await Database.insert_many("personality_cards", cards_to_insert)
                if len(result) == len(PERSONALITY_CARDS):
                    logger.info("✅ 卡片数据导入成功")
                else:
                    logger.error("❌ 卡片数据导入不完整")
                    return False
            except Exception as e:
                logger.error(f"❌ 卡片数据导入失败: {e}")
                return False
        else:
            logger.info("🎮 卡片数据完整(8/8)，跳过导入")
        
        # 验证数据完整性
        final_question_count = await Database.get_collection("personality_questions").count_documents({})
        final_card_count = await Database.get_collection("personality_cards").count_documents({})
        
        logger.info(f"🎮 最终数据统计 - 题目: {final_question_count}/16, 卡片: {final_card_count}/8")
        
        if final_question_count == 16 and final_card_count == 8:
            logger.info("🎉 性格测试数据初始化完成！抽卡游戏已就绪")
            return True
        else:
            logger.error("❌ 抽卡游戏数据初始化不完整")
            return False
            
    except Exception as e:
        logger.error(f"❌ 初始化抽卡游戏数据异常: {e}", exc_info=True)
        return False
# ===== 性格测试数据初始化相关结束 =====

# 全局变量用于控制自动保存任务
auto_save_task = None

async def auto_save_to_database():
    """
    每10秒自动保存所有单例实例到数据库的后台任务
    """
    global auto_save_task
    logger.info("启动自动保存任务，每10秒保存一次所有单例数据到数据库")
    
    while True:
        try:
            await asyncio.sleep(10)  # 等待10秒
            
            logger.info("🔄 开始执行自动保存...")
            start_time = time.time()
            
            # 执行数据完备性检查（在保存前清理无效数据）
            try:
                logger.info("🔍 开始数据完备性检查...")
                data_integrity = DataIntegrity()
                integrity_result = await data_integrity.run_integrity_check()
                
                if integrity_result["success"]:
                    logger.info(f"✅ 数据完备性检查完成: {integrity_result['checks_completed']}/{integrity_result['total_checks']} 项检查通过")
                else:
                    logger.warning(f"⚠️ 数据完备性检查部分失败: {integrity_result['checks_completed']}/{integrity_result['total_checks']} 项检查通过")
                    if integrity_result["errors"]:
                        for error in integrity_result["errors"]:
                            logger.warning(f"⚠️ 完备性检查错误: {error}")
            except Exception as e:
                logger.error(f"❌ 数据完备性检查失败: {e}")
            
            # 保存UserManagement数据
            try:
                user_manager = UserManagement()
                user_save_success = await user_manager.save_to_database()  # 保存所有用户
                if user_save_success:
                    logger.info("✅ UserManagement数据保存成功")
                else:
                    logger.warning("⚠️ UserManagement数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ UserManagement数据保存失败: {e}")
            
            # 保存MatchManager数据
            try:
                match_manager = MatchManager()
                match_save_success = await match_manager.save_to_database()  # 保存所有匹配
                if match_save_success:
                    logger.info("✅ MatchManager数据保存成功")
                else:
                    logger.warning("⚠️ MatchManager数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ MatchManager数据保存失败: {e}")
            
            # 保存ChatroomManager数据
            try:
                chatroom_manager = ChatroomManager()
                chatroom_save_success = await chatroom_manager.save_chatroom_history()  # 保存所有聊天室历史
                if chatroom_save_success:
                    logger.info("✅ ChatroomManager数据保存成功")
                else:
                    logger.warning("⚠️ ChatroomManager数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ ChatroomManager数据保存失败: {e}")
            
            # 保存AIResponseProcessor数据
            try:
                ai_processor = AIResponseProcessor()
                ai_save_success = await ai_processor.save_to_database()  # 保存AI聊天数据到数据库
                if ai_save_success:
                    logger.info("✅ AIResponseProcessor数据保存成功")
                else:
                    logger.warning("⚠️ AIResponseProcessor数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ AIResponseProcessor数据保存失败: {e}")
            
            # 保存PersonalityTestManager数据
            try:
                from app.services.https.PersonalityTestManager import PersonalityTestManager
                personality_manager = PersonalityTestManager()
                personality_save_success = await personality_manager.save_to_database()  # 保存性格测试数据到数据库
                if personality_save_success:
                    logger.info("✅ PersonalityTestManager数据保存成功")
                else:
                    logger.warning("⚠️ PersonalityTestManager数据保存部分失败")
            except Exception as e:
                logger.error(f"❌ PersonalityTestManager数据保存失败: {e}")
            
            elapsed_time = time.time() - start_time
            logger.info(f"🔄 自动保存完成，耗时: {elapsed_time:.3f}秒")
            
        except asyncio.CancelledError:
            logger.info("自动保存任务被取消")
            break
        except Exception as e:
            logger.error(f"自动保存任务发生错误: {e}")
            # 发生错误时等待一段时间再继续
            await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global auto_save_task
    
    # 启动时连接数据库
    logger.info("正在连接数据库...")
    try:
        await Database.connect()  # 恢复数据库连接
        logger.info("数据库连接成功")
        
        # 初始化性格测试数据（抽卡游戏基础数据） - 新增功能
        logger.info("🎮 正在初始化抽卡游戏基础数据...")
        personality_data_success = await init_personality_data()
        if personality_data_success:
            logger.info("✅ 抽卡游戏基础数据初始化成功")
        else:
            logger.warning("⚠️ 抽卡游戏基础数据初始化失败，但不影响其他功能")
        
        # 初始化UserManagement缓存
        logger.info("正在初始化UserManagement缓存...")
        user_manager = UserManagement()
        await user_manager.initialize_from_database()
        logger.info("UserManagement缓存初始化完成")
        
        # 初始化MatchManager缓存
        logger.info("正在初始化MatchManager缓存...")
        match_manager = MatchManager()
        await match_manager.construct()
        logger.info("MatchManager缓存初始化完成")
        
        # 初始化ChatroomManager缓存
        logger.info("正在初始化ChatroomManager缓存...")
        chatroom_manager = ChatroomManager()
        construct_success = await chatroom_manager.construct()  # 从数据库加载聊天室数据
        
        # 检查初始化状态
        if construct_success:
            logger.info(f"ChatroomManager缓存初始化完成 - 加载了 {len(chatroom_manager.chatrooms)} 个聊天室")
            logger.info(f"ChatroomManager可用的聊天室ID: {list(chatroom_manager.chatrooms.keys())}")
        else:
            logger.error("ChatroomManager缓存初始化失败")
            
        logger.info("ChatroomManager缓存初始化完成")
        
        # 初始化N8nWebhookManager
        logger.info("正在初始化N8nWebhookManager...")
        n8n_webhook_manager = N8nWebhookManager()
        logger.info("N8nWebhookManager初始化完成")
        
        # 初始化AIResponseProcessor
        logger.info("正在初始化AIResponseProcessor...")
        ai_processor = AIResponseProcessor()
        await ai_processor.initialize_from_database()  # 从数据库加载数据到内存
        logger.info("AIResponseProcessor初始化完成")
        
        # 初始化PersonalityTestManager
        logger.info("正在初始化PersonalityTestManager...")
        from app.services.https.PersonalityTestManager import PersonalityTestManager
        personality_manager = PersonalityTestManager()
        await personality_manager.initialize_from_database()  # 从数据库加载数据到内存
        logger.info("PersonalityTestManager初始化完成")
        
        # 启动自动保存任务
        logger.info("正在启动自动保存后台任务...")
        auto_save_task = asyncio.create_task(auto_save_to_database())
        logger.info("自动保存后台任务已启动")
        
    except Exception as e:
        logger.error(f"数据库连接或初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时的清理工作
    logger.info("正在关闭服务...")
    
    # 取消自动保存任务
    if auto_save_task and not auto_save_task.done():
        logger.info("正在停止自动保存任务...")
        auto_save_task.cancel()
        try:
            await auto_save_task
        except asyncio.CancelledError:
            logger.info("自动保存任务已停止")
    
    # 执行最后一次保存
    logger.info("执行最后一次数据保存...")
    try:
        user_manager = UserManagement()
        await user_manager.save_to_database()
        logger.info("最终用户数据保存完成")
        
        match_manager = MatchManager()
        await match_manager.save_to_database()
        logger.info("最终匹配数据保存完成")
        
        chatroom_manager = ChatroomManager()
        await chatroom_manager.save_chatroom_history()
        logger.info("最终聊天室数据保存完成")
        
        ai_processor = AIResponseProcessor()
        await ai_processor.save_to_database()
        logger.info("最终AI聊天数据保存完成")
    except Exception as e:
        logger.error(f"最终数据保存失败: {e}")
    
    # 断开数据库连接
    logger.info("正在关闭数据库连接...")
    await Database.close()  # 恢复数据库关闭
    logger.info("数据库连接已关闭")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="New LoveLush User Service API",
    version=settings.VERSION,
    lifespan=lifespan,
    # 本地测试时，将 docs_url 和 redoc_url 设置为绝对路径
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "users",
            "description": "用户相关操作",
        },
        {
            "name": "matches",
            "description": "匹配相关操作",
        },
        {
            "name": "chatrooms",
            "description": "聊天室相关操作",
        }
    ]
)

# 全局请求和响应日志中间件
@app.middleware("http")
async def log_requests_and_responses(request: Request, call_next):
    # 生成请求ID
    request_id = f"req_{int(time.time() * 1000)}"
    
    # 记录请求开始
    logger.info(f"🔵 [{request_id}] ====== 收到新请求 ======")
    logger.info(f"🔵 [{request_id}] 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🔵 [{request_id}] 方法: {request.method}")
    logger.info(f"🔵 [{request_id}] URL: {request.url}")
    logger.info(f"🔵 [{request_id}] 路径: {request.url.path}")
    logger.info(f"🔵 [{request_id}] 客户端IP: {request.client.host if request.client else 'Unknown'}")
    
    # 记录请求前单例状态
    try:
        singleton_status_before = SingletonStatusReporter.get_status_summary()
        logger.info(f"🔵 [{request_id}] ====== 请求前单例状态 ======")
        logger.info(f"🔵 [{request_id}] {singleton_status_before}")
    except Exception as e:
        logger.error(f"🔵 [{request_id}] 获取单例状态失败: {e}")
    
    # 记录请求头
    logger.info(f"🔵 [{request_id}] ====== 请求头 ======")
    for header_name, header_value in request.headers.items():
        logger.info(f"🔵 [{request_id}] {header_name}: {header_value}")
    
    # 记录请求体（如果是POST/PUT/PATCH请求）
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                logger.info(f"🔵 [{request_id}] ====== 请求体 ======")
                logger.info(f"🔵 [{request_id}] 原始数据: {body}")
                try:
                    # 尝试解析JSON
                    json_body = json.loads(body)
                    logger.info(f"🔵 [{request_id}] JSON数据: {json.dumps(json_body, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    logger.info(f"🔵 [{request_id}] 非JSON数据: {body.decode('utf-8', errors='ignore')}")
            else:
                logger.info(f"🔵 [{request_id}] ====== 请求体: 空 ======")
        except Exception as e:
            logger.error(f"🔵 [{request_id}] 读取请求体失败: {e}")
    
    # 记录请求开始时间
    start_time = time.time()
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应信息
        logger.info(f"🟢 [{request_id}] ====== 响应信息 ======")
        logger.info(f"🟢 [{request_id}] 状态码: {response.status_code}")
        logger.info(f"🟢 [{request_id}] 处理时间: {process_time:.3f}秒")
        
        # 记录响应头
        logger.info(f"🟢 [{request_id}] ====== 响应头 ======")
        for header_name, header_value in response.headers.items():
            logger.info(f"🟢 [{request_id}] {header_name}: {header_value}")
        
        # 尝试记录响应体（如果是JSON响应）
        try:
            # 获取响应体
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # 重新创建响应对象（因为body_iterator只能读取一次）
            from fastapi.responses import Response
            new_response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
            if response_body:
                logger.info(f"🟢 [{request_id}] ====== 响应体 ======")
                try:
                    # 尝试解析JSON
                    json_response = json.loads(response_body)
                    logger.info(f"🟢 [{request_id}] JSON响应: {json.dumps(json_response, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    logger.info(f"🟢 [{request_id}] 非JSON响应: {response_body.decode('utf-8', errors='ignore')}")
            else:
                logger.info(f"🟢 [{request_id}] ====== 响应体: 空 ======")
            
            # 记录响应后单例状态
            try:
                singleton_status_after = SingletonStatusReporter.get_status_summary()
                logger.info(f"🟢 [{request_id}] ====== 响应后单例状态 ======")
                logger.info(f"🟢 [{request_id}] {singleton_status_after}")
            except Exception as e:
                logger.error(f"🟢 [{request_id}] 获取响应后单例状态失败: {e}")
            
            logger.info(f"🟢 [{request_id}] ====== 请求完成 ======")
            return new_response
            
        except Exception as e:
            logger.error(f"🟢 [{request_id}] 读取响应体失败: {e}")
            
            # 记录响应后单例状态 (错误情况)
            try:
                singleton_status_after = SingletonStatusReporter.get_status_summary()
                logger.info(f"🟢 [{request_id}] ====== 响应后单例状态 (异常) ======")
                logger.info(f"🟢 [{request_id}] {singleton_status_after}")
            except Exception as status_e:
                logger.error(f"🟢 [{request_id}] 获取响应后单例状态失败: {status_e}")
                
            logger.info(f"🟢 [{request_id}] ====== 请求完成 ======")
            return response
            
    except Exception as e:
        # 记录异常
        process_time = time.time() - start_time
        logger.error(f"🔴 [{request_id}] ====== 请求异常 ======")
        logger.error(f"🔴 [{request_id}] 异常信息: {str(e)}")
        logger.error(f"🔴 [{request_id}] 处理时间: {process_time:.3f}秒")
        logger.error(f"🔴 [{request_id}] ====== 请求失败 ======")
        raise

# 注册HTTP API路由
app.include_router(api_router, prefix="/api/v1")
logger.info(f"HTTP API路由已注册")

# 批量注册WebSocket路由
for ws_router in all_ws_routers:
    app.include_router(ws_router)
logger.info(f"WebSocket路由已注册")

# 添加 CORS 中间件，只允许特定来源
cors_origins = [
    "https://cupid-yukio-frontend.vercel.app",  # 生产环境前端地址
    "https://cupid-yukio-frontend-test.vercel.app",
    "http://localhost:5173",  # 本地开发环境前端地址
    "http://127.0.0.1:5173",  # 本地IP地址
]

logger.info(f"CORS允许的域名: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源头
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

@app.get("/")
async def root():
    logger.debug("访问根路径")
    return {"message": "Welcome to New LoveLush User Service API"}

if __name__ == "__main__":
    logger.info(f"启动服务器: {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # 生产环境配置 - 服务器环境
    uvicorn_config = {
        "app": "app.server_run:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,
        "workers": 1
    }

    # 本地测试配置 - 注释掉，使用生产环境配置
    # uvicorn_config = {
    #     "app": "app.server_run:app",
    #     "host": "127.0.0.1",
    #     "port": 8001,
    #     "reload": True,
    #     "workers": 1
    # }
    
    try:
        uvicorn.run(**uvicorn_config)
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        sys.exit(1)