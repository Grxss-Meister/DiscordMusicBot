import discord
from discord.ui import Button, View, Select
from discord import SelectOption
from discord.ext import commands
import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
import json 
import os
from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.is_playing = {}
        self.is_paused = {}
        self.music_queue = {}
        self.queue_index = {}
        
        self.YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        
        #Feel free to change the color of the embeds.
        self.embedBlue = 0x2c76dd 
        self.embedRed = 0xdf1141
        self.embedGreen = 0x0eaa51
        
        self.vc = {}
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.music_queue[id] = []
            self.queue_index[id] = 0
            self.vc[id] = None
            self.is_playing[id] = self.is_paused[id] = False 
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.bot.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.bot.user.id and self.vc[id].is_connected():
                self.is_playing[id] = self.is_paused[id] = False
                self.music_queue[id] = []
                self.queue_index[id] = 0
                await self.vc[id].disconnect()
        
            
    def generate_embed(self, song, author):
        
        embed = discord.Embed(
        title='Now Playing',
        description=f'[{song["title"]}]({song["link"]})',
        color=self.embedBlue )
        embed.set_thumbnail(url=song['thumbnail'])
        embed.set_footer(
        text=f'Song added by: {str(author)}',
        icon_url=author.display_avatar.url)
        return embed
    
    def added_song_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.display_avatar.url
        
        embed = discord.Embed(title='Song added to queue!', description=f'[{title}]({link})', color=self.embedRed)  
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar) 
        return embed
              
    
    def removed_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.display_avatar.url
        
        embed = discord.Embed(title='Song removed from queue!', description=f'[{title}]({link})', color=self.embedRed)  
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song removed by: {str(author)}', icon_url=avatar) 
        return embed
        
   
    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()     
            if self.vc[id] == None:    
                await ctx.send("Could not connect to the voice channel.")
                return 
        else:
            await self.vc[id].move_to(channel)  
            
    def get_YT_title(self, videoID):
        try:
            params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % videoID}
            url = "https://www.youtube.com/oembed?" + parse.urlencode(params)
            with request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return data["title"]
        except:
            try:
                with YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(
                    "https://www.youtube.com/watch?v=" + videoID,
                    download=False)
                    return info.get('title', 'Unknown Title')
            except:
                return "Unknown Title"
    
    def search_YT(self, search):
        queryString = parse.urlencode({"search_query": search})
        htmContent = request.urlopen("https://www.youtube.com/results?" + queryString)
        searchResults = re.findall(r'\/watch\?v=(.{11})', htmContent.read().decode())
        searchResults = list(dict.fromkeys(searchResults))
        return searchResults[0:10]
    
    def extract_YT(self, url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info(url, download=False)
            except: 
                return False
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info.get('url') or info['formats'][0]['url'],
            'title': info['title']} 
        
        
    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
             return
        if self.queue_index[id] + 1 < len(self.music_queue[id]):
             self.is_playing[id] = True
             self.queue_index[id] += 1
             
             song = self.music_queue[id][self.queue_index[id]][0]
             author = self.music_queue[id][self.queue_index[id]][2]
             message = self.generate_embed(song, author)
             coro = ctx.send(embed = message)
             fut = run_coroutine_threadsafe(coro, self.bot.loop)
             try:
                 fut.result()
             except:
                 pass
             
             self.vc[id].play(discord.FFmpegPCMAudio(
                 song['source'], **self.FFMPEG_OPTIONS), after =lambda e: self.play_next(ctx))   
        else:
            self.queue_index[id] += 1
            self.is_playing[id] = False
                
             
    async def play_music(self, ctx):
        id = int(ctx.guild.id)
        if self.queue_index[id] < len(self.music_queue[id]):
            self.is_playing[id] = True
            self.is_paused[id] = False
            
            await self.join_VC(ctx, self.music_queue[id][self.queue_index[id]][1])
            
            song = self.music_queue[id][self.queue_index[id]][0]
            author = self.music_queue[id][self.queue_index[id]][2]
            message = self.generate_embed(song, author)
            await ctx.send(embed =message)
            
            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after =lambda e: self.play_next(ctx))
        else:
            await ctx.send("There are no more songs in the queue.")
            self.is_playing[id] = False   


    @commands.command(name = "add", aliases = ["a"], help="Adds song to the queue")
    async def add(self, ctx, *args):
        search = " ".join(args)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You are not connected to a voice channel.")
            return
        if not args:
            await ctx.send("You need to specify a song to be added!")
        else:
            song = self.extract_YT(self.search_YT(search)[0])
            if type(song) == type(True):
                await ctx.send("Could not download the song. Try different keywords!")
                return
            else:
                self.music_queue[ctx.guild.id].append([song, userChannel, ctx.author])
                message = self.added_song_embed(ctx, song)
                await ctx.send(embed=message)

    
    @commands.command(name = "remove", aliases = ["r"], help="Removes the last added song of the queue")
    async def remove(self, ctx):
        id = int(ctx.guild.id)
        
        if not self.music_queue[id]:
            await ctx.send("There are no songs to be removed.")
            return

        # Den Index des letzten Songs speichern, BEVOR wir ihn löschen
        last_song_index = len(self.music_queue[id]) - 1
        
        # Den Song entfernen
        removed_song = self.music_queue[id].pop()
        songRemoved = self.removed_embed(ctx, removed_song[0])
        await ctx.send(embed=songRemoved)

        # Nur wenn der gelöschte Song AUCH der gerade spielende Song war, stoppen wir!
        if self.queue_index[id] == last_song_index:
            if self.vc[id] != None and self.is_playing[id]:
                self.is_playing[id] = False
                self.vc[id].stop()
            
            # Index korrigieren, falls wir am Ende der Liste waren
            self.queue_index[id] -= 1
            if self.queue_index[id] < 0:
                self.queue_index[id] = 0
        else:
            pass
        
     
    @commands.command(name = "skip", aliases = ["next", "sk"], help="Skips the current song which is being played")
    async def skip(self, ctx):
        id = int(ctx.guild.id)

        if not self.music_queue[id]:
            await ctx.send("There are no songs in the queue.")
            return

        if self.vc[id] == None or not self.vc[id].is_connected():
            await ctx.send("You are not connected to a voice channel.")
            return

        if self.queue_index[id] >= len(self.music_queue[id]) - 1:
            await ctx.send("There is no song to go forward to.")
            self.is_playing[id] = False
            self.is_paused[id] = False
            if self.vc[id]:
                self.vc[id].stop()
        else:
            self.vc[id].stop()
         
      
    @commands.command(name = "previous", aliases = ["back", "pr"], help="Goes back to the previous song in the queue") 
    async def previous(self, ctx):
        id = int(ctx.guild.id)
    
        if not self.music_queue[id]:
            await ctx.send("There are no songs in the queue.")
            return
    
        if self.vc[id] == None:
            await ctx.send("You are not connected to a voice channel.")
            return

        if self.queue_index[id] <= 0:
            await ctx.send("There is no previous song to go back to. Replaying current song.")
            self.vc[id].pause()
            await self.play_music(ctx)
        else:
            self.vc[id].pause()
            self.queue_index[id] -= 1
            await self.play_music(ctx)
        
                    
    @commands.command(name = "pause", aliases = ["ps", "stop"], help="Pauses the current song")
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no song to be paused at the moment.")
        elif self.is_playing[id]:
            await ctx.send("Song paused!")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()
            
    @commands.command(name = "resume", aliases = ["re", "continue"], help="Resumes the paused song")
    async def resume(self, ctx):
        id = int(ctx.guild.id)   
        if not self.vc[id]:
            await ctx.send("There is no song to be resumed at the moment.")
        elif self.is_paused[id]:
            await ctx.send("The song is now playing!")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()
        
    @commands.command(name = "play", aliases = ["p"], help="Plays a song via the title or the youtube link")
    async def play(self, ctx, *args):
        search = " ".join(args)
        id = int(ctx.guild.id)
        
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You are not connected to a voice channel.")
            return

        if not args: 
            if len(self.music_queue[id]) == 0:
                await ctx.send("There are no songs to be played.")
                return
            
            if not self.is_playing[id]:
                # FIX: Wir zwingen den Index auf den LETZTEN Song in der Queue
                self.queue_index[id] = len(self.music_queue[id]) - 1
                await self.play_music(ctx)
            else:
                if self.is_paused[id]:
                    self.is_paused[id] = False
                    self.is_playing[id] = True
                    self.vc[id].resume()
        else: 
            song_list = self.search_YT(search)
            song = self.extract_YT(song_list[0])
            if type(song) == type(True):
                await ctx.send("Could not download this song.")
            else:
                self.music_queue[id].append([song, userChannel, ctx.author])
                
                if not self.is_playing[id]:
                    # FIX: Auch hier sofort auf den neuen Song springen
                    self.queue_index[id] = len(self.music_queue[id]) - 1
                    await self.play_music(ctx)
                else:
                    message = self.added_song_embed(ctx, song)
                    await ctx.send(embed=message)
            
    
    @commands.command(name = "clear", aliases = ["c", "delete"], help="Clears the complete queue")
    async def clear(self, ctx):
        id = int(ctx.guild.id)
        if self.vc[id]!= None and self.is_playing[id]:
            self.is_playing[id] = self.is_paused[id] = False
            self.vc[id].stop()
        if self.music_queue[id] != []:
            await ctx.send("The music queue has been cleared.")
            self.music_queue[id] = []
        self.queue_index[id] = 0
           
            
    @commands.command(name = "queue", aliases = ["q", "list"], help="Gives u the list of the songs in the queue")
    async def queue(self, ctx):
        id = int(ctx.guild.id)
        returnValue = ""
        if self.music_queue[id] == [] or self.queue_index[id] >= len(self.music_queue[id]):
            await ctx.send("There are no songs in the queue.")
            return
        
        for i in range(self.queue_index[id], len(self.music_queue[id])):
            upNextSong = len(self.music_queue[id]) - self.queue_index[id]
            if i > 5 + upNextSong: #Here u can increase the number of the songs shown in the queue
                break
            returnIndex = i - self.queue_index[id] 
            if returnIndex == 0:
                returnIndex = "Playing"
            elif returnIndex == 1:
                returnIndex = "Next"
            returnValue += f"{returnIndex} - [{self.music_queue[id][i][0]['title']}]({self.music_queue[id][i][0]['link']})\n"
            
        if returnValue == "":
            await ctx.send("There are no songs in the queue.")
            return 
            
        queue = discord.Embed(
            title = "Current queue",
            description=returnValue,
            color=self.embedGreen)
        await ctx.send(embed=queue)
    
                 
    @commands.command(name = "join", aliases = ["j"], help="The Bot joins the VC")
    async def join(self, ctx):
        if ctx.author.voice:
            userChannel = ctx.author.voice.channel
            await self.join_VC(ctx, userChannel)
            await ctx.send(f"Bot has joined {userChannel}.") #You can put any message here. And also change the name of the Bot
        else:
            await ctx.send("You are not connected to a voice channel.")     
            
    @commands.command(name = "leave",  aliases = ["l", "disconnect", "d"],  help="The Bot leaves the VC") 
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.music_queue[id] = []
        self.queue_index[id] = 0
        if self.vc[id] != None:
            await ctx.send("Bot has left the voice channel.") #You can put any message here. And also change the name of the Bot
            await self.vc[id].disconnect()
            self.vc[id] = None
            
    @commands.command(name="search", aliases=["s", "find"], help="Searched for 10 songs of the given keyword")
    async def search(self, ctx, *args):
        search = " ".join(args)

        if not args:
            await ctx.send("You must specify a search Term!")
            return

        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be connected to a voice channel!")
            return

        await ctx.send("Fetching search results . . .")

        songTokens = self.search_YT(search)

        songNames = []
        embedText = ""
        options = []

        #LISTE + OPTIONS
        for i, token in enumerate(songTokens[:10]):
            url = "https://www.youtube.com/watch?v=" + token
            title = self.get_YT_title(token)

            songNames.append(title)
            embedText += f"{i+1} - [{title}]({url})\n"

            options.append(discord.SelectOption(
                label=f"{i+1} - {title[:90]}",
                value=str(i)))

        #EMBED
        embed = discord.Embed(
            title="Search Results",
            description=embedText,
            color=self.embedRed)

        #SELECT MENU
        select = Select(placeholder="Select an option", options=options)

        async def select_callback(interaction):
            chosenIndex = int(select.values[0])
            songRef = self.extract_YT(songTokens[chosenIndex])

            if type(songRef) == type(True):
                await interaction.response.send_message(
                "Could not download the song.",
                ephemeral=True)
                return 

            self.music_queue[ctx.guild.id].append([songRef, userChannel, ctx.author])

            embedResponse = discord.Embed(
                title=f"Option #{chosenIndex + 1} Selected",
                description=f"[{songRef['title']}]({songRef['link']}) added to the queue!",
                color=self.embedRed)
            embedResponse.set_thumbnail(url=songRef["thumbnail"])
            embedResponse.set_footer(
                text=f"Song added by: {str(ctx.author)}",
                icon_url=ctx.author.display_avatar.url)

            await interaction.response.send_message(embed=embedResponse)

        select.callback = select_callback

        # VIEW
        view = View()
        view.add_item(select)

       
        await ctx.send(embed=embed, view=view)
    