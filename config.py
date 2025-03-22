import os
from dotenv import load_dotenv
import json


with open('challenges/questions.json', 'r') as file:
	data = json.loads(file.read())

load_dotenv()

GEMINI_KEY = os.getenv('GEMINI_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

