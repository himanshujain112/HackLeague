import discord

# Assign Roles based on XP
async def assign_role(user, guild, role_name):
    """Assigns roles based on XP thresholds, creating them if they don't exist."""
    #print(f"🔍 Checking roles for {user.name} with {new_score} XP")

    # Ensure the bot has Manage Roles permission
    if not guild.me.guild_permissions.manage_roles:
        print(f"⚠️ Bot lacks 'Manage Roles' permission in {guild.name}!")
        return "⚠️ I don't have permission to assign roles!"
    
    # for xp, role_name in sorted(ROLE_THRESHOLDS.items(), reverse=True):
        # if new_score >= xp:
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
    bot_highest_position = guild.me.top_role.position
    print(f"Bot Role Position: {bot_highest_position}, Target Role Position: {role.position}")

    if bot_highest_position <= role.position:
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

