import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embedOrange = 0xeab148 #You can the change color to your liking.
        
    @commands.Cog.listener()
    async def on_ready(self):
        sendToChannels = []
        for guild in self.bot.guilds:
            channel = guild.text_channels[0]
            sendToChannels.append(channel)
        helloEmbed = discord.Embed(
            title = "Hello there", #You can put any title message here
            description="Hey to use me use the command **`!help`**", #You can change the description of the greeting message here
            color = self.embedOrange 
        )
        for channel in sendToChannels:
            await channel.send(embed=helloEmbed)
            
    @commands.command(
        name = 'help',
        aliases=["h"],
        help="")
    async def help(self, ctx):
        helpCog = self.bot.get_cog("help_cog")
        musicCog = self.bot.get_cog("music_cog")
        commands = helpCog.get_commands() + musicCog.get_commands()
        
        commandDescription = "** !help ** -Provides a descripton of all commands"
        for c in commands:
            message = c.help   
            commandDescription += f"**`!{c.name}`** {c.help}\n"
        commandsEmbed = discord.Embed(
            title = "Command List", 
            description=commandDescription,
            color=self.embedOrange
        )
        await ctx.send(embed=commandsEmbed)