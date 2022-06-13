import discord
from discord.ext import commands
from discord_slash import cog_ext
import asyncio
import random
import os
import json
from datetime import datetime

def randcre(n:int):
  num = ["0","1","2","3","4","5","6","7","8","9"]
  alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
  spsy = ["!","@","#","$","&","^","%","?"]
  N_alph = 0.3*n + random.randint(n*0.1,n*0.2)
  N_spsy = 0.2*n
  N_num = n - N_alph - N_spsy
  result = ""
  for i in range(n):
    choice = random.randint(0,2)
    if (choice == 0):
      if (N_alph > 0):
        result += random.choice(alphabet)
        N_alph -=1
      else:
        choice = 1
    if (choice == 1):
      if (N_spsy > 0):
        result += random.choice(spsy)  
        N_spsy -= 1
      else:
        choice = 2
    if (choice == 2):
      if (N_num>0):
        result += random.choice(num)  
        N_num -= 1
      else:
        if (N_alph > 0):
          result += random.choice(alphabet)
          N_alph -=1
        else:
          result += random.choice(spsy)  
          N_spsy -= 1
  return result

def newaccess(ctx,id:str):
  while(1):
    access = randcre(20)
    with open("access.json", "r",encoding = "utf-8") as res:
      check = json.load(res)
    if access not in check.values():
      break
  with open("access.json", "r",encoding = "utf-8") as res:
    data = json.load(res)
    with open('access.json','w') as w:
      data[id] = access
      json.dump(data,w)
  return access

class verify(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @cog_ext.cog_slash(name = "RuleTest",description = "Start a new test to get the access key",guild_ids = [917962071189123083])
  async def RuleTest(self,ctx):
    if (ctx.author == os.environ['bad']):
      return
    q_a = {}
    q_a["Q1"] = "C"
    q_a["Q2"] = "C"
    q_a["Q3"] = "B"
    q_a["Q4"] = "A"
    q_a["Q5"] = "A"
    access = 1
    for i in range(5):
      q = ""
      a = ""
      if i == 0:
        q = "題目1 請問您使用Discord的狀況(回答大寫字母) (A)空頭帳號 (B)有在用 (C)Discord就是人生啊!"
        a = q_a["Q1"]
      elif i == 1:
        q = "題目2 請問您是否已經了解本群群規之規範並同意之?(回答大寫字母) (A)沒看啦 (B)沒看但同意 (C)閱讀完畢並且同意"
        a = q_a["Q2"]
      elif i == 2:
        q = "題目3 請問下列何者並不屬於本群所規範限制或禁止之內容?(回答大寫字母) (A)未成年之類犯罪R-18內容 (B)花式RickRoll (C)釣魚或詐騙連結"
        a = q_a["Q3"]
      elif i == 3:
        q = "題目4 請問面對群組內出現辱罵等內容之應對方式下列何者為非?(回答大寫字母) (A)直接對幹 (B)去#踹共處理 (C)投訴他"
        a = q_a["Q4"]
      elif i == 4:
        q = "題目5 請問您是否願意遵守本群群規?(回答大寫字母) (A)同意 (B)不同意"
        a = q_a["Q5"]
      await ctx.author.send(q)
      msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
      if (msg.content == a):
        await ctx.author.send("Correct Answer!")
      else:
        await ctx.author.send("Wrong Answer!")
        access = 0
        break
    if (access):
      key = newaccess(ctx,ctx.author.name)
      await ctx.author.send(f"[ {key} ] is your access key for /check")
    else:
      await ctx.author.send("I'm sorry that you didn't pass the test.")    
  
  @cog_ext.cog_slash(name = "check",description = "use this to login (you need access key)",guild_ids = [917962071189123083])
  async def check(self,ctx,access_key):
    can_use_channel = self.bot.get_channel(957304996574162944)
    if (ctx.channel != can_use_channel):
      await ctx.send(f"{ctx.author.name} Wrong channel, not here")
      return
    with open("access.json", "r",encoding = "utf-8") as res:
      check = json.load(res)
    if (ctx.author.name in check.keys()):
      if (access_key in check.values()):
        with open("access.json", "r",encoding = "utf-8") as res:
          data = json.load(res)
          with open('access.json','w') as w:
            del data[ctx.author.name]
            json.dump(data,w)
        role = self.bot.get_guild(ctx.guild_id).get_role(949665751755796561)
        await ctx.author.add_roles(role)
        embed = discord.Embed(title = "歡迎來到死人拉麵麻園",color = 0x00d118,timestamp = datetime.utcnow())
        embed.add_field(name = f"{ctx.author.name} 已通過驗證",value = "到 <#949666464053485619> 獲得更多身分組!",inline = False)      
        await ctx.send(embed = embed)
      else:
        await ctx.send(f"{ctx.author.name} Wrong access key!")
    else:
      await ctx.send(f"{ctx.author.name}You don't get any access key!")
      
def setup(bot):
  bot.add_cog(verify(bot))