import discord
from discord.ext import commands
from discord.ui import View, Button

class Core(commands.Cog):
    """Core commands for the bot."""

    def __init__(self, bot):
        self.bot = bot
    
    @discord.app_commands.command(name='ping')
    async def ping(self, interaction: discord.interactions):
        """Check if the bot is online and responsive."""
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        await interaction.response.send_message(f'🏓 Pong! Latency: {latency}ms', ephemeral=True)

    @discord.app_commands.command(name="help")
    async def help(self, interaction: discord.interactions):
        """Displays a list of available commands."""
        embed = discord.Embed(
            title="📜 HackLeague Bot Commands",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )

        embed.add_field(name="🎯 General Commands", value="`/ping` - Check bot latency\n`/help` - Show this help message", inline=False)
        embed.add_field(name="⚙ Admin", value="`/challenge` - Start a daily coding challenge (easy, medium & hard)\n`/assign_role` - Assign a role to users.", inline=False)
        #embed.add_field(name="📜 Submissions", value="`/submit <question_id> <code>` - Submit code for AI validation", inline=False)
        embed.add_field(name="🏆 Leaderboard", value="`/leaderboard` - Show XP leaderboard", inline=False)
        embed.add_field(name="🔥 Streaks", value="`/streaks` - Check your current streaks.", inline=False)
        

        embed.set_footer(text="Use /help to view this list anytime! 🚀")
        view = supportView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class supportView(View):
    """Interactive UI for submitting coding challenges and donating."""
    def __init__(self):
        super().__init__(timeout=None)  # ✅ Ensure persistence
        self.add_item(DonateButton())
class DonateButton(Button):
    """Button for donations."""
    def __init__(self):
        super().__init__(label="Support HackLeague!", style=discord.ButtonStyle.link, url="https://ko-fi.com/himanshuj112")

async def setup(bot):
    """Load the Core cog."""
    await bot.add_cog(Core(bot))
    bot.add_view(supportView())