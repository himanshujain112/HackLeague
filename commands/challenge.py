# import discord
# from discord.ext import commands
# from database.db import DBManager
# from config import data

# class Challenges(commands.Cog):
#     """To start the challenges"""

#     def __init__(self, bot):
#         self.bot = bot
#         self.db = DBManager()  # Initialize the database manager
    
#     @discord.app_commands.command(name="daily_challenge", description="Generates a coding challenge for the day!")
#     @discord.app_commands.checks.has_permissions(manage_guild=True)
#     async def daily_challenge(self, interaction: discord.interactions, difficulty: str = 'easy'):
#         guild_id = str(interaction.guild_id)
#         difficulty = difficulty.lower()

#         #Validate difficulty
#         if difficulty not in ['easy', 'medium', 'hard']:
#             await interaction.response.send_message("❌ Invalid difficulty! Choose from: `easy`, `medium`, or `hard`.", ephemeral=True)
#             return
    
#         # Fetch last used challenge index from DB
#         current_index = self.db.get_challenge_index(guild_id, difficulty)
#         filtered_data = [item for item in data if item['difficulty'].lower() == difficulty]

#         if not filtered_data:
#             await interaction.response.send_message(f"❌ No challenges found for difficulty: {difficulty}")
#             return
    
#         #Reset index if out of range
#         if current_index >= len(filtered_data):
#             current_index=0
        
#         #Get current Challenge

#         challenge = filtered_data[current_index]
#         id, ques, hint, test_input, expected_output = challenge['id'], challenge['question'], challenge['hint'], challenge['input'], challenge['output']

#         # Update challenge index in DB
#         new_index = current_index + 1
#         self.db.update_challenge_index(guild_id, difficulty, new_index)

#         embed = discord.Embed(
#         title="🚀 **Coding Challenge of the Day** 🚀",
#         description=f"**Challenge ID:** {id}\n"
#                 f"**Difficulty:** {['🟢 Easy', '🟠 Medium', '🔴 Hard'][['easy', 'medium', 'hard'].index(difficulty)]}",
#         color=discord.Color.blue()
#         )

#         # First row (side by side)
#         embed.add_field(name="💭 Question", value=ques, inline=True)
#         embed.add_field(name="💡 Hint", value=f"||{hint}||", inline=True)

#         # Ensure an empty field to balance the next row
#         embed.add_field(name="\u200b", value="\u200b", inline=True)  # Invisible spacer

#         # Second row (side by side)
#         embed.add_field(name="🔍 Example Input", value=f"`{test_input}`", inline=True)
#         embed.add_field(name="🎯 Example Output", value=f"`{expected_output}`", inline=True)

#         # Support Link (New Row)
#         embed.add_field(
#             name="💙 Love HackLeague?", 
#             value="[Support on Ko-Fi](https://ko-fi.com/himanshuj112)", 
#             inline=False  # Forces it to be on a new row
#         )

        
#     #     await interaction.response.send_message(
#     #     f"🚀 **Coding Challenge of the Day** 🚀\n\n"
#     #     f"📋 **Challenge ID:** {id}\n"
#     #     f"⚡ **Difficulty:** {['🟢 Easy', '🟠 Medium', '🔴 Hard'][['easy', 'medium', 'hard'].index(difficulty)]}\n"
#     #     f"💭 **Question:** {ques}\n"
#     #     f"💡 **Hint:** ||{hint}||\n\n"
#     #     f"🔍 **Example Input:** `{test_input}`\n"
#     #     f"🎯 **Example Output:** `{expected_output}`\n"
#     #     f"@everyone 🔥✨🚀\n"
#     #     "-------------------------\n"
#     #     "💙 Love HackLeague? Consider supporting the project! [Ko-Fi](<https://ko-fi.com/himanshuj112>)"
#     # )
#         await interaction.response.send_message(embed=embed, ephemeral=False)


