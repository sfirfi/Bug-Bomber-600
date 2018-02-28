import discord
import time
from discord.ext import commands
from utils import permissions


class ModerationCog:
    """This cog includes the mod utils so ban, kick, mute, warn, etc"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return permissions.hasPermission(ctx, "moderation")

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

    @commands.group(name='perms', aliases=['permissions'])
    async def perms(self, ctx:commands.Context):
        if ctx.invoked_subcommand is None:
            permshelp = "`perms` - Shows this help text"\
                        "\n\n`perms add <role> <permission>` -  Adds the given permission to the role **unfinished**" \
                        "\n\n`perms available` - Shows all available permissions **unfinished**"\
                        "\n\n`perms list <role>` - Shows the current permissions of the given role"\
                        "\n\n`perms rmv <role> <permission>` - Removes the given permission form the role **unfinished**"
            embed = discord.Embed(title='Permissions help', color=0x7c519f)
            embed.add_field(name='\u200b', value=permshelp, inline=True)
            await ctx.send(embed=embed)

    @perms.command()
    async def add(self, ctx:commands.Context, role: discord.Role, permission):
        await ctx.send("Add command")

    @perms.command()
    async def list(self, ctx:commands.Context, role: discord.Role):
        await ctx.send(f"**Permissions of {role.name}**```{permissions.listPermissions(ctx, role)}```")

    @perms.command(name='available', aliases=['avbl', 'avail', 'avl', 'av'])
    async def available(self, ctx:commands.Context):
        await ctx.send("available")

    @perms.command()
    async def rmv(self, ctx:commands.Context, role: discord.Role, permission):
        await ctx.send("rmv")



def setup(bot):
    bot.add_cog(ModerationCog(bot))
