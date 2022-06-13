import discord
from discord.ext import commands
from discord_slash import cog_ext
from replit import db
import json
import random
import os
import math
import asyncio
from datetime import datetime
from discord_slash.utils.manage_commands import create_option, create_choice

guild_id = db["guild_id"]

item_list = {
  "pickaxe":{"name":"⛏️鐵鎬","id":"0001","price":0},
  "gold":{"name":"🟨黃金","id":"0002","price":2000},
  "rock":{"name":"🪨石頭","id":"0003","price":2},  
  "diamond":{"name":"💎鑽石","id":"0004","price":5000},
  "armor_pieces":{"name":"💠強化結晶","id":"0005","price":100},
  "premium_ticket":{"name":"🎟️高級券","id":"0006","price":10000000}
}
item_option = create_option(
  name = "item",
  description = "chooce a item",
  option_type=3,
  required = True,
  choices = [
    create_choice(name = "石頭",value = "rock"),
    create_choice(name = "🟨黃金",value="gold"),
    create_choice(name = "💎鑽石",value="diamond"),
    create_choice(name = "💠強化結晶",value="armor_pieces"),
    create_choice(name = "🎟️高級券",value="premium_ticket")
  ]
 )

class economy(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @cog_ext.cog_slash(name = "tool",guild_ids = guild_id)
  async def tool(self,ctx):
    if await authorlock(ctx):
      
      with open("bank.json","r",encoding = "utf-8") as r:
        bank = json.load(r)
        with open("bank.json","w",encoding = "utf-8") as w:
          for i in bank["user"].keys():
            bank["user"][i]["tool"] = {"pickaxe":1}
          json.dump(bank,w)
          await ctx.send("已更新")      
  
  @cog_ext.cog_slash(name = "account", description = "Check your account", guild_ids = guild_id)
  async def account(self,ctx):
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
    if not await check_account(str(ctx.author.id)):
      await ctx.send("找不到你的帳戶, 是否要現在幫你創建帳戶?(Y/N)")
      create = await self.bot.wait_for('message', check = lambda message: message.author == ctx.author)
      if (create.content == "Y"):
        await ctx.send("好的, 請稍後")
        await asyncio.sleep(1)
        with open("bank.json","w",encoding = "utf-8") as w:
          bank["user"][ctx.author.id] = {"money":100,"storage":{},"tool":{"pickaxe":1}}
          json.dump(bank,w)
        await ctx.send("已完成帳號的創建")
        await account_information(ctx)
      else:
        await ctx.send("了解, 先不創建")
    else:
      await account_information(ctx)

  @cog_ext.cog_slash(name = "sell", description = "sell something", guild_ids = guild_id,options = [item_option,create_option(name = "count",description = "count",option_type = 4,required = True)])
  async def sell(self,ctx,item,count:int):
    if await check_account(str(ctx.author.id)):
      global item_list
      id = str(ctx.author.id)
      price = 0
      if item not in item_list.keys():
        await ctx.send("未知的物品!")
        return
      else:
        price = item_list[item]["price"]
        item_id = item_list[item]["id"]
        item = item_list[item]["name"]

      with open("bank.json","r",encoding = "utf-8") as r:
        bank = json.load(r)
        if item_id in bank["user"][id]["storage"].keys():
          if bank["user"][id]["storage"][item_id] < count:
            await ctx.send("你沒有這麼多可以賣!")
          else:
            await add_item(id,item_id,count*(-1))
            money = price * count
            await deposite(id,money)
            await ctx.send(f"你賣掉了{count}個{item}, 賺到了{money}🪙")
        else:
          await ctx.send("你沒有這項物品!")
    else:
      await ctx.send("你還沒有帳戶!")   
  
  @cog_ext.cog_slash(name = "shop", description = "create or show a shop",guild_ids = guild_id)
  async def shop(self,ctx,target:discord.Member):
    
    if target.id == ctx.author.id:
      id = ctx.author.id
      if await check_account(str(id)):
        with open("bank.json","r",encoding = "utf-8") as r:
          bank = json.load(r)
          if str(id) not in bank["shop"].keys():
            with open("bank.json","w",encoding = "utf-8") as w: 
              bank["shop"][str(id)] = {}
              json.dump(bank,w)
            await ctx.send(f"已創建 {ctx.author.name} 的商店")
          await shop_information(ctx,target)
      else:
        await ctx.send("你沒有帳戶!")
    else:
      if await check_account(str(target.id)):
        await shop_information(ctx,target)
      else:
        await ctx.send("找不到此人的帳戶!")

  @cog_ext.cog_slash(name = "shop_add", description = "add or edit a item in your shop", guild_ids = guild_id,options = [
    item_option,
    create_option(name = "price",description = "price",option_type=4,required = True),
    create_option(name = "count",description = "count",option_type=4,required = True)
  ])
  async def shop_add(self,ctx,item,price:int,count:int):
    
    id = str(ctx.author.id)
    if await check_account(id):
      global item_list
      with open("bank.json","r",encoding = "utf-8") as r:
        b = json.load(r)
        if id not in b["shop"].keys():
          await ctx.send("你沒有商店!")
          return
      if item not in item_list.keys():
        await ctx.send("未知的物品!")
        return
      else:
        item_id = item_list[item]["id"]
        item = item_list[item]["name"]
      with open("bank.json","r",encoding = "utf-8") as r:
        bank = json.load(r)
        if item_id not in bank["user"][id]["storage"].keys():
          await ctx.send("你沒有這個物品!")
          return
        if bank["user"][id]["storage"][item_id] < count:
          await ctx.send("你沒有這麼多物品!")
          return
        with open("bank.json","w",encoding = "utf-8") as w:
          bank["user"][id]["storage"][item_id] -= count
          if item_id in bank["shop"][id].keys():
            bank["shop"][id][item_id]["count"] += count
            bank["shop"][id][item_id]["price"] = price
            await ctx.send(f"已更改商品{item}的售價為 {price}🪙 庫存增加{count}個")
          else:
            bank["shop"][id][item_id] = {"count":count,"price":price}
            await ctx.send(f"已新增商品{item} 售價{price}🪙 庫存{count}個")
          
          json.dump(bank,w)
    else:
      await ctx.send("你沒有帳戶!")

  @cog_ext.cog_slash(name = "buy", description = "buy something in a shop", guild_ids = guild_id,
    options = [
      create_option(name = "shop",description = "choose a user's shop",option_type=6,required = True),
      item_option,
      create_option(name = "count",description = "count",option_type=4,required = True)
    ]
  )
  async def buy(self,ctx,shop:discord.Member,item:str,count:int):
    global item_list
    
    id = str(shop.id)
    customer = str(ctx.author.id)
    if await check_account(id):
      pass
    else:
      await ctx.send("你沒有帳戶!")
      return
    if item not in item_list.keys():
      await ctx.send("未知的物品!")
      return
    else:
      item_id = item_list[item]["id"]
      item = item_list[item]["name"]
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
      if id not in bank["shop"].keys():
        await ctx.send("找不到此商店!")
        return
      shop = bank["shop"][id]
      if item_id not in shop.keys():
        await ctx.send("該商店並未販賣此商品!")
        return
      if shop[item_id]["count"] < count:
        await ctx.send("該商店庫存不足!")
        return
      if (shop[item_id]["price"] * count) > bank["user"][customer]["money"]:
        await ctx.send(f"你所持金錢不足!")
        return
      
      with open("bank.json","w",encoding = "utf-8") as w:
        #user
        bank["user"][customer]["money"] -= shop[item_id]["price"] * count
        if item_id not in bank["user"][customer]["storage"].keys():
          bank["user"][customer]["storage"][item_id] = count
        else:
          bank["user"][customer]["storage"][item_id] += count
        #shop
        shop[item_id]["count"] -= count
        bank["user"][id]["money"] += shop[item_id]["price"] * count
        json.dump(bank,w)

      trade = discord.Embed(color = 0x0ecc00,timestamp = datetime.utcnow())
      trade.add_field(name = "交易成功!",value = f"<@{customer}>於<@{id}>的商店購買了{count}個 {item} ,花費{shop[item_id]['price'] * count}🪙")
      await ctx.send(embed = trade)
      
  @cog_ext.cog_slash(name = "remit", description = "remit your money to someone", guild_ids = guild_id)
  async def remit(self,ctx,target:discord.Member,money:int):
    
    id = str(ctx.author.id)
    if await check_account(id):
      pass
    else:
      await ctx.send("你沒有帳戶!")
      return
    target_id = str(target.id)
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
      if target_id not in bank["user"].keys():
        await ctx.send("找不到此人的帳戶!")
        return
      if bank["user"][id]["money"] < money:
        await ctx.send("你的金錢不足!")
        return
      await deposite(id,money*(-1))
      await deposite(target_id,money)
      embed=discord.Embed(color = 0x0ecc00,timestamp = datetime.utcnow())
      embed.set_author(name=ctx.author)
      embed.add_field(name="成功轉帳!", value=f"<@{id}>匯了{money}🪙給<@{target_id}>", inline=False)
      await ctx.send(embed=embed)


  @cog_ext.cog_slash(name = "upgrade", description = "upgrade your tool", guild_ids = guild_id)
  async def upgrade(self,ctx,tool):
    
    id = str(ctx.author.id)
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
      info = discord.Embed(title = "升級確認")
      if tool == "pickaxe" or tool == "Pickaxe":
        level = bank["user"][id]["tool"]["pickaxe"]
        if level == 30:
          await ctx.send("你的⛏️鐵鎬已經滿等了, 無法再升級!")
          return
        money_need = round(math.pow((level + 1),3)*0.5+104)
        crsytal_need = round(math.pow(level,1.5))
        info.add_field(name = f"⛏️鐵鎬等級  {level}",value = f"升級為 ⛏️鐵鎬等級  {level+1}")
        info.add_field(name = "升級所需",value=f"🪙金幣 x{money_need}\n💠強化結晶 x{crsytal_need}")
        msg = await ctx.send(embed = info)
        msg2 = await msg.reply("請確認所需之素材皆完備後輸入Y確認")
        answer = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)  
        if answer.content == "Y":
          await answer.delete()
          if bank["user"][id]["money"] < money_need:
            await msg2.edit(content = "金錢不夠!")  
            return
          if bank["user"][id]["storage"]["0005"] < crsytal_need:
            await msg2.edit(content = "強化結晶不夠!")  
            return
          await msg2.edit(content = "準備開始升級工具")
          await asyncio.sleep(2)
          await deposite(id,int(money_need))
          with open("bank.json","w",encoding = "utf-8") as w:
            bank["user"][id]["storage"]["0005"] -= crsytal_need
            bank["user"][id]["money"] -= money_need
            bank["user"][id]["tool"]["pickaxe"]+=1
            json.dump(bank,w)
          info2 = discord.Embed(color = 0x0ecc00) 
          info2.add_field(name = "升級成功!", value = f"升級為 ⛏️鐵鎬等級  {level+1}")
          await msg2.edit(content = "",embed = info2)          
        else:
          await answer.delete()
          await msg2.edit(content = "已取消強化")

