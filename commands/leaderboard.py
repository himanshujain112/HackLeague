import discord
from discord.ext import commands
from database.db import DBManager

class Leaderboard(commands.Cog):
    """Leaderboard & XP System."""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()  # Initialize the database manager
    
    @discord.app_commands.command(name="leaderboard", description="Show the XP leaderboard")
    async def leaderboard(self, interaction: discord.interactions):
        """Displays the XP leaderboard."""
        await interaction.response.defer()  # ✅ Defer the response if processing takes time

        try:
            leaderboard_data = self.db.get_leaderboard(interaction.guild_id)  # Fetch leaderboard from DB

            embed = discord.Embed(
                title="🏆 Leaderboard",
                description="Top XP earners in this server:",
                color=discord.Color.blue()
            )

            if leaderboard_data:
                for i, row in enumerate(leaderboard_data, start=1):
                    user_id, score, streak = row
                    user = await self.bot.fetch_user(user_id)  # Fetch user object
                    username = user.name if user else f"Unknown User ({user_id})"  # ✅ Handle missing users
                    embed.add_field(
                        name=f"{i}. @{username}",
                        value=f"**{score} XP** | 🔥 Streak: {streak} Days",
                        inline=False
                    )
            else:
                embed.description = "No leaderboard data found."

            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send("An error occurred while fetching the leaderboard. Please try again later.", ephemeral=True)
    
    @discord.app_commands.command(name="streaks", description="Show users current streaks.")
    async def streaks(self, interaction: discord.interactions):
        """Displays users current streaks."""
        try:
            #await interaction.response.defer(thinking=True)  # Defer the response if processing takes time
            streak = self.db.get_streak(str(interaction.user.id), str(interaction.guild_id))
            if streak is None or streak <= 0:
                embed = discord.Embed(
                    title="🔥 Your Streak",
                    color=discord.Color.red()
                )
                embed.description = "You don't have any streak yet. Participate in challenges to start your streak!"
            else:
                embed = discord.Embed(
                    title="🔥 Your Streak",
                    description=f"Your current streak is **{streak}** days!",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Keep up the great work! Participate in challenges to maintain your streak.")
               # embed.color = discord.Color.red()
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send("An error occurred while fetching your streak data. Please try again later.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
