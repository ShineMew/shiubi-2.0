import discord
from discord.ext import commands
from discord_slash import cog_ext
import youtube_dl
import playMusic as pm
from replit import db

guild_id = [882411725213810728,843724526381563924,882263805734813707,863745416989507614,917962071189123083]


class music(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @cog_ext.cog_slash(name = "clear",description = "清空我的歌單", guild_ids = guild_id)
  async def clear(self,ctx):
    await pm.clear(self,ctx)

  @cog_ext.cog_slash(name = "save",description = "儲存目前的歌單(建議先用/plist確認現在的歌單內容)", guild_ids = guild_id)
  async def save(self,ctx,name):
    await pm.save_queue(self,ctx,name)

  @cog_ext.cog_slash(name = "old",description = "讀取以前儲存的歌單(建議先用/show查看有哪些可以讀取)", guild_ids = guild_id)
  async def old(self,ctx,name):
    if ctx.voice_client is None:
      await ctx.author.voice.channel.connect()
    await pm.old(self,ctx,name)

  @cog_ext.cog_slash(name = "show",description = "顯示以前儲存的歌單", guild_ids = guild_id)
  async def show(self,ctx):
    await pm.show_old(self,ctx)

  @cog_ext.cog_slash(name = "join",description = "加入你現在所在的語音頻道", guild_ids = guild_id)
  async def join(self,ctx):
    if ctx.author.voice is None:
      await ctx.send("[疑惑] 該去哪?(找不到語音頻道)")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
      await ctx.send("[告知] 成功加入")
    else:
      await ctx.voice_channel.move_to(voice_channel)
    
  @cog_ext.cog_slash(name = "leave",description = "離開現在所在的語音頻道", guild_ids = guild_id)
  async def leave(self,ctx):
    if ctx.voice_client is not None:
      await ctx.voice_client.disconnect()
      await ctx.send(f"[告知] 應{ctx.author.name}要求, 先離席了")
    else:
      await ctx.send("[疑惑] 還沒進去")

  @cog_ext.cog_slash(name = "play",description = "播放url後的內容(你最好給我使用youtube)", guild_ids = guild_id)
  async def play(self,ctx,url):
    if ctx.voice_client is not None:#bot is already in channel
      await pm.play(self,ctx,url)
    else:
      if ctx.author.voice.channel is not None:#author is in channel
        await ctx.author.voice.channel.connect()
        await pm.play(self,ctx,url)
      else:
        await ctx.send("[疑惑] 該去哪?(找不到語音頻道)")

  @cog_ext.cog_slash(name = "pau",description = "暫停現在播放的歌", guild_ids = guild_id)
  async def pau(self,ctx):
    if ctx.voice_client.is_playing():
      await ctx.send("[暫停]")
      ctx.voice_client.pause()
    else:
      await ctx.send("[疑惑]?")

  @cog_ext.cog_slash(name = "res",description = "繼續剛剛暫停的歌", guild_ids = guild_id)
  async def res(self,ctx):
    if not ctx.voice_client.is_playing():
      await ctx.send("[繼續]")
      ctx.voice_client.resume()
    else:
      await ctx.send("[疑惑]?")

  @cog_ext.cog_slash(name = "swl",description = "切換單曲循環", guild_ids = guild_id)
  async def swl(self,ctx):
    await pm.loop_switch(self,ctx)

  @cog_ext.cog_slash(name = "swq",description = "切換循環播放", guild_ids = guild_id)
  async def swq(self,ctx):
    await pm.queue_switch(self,ctx)

  @cog_ext.cog_slash(name = "swr",description = "切換隨機播放", guild_ids = guild_id)
  async def swr(self,ctx):
    await pm.random_switch(self,ctx)

  @cog_ext.cog_slash(name = "plist",description = "顯示現在的播放清單", guild_ids = guild_id)
  async def plist(self,ctx):
    await pm.songQueue(self,ctx)

  @cog_ext.cog_slash(name = "skip",description = "跳過現在播放的歌", guild_ids = guild_id)
  async def skip(self,ctx):
    await pm.skip(self,ctx)

def setup(bot):
  bot.add_cog(music(bot))