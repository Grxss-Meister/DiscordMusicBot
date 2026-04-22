import discord
from discord.ext import commands
from music_cog import music_cog
from help_cog import help_cog
import os

intents = discord.Intents.default()
intents.message_content = True  
         
bot = commands.Bot(command_prefix="!", intents=intents)

bot.remove_command('help')

async def load_extensions():
    await bot.add_cog(music_cog(bot))
    await bot.add_cog(help_cog(bot))

@bot.event
async def on_ready():
    print(f'{bot.user} ist jetzt online!')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "token.txt"), "r") as file:
    token = file.readlines()[0].strip()

import asyncio
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)
        
asyncio.run(main())