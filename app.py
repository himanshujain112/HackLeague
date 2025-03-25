import discord
from discord.ext import commands
from discord import app_commands
from config import DISCORD_TOKEN, data, ROLE_THRESHOLDS
from ai import generate
from leaderboard import DBManager

dbConn = DBManager()
print("✅ Database connected", dbConn)

# Bot Setup
bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())
bot.intents.members = True
bot.intents.message_content = True
bot.intents.presences = True
bot.intents.voice_states = False  # Explicitly disable voice support

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Synced Commands. 🚀 Logged in as {bot.user}')

# Handle permission errors globally
async def no_permission(interaction: discord.Interaction):
    """Send a message when the user lacks permission."""
    await interaction.response.send_message(
        "❌ You don't have permission to create new challenges!\nWait for Admins or Mods to start a new challenge. 😉",
        ephemeral=True
    )

@bot.tree.command(name='challenge', description='Generate a coding challenge for the day.')
@app_commands.describe(difficulty='The difficulty of the challenge you want to generate.')
@app_commands.checks.has_permissions(manage_guild=True)
async def challenge(interaction: discord.Interaction, difficulty: str = 'easy'):
    guild_id = str(interaction.guild_id)
    difficulty = difficulty.lower()

    # Validate difficulty
    if difficulty not in ['easy', 'medium', 'hard']:
        await interaction.response.send_message("❌ Invalid difficulty! Choose from: `easy`, `medium`, or `hard`.")
        return

    # Fetch last used challenge index from DB
    current_index = dbConn.get_challenge_index(guild_id, difficulty)
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
        f"🚀 **Coding Challenge of the Day** 🚀\n\n"
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

@challenge.error
async def challenge_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await no_permission(interaction)

# Assign Roles based on XP
async def assign_role(user, guild, new_score):
    """Assigns roles based on XP thresholds, creating them if they don't exist."""
    print(f"🔍 Checking roles for {user.name} with {new_score} XP")

    # Ensure the bot has Manage Roles permission
    if not guild.me.guild_permissions.manage_roles:
        print(f"⚠️ Bot lacks 'Manage Roles' permission in {guild.name}!")
        return "⚠️ I don't have permission to assign roles!"
    
    for xp, role_name in sorted(ROLE_THRESHOLDS.items(), reverse=True):
        if new_score >= xp:
            role = discord.utils.get(guild.roles, name=role_name)

            # **Create role if missing**
            if role is None:
                try:
                    role = await guild.create_role(name=role_name, colour=discord.Colour.random())
                    print(f"🆕 Created new role: {role_name}")
                except discord.Forbidden:
                    print(f"⚠️ Missing permission to create role: {role_name}")
                    return "⚠️ I don't have permission to create roles!"
                except Exception as e:
                    print(f"❌ Error creating role: {e}")
                    return f"⚠️ Failed to create role! Error: {e}"

            # **Check bot's highest role position**
            bot_member = guild.me
            print(f"Bot Role Position: {bot_member.top_role.position}, Target Role Position: {role.position}")

            if bot_member.top_role.position <= role.position:
                print(f"⚠️ Cannot assign '{role_name}', bot's role is too low in hierarchy!")
                return f"⚠️ I can't assign the **{role_name}** role because my role is below it!"

            # **Assign role to the user**
            if role not in user.roles:
                try:
                    await user.add_roles(role)
                    print(f"🎉 Assigned '{role_name}' to {user.name}!")
                    return f"🎉 Congrats <@{user.id}>, you've earned the **{role_name}** role!"
                except discord.Forbidden:
                    print(f"⚠️ Missing permission to assign '{role_name}'!")
                    return "⚠️ I don't have permission to assign roles!"
                except Exception as e:
                    print(f"❌ Error assigning role: {e}")
                    return f"⚠️ Failed to assign role! Error: {e}"

    return None  # No new role assigned

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

        # **Get question details**
        question_data = next((item for item in data if item['id'] == question_id), None)
        if question_data is None:
            await interaction.followup.send("❌ Question ID not found.")
            return

        # **Send code for AI review**
        response = await generate(code, question_data['question'])

        # **If correct, update XP and track streaks**
        if "Correct!" in response or "correct!" in response:
            new_score, streak, bonus_xp = dbConn.update_xp(user_id, guild_id, 50)
            dbConn.mark_question_as_solved(user_id, guild_id, question_id)

            # **Assign role based on new XP**
            role_message = await assign_role(interaction.user, interaction.guild, new_score) if interaction.user else None

            role_msg = f"\n{role_message}" if role_message else ""

            await interaction.followup.send(f"{response}\n\n{role_msg}")
        else:
            await interaction.followup.send(response)

    except Exception as e:
        await interaction.followup.send(f"⚠️ An error occurred while processing your submission: {e}")

@bot.tree.command(name='leaderboard', description='Check your rankings in the server.')
async def leaderboard(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        leaderboardData = dbConn.get_leaderboard(interaction.guild_id)
        await interaction.followup.send(leaderboardData if leaderboardData else "No leaderboard data found.")
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching the leaderboard data. Please try again later.")

@bot.tree.command(name='streak', description='Check your current streak.')
async def streak(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        streak = dbConn.get_streak(str(interaction.user.id), str(interaction.guild_id))
        await interaction.followup.send(f"🔥 **Current Streak:** {streak} days!")
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching your streak data. Please try again later.")
        
bot.run(DISCORD_TOKEN)
