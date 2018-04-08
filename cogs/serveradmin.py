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


    @commands.group()
    async def disable(self, ctx:commands.Context):
        """Base command for disabeling features"""
        pass

    @disable.command()
    async def mute(self, ctx:commands.Context):
        """Disable the mute feature"""
        role = discord.utils.get(ctx.guild.roles, id=Configuration.getConfigVar(ctx.guild.id, "MUTED"))
        if role is not None:
            for member in role.members:
                await member.remove_roles(role, reason=f"Mute feature has been dissabled")
        Configuration.setConfigVar(ctx.guild.id, "MUTED", 0)
        await ctx.send("Mute feature has been dissabled, all people muted have been unmuted and the role can now be removed")

    @disable.command(name="announce")
    async def announce1(self, ctx:commands.Context):
        Configuration.setConfigVar(ctx.guild.id, "ANNOUNCE", 0)
        await ctx.send("The announce channel has been reseted.")


def setup(bot):
    bot.add_cog(Serveradmin(bot))
