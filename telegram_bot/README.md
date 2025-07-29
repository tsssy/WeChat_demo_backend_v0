# Cupid Yukio Matchmaker Bot

A sophisticated AI-powered matchmaking bot system that interacts with Google's Gemini AI to help users find meaningful connections. Features gender-specific personalized guidance and Telegram bot integration.

## Features

- **Gender-Specific Prompts**: Personalized guidance based on user gender (male, female, or neutral)
- **Telegram Bot Integration**: Full Telegram bot with gender selection and conversation handling
- **Typing Indicators**: Real-time feedback showing when the bot is processing messages
- **Structured System Prompt**: Organized into Role, Object, Skill, Constraint, and Workflow sections
- **Message History Tracking**: Maintains chronological conversation history in "[who says]: [says what]" format
- **Session Management**: Clear history functionality for new sessions
- **Statistics Tracking**: Monitor conversation metrics and session duration
- **Error Handling**: Robust error handling for API communication issues

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables using one of these methods:

### **Method A: Automatic Setup (Recommended)**
```bash
python setup_env.py
```
This will prompt you to enter your API key and create the `.env` file automatically.

### **Method B: Manual Setup**
1. Copy the template: `cp env_template.txt .env`
2. Edit `.env` and configure the following variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - `API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)
   - MongoDB configuration (if using direct database access)

### **Method C: Environment Variable**
```bash
export GEMINI_API_KEY="your_api_key_here"
export API_BASE_URL="http://localhost:8000"
```

## Usage

### Telegram Bot (Recommended)

Run the Telegram bot:
```bash
python main.py
```

The bot will:
1. Ask users to select their gender (male/female)
2. Initialize a personalized matchmaker bot for each user
3. Show typing indicators while processing messages
4. Provide gender-specific guidance and advice
5. Maintain separate conversation sessions for each user

**Features:**
- **Typing Indicators**: Shows "Cupid Yukio is typing..." while processing messages
- **Real-time Feedback**: Users know the bot is working on their request
- **Smooth UX**: Prevents users from thinking the bot is unresponsive

### Basic Usage with Gender Selection

```python
from matchmaker_bot import MatchmakerBot
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the bot with gender-specific prompts
api_key = os.getenv("GEMINI_API_KEY")
bot = MatchmakerBot(api_key, gender="male")  # Options: "male", "female", "neutral"

# Send a message and get response
response = bot.send_message("Hello, I'm looking for a meaningful relationship.")
print(response)
```

### Interactive Mode with Gender Selection

Run the bot in interactive mode:
```bash
python matchmaker_bot.py
```

The bot will prompt you to select your gender for personalized guidance.

Available commands:
- `quit` - Exit the bot
- `stats` - Show session statistics
- `clear` - Clear conversation history and start new session
- `history` - Display conversation history

### Testing Gender-Specific Prompts

Test how the bot responds differently based on gender:
```bash
python test_gender_prompts.py
```

This script demonstrates the differences in responses for male, female, and neutral users.

### Advanced Usage

```python
# Get conversation history
history = bot.get_conversation_history()

# Get formatted context
context = bot.get_formatted_context()

# Get session statistics
stats = bot.get_session_stats()

# Clear history for new session
bot.clear_history()
```

## Gender-Specific Features

The bot provides different guidance based on the user's gender:

### For Male Users
- Understanding modern dating dynamics and expectations
- Learning effective communication strategies for building emotional connections
- Developing confidence while maintaining authenticity
- Navigating traditional vs. modern relationship roles
- Understanding female perspectives on dating and relationships
- Building emotional intelligence and empathy skills

### For Female Users
- Understanding your own worth and setting healthy boundaries
- Recognizing red flags and green flags in potential partners
- Balancing independence with partnership in relationships
- Communicating needs and expectations clearly
- Understanding male perspectives on dating and relationships
- Building self-confidence and maintaining personal identity

### For Neutral/Other Users
- Universal principles of healthy relationships
- Effective communication and personal growth
- Focus on compatibility regardless of gender identity

## System Prompt Structure

The bot uses a modular system prompt structure with separate markdown files for each section:

### Core Prompt Files (in `prompt/` folder)
1. **`role.md`**: Defines the bot's identity as Cupid Yukio, an advanced AI matchmaker
2. **`object.md`**: Outlines the primary objectives for facilitating successful matches
3. **`skill.md`**: Lists expertise areas including psychology, relationship dynamics, and compatibility analysis
4. **`constraint.md`**: Establishes safety, privacy, and ethical guidelines
5. **`workflow.md`**: Provides a structured 4-phase approach for interactions

### Gender-Specific Files
6. **`male.md`**: Tailored guidance for male users
7. **`female.md`**: Tailored guidance for female users
8. **`neutral.md`**: Universal guidance for neutral/other users

The bot dynamically reads these files and combines them to create the complete system prompt based on the user's gender selection.

## Customizing Prompts

You can easily customize the bot's behavior by editing the markdown files in the `prompt/` folder:

- **Edit core behavior**: Modify `role.md`, `object.md`, `skill.md`, `constraint.md`, or `workflow.md`
- **Adjust gender-specific advice**: Update `male.md`, `female.md`, or `neutral.md`
- **Add new sections**: Create additional markdown files and update the bot code

See `prompt/README.md` for detailed documentation on the prompt file structure.

## Message History Format

The bot maintains conversation history in chronological order with the format:
```
[System]: System prompt content
[User]: User message
[Bot]: Bot response
[User]: Another user message
[Bot]: Another bot response
```

## Error Handling

The bot includes comprehensive error handling for:
- API key validation
- Model initialization failures
- Network communication issues
- Invalid responses
- Gender parameter validation

## Requirements

- Python 3.7+
- Google Generative AI API key
- python-telegram-bot (for Telegram integration)
- Internet connection for API communication

## License

This project is open source and available under the MIT License. 