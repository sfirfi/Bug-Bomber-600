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
        embed.add_field(name='Uptime', value=Util.chop_microseconds(datetime.now()-ctx.bot.starttime),inline=True)
        embed.add_field(name='Description', value="A little, maybe not that little bot build to fullfil the needs of the Bug Hunters of the Bug-Bombing Area 600\nThe bot currently is in Work in progress", inline=True)
        await ctx.send(embed=embed)
        
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Shows information about the chosen user"""
        if member == None:
            member = ctx.author
        embed = discord.Embed(color=0x7289DA)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.name} at {ctx.message.created_at.replace(second=0, microsecond=0)}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Name", value=f"{member.name}#{member.discriminator}", inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick, inline=True)
        embed.add_field(name="Account Created At", value=f"{member.created_at.replace(second=0, microsecond=0)} ({(ctx.message.created_at - member.created_at).days} days ago)", inline=True)
        embed.add_field(name="Joined At", value=f"{member.joined_at.replace(second=0, microsecond=0)} ({(ctx.message.created_at - member.joined_at).days} days ago)", inline=True)
        embed.add_field(name="Bot Account", value=member.bot, inline=True)
        embed.add_field(name="Avatar URL", value=member.avatar_url)
        await ctx.send(embed=embed)


    async def __local_check(self, ctx:commands.Context):
        return await permissions.hasPermission(ctx, "utils")


def setup(bot):
    bot.add_cog(ServerutilsCog(bot))