async def mine_check(msg):
  if await check_account(str(msg.author.id)):
    
    id = str(msg.author.id)
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
      level = bank["user"][id]['tool']['pickaxe']
    info = discord.Embed(title = f"{msg.author.name} 的挖掘機率",description = f"鐵鎬等級 {level}等")
    info.add_field(name = "石頭🪨", value = f"{round((1-level/600)*10000)/100}%",inline = False)
    info.add_field(name = "黃金🟨", value = f"{round(level/600*10000)/100}%",inline = False)
    info.add_field(name = "強化結晶💠", value = f"{round( 1/(pow(0.9,level) * 480)*10000 )/100}%",inline = False)
    info.add_field(name = "鑽石💎", value = f"{round(level/3000*10000)/100}%",inline = False)
    await msg.channel.send(embed = info)
  else:
    await msg.channel.send(f"{msg.author.name}你還沒有帳戶!")

async def mine(msg):
  if await check_account(str(msg.author.id)):
    with open("bank.json","r",encoding = "utf-8") as r:
      bank = json.load(r)
    pickaxe = bank["user"][str(msg.author.id)]["tool"]["pickaxe"]
    mine = random.randint(0,round(600/pickaxe))
    pieces = random.randint(0,round(480*pow(0.9,pickaxe)))
    c = [random.randint(1,6) for i in range(1,6)]
    count = 0
    for i in c:
      count += i
    count = round(count/6)
    if mine == 10 and random.randint(0,10) == 5:
      await msg.channel.send(f"{msg.author.name} 超級幸運, 挖到了{round(count*0.5)}塊鑽石💎!")
      await add_item(str(msg.author.id),"0004",round(count*0.5))
    else:
      if mine == 10:
        await msg.channel.send(f"{msg.author.name} 十分幸運, 挖到了{round(count*0.5)}塊黃金🟨!")
        await add_item(str(msg.author.id),"0002",count)
      else:
        await msg.channel.send(f"{msg.author.name} 挖到了{count}塊石頭🪨!")
        await add_item(str(msg.author.id),"0003",count)
      if pieces == 4:
        await msg.channel.send(f"{msg.author.name} 額外挖到了{count}塊強化結晶💠!")
        await add_item(str(msg.author.id),"0005",count)
  else:
    await msg.channel.send(f"{msg.author.name} 你還沒有帳戶!")

