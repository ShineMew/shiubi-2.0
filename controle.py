import discord
from discord.ext import commands
from discord_slash import cog_ext
import asyncio
from datetime import datetime
import math
import json
import random
from replit import db

comprefix = "$"

guild_id = db["guild_id"]
  
async def check_role_developer(ctx):
  for i in range(len(ctx.author.roles)):
    if ctx.author.roles[i].name == "管理員":
      return True    

def _round(n):
  return round(n*1000)/1000

class controle(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @cog_ext.cog_slash(name = "status", description = "get a list of all the members' status in this server", guild_ids = guild_id)
  async def get_member(self,ctx,hidden:bool):
    list = discord.Embed(title = "成員狀態",color = 0xffd500)
    n = 0
    online = ""
    offline = []
    mobile_n = 0
    desktop_n = 0
    mobile = ""
    desktop = ""
    for member in ctx.guild.members:
      if (member.bot):
        continue
      n += 1
      if str(member.status) != "offline":
        online += f"<@{member.id}> "
        if member.is_on_mobile():
          mobile_n += 1
          mobile += f"<@{member.id}> "
        else:
          desktop_n += 1
          desktop += f"<@{member.id}>"
      else:
        offline.append(f"<@{member.id}>")
    
    list.add_field(name = f"線上人數 {n - len(offline)} / {n}人",value = online,inline = False)
    if desktop_n > 0:
      list.add_field(name = f"使用電腦 {desktop_n} / {n - len(offline)}人",value = desktop,inline = False)
    if mobile_n > 0:
      list.add_field(name = f"使用手機 {mobile_n} / {n - len(offline)}人",value = mobile,inline = False)
    await ctx.send(embed = list,hidden = hidden)

  @cog_ext.cog_slash(name = "team", description = "devide something into groups", guild_ids = guild_id)
  async def team(self,ctx,stuff,count:int,team:int):
    list = stuff.split(" ")
    if (count*team>len(list)):
      await ctx.send("輸入數據有誤")
      return
    
    Tembed = discord.Embed(color = 0xe175ff).add_field(name = stuff,value = f"分{team}組  每組{count}人")
    embed = discord.Embed(color = 0xffd500)
    for i in range(team):
      s = ""
      for j in range(count):
        choice = random.randint(0,len(list)-1)
        s += f"{list[choice]} "
        del list[choice]
      embed.add_field(name = f"Team {i+1}",value = s,inline = False)
    for i in list:
      s = ""
      s += f"{i} "
    embed.add_field(name = "Unclassified",value = s,inline = False)
    try:
      await ctx.send(embed = Tembed)
      await ctx.channel.send(embed = embed)
    except:  
      await ctx.send(embed = embed)
    
  @cog_ext.cog_slash(name = "repeat", description = "send a message serveral times", guild_ids = guild_id)   
  async def mention(self,ctx,msg:str,times:int,newline:bool):
    s = ""
    for i in range(times):
      s += msg
      if newline:
        s += "\n"
    await ctx.send(s)
    

  
  @cog_ext.cog_slash(name = "lire", description = "linear regression", guild_ids = guild_id)
  async def lire(self,ctx,xy_data):
    stx = []
    sty = []
    x = []
    y = []
    data = xy_data.split(" ")
    for i in range(len(data)):
      if (i%2):
        y.append(float(data[i]))
      else:
        x.append(float(data[i])) 
    avx = 0
    avy = 0
    sdx = 0
    sdy = 0
    ssx = 0
    ssy = 0
    r = 0
    for i in x:
      avx += i
      ssx += i*i
    for i in y:
      avy += i
      ssy += i*i
    avx /= len(x)
    avy /= len(y)
    print (avx)
    print (avy)
    sdx = math.sqrt(ssx/len(x)-avx*avx)
    sdy = math.sqrt(ssy/len(y)-avy*avy)
    for i in x:
      stx.append((i - avx)/sdx)
    for i in y:
      sty.append((i - avy)/sdy)
    for i in range(len(x)):
      r += stx[i]*sty[i]
    r/= len(x)
    p = r * sdy / sdx
    q = avy - ((r * sdy * avx)/sdx) 
    
    embed = discord.Embed(title = "二維數據分析",color = 0xffd500)
    sdxy = "["
    dxy = "["
    for i in range(len(x)):
      dxy += f" ( {x[i]} , {y[i]} )"
      sdxy += f" ( {_round(stx[i])} , {_round(sty[i])} )"
    dxy += " ]"
    sdxy += " ]"
    embed.add_field(name = "(x,y)",value=dxy,inline = True)
    embed.add_field(name = "x的標準差",value=_round(sdx),inline = True)
    embed.add_field(name = "y的標準差",value=_round(sdy),inline = True)
    embed.add_field(name = "標準化數據(X,Y)",value=sdxy,inline = True)
    embed.add_field(name = "相關係數r",value=_round(r),inline = True)
    if (q>0):
      embed.add_field(name = "(x,y)的回歸方程式",value= f"y = {_round(p)}x + {_round(q)}",inline = True)
    else:
      embed.add_field(name = "(x,y)的回歸方程式",value= f"y = {_round(p)}x {_round(q)}",inline = True)
    
    await ctx.send(embed = embed)
  
  @cog_ext.cog_slash(name = "cb",description = "print the whole combination(two) of the elements",guild_ids = guild_id)
  async def combinatoric(self,ctx,stuff):
    c = ctx.channel
    embed = discord.Embed(title = f"{stuff}組合",color = 0xffd500)
    ele = stuff.split(" ")
    x= 0
    for i in range(0,len(ele)-1):
      for j in range(i+1,len(ele)):
        x+=1
        embed.add_field(name = x,value=f"[{ele[i]},{ele[j]}]",inline = True)
    await c.send(embed = embed)

  @cog_ext.cog_slash(name = "embed",description = "Maybe you need a bigger space, umm?",guild_ids= guild_id)
  async def embed(self,ctx,title,subtitle,item,item_value):      
    if title == "none":
      title = ""
    if subtitle == "none":
      subtitle = ""
    embed = discord.Embed(title = title,description = subtitle)
    name = item.split(" ")
    value = item_value.split(" ")
    if item != "none":
      for i in range(len(name)):
        embed.add_field(name = name[i],value = value[i],inline = True)
    await ctx.channel.send(embed = embed)
    

  @cog_ext.cog_slash(name = "clean",description = "清除一些惱人的東西",guild_ids = guild_id)
  async def clean(self,ctx,num:int):
    if await check_role_developer(ctx):
      await ctx.channel.purge(limit=num)
      await ctx.send(f"清除了{num}個東西, 乾淨多了")
    else:
      await ctx.send(f"[ERROR] {ctx.author.name}權限不足,無法使用/clean")

def setup(bot):
  bot.add_cog(controle(bot))