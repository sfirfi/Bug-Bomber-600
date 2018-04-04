import discord
from datetime import datetime
from discord.ext import commands
from utils import permissions
from utils import Util


class UtilsCog:
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
    async def userinfo(self, ctx : commands.Context, user : str = None):
        """Shows information about the chosen user"""
        if user == None:
            user = ctx.author
            member = ctx.guild.get_member(user.id)
        if user != ctx.author:
            try:
                member = await commands.MemberConverter().convert(ctx, user)
                user = member
            except:
                user = await ctx.bot.get_user_info(int(user))
                member = None
        conn = ctx.bot.DBC
        conn.query(f"SELECT id, warning from warnings where member = {user.id} AND guild = {ctx.guild.id}")
        warnings = conn.fetch_rows()
        warns = len(warnings)
        embed = discord.Embed(color=0x7289DA)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author.name} at {ctx.message.created_at.replace(second=0, microsecond=0)}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Name", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Total Warn Count", value=f"{warns}", inline=True)
        embed.add_field(name="Bot Account", value=user.bot, inline=True)
        embed.add_field(name="Animated Avatar", value=user.is_avatar_animated(), inline=True)
        if member != None:
            account_joined = member.joined_at.strftime("%d-%m-%Y")
            embed.add_field(name="Nickname", value=member.nick, inline=True)
            embed.add_field(name="Top Role", value=member.top_role.name, inline=True)
            embed.add_field(name="Joined At", value=f"{account_joined} ({(ctx.message.created_at - member.joined_at).days} days ago)", inline=True)
        account_made = user.created_at.strftime("%d-%m-%Y")
        embed.add_field(name="Account Created At", value=f"{account_made} ({(ctx.message.created_at - user.created_at).days} days ago)", inline=True)
        embed.add_field(name="Avatar URL", value=user.avatar_url)
        await ctx.send(embed=embed)


    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "fun")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

def setup(bot):
    bot.add_cog(UtilsCog(bot))
