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


async def no_permission(interaction: discord.Interaction):
    """Send a message when the user lacks permission."""
    await interaction.response.send_message(
        "❌ You don't have permission to create new challenges! \nWait for Admins or Mods to start new challenge (;", ephemeral=True
    )

@bot.tree.command(name='challenge', description='Generate a coding challenge for the day.')
@app_commands.describe(difficulty='The difficulty of the challenge you want to generate.')
@app_commands.checks.has_permissions(manage_guild=True)
async def challenge(interaction: discord.Interaction, difficulty: str = 'easy'):
    guild_id = str(interaction.guild_id)

    # Validate difficulty
    difficulty = difficulty.lower()
    if difficulty not in ['easy', 'medium', 'hard']:
        await interaction.response.send_message("❌ Invalid difficulty! Choose from: `easy`, `medium`, or `hard`.")
        return

    # Fetch last used challenge index from DB
    current_index = dbConn.get_challenge_index(guild_id, difficulty)

    # Get challenges filtered by difficulty
    filtered_data = [item for item in data if item['difficulty'].lower() == difficulty]
    if not filtered_data:
        await interaction.response.send_message(f"❌ No challenges found for difficulty: {difficulty}")
        return

    # Reset index if out of range
    if current_index >= len(filtered_data):
        current_index = 0  

    # Get current challenge
    challenge = filtered_data[current_index]
    id, ques, hint, test_input, expected_output = challenge['id'], challenge['question'], challenge['hint'], challenge['input'], challenge['output']

    # Update challenge index in DB
    new_index = current_index + 1
    dbConn.update_challenge_index(guild_id, difficulty, new_index)

    await interaction.response.send_message(
        "🚀 **Coding Challenge of the Day** 🚀\n\n"
        f"📋 **Challenge ID:** {id}\n"
        f"⚡ **Difficulty:** {['🟢 Easy', '🟠 Medium', '🔴 Hard'][['easy', 'medium', 'hard'].index(difficulty)]}\n"
        f"💭 **Question:** {ques}\n"
        f"💡 **Hint:** ||{hint}||\n\n"
        f"🔍 **Example Input:** `{test_input}`\n"
        f"🎯 **Example Output:** `{expected_output}`\n"
        f"@everyone 🔥✨🚀\n"
        "-------------------------\n"
        "💙 Love HackLeague? Consider supporting the project! [Ko-Fi](<https://ko-fi.com/himanshuj112>)"
    )

# Handle permission errors globally
@challenge.error
async def challenge_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await no_permission(interaction)

@bot.tree.command(name='submit', description='Submit a code for review.')
@app_commands.describe(question_id='The ID of the question you are submitting a solution for.', code='The code you want to submit for review.')
async def submit(interaction: discord.Interaction, question_id: int, code: str):
    try:
        await interaction.response.defer()
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)

        # **Check if user has already solved the question**
        if dbConn.has_solved_question(user_id, guild_id, question_id):
            await interaction.followup.send("✅ You've already solved this challenge! You can't submit again for XP.")
            return

        # Get question details
        question_data = next((item for item in data if item['id'] == question_id), None)
        if question_data is None:
            await interaction.followup.send("❌ Question ID not found.")
            return

        # Send code for AI review
        response = await generate(code, question_data['question'])

        # If correct, award XP and store solved challenge
        if "Correct!" in response or "correct!" in response:
            dbConn.update_xp(user_id, guild_id, 50)  # Award XP
            dbConn.mark_question_as_solved(user_id, guild_id, question_id)  # Save completion

        await interaction.followup.send(response)

    except Exception as e:
        await interaction.followup.send("⚠️ An error occurred while processing your submission. Please try again later.")


@bot.tree.command(name='leaderboard', description='Check your rankings in the server.')
async def leaderboard(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        leaderboardData = dbConn.get_leaderboard(interaction.guild_id)
        if not leaderboardData:
            await interaction.followup.send("No leaderboard data found.")
            return
        await interaction.followup.send(leaderboardData)
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching the leaderboard data. Please try again later.")
        
bot.run(DISCORD_TOKEN)
