import os
from dotenv import load_dotenv
import json
load_dotenv()

with open('challenges/questions.json', 'r') as file:
	data = json.loads(file.read())



GEMINI_KEY = os.getenv('GEMINI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

