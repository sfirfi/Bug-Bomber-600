import discord 
from datetime import datetime 
from discord.ext import commands 
from utils import permissions 
from utils import Util
from utils import Configuration

class bugtestCog:
    """This cog includes the embeds for Bug Hunters to test out as needed.""" 
    def __init__(self,bot):
        self.bot = bot 

    @commands.command()
    async def unmaskedlink(self, ctx):
        """Shows an embed for unmasked links."""
        embed = discord.Embed(color=0x98f5ff)
        embed.add_field(name='Name', value=f"Discord's Terms of Services", inline=True)
        embed.add_field(name='Link and Description', value=f"https://discordapp.com/terms This is the Terms of Services by DiscordApp.", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def emoji(self, ctx):
        """Shows an embed for emojis"""
        embed = discord.Embed(color=0x98f5ff)
        embed.add_field(name='Emote', value=f"Emojis", inline=True)
        embed.add_field(name='More Emotes', value=f":heart::heart::heart::heart::heart::heart:", inline=True)
        await ctx.send(embed=embed)
    @commands.command()
    async def maskedlink(self, ctx):
        """Shows an embed for masked links."""
        embed = discord.Embed(UnicodeTranslateError=0x98f5ff)
        embed.add_field(name='Name', value=f"Discord's Terms of Services.", inline=True)
        embed.add_field(name='Link', value=f"[This is the Terms of Services by DiscordApp.](https://discordapp.com/terms)", inline=True)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(bugtestCog(bot))