async def add_item(id:str,stuff,count:int):  
  with open("bank.json","r",encoding = "utf-8") as r:
    bank = json.load(r)
    with open("bank.json","w",encoding = "utf-8") as w:
      if stuff not in bank["user"][id]["storage"].keys():
        bank["user"][id]["storage"][stuff] = count
      else:
        bank["user"][id]["storage"][stuff] += count
      json.dump(bank,w)

async def deposite(id:str,money:int): 
  with open("bank.json","r",encoding = "utf-8") as r:
    bank = json.load(r)
    with open("bank.json","w",encoding = "utf-8") as w:
      bank["user"][id]["money"] += money
      json.dump(bank,w)

async def check_account(id:str):
  with open("bank.json","r",encoding = "utf-8") as r:
    bank = json.load(r)
  if id not in bank["user"].keys():
    return False
  else:
    return True

async def account_information(ctx):
  global item_list
  with open("bank.json","r",encoding = "utf-8") as r:
    bank = json.load(r)
  data = bank["user"][str(ctx.author.id)]
  info = discord.Embed(title = f"{ctx.author.name}的帳戶資訊",color = 0xe0d900)
  info.add_field(name = "帳戶持有金幣",value = f"🪙{data['money']}",inline = False)
  info.set_thumbnail(url = ctx.author.avatar_url)
  if (len(data["storage"].keys()) == 0):
    items = "一無所有"
  else:
    items = ""
    for stuff,count in data["storage"].items():
      for i in item_list.keys():
        if item_list[i]["id"] == stuff:
          stuff = item_list[i]["name"]
          break
      items += f"{stuff}:{count}\n"
  info.add_field(name = "持有物品",value = items,inline = False)
  tools = ""
  for tool,level in data["tool"].items():
    tool = item_list[tool]["name"]
    tools += f"{tool}  {level}等\n"
    
  info.add_field(name = "工具",value = tools,inline = False)
  await ctx.send(embed = info)

async def shop_information(ctx,user):
  with open("bank.json","r",encoding = "utf-8") as r:
    bank = json.load(r)
  if str(user.id) not in bank["shop"].keys():
    await ctx.send("找不到此人的商店")
    return
  data = bank["shop"][str(user.id)]
  info = discord.Embed(title = f"{user.name}的商店",color = 0xe0d900)
  info.set_thumbnail(url = user.avatar_url)
  if (len(data.keys()) == 0):
    info.add_field(name = "空空如也",value = "尚未上架商品",inline = False)
  else:
    for item, pc in data.items():
      for i in item_list.keys():
        if item_list[i]["id"] == item:
          item = item_list[i]["name"]
          break
      price = pc["price"]
      count = pc["count"]
      s = ""
      if count == 0:
        s += "已售罄"
      else:
        s += f"庫存 {count}個"
      info.add_field(name = f"商品:{item}  售價 {price}🪙",value = s,inline = False)
  await ctx.send(embed = info)

async def authorlock(ctx):
  if ctx.author.id == int(os.environ['shinmew']):
    return True
  else:
    await ctx.send("該申請未受回應(身分不符)",hidden = True)
    return False

def setup(bot):
  bot.add_cog(economy(bot))