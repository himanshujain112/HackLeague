import asyncio
import discord
import datetime
from discord.ext import commands
from config import DISCORD_TOKEN, COMMAND_MODULES
from utils.logger import get_logger
#from memory_profiler import profile

logger = get_logger("app", "logs/app.log")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

#Load command modules
#@profile
async def load_commands():
    for file in COMMAND_MODULES:
        try:
            await bot.load_extension(file)
            #print(f"Command {file} loaded successfully.")
        except Exception as e:
            logger.info(f"Failed to load extension {file}: {e}")
            #print(f"Failed to load extension {file}: {e}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.Game(name="Vibing | /help for more!"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        logger.error(f"Command not found: {ctx.command} - {error}")
        #await ctx.send("Command not found. Use '/help' to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        logger.error(f"Missing required argument: {ctx.command} - {error}")
        #await ctx.send("Missing required argument.")
    elif isinstance(error, commands.BadArgument):
        logger.error(f"Bad argument: {ctx.command} - {error}")
        #await ctx.send("Bad argument.")
    else:
        logger.error(f"An error occurred: {ctx.command} - {error}")
        #await ctx.send(f"An error occurred: {error}")


#start bot
async def main():
    async with bot:
        await load_commands()
        await bot.start(DISCORD_TOKEN)
        logger.info("Bot started at: ", datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
asyncio.run(main())
