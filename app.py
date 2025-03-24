import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN, data
from ai import generate
from leaderboard import DBManager

dbConn = DBManager()
print("Database connected", dbConn)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
bot.intents.members = True
bot.intents.message_content = True
bot.intents.presences = True

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

@commands.has_role('Admin', 'Moderator')
@bot.tree.command(name='challenge', description='Generate a coding challenge for the day.')
@app_commands.describe(difficulty='The difficulty of the challenge you want to generate.')
async def challenge(interaction: discord.Interaction, difficulty: str='easy'):
    if not hasattr(bot, 'challenge_index'):
        bot.challenge_index = 0

    filtered_data = [item for item in data if item['difficulty'].lower() == difficulty.lower()]
    if not filtered_data:
        await interaction.response.send_message(f"No challenges found for difficulty: {difficulty}")
        return

    bot.challenge_index = (bot.challenge_index + 1) % len(filtered_data)
    
    id, diff, ques, hint, test_input, expected_output = filtered_data[bot.challenge_index]['id'], filtered_data[bot.challenge_index]['difficulty'], filtered_data[bot.challenge_index]['question'], filtered_data[bot.challenge_index]['hint'], filtered_data[bot.challenge_index]['input'], filtered_data[bot.challenge_index]['output']
    await interaction.response.send_message(
    "🚀 **Coding Challenge of the Day** 🚀\n\n"
    f"📋 **Challenge ID:** {id}\n"
    f"⚡ **Difficulty:** {['🟢 Easy', '🟠 Medium', '🔴 Hard'][['easy','medium','hard'].index(diff.lower())]}\n"
    f"💭 **Question:** {ques}\n"
    f"💡 **Hint:** ||{hint}||\n\n"
    f"🔍 **Example Input:** `{test_input}`\n"
    f"🎯 **Example Output:** `{expected_output}`\n"
    f"@everyone 🔥✨🚀\n"
    "-------------------------"
)

@bot.tree.command(name='submit', description='Submit a code for review.')
@app_commands.describe(question_id='The ID of the question you are submitting a solution for.', code='The code you want to submit for review.')
async def submit(interaction: discord.Interaction, question_id: int, code: str):
    try:
        await interaction.response.defer()
        question_data = next((item for item in data if item['id'] == question_id), None)
        if question_data is None:
            await interaction.followup.send("Question ID not found.")
            return
        #print(question_data['question'])
        response = await generate(code, question_data['question'])
        if "Correct!" in response or "correct!" in response:
            dbConn.update_xp(interaction.user.id, interaction.guild_id, 50)
        await interaction.followup.send(response)
        #await interaction.response.send_message('Code submitted!')
    except Exception as e:
        await interaction.followup.send("An error occurred while processing your submission. Please try again later.")

@bot.tree.command(name='leaderboard', description='Check your rankings in the server.')
async def leaderboard(interaction: discord.Interaction):
    leaderboardData = dbConn.get_leaderboard(interaction.guild_id)
    if not leaderboardData:
        await interaction.response.send_message("No leaderboard data found.")
        return
    await interaction.response.send_message(leaderboardData)

bot.run(DISCORD_TOKEN)
