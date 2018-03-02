import discord
from datetime import datetime
from discord.ext import commands
from utils import permissions
from utils import Util


class ServerutilsCog:
    """This cog includes the server utils so self assignable roles and the server"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx: commands.Context):
        """Shows information about the bot"""
        embed = discord.Embed(color=0x98f5ff)
        embed.add_field(name='Name', value=f"{ctx.bot.user.name}", inline=True)
        embed.add_field(name='uptime', value=Util.chop_microseconds(datetime.now()-ctx.bot.starttime),inline=True)
        embed.add_field(name='Description', value="A little, maybe not that little bot build to fullfil the needs of the Bug Hunters of the Bug-Bombing Area 600\nThe bot currently is in Work in progress", inline=True)
        await ctx.send(embed=embed)

    async def __local_check(self, ctx:commands.Context):
        return await permissions.hasPermission(ctx, "utils")


def setup(bot):
    bot.add_cog(ServerutilsCog(bot))
