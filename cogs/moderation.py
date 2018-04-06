import discord
import time
import math
from discord.ext import commands
from utils import permissions
from utils import Util
from utils import Configuration

#Converters
class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity

#Actual Cog
class ModerationCog:
    """This cog includes the mod utils like ban, kick, mute, warn, etc"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "moderation")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx:commands.Context, *, page = ""):
        """Shows all roles of the server and their IDs"""
        rolesPerPage = 20
        roles = ""
        ids = ""
        pages = math.ceil(len(ctx.guild.roles)/rolesPerPage)
        if page == "" or not page.isdigit():
            page = 1
        elif int(page) <=1 or int(page) > pages:
            page = 1

        for i in range(rolesPerPage*(int(page)-1),rolesPerPage*int(page)):
            if i < len(ctx.guild.roles):
                role = ctx.guild.roles[i]
                roles += f"<@&{role.id}>\n\n"
                ids += str(role.id) + "\n\n"
            else:
                break

        embed = discord.Embed(title=ctx.guild.name + " roles", color=0x54d5ff)
        embed.add_field(name="\u200b", value=roles, inline=True)
        embed.add_field(name="\u200b", value=ids, inline=True)
        embed.set_footer(text=f"Page {page} of {pages}")
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Shows the Gateway Ping"""
        t1 = time.perf_counter()
        await ctx.trigger_typing()
        t2 = time.perf_counter()
        await ctx.send(f":hourglass: Gateway Ping is {round((t2 - t1) * 1000)}ms :hourglass:")

    @commands.group(name='perms', aliases=['permissions'])
    @commands.guild_only()
    async def perms(self, ctx:commands.Context):
        """Manages the permissions."""
        if ctx.invoked_subcommand is None:
            permshelp = "`perms` - Shows this help text"\
                    "\n\n`perms add <role> <permission>` -  Adds the given permission to the role" \
                    "\n\n`perms available` - Shows all available permissions"\
                    "\n\n`perms list <role>` - Shows the current permissions of the given role"\
                    "\n\n`perms rmv <role> <permission>` - Removes the given permission form the role"
            embed = discord.Embed(title='Permissions help', color=0x7c519f)
            embed.add_field(name='\u200b', value=permshelp, inline=True)
            await ctx.send(embed=embed)

    @perms.command()
    async def add(self, ctx:commands.Context, role: discord.Role, permission):
        """Adds the given permission to the role."""
        await ctx.send(permissions.addPermission(ctx, role, permission))

    @perms.command()
    async def list(self, ctx:commands.Context, role: discord.Role):
        """Shows all available permissions."""
        perms = permissions.listPermissions(ctx, role)
        if perms == '':
            perms = "This role doesn't has any permissions."

        embed = discord.Embed(title=f"Permissions of {role.name}", color=0x7c519f)
        embed.add_field(name='\u200b', value=perms, inline=True)
        await ctx.send(embed=embed)

    @perms.command(name='available', aliases=['avbl', 'avail', 'avl', 'av'])
    async def available(self, ctx:commands.Context):
        """Shows the current permissions of the given role."""
        info =  "`*`    - Grants access to all commands\n"\
                "`cog.*`    - Grants access to all commands of the cog \n"\
                "`cog.command`  - Grants access to command"
        avail = ""
        for perm in permissions.listAvailable(ctx):
            avail += f"{perm}\n"

        embed = discord.Embed(title='Available permissions', color=0x7c519f)
        embed.add_field(name='Information', value=info, inline=True)
        embed.add_field(name='Available permissions', value=avail, inline=False)
        await ctx.send(embed=embed)

    @perms.command()
    async def rmv(self, ctx:commands.Context, role: discord.Role, permission):
        """Removes the given permission from the role."""
        await ctx.send(permissions.rmvPermission(ctx, role, permission))

    @commands.command()
    @commands.guild_only()
    async def announce(self, ctx: commands.Context,*,announce = ""):
        """Announces the given text in the set announcement channel."""
        channel = ctx.bot.get_channel(int(Configuration.getConfigVar(ctx.guild.id, "ANNOUNCE")))
        if channel != None:
            if(announce != ""):
                await channel.send(announce)
            else:
                await ctx.send("You need to give me a message that I can announce.")
        else:
            await ctx.send("There is no announce channel set!")

    @commands.command()
    @commands.guild_only()
    async def warn(self, ctx: commands.Context, member: discord.Member, *, warning = ""):
        """Warns a user."""
        if warning != "" and member.id != ctx.author.id and member.id != ctx.bot.user.id:
            ctx.bot.DBC.query(f"INSERT INTO warnings (guild,member,warning,moderator, time) VALUES ({ctx.guild.id}, {member.id},'{warning}',{ctx.message.author.id}, UTC_TIMESTAMP())")
            await ctx.send(f":warning: {member.name} ({member.id}) has been warned. Warn message: `{warning}`")
            await member.send(f"A moderator warned you in {ctx.guild.name} for {warning}")
        elif member.id == ctx.author.id or member.id == ctx.bot.user.id:
            await ctx.send("You can't warn that user!")
        else:
            await ctx.send("You need to enter a Warning message.")

    @commands.group()
    @commands.guild_only()
    async def warnings(self, ctx: commands.Context):
         """Show and manage Warnings.."""
         if ctx.invoked_subcommand is None:
            warningshelp = "`warnings` - Shows this help text"\
                    "\n\n`warnings info <id>` - Shows all information of the given warning"\
                    "\n\n`warnings list <user> [<page>]` - Shows all warnings of the given user"
            embed = discord.Embed(title='Warnings help', color=0x54ffff)
            embed.add_field(name='\u200b', value=warningshelp, inline=True)
            await ctx.send(embed=embed)

    @warnings.command(name="list")
    async def list2(self, ctx: commands.Context, member: discord.Member, page: str= ""):
        conn = ctx.bot.DBC
        conn.query(f"SELECT id, warning from warnings where member = {member.id} AND guild = {ctx.guild.id}")
        warnings = conn.fetch_rows()
        if(len(warnings) is 0):
            await ctx.send("This user doesn't has any warnings.")
        else:
            warningsPerPage = 5
            warns = "```\nGlobal ID | Warning message\n"
            pages = math.ceil(len(warnings)/warningsPerPage)
            if page == "" or not page.isdigit():
                page = 1
            elif int(page) <=1 or int(page) > pages:
                page = 1

            for i in range(warningsPerPage*(int(page)-1),warningsPerPage*int(page)):
                if i < len(warnings):
                    warns += f"{warnings[i]['id']}: {warnings[i]['warning']}\n"
                else:
                    break

            embed = discord.Embed(title=f"Warnings of {member.name}", color=0x54ffff)
            embed.add_field(name="\u200b", value=warns + "```", inline=True)
            embed.set_footer(text=f"Page {page} of {pages}")
            await ctx.send(embed=embed)


    @warnings.command()
    async def info(self, ctx: commands.Context, warning: int):
        conn = ctx.bot.DBC
        conn.query(f"SELECT * FROM warnings where id = {warning} AND guild = {ctx.guild.id}")
        warning = conn.fetch_rows()
        if len(warning) is 0:
            await ctx.send("I can't find that warning.")
        else:
            warning = warning[0]
            embed = discord.Embed(title=f"Warning {warning['ID']}", color=0x54ffff)
            embed.add_field(name='Member', value=ctx.bot.get_user(warning['member']).name, inline=True)
            embed.add_field(name='Moderator', value=ctx.bot.get_user(warning['moderator']).name, inline=True)
            embed.add_field(name='UTC Time', value=warning['time'], inline=True)
            embed.add_field(name='Warning', value=warning['warning'], inline=False)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason = "No reason given."):
        """Kicks an user from the server."""
        await ctx.guild.kick(user, reason=f"Moderator: {ctx.author.name} ({ctx.author.id}) Reason: {reason}")
        await ctx.send(f":ok_hand: {user.name} ({user.id}) was kicked. Reason: `{reason}`")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason = "No reason given"):
        """Bans an user from the server."""
        await ctx.guild.ban(user, reason=f"Moderator: {ctx.author.name} ({ctx.author.id}) Reason: {reason}")
        await ctx.send(f":ok_hand: {user.name} ({user.id}) was banned. Reason: `{reason}`")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    async def forceban(self, ctx, user_id: int, *, reason = "No reason given"):
        """Bans a user even if they are not in the server"""
        user = await ctx.bot.get_user_info(user_id)
        if user == ctx.author or user == ctx.bot.user:
            await ctx.send("You cannot ban that user!")
        else:
            await ctx.guild.ban(user, reason=f"Moderator: {ctx.author.name} ({ctx.author.id}) Reason: {reason}")
            await ctx.send(f":ok_hand: {user.name} ({user.id}) was banned. Reason: `{reason}`")

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason = "No reason given"):
        """Unbans an user from the server."""
        await ctx.guild.unban(member.user, reason=f"Moderator: {ctx.author.name} ({ctx.author.id}) Reason: {reason}")
        await ctx.send(f":ok_hand: {member.user.name} ({member.user.id}) has been unbanned. Reason: `{reason}`")
        #This should work even if the user isn't cached

def setup(bot):
    bot.add_cog(ModerationCog(bot))
