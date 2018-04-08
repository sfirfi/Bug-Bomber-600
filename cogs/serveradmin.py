import discord
from discord.ext import commands

from utils import Configuration
from utils import permissions


class Serveradmin:

    def __init__(self, bot):
        self.bot = bot

    def __unload(self):
        pass

    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "serveradmin")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

    @commands.group()
    async def configure(self, ctx:commands.Context):
        """Configure server specific settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send("See the subcommands (!help configure) for configurations")

    @configure.command()
    async def prefix(self, ctx:commands.Context, newPrefix):
        """Sets a new prefix for this server"""
        Configuration.setConfigVar(ctx.guild.id, "PREFIX", newPrefix)
        await ctx.send(f"The server prefix is now `{newPrefix}`")

    @configure.command()
    async def announce(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the announce channel"""
        Configuration.setConfigVar(ctx.guild.id, "ANNOUNCE", channel.id)
        await ctx.send(f"The announces channel now is <#{channel.id}>")

    @configure.command()
    @commands.bot_has_permissions(manage_roles=True)
    async def muteRole(self, ctx:commands.Context, role:discord.Role):
        """Sets what role to use for mutes"""
        guild:discord.Guild = ctx.guild
        if not guild.me.top_role > role:
            await ctx.send(f"I need a role that is higher then the {role.mention} role to be able to add it to people")
            return
        Configuration.setConfigVar(ctx.guild.id, "MUTED", int(role.id))
        await ctx.send(f"{role.mention} will now be used for muting people, denying send permissions for the role")
        for channel in guild.text_channels:
            await channel.set_permissions(role, reason="Automatic mute role setup", send_messages=False, add_reactions=False)
        for channel in guild.voice_channels:
            await channel.set_permissions(role, reason="Automatic mute role setup", speak=False, connect=False)


def setup(bot):
    bot.add_cog(Serveradmin(bot))