#     # Handle permission errors globally
#     async def no_permission(self, interaction: discord.Interaction):
#         """Send a message when the user lacks permission."""
#         await interaction.response.send_message(
#             "❌ You don't have permission to create new challenges!\nWait for Admins or Mods to start a new challenge. 😉",
#             ephemeral=True
#         )

#     @daily_challenge.error
#     async def challenge_error(self, interaction: discord.Interaction, error):
#         if isinstance(error, discord.app_commands.MissingPermissions):
#             await self.no_permission(interaction)

# async def setup(bot):
#     await bot.add_cog(Challenges(bot))

import discord
from discord.ext import commands
from database.db import DBManager
from config import data, ROLE_THRESHOLDS
from utils.assign_roles import assign_role
from ai.validator import generate

class CodeChallenge(commands.Cog):
    """Handles coding challenges and user submissions."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()

    @discord.app_commands.command(name="challenge", description="Generate and submit coding challenges!")
    @discord.app_commands.checks.has_permissions(manage_guild=True)
    async def challenge(self, interaction: discord.Interaction, difficulty: str = 'easy'):
        """Generates a coding challenge for the user."""
        guild_id = str(interaction.guild_id)
        difficulty = difficulty.lower()

        if difficulty not in ['easy', 'medium', 'hard']:
            await interaction.response.send_message("❌ Invalid difficulty! Choose from: `easy`, `medium`, or `hard`.", ephemeral=True)
            return
        
        current_index = self.db.get_challenge_index(guild_id, difficulty)
        filtered_data = [item for item in data if item['difficulty'].lower() == difficulty]
        if not filtered_data:
            await interaction.response.send_message(f"❌ No challenges found for difficulty: {difficulty}")
            return
        
        if current_index >= len(filtered_data):
            current_index = 0
        
        challenge = filtered_data[current_index]
        new_index = current_index + 1
        self.db.update_challenge_index(guild_id, difficulty, new_index)
        
        embed = discord.Embed(
            title="🚀 **Coding Challenge of the Day!** 🚀",
            description=f"**Challenge ID:** {challenge['id']}\n**Difficulty:** {difficulty.capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="💭 Question", value=challenge['question'], inline=False)
        embed.add_field(name="💡 Hint", value=f"||{challenge['hint']}||", inline=False)
        embed.add_field(name="🔍 Example Input", value=f"`{challenge['input']}`", inline=True)
        embed.add_field(name="🎯 Example Output", value=f"`{challenge['output']}`", inline=True)
        
        view = ChallengeView()
        await interaction.response.send_message(embed=embed, view=view)

    async def submit_code(self, interaction: discord.Interaction, question_id: int, code: str):
        """Handles user code submissions."""
        await interaction.response.defer()
        try:
            user_id, guild_id = str(interaction.user.id), str(interaction.guild_id)

            # Check if the user has already solved the question
            if self.db.has_solved_question(user_id, guild_id, question_id):
                await interaction.followup.send("✅ You've already solved this challenge! You can't submit again!", ephemeral=True)
                return

            # Get question data
            print(f"Provided question_id: {question_id} (Type: {type(question_id)})")
            print(f"Available IDs in data: {[item['id'] for item in data]}")
            print(f"ID types in data: {[type(item['id']) for item in data]}")

            question_data = next((item for item in data if item['id'] == int(question_id)), None)
            print(question_data)
            #print(f"❌ Question ID not found. Provided ID: {question_id}")
            if not question_data:
                await interaction.followup.send("❌ Question ID not found.", ephemeral=True)
                return

            # Generate response
            response = await generate(user_id, code, question_data['question'])

            if "correct!" in response.lower() or "congrats!" in response.lower():
                # Update XP and mark question as solved
                new_score, _, _ = self.db.update_xp(user_id, guild_id, 50)
                self.db.mark_question_as_solved(user_id, guild_id, question_id)

                # Find the highest role user qualifies for
                new_role_name = None
                for xp, role_name in sorted(ROLE_THRESHOLDS.items(), reverse=True):
                    if new_score >= xp:
                        new_role_name = role_name
                        break  # Stop at the first matching role (highest one)

                if new_role_name:
                    guild = interaction.guild
                    new_role = discord.utils.get(guild.roles, name=new_role_name)

                    # ✅ If the role does not exist, create it
                    if new_role is None:
                        try:
                            new_role = await guild.create_role(
                                name=new_role_name,
                                reason="Auto-created role for XP system"
                            )
                            print(f"✅ Created new role: `{new_role_name}`")
                        except discord.Forbidden:
                            await interaction.followup.send("⚠️ Bot lacks permission to create roles. Please check role permissions.")
                            print(f"❌ Bot lacks permission to create `{new_role_name}`.")
                            return
                        except Exception as e:
                            await interaction.followup.send(f"⚠️ Error creating role `{new_role_name}`. Contact an admin.")
                            print(f"❌ Error creating role `{new_role_name}`: {e}")
                            return

                    # Find user's current role from ROLE_THRESHOLDS
                    user_roles = interaction.user.roles
                    old_role = next(
                        (discord.utils.get(guild.roles, name=role) for role in ROLE_THRESHOLDS.values() if discord.utils.get(guild.roles, name=role) in user_roles), 
                        None
                    )

                    # Remove old role if exists
                    if old_role and old_role != new_role:
                        await interaction.user.remove_roles(old_role)

                    # Assign the new role
                    if new_role not in user_roles:
                        try:
                            await interaction.user.add_roles(new_role)
                            await interaction.followup.send(
                                f"{response}\n 🎉 Congrats <@{interaction.user.id}>, you've been promoted to **{new_role_name}**!",
                                ephemeral=False
                            )
                            print(f"✅ Assigned role `{new_role_name}` to {interaction.user.id}")
                        except discord.Forbidden:
                            await interaction.followup.send("⚠️ Bot lacks permission to manage roles. Please check role hierarchy.", ephemeral=True)
                            print(f"❌ Bot lacks permission to assign `{new_role_name}`.")
                        return
            else:
                await interaction.followup.send(response, ephemeral=False)
                return
            await interaction.followup.send(response, ephemeral=False)
        except Exception as e:
            await interaction.followup.send("⚠️ An error occurred while processing your submission. Please try again later!", ephemeral=True)
            print(f"❌ Error in `submit_code`: {e}")


class ChallengeView(discord.ui.View):
    """Interactive UI for submitting coding challenges and donating."""
    def __init__(self):
        super().__init__(timeout=None)  # ✅ Ensure persistence
        self.add_item(DonateButton())

    @discord.ui.button(label="Submit Code", style=discord.ButtonStyle.primary, custom_id="submit_code_button")
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CodeSubmissionModal())

class CodeSubmissionModal(discord.ui.Modal, title="Submit Your Code"):
    """Modal for users to submit their code."""
    question_id =discord.ui.TextInput(label="Enter Question Id", style=discord.TextStyle.short, placeholder="Write Question id here...")
    code = discord.ui.TextInput(label="Enter your code", style=discord.TextStyle.paragraph, placeholder="Write your solution here...")
    
    def __init__(self):
        super().__init__()
    
    async def on_submit(self, interaction: discord.Interaction):
        cog = interaction.client.get_cog("CodeChallenge")
        if cog:
            await cog.submit_code(interaction, self.question_id.value, self.code.value)

class DonateButton(discord.ui.Button):
    """Button for donations."""
    def __init__(self):
        super().__init__(label="Support HackLeague!", style=discord.ButtonStyle.link, url="https://ko-fi.com/himanshuj112")

async def setup(bot):
    """Registers the cog with the bot and ensures persistent views."""
    await bot.add_cog(CodeChallenge(bot))
    bot.add_view(ChallengeView())  # ✅ Ensuring view persistence
