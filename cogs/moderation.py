import discord
import time
from discord.ext import commands
from utils import permissions


class ModerationCog:
    """This cog includes the mod utils so ban, kick, mute, warn, etc"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return permissions.hasPermission(ctx.author.roles, "moderation", ctx.command)

    # The kick command isn't finished yet, it currently is a way to test
    # the Permissions system
    @commands.command(name='kick')
    async def kick(self, ctx):
        await ctx.send('valid')

    @commands.command()
    async def roles(selfs, ctx:commands.Context):
        roles = ""
        ids = ""
        for role in ctx.guild.roles:
            roles += f"<@&{role.id}>\n\n"
            ids += str(role.id) + "\n\n"
        embed = discord.Embed(title=ctx.guild.name + " roles", color=0x54d5ff)
        embed.add_field(name="\u200b", value=roles, inline=True)
        embed.add_field(name="\u200b", value=ids, inline=True)
        await ctx.send(ctx.channel, embed=embed)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        t1 = time.perf_counter()
        await ctx.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send(f":hourglass: Gateway ping is {round((t2 - t1) * 1000)}ms :hourglass:")



def setup(bot):
    bot.add_cog(ModerationCog(bot))
