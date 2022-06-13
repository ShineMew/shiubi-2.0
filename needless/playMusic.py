import discord
import youtube_dl
from replit import db
import random

#basic settings
random_play = False
solo_loop_play = False
whole_queue_play = False
song_queue = []
YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}

def changePos(a: int, b: int):
  empty = song_queue[a]
  song_queue[a] = song_queue[b]
  song_queue[b] = empty

async def clear(self,ctx):
  global song_queue
  await ctx.send(f"[告知] 應{ctx.author.name}要求清空歌單")
  song_queue = []

#main
async def play(self, ctx, url):
  song_queue.append(url)
  if not ctx.voice_client.is_playing():
    FFMPEG_OPTIONS = {
      "before_options":
      "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
      "options": "-vn"
    }
    vc = ctx.voice_client
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(song_queue[0], download=False)
      url2 = info["formats"][0]["url"]
      song_name = info["title"]
      thumb_url = info["thumbnails"][0]["url"]
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
    if (whole_queue_play):
      song_queue.append(song_queue[0])
      del song_queue[0]
    elif (random_play):
      rand_url = random.randrange(1, len(song_queue)-1)
      changePos(rand_url, 0)
    elif (solo_loop_play):
      print("solo_loop_play")
    else:
      del song_queue[0]
    vc.play(source=source,after=lambda e: vc.loop.create_task(play(self, ctx,url)))
    embed = discord.Embed(title="準備播放", color=0xe175ff)
    embed.add_field(name="歌名: ", value=song_name, inline=False)
    embed.set_thumbnail(url=thumb_url)
    c = ctx.channel
    await c.send(embed=embed)
  else:
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      embed = discord.Embed(title="已加入歌單", color=0xe175ff)
      info = ydl.extract_info(url, download=False)
      thumb_url = info["thumbnails"][0]["url"]
      song_name = info["title"]
      embed.add_field(name = "歌名: ", value = song_name, inline=False)
      embed.set_thumbnail(url = thumb_url)
    c = ctx.channel
    await c.send(embed = embed)

async def playnext(self, ctx):
  if not ctx.voice_client.is_playing():
    FFMPEG_OPTIONS = {
      "before_options":
      "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
      "options": "-vn"
    }
    vc = ctx.voice_client
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(song_queue[0], download=False)
      url2 = info["formats"][0]["url"]
      song_name = info["title"]
      thumb_url = info["thumbnails"][0]["url"]
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
    if (whole_queue_play):
      song_queue.append(song_queue[0])
      del song_queue[0]
    elif (random_play):
      rand_url = random.randrange(1, len(song_queue)-1)
      changePos(rand_url, 0)
    elif (solo_loop_play):
      print("solo_loop_play")
    else:
      del song_queue[0]
    vc.play(source=source,after=lambda e: vc.loop.create_task(playnext(self, ctx)))
    embed = discord.Embed(title="準備播放", color=0xe175ff)
    embed.add_field(name="歌名: ", value=song_name, inline=False)
    embed.set_thumbnail(url=thumb_url)
    c = ctx.channel
    await c.send(embed=embed)

#switch mode
async def loop_switch(self, ctx):
  global random_play
  global solo_loop_play
  global whole_queue_play
  if solo_loop_play:
    solo_loop_play = False
    await ctx.send("單曲循環[OFF]")
  else:
    solo_loop_play = True
    whole_queue_play = False
    random_play = False
    await ctx.send("單曲循環[ON]\n歌單循環[OFF]\n隨機播歌[OFF]")

async def queue_switch(self, ctx):
  global random_play
  global solo_loop_play
  global whole_queue_play
  if whole_queue_play:
    whole_queue_play = False
    await ctx.send("歌單循環[OFF]")
  else:
    whole_queue_play = True
    solo_loop_play = False
    random_play = False
    await ctx.send("歌單循環[ON]\n單曲循環[OFF]\n隨機播歌[OFF]")

async def random_switch(self, ctx):
  global random_play
  global solo_loop_play
  global whole_queue_play
  if random_play:
    random_play = False
    await ctx.send("隨機播歌[OFF]")
  else:
    solo_loop_play = False
    whole_queue_play = False
    random_play = True
    await ctx.send("隨機播歌[ON]\n歌單循環[OFF]\n單曲循環[OFF]")

#the songs stored
async def songQueue(self, ctx):
  if solo_loop_play:
    _loop = "[ON]"
  else:
    _loop = "[OFF]"
  if whole_queue_play:
    _loop_queue = "[ON]"
  else:
    _loop_queue = "[OFF]"
  if random_play:
    _rando = "[ON]"
  else:
    _rando = "[OFF]"
  embed = discord.Embed(title="歌單內容", color=0xe175ff)
  embed.add_field(
    name="播放模式",
    value=f"單曲循環模式:{_loop} 歌單循環模式:{_loop_queue} 隨機播歌模式:{_rando}",
    inline=False)
  for i in range(len(song_queue)):
    try:
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(song_queue[i], download=False)
        song_name = info["title"]
      embed.add_field(name=f"第{i+1}首:", value=song_name, inline=False)
    except:
      del song_queue[i]
      i -= 1
  c = ctx.channel
  await c.send(embed=embed)

async def show_old(self, ctx):
  embed = discord.Embed(title="儲存中的播放清單:", color=0xe175ff)
  for key in db:
    _list = []
    _list = _list + list(db[key])
    embed.add_field(name=f"清單: {key}", value=f"含有{len(_list)}首歌", inline=False)
  await ctx.send(embed=embed)

async def old(self, ctx, name):
  global song_queue
  if name in db.keys():
    song_queue = []
    song_queue = song_queue + list(db[name])
    await ctx.send(f"載入 {name} 清單")
    await songQueue(self, ctx)
    await playnext(self, ctx)
  else:
    await ctx.send(f"[ERROR] 沒有清單{name}")

async def save_queue(self, ctx, listname):
  db[listname] = song_queue
  await ctx.send(f"[告知] 成功建立 {listname} 清單")
  await songQueue(self, ctx)

#skip
async def skip(self, ctx):
  ctx.voice_client.pause()
  await ctx.send(f"[告知] 已跳過歌曲")
  await playnext(self, ctx)
