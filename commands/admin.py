import discord
from discord.ext import commands
from utils.assign_roles import assign_role

class Admin(commands.Cog):
    """Admin-only commands for managing the bot."""

    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="assign_role", description="Assign a role to a user.")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def assign_role(self, interaction: discord.Interaction, user: discord.User, role: discord.Role):
        """Assign a role to a user."""
        await interaction.response.defer(thinking=True)
        try:
            member = interaction.guild.get_member(user.id)
            if member:
                await assign_role(member, interaction.guild, role.name)
                await interaction.followup.send(f"✅ Role `{role.name}` assigned to {user.mention}!")
            else:
                await interaction.followup.send("❌ User not found in the server.")
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to assign role: {e}")
        

    @assign_role.error
    async def assign_role_error(self, interaction: discord.Interaction, error):
        """Handles errors for the assign_role command."""
        if isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ An error occurred: {error}", ephemeral=True)
            
async def setup(bot):
    """Load the Admin cog."""
    await bot.add_cog(Admin(bot))