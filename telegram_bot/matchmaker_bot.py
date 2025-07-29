import base64
import os
import asyncio
import json
import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def safe_encode_string(text: str) -> str:
    """
    安全地将字符串编码为UTF-8，处理任何编码问题
    
    Args:
        text (str): 输入字符串
        
    Returns:
        str: 安全的UTF-8字符串
    """
    if text is None:
        return ""
    
    # 确保是字符串类型
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            text = text.decode('utf-8', errors='ignore')
    elif not isinstance(text, str):
        text = str(text)
    
    # 直接清理所有非ASCII字符，避免编码问题
    cleaned_text = ""
    for char in text:
        # 只保留ASCII字符（0-127）
        if ord(char) < 128:
            cleaned_text += char
        else:
            # 替换非ASCII字符为空格
            cleaned_text += " "
    
    # 额外检查：确保结果可以编码为ASCII
    try:
        cleaned_text.encode('ascii')
        return cleaned_text
    except UnicodeEncodeError:
        # 如果还有问题，进一步清理
        final_text = ""
        for char in cleaned_text:
            try:
                char.encode('ascii')
                final_text += char
            except UnicodeEncodeError:
                final_text += " "
        return final_text


class MatchmakerBot:
    """
    A bot system that interacts with Gemini AI for matchmaking purposes.
    Features structured system prompts and message history tracking.
    """
    
    def __init__(self, api_key: str, gender: str = "neutral", model_name: str = "gemini-2.5-flash"):
        """
        Initialize the MatchmakerBot with Gemini AI configuration.
        
        Args:
            api_key (str): Google Gemini API key
            gender (str): User's gender ("male", "female", or "neutral")
            model_name (str): Name of the Gemini model to use
        """
        self.api_key = api_key
        self.gender = gender.lower()
        self.model_name = model_name
        self.message_history: List[Dict[str, str]] = []
        self.client = None
        
        # Configure Gemini AI
        try:
            self.client = genai.Client(api_key=self.api_key)
            
            # Initialize conversation with system prompt
            self._initialize_conversation()
        except Exception as e:
            print(f"Error initializing Gemini AI: {str(e)}")
            raise
    
    def _read_prompt_file(self, filename: str) -> str:
        """
        Read a prompt file from the prompt folder.
        
        Args:
            filename (str): Name of the prompt file (e.g., 'role.md')
            
        Returns:
            str: Content of the prompt file
        """
        prompt_dir = os.path.join(os.path.dirname(__file__), 'prompt')
        file_path = os.path.join(prompt_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                # 确保内容是UTF-8编码的字符串
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                elif not isinstance(content, str):
                    content = str(content)
                return content
        except FileNotFoundError:
            print(f"Warning: Prompt file {filename} not found. Using default content.")
            return f"# {filename.upper().replace('.md', '')}\n\nDefault content for {filename}"
        except Exception as e:
            print(f"Error reading prompt file {filename}: {str(e)}")
            return f"# {filename.upper().replace('.md', '')}\n\nError loading content for {filename}"
    
    def _get_system_prompt(self) -> str:
        """
        Generate the structured system prompt by reading from markdown files.
        
        Returns:
            str: Complete system prompt
        """
        # Read base prompt sections
        role = self._read_prompt_file('role.md')
        object_section = self._read_prompt_file('object.md')
        skill = self._read_prompt_file('skill.md')
        constraint = self._read_prompt_file('constraint.md')
        workflow = self._read_prompt_file('workflow.md')
        
        # Read gender-specific section
        if self.gender == "male":
            gender_specific = self._read_prompt_file('male.md')
        elif self.gender == "female":
            gender_specific = self._read_prompt_file('female.md')
        else:
            gender_specific = self._read_prompt_file('neutral.md')
        
        # Combine all sections
        system_prompt = f"""
# MATCHMAKER BOT SYSTEM PROMPT

{role}

{object_section}

{skill}

{constraint}

{workflow}

{gender_specific}
"""
        
        # 确保系统提示词是安全的UTF-8字符串
        system_prompt = system_prompt.strip()
        if isinstance(system_prompt, bytes):
            system_prompt = system_prompt.decode('utf-8', errors='ignore')
        elif not isinstance(system_prompt, str):
            system_prompt = str(system_prompt)
        
        # 移除任何可能导致编码问题的字符
        try:
            system_prompt.encode('ascii')
        except UnicodeEncodeError:
            # 如果包含非ASCII字符，尝试清理
            system_prompt = system_prompt.encode('utf-8', errors='ignore').decode('utf-8')
        
        return system_prompt
    
    def _initialize_conversation(self):
        """Initialize the conversation with the system prompt."""
        if self.client is None:
            raise RuntimeError("Client not initialized. Please check your API key.")
        
        system_prompt = self._get_system_prompt()
        
        # Add system prompt as the first message
        self._add_to_history("System", system_prompt)
    
    def _add_to_history(self, speaker: str, message: str):
        """
        Add a message to the conversation history.
        
        Args:
            speaker (str): Who is speaking (User, Bot, System, etc.)
            message (str): The message content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.message_history.append({
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message
        })
    
    def _format_context(self) -> str:
        """
        Format the message history as context for the model.
        
        Returns:
            str: Formatted context string
        """
        if not self.message_history:
            return ""
        
        context_lines = []
        for entry in self.message_history:
            context_lines.append(f"[{entry['speaker']}]: {entry['message']}")
        
        return "\n".join(context_lines)
    
    def _build_conversation_contents(self, user_message: str) -> List[types.Content]:
        """
        Build the conversation contents including history and current message.
        
        Args:
            user_message (str): The current user message
            
        Returns:
            List[types.Content]: List of content objects for the API
        """
        contents = []
        
        # Add system prompt first
        system_prompt = safe_encode_string(self._get_system_prompt())
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=system_prompt)]
            )
        )
        
        # Gender-specific acknowledgment
        if self.gender == "male":
            acknowledgment = "I understand. I am Cupid Yukio, your AI matchmaker. I'm ready to help you find meaningful connections and provide guidance tailored to your perspective as a male user."
        elif self.gender == "female":
            acknowledgment = "I understand. I am Cupid Yukio, your AI matchmaker. I'm ready to help you find meaningful connections and provide guidance tailored to your perspective as a female user."
        else:
            acknowledgment = "I understand. I am Cupid Yukio, your AI matchmaker. I'm ready to help you find meaningful connections."
        
        contents.append(
            types.Content(
                role="model",
                parts=[types.Part.from_text(text=acknowledgment)]
            )
        )
        
        # Add conversation history (excluding system messages)
        for entry in self.message_history:
            message_text = safe_encode_string(entry["message"])
            
            if entry["speaker"] == "User":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=message_text)]
                    )
                )
            elif entry["speaker"] == "Bot":
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=message_text)]
                    )
                )
        
        # Add current user message
        user_message = safe_encode_string(user_message)
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )
        
        return contents
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message to the bot and get a response.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The bot's response
        """
        # 确保用户输入是安全的UTF-8字符串
        user_message = safe_encode_string(user_message)
        
        # Add user message to history
        self._add_to_history("User", user_message)
        
        # Handle cheat code for testing
        if user_message == "aaa南姐直接把我踢到了结尾":
            cheat_response = "你问题很大啊小伙子：\n问题1: 太细\n问题2: 太短\n问题3: 太快\n#end"
            self._add_to_history("Bot", cheat_response)
            return cheat_response
        
        max_retries = 10
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.client is None:
                    raise RuntimeError("Client not initialized. Please check your API key.")
                
                # Build conversation contents
                contents = self._build_conversation_contents(user_message)
                
                # Configure generation
                generate_content_config = types.GenerateContentConfig(
                    thinking_config = types.ThinkingConfig(
                        thinking_budget=0#-1
                    ),
                    response_mime_type="text/plain",
                )
                
                # Get response from Gemini
                response_text = ""
                for chunk in self.client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        # 确保文本是安全的UTF-8字符串
                        chunk_text = safe_encode_string(chunk.text)
                        response_text += chunk_text
                
                # 检查是否是最终总结（包含 partner profile）
                if "Your Ideal Partner Profile" in response_text and "#end" not in response_text:
                    # 强制分割消息：先发送 partner profile，再发送问题工具包
                    parts = self._split_final_summary(response_text)
                    if len(parts) == 2:
                        # 只添加第一部分到历史记录，第二部分由 main.py 处理
                        self._add_to_history("Bot", parts[0])
                        # 在历史记录中标记第二部分
                        self._add_to_history("Bot", f"[SPLIT_PART_2] {parts[1]}")
                        return response_text  # 返回完整内容，让 main.py 处理分割
                    else:
                        # 如果分割失败，按原样处理
                        self._add_to_history("Bot", response_text)
                        return response_text
                else:
                    # 正常情况，直接将AI回复加入历史
                    self._add_to_history("Bot", response_text)
                    return response_text
                
            except Exception as e:
                error_str = str(e)
                retry_count += 1
                print(f"Error communicating with Gemini AI: {error_str}")
                print(f"Error type: {type(e).__name__}")
                print(f"User message type: {type(user_message)}")
                print(f"User message length: {len(str(user_message))}")
                print(f"Trying again... (attempt {retry_count}/{max_retries})")
                
                # Wait a bit before retrying (exponential backoff)
                import time
                time.sleep(2 ** retry_count)  # 2, 4, 8, 16, 32 seconds
                
                continue
        
        # If we've exhausted all retries
        final_error = f"Failed to get response after {max_retries} attempts due to persistent errors"
        self._add_to_history("System", final_error)
        return final_error
    
    async def send_message_async(self, user_message: str) -> str:
        """
        Send a message to the bot and get a response asynchronously.
        This method is designed to work with typing indicators.
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The bot's response
        """
        # Run the synchronous send_message method in a thread pool
        return await asyncio.to_thread(self.send_message, user_message)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List[Dict[str, str]]: List of message entries with timestamp, speaker, and message
        """
        return self.message_history.copy()
    
    def get_formatted_context(self) -> str:
        """
        Get the formatted context string for debugging or analysis.
        
        Returns:
            str: Formatted context string
        """
        return self._format_context()
    
    def _split_final_summary(self, response_text: str) -> list[str]:
        """
        分割最终总结为两部分：只保留 Ideal Partner Profile 及其后内容为第一条，第二条为筛选问题部分。
        优先用 *** 分割，其次用 Filter Questions/筛选问题等关键词分割，分割点保留在第二部分开头。
        增强健壮性：分割关键词不区分大小写，支持:号。
        """
        import re
        # 1. 优先用 *** 分割（不区分大小写，允许前后有空格/换行）
        split_match = re.search(r"\n?\s*\*\*\*\s*\n?", response_text, re.IGNORECASE)
        if split_match:
            split_pos = split_match.start()
            profile_part = response_text[:split_pos].strip()
            questions_part = response_text[split_match.end():].strip()
            return [profile_part, questions_part]

        # 2. 用“Filter Questions”等关键词分割，保留分割词在第二部分
        pattern = re.compile(
            r"(filter questions:?|筛选问题:?|问题工具包:?|提问建议:?|约会提问:?|推荐提问:?|建议提问:?|实用提问:?|情景提问:?|初期提问:?)",
            re.IGNORECASE
        )
        match = pattern.search(response_text)
        if match:
            split_pos = match.start()
            profile_part = response_text[:split_pos].strip()
            questions_part = response_text[split_pos:].strip()
            return [profile_part, questions_part]

        # 3. 兜底：返回原文，并打印调试信息
        print("[SPLIT_DEBUG] 分割失败，原文如下：\n", response_text)
        return [response_text]
    
    def clear_history(self):
        """Clear the conversation history and start a new session."""
        self.message_history.clear()
        self._initialize_conversation()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current session.
        
        Returns:
            Dict[str, Any]: Session statistics
        """
        if not self.message_history:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "bot_messages": 0,
                "system_messages": 0,
                "session_duration": "0 minutes"
            }
        
        user_count = sum(1 for msg in self.message_history if msg["speaker"] == "User")
        bot_count = sum(1 for msg in self.message_history if msg["speaker"] == "Bot")
        system_count = sum(1 for msg in self.message_history if msg["speaker"] == "System")
        
        # Calculate session duration
        first_msg = self.message_history[0]["timestamp"]
        last_msg = self.message_history[-1]["timestamp"]
        
        start_time = datetime.strptime(first_msg, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(last_msg, "%Y-%m-%d %H:%M:%S")
        duration = end_time - start_time
        
        return {
            "total_messages": len(self.message_history),
            "user_messages": user_count,
            "bot_messages": bot_count,
            "system_messages": system_count,
            "session_duration": f"{duration.seconds // 60} minutes"
        }


# Example usage and testing
if __name__ == "__main__":
    # Get API key from environment variable (loaded from .env file)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ API Key not found!")
        print("\n📝 To set up your API key:")
        print("1. Copy env_template.txt to .env")
        print("2. Replace 'your_actual_api_key_here' with your real Gemini API key")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        print("\nExample .env file content:")
        print("GEMINI_API_KEY=AIzaSyC...your_actual_key_here")
        exit(1)
    
    # Get user gender preference
    print("=== Cupid Yukio Matchmaker Bot ===")
    print("Please select your gender for personalized guidance:")
    print("1. Male")
    print("2. Female") 
    print("3. Neutral/Other")
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice == "1":
            gender = "male"
            break
        elif choice == "2":
            gender = "female"
            break
        elif choice == "3":
            gender = "neutral"
            break
        else:
            print("Please enter 1, 2, or 3.")
    
    # Initialize the bot with gender
    bot = MatchmakerBot(api_key, gender=gender)
    
    # Example conversation
    print(f"=== Cupid Yukio Matchmaker Bot (Gender: {gender.capitalize()}) ===")
    print("Type 'quit' to exit, 'stats' for session statistics, 'clear' to start new session")
    print("Type 'history' to see conversation history")
    print("-" * 50)
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("Goodbye! Session ended.")
            break
        elif user_input.lower() == 'stats':
            stats = bot.get_session_stats()
            print(f"\nSession Statistics:")
            print(f"Total messages: {stats['total_messages']}")
            print(f"User messages: {stats['user_messages']}")
            print(f"Bot messages: {stats['bot_messages']}")
            print(f"Session duration: {stats['session_duration']}")
            print("-" * 50)
            continue
        elif user_input.lower() == 'clear':
            bot.clear_history()
            print("Session cleared. Starting fresh conversation.")
            print("-" * 50)
            continue
        elif user_input.lower() == 'history':
            history = bot.get_conversation_history()
            print(f"\nConversation History ({len(history)} messages):")
            print("-" * 50)
            for entry in history:
                print(f"[{entry['timestamp']}] {entry['speaker']}: {entry['message'][:100]}{'...' if len(entry['message']) > 100 else ''}")
            print("-" * 50)
            continue
        elif not user_input:
            continue
        
        # Get bot response
        response = bot.send_message(user_input)
        print(f"Bot: {response}")
        print("-" * 50)
