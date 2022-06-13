import discord
from discord.ext import commands
from discord_slash import cog_ext
import wavelink
import random
from replit import db
import json
from replit import db

guild_id = db["guild_id"]

# v res pau leave loop cycle playlist | x  jump skip shuffle 
class wavelinkmusic(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    self.server = {}
    self.is_cycle = False
    self.is_shuffle = False
    bot.loop.create_task(self.node_connect())

  async def node_connect(self):
    await self.bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot = self.bot,
                                        host = "lavalink.kapes.eu",
                                        port = 2222, 
                                        password = "lavalinkplay")

  @commands.Cog.listener()
  async def on_wavelink_node_ready(self, node: wavelink.Node):
    print(f"Node <{node.identifier}> is ready !")
    

  @commands.Cog.listener()
  async def on_wavelink_track_end(self, player:wavelink.Player, track: wavelink.Track, reason):
    ctx = player.ctx
    vc: player = ctx.voice_client

    if vc.loop:
      return await vc.play(track)
    elif self.is_cycle:
      _track = await wavelink.YouTubeTrack.search(query = str(track.uri), return_first = True)
      vc.queue.put(_track)
    if vc.queue.is_empty:
      return print("[wavelink music] vcqueue is empty")

    next_track = vc.queue.get()
    await vc.play(next_track)
    info = await songinfo(ctx,next_track)
    await ctx.send(embed = info)
    
  @cog_ext.cog_slash(name = "join",description = "加入你現在所在的語音頻道", guild_ids = guild_id)
  async def join(self,ctx):
    if ctx.author.voice is None:
      await ctx.send("[Error] You are not in a voice channel.")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
      await ctx.send(f"Joined {voice_channel}")
    else:
      await ctx.voice_channel.move_to(voice_channel)

  @cog_ext.cog_slash(name = "leave",description = "離開現在所在的語音頻道", guild_ids = guild_id)
  async def leave(self,ctx):
    if ctx.voice_client:
      voice_channel = ctx.author.voice.channel
      await voice_channel.disconnect()
      await ctx.send(f"Left {voice_channel}")
    else:
      await ctx.send("[Error] I am not in a voice channel.",hidden = True)

  @cog_ext.cog_slash(name = "pau",description = "暫停現在播放的歌", guild_ids = guild_id)
  async def pau(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    if not ctx.voice_client.is_paused():
      await ctx.send("[Paused]")
      await ctx.voice_client.pause()
    else:
      await ctx.send("[Error] Something went wrong", hidden = True)

  @cog_ext.cog_slash(name = "res",description = "繼續剛剛暫停的歌", guild_ids = guild_id)
  async def res(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    if ctx.voice_client.is_paused():
      await ctx.send("[Resumed]")
      await ctx.voice_client.resume()
    else:
      await ctx.send("[Error] Something went wrong",hidden = True)
      
  @cog_ext.cog_slash(name = "skip",description = "跳過現在播放的歌", guild_ids = guild_id)
  async def skip(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    vc: wavelink.Player = ctx.voice_client
    await ctx.send(f"Skipped **{vc.track.title}**")
    return await vc.stop()

  
  @cog_ext.cog_slash(name = "play",description = "播放歌曲", guild_ids = guild_id)
  async def play(self,ctx,*,song):
    if not ctx.voice_client:
      vc: wavelink.Player = await ctx.author.voice.channel.connect(cls = wavelink.Player)
    vc: wavelink.Player = ctx.voice_client
    vc.ctx = ctx
    vc.loop = False

    alreadyplaying = ctx.voice_client.is_playing() or ctx.voice_client.is_paused()
    track = None
    playlist_firstplay = False
    if "https://" in song:
      if "list=" in song:
        playlist = await vc.node.get_playlist(identifier = song, cls = wavelink.YouTubePlaylist)
        if vc.queue.is_empty and not alreadyplaying:
          playlist_firstplay = True
        vc.queue.extend(playlist.tracks)
        track = vc.queue.get()
      else:
        _track = await vc.node.get_tracks(query = song, cls = wavelink.YouTubeTrack)
        track = _track[0]
    else:
      track = await wavelink.YouTubeTrack.search(query = song, return_first = True)
      await ctx.send(f"**Searching** `{song}`")
    
    
    if (vc.queue.is_empty or playlist_firstplay) and not alreadyplaying:
      info = await songinfo(ctx, track)
      await ctx.send(embed = info)
      await vc.play(track)
      await vc.set_volume(25)
    else:
      await vc.queue.put_wait(track)
      info = discord.Embed(title = f"Added  {track.title}",description = f"[YoutubeURL]({str(track.uri)})",color = 0x0062ff)
      info.set_author(name = f"Artist: {track.author}")
      info.set_footer(text = ctx.author,icon_url=str(ctx.author.avatar_url))
      info.set_thumbnail(url = track.thumbnail)

      song_length = await get_duration(track.length)
      info.add_field(name = "Length", value = song_length,inline = False)
      
      await ctx.send(embed = info)


  @cog_ext.cog_slash(name = "loop",description = "切換單曲循環", guild_ids = guild_id)
  async def loop(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    vc: wavelink.Player = ctx.voice_client

    try:
      vc.loop ^= True
    except Exception:
      vc.loop = False

    return await ctx.send("[Loop] Enabled") if vc.loop else await ctx.send("[Loop] Disabled")

  @cog_ext.cog_slash(name = "cycle",description = "切換歌單循環", guild_ids = guild_id)
  async def cycle(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    self.is_cycle ^= True 
    return await ctx.send("[Cycle] Enabled") if self.is_cycle else await ctx.send("[Cycle] Disabled")

  @cog_ext.cog_slash(name = "shuffle",description = "隨機歌單順序", guild_ids = guild_id)
  async def shuffle(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    vc: wavelink.Player = ctx.voice_client
    self.is_shuffle = True
    playlist = vc.queue.copy()
    playlist = list(playlist)   
    random.shuffle(playlist)
    vc.queue.clear()
    vc.queue.extend(playlist)
    return await ctx.send("[Shuffle]")

  @cog_ext.cog_slash(name = "playlist",description = "顯示歌單", guild_ids = guild_id)
  async def playlist(self,ctx):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.",hidden = True)
    vc: wavelink.Player = ctx.voice_client
    if vc.queue.is_empty:
      return await ctx.send("[Error] Song Queue is Empty.")

    queue = vc.queue.copy()
    sq = discord.Embed(title = "Playlist", color = 0x0062ff)
    sq.add_field(name = "NowPlaying",value = str(vc.track),inline = False)
    songs = ""
    mode = ""
    i = 1
    songlen_outoflimit = False
    for song in queue:
      if len(songs) + len(f"{i} {song}\n") < 1024:
        songs += f"{i} {song}\n"
      else:
        songlen_outoflimit = True
        if songlen_outoflimit:
          songs+="..."
      i += 1
    sq.add_field(name = f"{len(queue)} songs", value = songs,inline = False)
    if vc.loop:
      mode += "**Loop** "
    if self.is_cycle:
      mode += "**Cycle** "
    if self.is_shuffle:
      mode += "**Shuffle**"    
    mode = "**Default**" if not mode else mode
    sq.add_field(name = "Mode",value = mode,inline = False)    
    await ctx.send(embed = sq)

  @cog_ext.cog_slash(name = "playnow",description = "強制播放這首歌(請尊重別人)", guild_ids = guild_id)
  async def playrightnow(self,ctx,song:str):
    if not ctx.voice_client:
      return await ctx.send("[Error] I am not in a voice channel.", hidden = True)
      
    vc: wavelink.Player = ctx.voice_client

    track = None
    if "https://" in song:
      _track = await vc.node.get_tracks(query = song, cls = wavelink.YouTubeTrack)
      track = _track[0]
    else:
      track = await wavelink.YouTubeTrack.search(query = song, return_first = True)
      await ctx.send(f"**Searching** `{song}`")

    vc.queue.put_at_front(track)
    await vc.stop()
    return await ctx.send(f"強制插播 **{track.title}**")

async def get_duration(duration):
  hr = int(duration / 3600)
  duration -= hr * 3600
  min = int(duration / 60)
  duration -= min * 60
  sec = int(duration)
  if 0 < hr and hr < 10:
    hr = f"0{str(hr)}"
  if 0 <= min and min < 10:
    min = f"0{str(min)}"
  if 0 <= sec and sec < 10:
    sec = f"0{str(sec)}"
  return f"{hr}:{min}:{sec}" if hr else f"{min}:{sec}"

'''
async def check_server(self,server_guild):
  if server_guild not in self.server.keys():
    self.server[server_guild] = {
      "Song_loop":False,
      "Playlist_loop":False,
      "Shuffle":False,
      "song_queue": [],
    }
'''

async def songinfo(ctx, track:wavelink.YouTubeTrack):
  songinfo = discord.Embed(title = f"Now playing  {track.title}",description = f"Link: [YoutubeURL]({str(track.uri)})",color = 0x0062ff)
  songinfo.set_author(name = f"Artist: {track.author}")
  try:
    songinfo.set_thumbnail(url = track.thumbnail)
  except:
    print("[wavelink music] Can't load in thumbnail.")
  song_length = await get_duration(track.length)
  songinfo.add_field(name = "Length", value = song_length,inline = False)
  return songinfo
  

def setup(bot):
  bot.add_cog(wavelinkmusic(bot))