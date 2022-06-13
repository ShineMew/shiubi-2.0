import discord
from discord.ext import commands
from discord_slash import SlashCommand
from replit import db
import os
import json
import asyncio
from datetime import datetime
import random
#cogs
import keep_alive
import wavelinkmusic
import controle
import verify
import economy
import role

comprefix = "s;"
token = os.environ['token']
bot = commands.Bot(command_prefix = comprefix, intents = discord.Intents.all())
slash = SlashCommand(bot, sync_commands = True)

guild_id = [882411725213810728,843724526381563924,882263805734813707,863745416989507614,917962071189123083,962594076677533716,971806887559442483]
db["guild_id"] = guild_id

#load in cogs
cogs = [controle,verify,economy,wavelinkmusic,role]
for i in range(len(cogs)): 
  cogs[i].setup(bot)

songs = ["Tempestissimo","Don't Fight The Music","World Vanquisher","Grievous Lady","Trappola Bewitching","Monochrome Princess","Purgatorium"]

@bot.event
async def on_ready():
  print(f"{bot.user} is online")
  t = 0
  while (1):
    if not t % 120:
      await backup("bank.json")
      await presence()
    if not t % 5:
      await check_member()
    await asyncio.sleep(1)
    t+= 1

@bot.event
async def on_message(message):
  if message.author == bot.user:
    return
  msg = message.content

  anonymous = []
  for i in [882589533475065916,953301285308874822]:
    anonymous.append(bot.get_channel(i))
  if message.channel in anonymous:
    await message.delete()
    embed = discord.Embed(color = 0xe175ff ,timestamp = datetime.utcnow())
    if len(msg) >= 1:
      embed.add_field(name = "匿名",value = msg,inline = False)
    if len(message.attachments) >= 1:
      embed.set_image(url=message.attachments[0])
    await message.channel.send(embed = embed)

  msgboard = bot.get_channel(929635913821216788)
  if message.channel == msgboard:
    await message.delete()
    embed = discord.Embed(color = 0x0062ff ,timestamp = datetime.utcnow())
    if len(msg) >= 1:
      embed.add_field(name = f"{message.author}留言",value = msg,inline = False)
    if len(message.attachments) >= 1:
      embed.set_image(url=message.attachments[0])
    await message.channel.send(embed = embed)

  mine = bot.get_channel(966341688794677268)
  if message.channel == mine:
    if (msg == "mine" or msg == "Mine"):
      await message.delete()
      await economy.mine(message)
    if (msg == "info" or msg == "Info"):
      await message.delete()
      await economy.mine_check(message)
    
  if msg.startswith("s$help"):
    tmp = msg.split(" ")
    if len(tmp) == 1:
      return await helpcommand(message)
    elif tmp[1] == "commands":
      return await helpcommand(message)
    else:
      return await message.channel.send(f"Unknown command `{tmp[1]}`")
    
  
  await bot.process_commands(message)

@slash.slash(name = "avatar", description = "Get a user's avatar",guild_ids = guild_id)
async def avatar(ctx,target:discord.Member,hidden:bool):
  avatar = str(target.avatar_url)
  await ctx.send(avatar,hidden = hidden)
  
@slash.slash(name = "vote", description = "建立一個投票, 選項不能超過10個呦", guild_ids = guild_id)
async def vote(ctx,subject,options):
  _list = options.split(" ",10)
  emoji_num = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
  if len(_list) > 1:
    embed = discord.Embed(title = "投票: " + subject,color = 0xe175ff)
    for i in range(0,len(_list)):
      embed.add_field(name = f"選項{emoji_num[i]}",value = f"{_list[i]}",inline = False)
    _msg = await ctx.send(embed = embed)
    for i in range(0,len(_list)):
      await _msg.add_reaction(emoji_num[i])
  elif len(_list) == 1:
    embed = discord.Embed(title = "投票:",color = 0xe175ff)
    embed.add_field(name = "[主題] 是否同意",value = subject,inline = False)
    _msg = await ctx.send(embed = embed)
    await _msg.add_reaction("👍")
    await _msg.add_reaction("👎")
  else:
    await ctx.send("[ERROR] 引數不足")

@slash.slash(name = "rand",description = "隨機選擇你提供的內容, 每個選項用空格隔開",guild_ids = guild_id)
async def rand(ctx,subject,elements,count:int):
    ele = elements.split(" ")
    if len(ele) >= 2:
      count = 1 if count<1 else count
      try:      
        if (count > (len(ele))):
          return await ctx.send(f"[ERROR]Count must less than the length of list")
        sen = f"{subject} [{elements}]"
        ans = random.choices(ele,k=count)
        a = " "
        for i in ans:
          a += f"{i} "
        return await ctx.send(f"{sen}\n--> [{a}]")
      except Exception:
        return await ctx.send(f"[Error]{Exception}")
    else:
      await ctx.send("[ERROR]You just gave me 1 element!")

