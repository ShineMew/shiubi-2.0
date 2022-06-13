import discord
from discord.ext import commands

role_dic = {
  "<:hentai:889717279753900072>":889518752046137366,
  "<:nalega:889734185168809984>":888435917151416351,
  "<:gura_shiny:964565802139394068>":953265337460199424,
}

channels = [883686127997947934]

class role(commands.Cog):
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_raw_reaction_add(self,data):
    global role_dic
    global channels
    if data.channel_id in channels:
      rea = str(data.emoji)
      _role = role_dic[rea] if rea in role_dic.keys() else 0
      if not _role:
        role = self.bot.get_guild(data.guild_id).get_role(_role)
        await data.member.add_roles(role)
  
  @commands.Cog.listener()
  async def on_raw_reaction_remove(self,data):
    global role_dic
    if data.channel_id in channels:
      rea = str(data.emoji)
      _role = role_dic[rea] if rea in role_dic.keys() else 0
      if not _role:
        guild = self.bot.get_guild(data.guild_id)
        user = guild.get_member(data.user_id)
        role = guild.get_role(_role)
        await user.remove_roles(role)
      


def setup(bot):
  bot.add_cog(role(bot))