import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN, data
from ai import generate
import asyncio

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
bot.intents.members = True
bot.intents.message_content = True

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

@bot.tree.command(name='challenge', description='Generate a coding challenge for the day.')
async def challenge(interaction: discord.Interaction):
    id, diff, ques, hint = data[0]['id'], data[0]['difficulty'], data[0]['question'], data[0]['hint']
    await interaction.response.send_message(
    "🚀 **Coding Challenge of the Day** 🚀\n\n"
    f"📋 **Challenge ID:** {id}\n"
    f"⚡ **Difficulty:** {['🟢 Easy', '🟠 Medium', '🔴 Hard'][['easy','medium','hard'].index(diff.lower())]}\n"
    f"💭 **Question:** {ques}\n"
    f"💡 **Hint:** ||{hint}||\n\n"
    f"@everyone 🔥✨🚀\n"
    "-------------------------"
)
    #await interaction.response.send_message('Challenge generated!')

@bot.tree.command(name='submit', description='Submit a code for review.')
@app_commands.describe(code='The code you want to submit for review.')
async def submit(interaction: discord.Interaction, code: str):
    await interaction.response.defer()
    response = generate(code)
    await interaction.followup.send(f'```{response}```')
    #await interaction.response.send_message('Code submitted!')

@bot.tree.command(name='leaderboard', description='Check your rankings in the server.')
async def leaderboard(ctx):
    await ctx.send('Leaderboard generated!')

bot.run(DISCORD_TOKEN)