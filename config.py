import os
from dotenv import load_dotenv
import json
load_dotenv()

try:
	with open('challenges/questions.json', 'r') as file:
		data = json.loads(file.read())
except Exception as e:
	print(f"An error occurred while loading challenges: {e}")


GEMINI_KEY = os.getenv('GEMINI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

