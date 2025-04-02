import os
import json
from dotenv import load_dotenv  # type: ignore

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Load question data safely
data = []
questions_path = "questionBank/questions.json"

if os.path.exists(questions_path):
    try:
        with open(questions_path, "r", encoding="utf-8") as file:
            data = json.loads(file.read())
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error in questions.json: {e}")
    except Exception as e:
        print(f"❌ An error occurred while loading challenges: {e}")
else:
    print(f"⚠️ Warning: {questions_path} not found!")

# ✅ Get environment variables safely
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

if not DISCORD_TOKEN:
    print("❌ ERROR: DISCORD_TOKEN is missing in .env!")
if not GEMINI_KEY:
    print("❌ ERROR: GEMINI_KEY is missing in .env!")

# ✅ Load bot commands dynamically (Ensure `commands` folder exists)
COMMAND_MODULES = []
commands_path = "commands"

if os.path.exists(commands_path):
    COMMAND_MODULES = [
        f"commands.{file[:-3]}" for file in os.listdir(commands_path)
        if file.endswith(".py") and file not in ["__init__.py", "hackathon.py", "code_submission.py"]
    ]
else:
    print(f"⚠️ Warning: {commands_path} folder not found!")

# ✅ Role XP Thresholds
ROLE_THRESHOLDS = {
    100: "Beginner Coder",
    300: "Intermediate Coder",
    700: "Elite Coder",
    1500: "HackLeague Champion",
    3000: "HackLeague Legend"
}

def contains_duplicate(nums):
    """
    Check if any value appears at least twice in the array.

    Args:
        nums (list): List of integers.

    Returns:
        bool: True if any value appears at least twice, False otherwise.
    """
    return len(nums) != len(set(nums))