@slash.slash(name = "t",description = "我可以幫你傳達一些事情",guild_ids = guild_id)
async def t(ctx,msg):
  if ctx.author.id == int(os.environ['shinmew']):
    await ctx.send("已發送訊息", hidden = True)
    await ctx.channel.send(msg)
  else:
    bad = ["尻","ㄎㄠ","ㄎ","迅喵","辛喵","遜喵","訊喵"]
    for i in bad:
      if i in msg:
        return await ctx.send(f"Well, check your message again, maybe there are something bad words in it.", hidden = True)
    await ctx.send(msg)

@slash.slash(name = "sco",description = "音遊成績計算, 公式參考Arcaea",guild_ids = guild_id)
async def sco(ctx,perfect:int,great:int,good:int,bad:int,miss:int,combo:int):
    ap = 0
    fc = 0
    total = perfect + great + good + bad + miss
    spn = 10000000/total
    if(combo > total):
      await ctx.send("[ERROR]Something went wrong")
      return
    if (combo == total):
      if (perfect == total):
        ap = 1
      elif ((perfect + great) == total):
        fc = 1 
      else:
        await ctx.send("[ERROR]Something went wrong")
        return

    score = round((perfect+great*0.75)*spn + good*spn/3 + perfect)
    pureRate = round(perfect / total * 10000)/100
    completeRate = round((perfect+great) / total * 10000)/100
    rank = ""
    if (score >= 9900000):
      rank = "EX+"
    elif (score >= 9800000):
      rank = "EX"
    elif (score >= 9500000):
      rank = "AA"
    elif (score >= 9200000):
      rank = "A"
    elif (score >= 8900000):
      rank = "B"
    elif (score >= 8600000):
      rank = "C"
    else:
      rank = "D"
    embed = discord.Embed(title = f"{ctx.author.name}",color = 0xffd500)
    embed.add_field(name = "PureRate",value=f"{pureRate}%",inline = True)
    embed.add_field(name = "CompleteRate",value=f"{completeRate}%",inline = True)
    embed.add_field(name = "Rank",value=rank,inline = True)
    embed.add_field(name = "Perfect",value=perfect,inline = False)
    embed.add_field(name = "Great",value=great,inline = False)
    embed.add_field(name = "Good",value=good,inline = False)
    embed.add_field(name = "Bad",value=bad,inline = False)
    embed.add_field(name = "Miss",value=miss,inline = False)
    embed.add_field(name = "Combo",value=combo,inline = False)
    if ap:
      embed.add_field(name = "AP",value="All Perfect!",inline = False)
    if fc:
      embed.add_field(name = "FC",value="Full Combo!",inline = False)
    embed.add_field(name = "Your score",value=score,inline = True)
    embed.add_field(name = "Highest score",value=10000000 + total,inline = True)
    await ctx.send(embed = embed)

@slash.slash(name = "track", guild_ids = guild_id)
async def track(ctx,member:discord.Member):
  if (ctx.author.id == int(os.environ['shinmew'])):
    db["track_target"] = member.id
    if str(member.status) != "offline":
      db["track_status"] = "on"
    else:
      db["track_status"] = "off"
    await ctx.send(f"Tracking <@{member.id}>",hidden = True)

async def backup(file:str):
  with open(file,"r",encoding = "utf-8") as file_r:
    if os.path.getsize(file) <= 25:
      print(f"ERROR: The size of {file} is under 25bytes ({os.path.getsize(file)})")
      return
    d = os.path.getsize(file) - os.path.getsize("backup.json")
    if d<3 and d>-3:
      return
    data = json.load(file_r)
    print(f"Size of {file} : {os.path.getsize(file)} bytes")
    print(f"Size of backup.json : {os.path.getsize('backup.json')} bytes")
    print(f"backuped {file}")
    with open("backup.json","w",encoding = "utf-8") as backup_w:
      json.dump(data,backup_w)

async def helpcommand(message):
  with open("help.json","r",encoding = "utf-8") as r:
    helpj = json.load(r)
  info = discord.Embed(title = "指令列表")
  info.set_thumbnail(url = bot.user.avatar_url)
  info.add_field(name = "> **一般功能**",value = helpj["General"],inline = False)
  info.add_field(name = "> **經濟功能**",value = helpj["Economy"],inline = False)
  info.add_field(name = "> **音樂播放功能**",value = helpj["Music"],inline = False)
  info.add_field(name = "> **其他功能**",value = helpj["Other"],inline = False)
  
  await message.reply(embed = info)

async def check_member():
  s = await bot.fetch_user(os.environ['shinmew'])
  now = ""
  guild = bot.get_guild(882263805734813707)
  target = None
  for i in guild.members:
    if i.id == db["track_target"]:
      target = i
      break
  if str(target.status) != "offline":
    now = "on"
  else:
    now = "off"
  if now != db["track_status"]:
    await s.send(f"{target.name} is {now}line")
    db["track_status"] = now

async def presence():
  global songs
  custom=random.choice(songs)
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=custom))

keep_alive.keep_alive()
try:
  bot.run(token)
except:
  os.system("kill 1")