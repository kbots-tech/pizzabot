

"""These lines import the needed libraries, you'll also need to setup your requirements.txt for this (see readme)"""
from discord.ext import commands



bot = commands.Bot(
    command_prefix="d.",  # Change to desired prefix
    case_insensitive=True  # Commands aren't case-sensitive
)

"""This is the bot load function, you should see it print a message if it loaded in properly"""


@bot.event
async def on_ready():  # When the bot is ready
    print(str(bot.user) + ' is online')  # Prints the bots username and identifier

"""This is where you will add the additional cogs, you will need to add them as cogs.filename and they should be placed 
in the cogs folder.
Each time you add a final cog you should add it here so it will autoload on restart. For testing you can use the load 
cog command."""

extensions = [
    'cogs.pizza'
]

"""You won't need to touch this, this just makes sure this is the proper file"""
if __name__ == '__main__':  # Ensures this is the file being ran
    for extension in extensions:
        print(f"Loaded {extension}")
        bot.load_extension(extension)  # Loads every extension.

"""This is where you should put your bot token, the instructions for generating that can be found in the readme file"""
bot.run('BOT TOKEN GOES HERE')  # Starts the bot
