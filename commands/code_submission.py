import discord
from discord.ext import commands
from database.db import DBManager
from config import data, ROLE_THRESHOLDS
from utils.assign_roles import assign_role
from ai.validator import generate

class CodeSubmission(commands.Cog):
    """Handles AI Validation for user code submissions."""

    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()  # ✅ Properly initializes the database manager

    @discord.app_commands.command(name="submit", description="Submit your code for validation.")
    async def submit(self, interaction: discord.Interaction, question_id: int, code: str):
        """Handles user code submissions."""
        await interaction.response.defer()  # ✅ Defer response for AI processing

        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild_id)

            # ✅ Check if the user already solved this question
            if self.db.has_solved_question(user_id, guild_id, question_id):
                await interaction.followup.send("✅ You've already solved this challenge! You can't submit again!")
                return

            # ✅ Retrieve question details from config
            question_data = next((item for item in data if item['id'] == question_id), None)
            if question_data is None:
                await interaction.followup.send("❌ Question ID not found.")
                return

            # ✅ Send the code to AI for review
            response = await generate(user_id, code, question_data['question'])

            # ✅ If the answer is correct, update XP & assign a role
            if "Correct!" in response or "correct!" in response:
                new_score, streak, bonus_xp = self.db.update_xp(user_id, guild_id, 50)
                self.db.mark_question_as_solved(user_id, guild_id, question_id)

                # ✅ Assign a new role based on XP
                for xp, role_name in sorted(ROLE_THRESHOLDS.items(), reverse=True):
                    if new_score >= xp:
                        print(f"🔍 Assigning role '{role_name}' to {interaction.user.name} with {new_score} XP")
                        await assign_role(interaction.user, interaction.guild, role_name) if interaction.user else None
                        await interaction.followup.send(f"{response}\n 🎉 Congrats <@{interaction.user.id}>, you've earned the **{role_name}** role!")
                        return
                await interaction.followup.send(response)
            else:
                await interaction.followup.send(response)  # Send AI response if incorrect

        except Exception as e:
            await interaction.followup.send("⚠️ An error occurred while processing your submission. Please try again later!")
            print(f"❌ Error in `submit_code`: {e}")  # ✅ Log the error for debugging

async def setup(bot):
    """Loads the CodeSubmission Cog."""
    await bot.add_cog(CodeSubmission(bot))
