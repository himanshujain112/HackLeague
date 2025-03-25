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

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'🚀 Logged in as {bot.user}')

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
    
    # Ensure the bot has the correct permissions
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
                    return "⚠️ Failed to create role!"

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
                    return "⚠️ Failed to assign role!"

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
            user = interaction.guild.get_member(interaction.user.id)
            role_message = await assign_role(user, interaction.guild, new_score) if user else None

            streak_msg = f"🔥 **Streak:** {streak} days!" if streak > 1 else ""
            bonus_msg = f"💎 **Streak Bonus:** {bonus_xp} XP!" if bonus_xp > 0 else ""
            role_msg = f"\n{role_message}" if role_message else ""

            await interaction.followup.send(f"{response}\n\n{streak_msg}\n{bonus_msg}{role_msg}")
        else:
            await interaction.followup.send(response)

    except Exception as e:
        await interaction.followup.send("⚠️ An error occurred while processing your submission. Please try again later.")

@bot.tree.command(name='leaderboard', description='Check your rankings in the server.')
async def leaderboard(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        leaderboardData = dbConn.get_leaderboard(interaction.guild_id)
        await interaction.followup.send(leaderboardData if leaderboardData else "No leaderboard data found.")
    except Exception as e:
        await interaction.followup.send("An error occurred while fetching the leaderboard data. Please try again later.")



@bot.tree.command(name='testrole', description='Test role assignment.')
async def testrole(interaction: discord.Interaction):
    user = interaction.guild.get_member(interaction.user.id)
    role_message = await assign_role(user, interaction.guild, 100)
    await interaction.response.send_message(role_message if role_message else "No role assigned.")



bot.run(DISCORD_TOKEN)
