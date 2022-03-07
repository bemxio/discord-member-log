from discord.ext import commands
from discord import Intents
import toml

with open("config.toml", "r") as file:
    config = toml.load(file)

# member intent is required, for obvious reasons
intents = Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=config["BOT_PREFIX"],
    #help_command=None,
    intents=intents
)
bot.config = config # for global access in cogs

# loading cogs
bot.load_extension("cogs.events")
bot.load_extension("cogs.logging")

bot.run(config["BOT_TOKEN"])