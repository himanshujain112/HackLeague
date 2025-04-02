import discord
from discord.ext import commands
from discord.ui import Modal, TextInput, View
from database.hackathonDB import hackathonDB

hackDB = hackathonDB()
class Hackathon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="hackathon", description="Create a hackathon event")
    @discord.app_commands.checks.has_permissions(manage_guild=True)
    async def hackathonSetup(self, interaction: discord.Interaction):
        try:
            print("Hackathon command invoked")
            await interaction.response.send_message(view=HackathonView(), ephemeral=True)
        except Exception as e:
            print("Error at hakathon setup command", e)


class HackathonView(View):
    def __init__(self, timeout = None):
        super().__init__()
    
    @discord.ui.button(label="Create Hackathon", style=discord.ButtonStyle.primary)
    async def create_hackathon(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.send_modal(HackathonSetupModal())
        except Exception as e:
            print("Error at hackathon setup modal", e)
            await interaction.response.send_message("❌ Error while creating hackathon!", ephemeral=True)
    @discord.ui.button(label="View Previous Hackathons", style=discord.ButtonStyle.secondary)
    async def view_previous_hackathons(self, interaction: discord.Interaction, button: discord.ui.Button):
        hacks = hackDB.get_hackathons(interaction.guild_id)
        await interaction.response.send_message(hacks)

class HackathonSetupModal(Modal):
    def __init__(self):
        try:
            super().__init__(title="Setup Hackathon", timeout=None)
            print("HackathonSetupModal initialized")

            self.hackathon_title = TextInput(label="Hackathon Title", required=True)
            self.description = TextInput(label="Description", style=discord.TextStyle.long, required=True)
            self.tech_stack = TextInput(label="Tech Stack", required=True)
            self.start_date = TextInput(label="Start Date (YYYY-MM-DD)", required=True)
            self.end_date = TextInput(label="End Date (YYYY-MM-DD)", required=True)
            self.add_item(self.hackathon_title)
            self.add_item(self.description)
            self.add_item(self.tech_stack)
            self.add_item(self.start_date)
            self.add_item(self.end_date)
            print("HackathonSetupModal initialized")
        except Exception as e:
            print("Error at hackathon setup modal", e)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            hackDB.add_hackathon(interaction.guild_id, title=self.hackathon_title.value, description=self.description.value, tech_stack=self.tech_stack.value, start_date=self.start_date.value, end_date=self.end_date.value)
            embed = discord.Embed(
                title=f"🏆 {self.hackathon_title.value}",
                description=self.description.value,
                color=discord.Color.blue()
            )
            embed.add_field(name="🛠 Tech Stack", value=self.tech_stack.value, inline=False)
            embed.add_field(name="📅 Start Date", value=self.start_date.value, inline=True)
            embed.add_field(name="📅 End Date", value=self.end_date.value, inline=True)
            embed.set_footer(text="Will be waiting for your awesome projects!")
            print(f"Created hackathon: {self.hackathon_title.value} in {interaction.guild.name}")
            await interaction.response.send_message(embed=embed, view=HackathonResponseView())
        except Exception as e:
            print("Error at hackathon setup modal submit", e)
            await interaction.response.send_message("❌ Error while creating hackathon!", ephemeral=True)
    
class HackathonResponseView(View):
    def __init__(self, timeout = None):
        super().__init__(timeout=timeout)
    
    @discord.ui.button(label="Join Hackathon", style=discord.ButtonStyle.primary)
    async def join_hackathon(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ You have joined the hackathon!", ephemeral=True)
    @discord.ui.button(label="Submit Project", style=discord.ButtonStyle.success)
    async def submit_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Logic to submit project
        try:
            hackathon_id = hackDB.get_hackathon_id(interaction.guild_id)
            if hackathon_id is not None:
                project_sub = hackDB.add_submission(hackathon_id, interaction.user.id, )
            await interaction.response.send_message("✅ Project submitted successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Project submission failed, pls try again in some time!", ephemeral=True)

class ProjectSubmissionModal(Modal):
    def __init__(self, *, title = "Enter Project Repo Link...", timeout = None, custom_id = ...):
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        
        self.project_repo = TextInput(label="Project Repo: ", style=discord.TextStyle.long, placeholder="Your Project Github Repo/Link here...", required=True)
        self.add_item(self.project_repo)
    
    async def on_submit(self, interaction):
        try:
            hackathon_id = hackDB.get_hackathon_id(interaction.guild_id)
            if hackathon_id is not None:
                project_sub = hackDB.add_submission(hackathon_id, interaction.user.id, self.project_repo.value)
                if project_sub:
                    await interaction.response.send_message("✅ Project submitted successfully!", ephemeral=True)
                await interaction.response.send_message("Project Submission Failed, pls try again!", ephemeral=True)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Hackathon(bot))