import os
from dotenv import load_dotenv
import json
load_dotenv()

try:
	with open('challenges/questions.json', 'r') as file:
		data = json.loads(file.read())
except Exception as e:
	print(f"An error occurred while loading challenges: {e}")

# 🎯 Role XP Thresholds
ROLE_THRESHOLDS = {
    100: "Beginner Coder",
    300: "Intermediate Coder",
    700: "Elite Coder",
    1500: "HackLeague Champion",
	3000: "HackLeague Legend"
}

GEMINI_KEY = os.getenv('GEMINI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

