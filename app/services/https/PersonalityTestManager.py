#!/usr/bin/env python3
"""
性格测试管理器
实现性格测试的核心业务逻辑，包括测试流程控制、计分算法、结果计算等
采用内存优先模式，定期与数据库同步
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid
import time
from app.core.database import Database
from app.utils.my_logger import MyLogger
logger = MyLogger("PersonalityTestManager")

class PersonalityTestManager:
    """
    性格测试管理器类
    实现单例模式，采用内存优先设计，提供完整的性格测试业务逻辑
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 内存数据结构
            cls._instance.questions = {}          # question_id -> 题目详情
            cls._instance.cards = {}             # card_id -> 卡片详情  
            cls._instance.test_sessions = {}     # session_id -> 测试会话详情
            cls._instance.user_histories = {}   # user_id -> 历史记录列表
            cls._instance.session_counter = 0   # 会话计数器
        return cls._instance
    
    async def initialize_from_database(self):
        """从数据库初始化内存数据"""
        if PersonalityTestManager._initialized:
            return
            
        try:
            logger.info("PersonalityTestManager: 开始从数据库加载数据到内存")
            
            # 加载题目数据
            questions_data = await Database.find("personality_questions", {})
            for question_data in questions_data:
                question_id = question_data.get("question_id")
                if question_id:
                    # 移除MongoDB的_id字段
                    question_data.pop("_id", None)
                    self.questions[question_id] = question_data
            
            # 加载卡片数据
            cards_data = await Database.find("personality_cards", {})
            for card_data in cards_data:
                card_id = card_data.get("card_id")
                if card_id:
                    # 移除MongoDB的_id字段
                    card_data.pop("_id", None)
                    self.cards[card_id] = card_data
            
            # 加载测试记录
            records_data = await Database.find("personality_test_records", {})
            for record_data in records_data:
                session_id = record_data.get("session_id")
                user_id = record_data.get("user_id")
                
                if session_id:
                    # 移除MongoDB的_id字段
                    record_data.pop("_id", None)
                    self.test_sessions[session_id] = record_data
                    
                    # 如果测试已完成，添加到用户历史记录
                    if record_data.get("completed", False) and user_id:
                        if user_id not in self.user_histories:
                            self.user_histories[user_id] = []
                        
                        # 避免重复添加
                        existing_sessions = [h.get("session_id") for h in self.user_histories[user_id]]
                        if session_id not in existing_sessions:
                            self.user_histories[user_id].append({
                                "session_id": session_id,
                                "result_card": record_data.get("result_card"),
                                "completed_at": record_data.get("completed_at")
                            })
            
            # 初始化会话计数器 - 使用时间戳避免冲突
            self.session_counter = int(time.time() * 1000)
            
            PersonalityTestManager._initialized = True
            
            logger.info(f"PersonalityTestManager: 成功加载 {len(self.questions)} 道题目，{len(self.cards)} 张卡片，{len(self.test_sessions)} 个测试会话")
            logger.info(f"PersonalityTestManager: 加载了 {sum(len(histories) for histories in self.user_histories.values())} 条用户历史记录")
            
        except Exception as e:
            logger.error(f"PersonalityTestManager: 从数据库加载数据失败: {str(e)}")
            PersonalityTestManager._initialized = True  # 即使失败也标记为已初始化，避免重复尝试
    
    async def save_to_database(self, session_id: Optional[str] = None) -> bool:
        """
        保存内存数据到数据库
        
        Args:
            session_id: 指定保存的会话ID，None表示保存所有数据
            
        Returns:
            是否保存成功
        """
        try:
            if session_id is None:
                # 保存所有测试会话
                success_count = 0
                total_sessions = len(self.test_sessions)
                
                for sid, session_data in self.test_sessions.items():
                    try:
                        # 检查数据库中是否存在
                        existing_session = await Database.find_one("personality_test_records", {"session_id": sid})
                        
                        if existing_session:
                            # 更新现有记录
                            await Database.update_one(
                                "personality_test_records",
                                {"session_id": sid},
                                {"$set": session_data}
                            )
                        else:
                            # 插入新记录
                            await Database.insert_one("personality_test_records", session_data)
                        
                        success_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存测试会话 {sid} 失败: {e}")
                        continue
                
                logger.info(f"性格测试数据保存完成: {success_count}/{total_sessions} 个测试会话")
                return success_count == total_sessions
                
            else:
                # 保存指定会话
                if session_id not in self.test_sessions:
                    logger.warning(f"测试会话 {session_id} 在内存中不存在")
                    return False
                
                session_data = self.test_sessions[session_id]
                
                # 检查数据库中是否存在
                existing_session = await Database.find_one("personality_test_records", {"session_id": session_id})
                
                if existing_session:
                    # 更新现有记录
                    await Database.update_one(
                        "personality_test_records",
                        {"session_id": session_id},
                        {"$set": session_data}
                    )
                else:
                    # 插入新记录
                    await Database.insert_one("personality_test_records", session_data)
                
                logger.info(f"测试会话 {session_id} 保存完成")
                return True
                
        except Exception as e:
            logger.error(f"保存性格测试数据到数据库失败: {str(e)}")
            return False
    
    async def start_new_test(self, user_id: int) -> Optional[Dict]:
        """
        开始新的性格测试 - 内存优先模式
        
        Args:
            user_id: 用户ID
            
        Returns:
            包含会话ID和第一道题目的字典，失败返回None
        """
        try:
            # 检查题目数据是否加载
            if len(self.questions) == 0:
                logger.error("题目数据未加载")
                return None
            
            # 生成新的会话ID
            session_id = str(uuid.uuid4())
            
            # 在内存中创建测试会话
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "answers": [],
                "scores": {},
                "result_card": None,
                "completed": False,
                "started_at": datetime.now(),
                "completed_at": None
            }
            
            # 保存到内存
            self.test_sessions[session_id] = session_data
            
            # 获取第一道题目
            first_question = self.questions.get("Q1")
            if not first_question:
                logger.error("第一道题目不存在")
                return None
            
            # 复制题目数据并移除选项中的personality_type字段
            first_question_copy = first_question.copy()
            cleaned_options = []
            for option in first_question_copy.get("options", []):
                cleaned_options.append({
                    "option": option["option"],
                    "text": option["text"]
                })
            first_question_copy["options"] = cleaned_options
            
            result = {
                "session_id": session_id,
                "first_question": first_question_copy,
                "progress": {
                    "current": 1,
                    "total": 16
                }
            }
            
            logger.info(f"成功开始新测试 - user_id: {user_id}, session_id: {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"开始新测试失败 - user_id: {user_id}, error: {e}")
            return None
    
    async def submit_answer(self, session_id: str, question_id: str, selected_option: str) -> Optional[Dict]:
        """
        提交答案并获取下一题或结果 - 内存优先模式
        
        Args:
            session_id: 测试会话ID
            question_id: 题目ID
            selected_option: 选择的选项
            
        Returns:
            包含下一题目或测试结果的字典，失败返回None
        """
        try:
            # 验证会话是否存在且未完成
            session = self.test_sessions.get(session_id)
            if not session:
                logger.error(f"会话不存在 - session_id: {session_id}")
                return None
            
            if session.get("completed", False):
                logger.error(f"测试已完成 - session_id: {session_id}")
                return None
            
            # 验证题目和答案是否有效
            question = self.questions.get(question_id)
            if not question:
                logger.error(f"题目不存在 - question_id: {question_id}")
                return None
            
            # 验证选项是否有效并获取对应的人格类型
            personality_type = None
            for option in question.get("options", []):
                if option["option"] == selected_option:
                    personality_type = option["personality_type"]
                    break
            
            if not personality_type:
                logger.error(f"无效答案 - question_id: {question_id}, option: {selected_option}")
                return None
            
            # 在内存中添加答案
            answer_record = {
                "question_id": question_id,
                "selected_option": selected_option,
                "personality_type": personality_type
            }
            
            session["answers"].append(answer_record)
            
            current_question_num = len(session["answers"])
            
            # 检查是否完成所有题目
            if current_question_num >= 16:
                # 完成测试，计算结果
                return await self._complete_test(session_id)
            else:
                # 获取下一题
                next_question_id = f"Q{current_question_num + 1}"
                next_question = self.questions.get(next_question_id)
                
                if not next_question:
                    logger.error(f"下一题不存在 - question_id: {next_question_id}")
                    return None
                
                # 复制题目数据并移除选项中的personality_type字段
                next_question_copy = next_question.copy()
                cleaned_options = []
                for option in next_question_copy.get("options", []):
                    cleaned_options.append({
                        "option": option["option"],
                        "text": option["text"]
                    })
                next_question_copy["options"] = cleaned_options
                
                result = {
                    "next_question": next_question_copy,
                    "progress": {
                        "current": current_question_num + 1,
                        "total": 16
                    },
                    "is_completed": False
                }
                
                logger.info(f"提交答案成功 - session_id: {session_id}, question: {current_question_num + 1}/16")
                return result
                
        except Exception as e:
            logger.error(f"提交答案失败 - session_id: {session_id}, error: {e}")
            return None
    
    async def _complete_test(self, session_id: str) -> Optional[Dict]:
        """
        完成测试，计算最终结果 - 内存优先模式
        
        Args:
            session_id: 测试会话ID
            
        Returns:
            测试结果字典
        """
        try:
            # 获取内存中的会话信息
            session = self.test_sessions.get(session_id)
            if not session:
                return None
            
            answers = session.get("answers", [])
            if len(answers) != 16:
                logger.error(f"答案数量不正确 - session_id: {session_id}, count: {len(answers)}")
                return None
            
            # 计算各人格类型得分
            scores = self._calculate_scores(answers)
            
            # 确定最终结果卡片
            result_card_id = self._determine_result_card(scores)
            
            # 从内存获取结果卡片详细信息
            result_card = self.cards.get(result_card_id)
            if not result_card:
                logger.error(f"获取结果卡片失败 - card_id: {result_card_id}")
                return None
            
            # 在内存中标记测试完成
            completed_at = datetime.now()
            session["scores"] = scores
            session["result_card"] = result_card_id
            session["completed"] = True
            session["completed_at"] = completed_at
            
            # 添加到用户历史记录
            user_id = session.get("user_id")
            if user_id:
                if user_id not in self.user_histories:
                    self.user_histories[user_id] = []
                
                self.user_histories[user_id].append({
                    "session_id": session_id,
                    "result_card": result_card_id,
                    "completed_at": completed_at
                })
                
                # 按完成时间倒序排列
                self.user_histories[user_id].sort(key=lambda x: x["completed_at"], reverse=True)
            
            result = {
                "session_id": session_id,
                "result_card": result_card,
                "scores": scores,
                "completed_at": completed_at.isoformat(),
                "is_completed": True
            }
            
            logger.info(f"测试完成 - session_id: {session_id}, result: {result_card_id}")
            return result
            
        except Exception as e:
            logger.error(f"完成测试失败 - session_id: {session_id}, error: {e}")
            return None
    
    def _calculate_scores(self, answers: List[Dict]) -> Dict[str, int]:
        """
        计算各人格类型得分
        
        Args:
            answers: 答案列表
            
        Returns:
            各人格类型得分字典
        """
        scores = {
            "A1": 0, "A2": 0, "A3": 0, "A4": 0,
            "A5": 0, "A6": 0, "A7": 0, "A8": 0
        }
        
        # 统计各人格类型出现次数
        for answer in answers:
            personality_type = answer.get("personality_type")
            if personality_type in scores:
                scores[personality_type] += 1
        
        return scores
    
    def _determine_result_card(self, scores: Dict[str, int]) -> str:
        """
        根据得分确定最终结果卡片
        
        Args:
            scores: 各人格类型得分字典
            
        Returns:
            最终结果卡片ID
        """
        # 找到得分最高的人格类型
        max_score = max(scores.values())
        
        # 如果有多个人格类型并列最高分，按优先级选择 (A1 > A2 > ... > A8)
        for card_id in ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]:
            if scores[card_id] == max_score:
                return card_id
        
        # 默认返回A1（理论上不会执行到这里）
        return "A1"
    
    async def get_test_result(self, session_id: str) -> Optional[Dict]:
        """
        获取测试结果 - 内存优先模式
        
        Args:
            session_id: 测试会话ID
            
        Returns:
            测试结果字典，未完成或不存在返回None
        """
        try:
            # 获取内存中的会话信息
            session = self.test_sessions.get(session_id)
            if not session:
                logger.error(f"会话不存在 - session_id: {session_id}")
                return None
            
            # 检查测试是否完成
            if not session.get("completed", False):
                logger.error(f"测试未完成 - session_id: {session_id}")
                return None
            
            result_card_id = session.get("result_card")
            if not result_card_id:
                logger.error(f"结果卡片ID为空 - session_id: {session_id}")
                return None
            
            # 从内存获取结果卡片详细信息
            result_card = self.cards.get(result_card_id)
            if not result_card:
                logger.error(f"获取结果卡片失败 - card_id: {result_card_id}")
                return None
            
            completed_at = session.get("completed_at")
            result = {
                "session_id": session_id,
                "result_card": result_card,
                "scores": session.get("scores", {}),
                "completed_at": completed_at.isoformat() if completed_at else None
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取测试结果失败 - session_id: {session_id}, error: {e}")
            return None
    
    async def get_user_test_history(self, user_id: int, limit: int = 10) -> Optional[Dict]:
        """
        获取用户测试历史记录 - 内存优先模式
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            历史记录字典
        """
        try:
            # 从内存获取历史记录
            user_history = self.user_histories.get(user_id, [])
            
            # 获取测试总次数
            total_tests = len(user_history)
            
            # 应用限制并处理历史记录
            limited_history = user_history[:limit] if limit > 0 else user_history
            
            processed_tests = []
            for record in limited_history:
                result_card_id = record.get("result_card")
                if result_card_id:
                    # 从内存获取卡片摘要信息
                    card = self.cards.get(result_card_id)
                    if card:
                        card_summary = {
                            "card_id": card["card_id"],
                            "card_name": card["card_name"],
                            "emoji": card["emoji"]
                        }
                        
                        completed_at = record.get("completed_at")
                        processed_tests.append({
                            "session_id": record["session_id"],
                            "result_card": card_summary,
                            "completed_at": completed_at.isoformat() if completed_at else None
                        })
            
            result = {
                "tests": processed_tests,
                "total_tests": total_tests
            }
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户测试历史失败 - user_id: {user_id}, error: {e}")
            return None
    
    async def cleanup_old_sessions(self, hours_ago: int = 24) -> int:
        """
        清理过期的未完成测试会话 - 内存优先模式
        
        Args:
            hours_ago: 多少小时前的会话需要清理
            
        Returns:
            清理的会话数量
        """
        try:
            from datetime import timedelta
            
            cutoff_time = datetime.now() - timedelta(hours=hours_ago)
            
            sessions_to_remove = []
            for session_id, session_data in self.test_sessions.items():
                # 只清理未完成的会话
                if not session_data.get("completed", False):
                    started_at = session_data.get("started_at")
                    if started_at and started_at < cutoff_time:
                        sessions_to_remove.append(session_id)
            
            # 从内存中移除过期会话
            for session_id in sessions_to_remove:
                del self.test_sessions[session_id]
            
            cleaned_count = len(sessions_to_remove)
            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 个过期的未完成测试会话")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
            return 0
    
    async def get_system_stats(self) -> Dict:
        """
        获取系统统计信息 - 内存优先模式
        
        Returns:
            系统统计信息字典
        """
        try:
            question_count = len(self.questions)
            card_count = len(self.cards)
            session_count = len(self.test_sessions)
            completed_tests = sum(1 for session in self.test_sessions.values() if session.get("completed", False))
            
            stats = {
                "question_count": question_count,
                "card_count": card_count,
                "session_count": session_count,
                "completed_tests": completed_tests,
                "expected_questions": 16,
                "expected_cards": 8,
                "system_ready": question_count == 16 and card_count == 8
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取系统统计失败: {e}")
            return {
                "question_count": 0,
                "card_count": 0,
                "session_count": 0,
                "completed_tests": 0,
                "expected_questions": 16,
                "expected_cards": 8,
                "system_ready": False
            } 