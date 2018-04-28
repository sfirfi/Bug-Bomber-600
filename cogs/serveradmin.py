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

    @commands.guild_only()
    @commands.group()
    async def configure(self, ctx: commands.Context):
        """Configure server specific settings"""
        if ctx.subcommand_passed is None:
            await ctx.send("See the subcommands (!help configure) for configurations.")

    @configure.command()
    async def prefix(self, ctx: commands.Context, newPrefix):
        """Sets a new prefix for this server"""
        Configuration.setConfigVar(ctx.guild.id, "PREFIX", newPrefix)
        await ctx.send(f"The server prefix is now `{newPrefix}`.")

    @configure.command()
    async def adminrole(self, ctx: commands.Context, roleID):
        """Sets the server admin role"""
        Configuration.setConfigVar(ctx.guild.id, "ADMIN_ROLE_ID", roleID)
        await ctx.send(f"The server admin role is now `{roleID}`.")

    @configure.command()
    async def modrole(self, ctx: commands.Context, roleID):
        """Sets the role with moderation rights"""
        Configuration.setConfigVar(ctx.guild.id, "MOD_ROLE_ID", roleID)
        await ctx.send(f"The server moderation role is now `{roleID}`.")

    @configure.command()
    async def muteRole(self, ctx: commands.Context, role: discord.Role):
        """Sets what role to use for mutes"""
        guild: discord.Guild = ctx.guild
        perms = guild.me.guild_permissions
        if not perms.manage_roles:
            await ctx.send("I require the 'manage_roles' permission to be able to add the role to people.")
            return
        if not guild.me.top_role > role:
            await ctx.send(f"I need a role that is higher then the {role.mention} role to be able to add it to people.")
            return
        Configuration.setConfigVar(ctx.guild.id, "MUTE_ROLE", int(role.id))
        await ctx.send(f"{role.mention} will now be used for muting people, denying send permissions for the role.")
        failed = []
        for channel in guild.text_channels:
            try:
                await channel.set_permissions(role, reason="Automatic mute role setup.", send_messages=False,
                                              add_reactions=False)
            except discord.Forbidden as ex:
                failed.append(channel.mention)
        for channel in guild.voice_channels:
            try:
                await channel.set_permissions(role, reason="Automatic mute role setup.", speak=False, connect=False)
            except discord.Forbidden as ex:
                failed.append(f"Voice channel {channel.name}")
        if len(failed) > 0:
            message = f"I was unable to configure muting in the following channels, there probably is an explicit deny on that channel for 'manage channel' on those channels or their category (if they are synced) for one of my roles (includes everyone role). Please make sure I can manage those channels and run this command again or deny the `send_messages` and `add_reactions` permissions for {role.mention} manually\n."
            for fail in failed:
                if len(message) + len(fail) > 2048:
                    await ctx.send(message)
                    message = ""
                message = message + fail
            if len(message) > 0:
                await ctx.send(message)
        else:
            await ctx.send(f"Automatic mute setup complete.")

    async def on_member_join(self, member):
        """Welcomes new members to the server."""
        if member.guild.id == 391356859518287895:
            channel = self.bot.get_channel(432333845086339072)
            server = self.bot.get_guild(391356859518287895)
            await channel.send(f"Welcome {member.mention}! Please read <#434755785164324904> and let a moderator (Bug Bomber Police) know when you have read the rules.")


    @commands.group()
    @commands.guild_only()
    async def disable(self, ctx: commands.Context):
        """Base command for disabling features"""
        pass

    @disable.command()
    async def mute(self, ctx: commands.Context):
        """Disable the mute feature"""
        role = discord.utils.get(ctx.guild.roles, id=Configuration.getConfigVar(ctx.guild.id, "MUTE_ROLE"))
        if role is not None:
            for member in role.members:
                await member.remove_roles(role, reason=f"Mute feature has been disabled.")
        Configuration.setConfigVar(ctx.guild.id, "MUTE_ROLE", 0)
        await ctx.send("Mute feature has been disabled, all people muted have been unmuted and the role can now be removed.")


def setup(bot):
    bot.add_cog(Serveradmin(bot))
