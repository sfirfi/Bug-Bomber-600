import discord
import math
import difflib
from datetime import datetime
from discord.ext import commands
from utils import permissions
from utils import Util
from utils import Configuration


class UtilsCog:
    """This cog includes the server utils such as self assignable roles and the server info related things."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx):
        """Shows information about the bot"""
        embed = discord.Embed(color=0x98f5ff)
        embed.add_field(name='Name', value=f"{ctx.bot.user.name}", inline=True)
        embed.add_field(name='Uptime', value=Util.chop_microseconds(datetime.now()-ctx.bot.starttime),inline=True)
        embed.add_field(name='Description', value="A little, maybe not that little bot build to fullfil the needs of the Bug Hunters of the Bug-Bombing Area 600\nThe bot is currently Work in progress", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, user: str = None):
        """Shows information about the chosen user."""
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
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Name", value=f"{user.name}#{user.discriminator}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Total Warn Count", value=f"{warns}", inline=True)
        embed.add_field(name="Bot Account", value=user.bot, inline=True)
        embed.add_field(name="Animated Avatar", value=user.is_avatar_animated(), inline=True)
        if member != None:
            account_joined = member.joined_at.strftime("%d-%m-%Y")
            embed.add_field(name="Nickname", value=member.nick, inline=True)
            if not member.top_role.is_default():
                embed.add_field(name="Top Role", value=member.top_role.name, inline=True)
            embed.add_field(name="Status", value=member.status, inline=True)
            embed.add_field(name="Joined At", value=f"{account_joined} ({(ctx.message.created_at - member.joined_at).days} days ago)", inline=True)
        account_made = user.created_at.strftime("%d-%m-%Y")
        embed.add_field(name="Account Created At", value=f"{account_made} ({(ctx.message.created_at - user.created_at).days} days ago)", inline=True)
        embed.add_field(name="Avatar URL", value=f"[Click Here]({user.avatar_url})")
        await ctx.send(embed=embed)

    @commands.group()
    async def invite(self, ctx):
        """searches for a valid invite and sends that."""
        if ctx.invoked_subcommand is None:
            invites = await ctx.guild.invites()
            if len(invites) > 0:
                inviteurl = None
                for invite in invites:
                    if invite.max_uses == 0 and invite.max_age == 0:
                        inviteurl = invite.url
                        break;

                if inviteurl is not None:
                    await ctx.send(inviteurl)
                else:
                    await ctx.send("there currently are no invites on this server.")
            else:
                await ctx.send("there currently are no invites on this server.")

    @invite.command(name='new')
    async def newInvite(self, ctx, uses :int = 1):
        """Generates a new invites based on your wished uses. By default the invite has one use."""
        invite = await ctx.guild.text_channels[0].create_invite(max_uses=(uses))
        invite_url = str(invite)
        await ctx.send(f"I've created an invite based of your input! Here is an invite with ``{uses}`` use(s). Link:\n{invite_url}")


    @commands.command(name='serverinfo', aliases=['server'])
    async def serverinfo(self, ctx):
        """Shows information about the current server."""
        guild_features = ", ".join(ctx.guild.features)
        print (guild_features)
        if guild_features == "":
            guild_features = None
        role_list = []
        for i in range(len(ctx.guild.roles)):
            role_list.append(ctx.guild.roles[i].name)
        guild_made = ctx.guild.created_at.strftime("%d-%m-%Y")
        embed = discord.Embed(color=0x7289DA)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Name", value=ctx.guild.name, inline=True)
        embed.add_field(name="ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
        embed.add_field(name="Text Channels", value=len(ctx.guild.text_channels), inline=True)
        embed.add_field(name="Voice Channels", value=len(ctx.guild.voice_channels), inline=True)
        embed.add_field(name="Total Channels", value=len(ctx.guild.text_channels) + len(ctx.guild.voice_channels), inline=True)
        embed.add_field(name="Created at", value=f"{guild_made} ({(ctx.message.created_at - ctx.guild.created_at).days} days ago)", inline=True)
        embed.add_field(name="VIP Features", value=guild_features, inline=True)
        if ctx.guild.icon_url != "":
            embed.add_field(name="Server Icon URL", value=f"[Click Here]({ctx.guild.icon_url})", inline=True)
        embed.add_field(name="Roles", value=", ".join(role_list), inline=True)
        await ctx.send(embed=embed)
        
    @commands.group()
    @commands.guild_only()
    async def selfrole(self, ctx):
        """Allows the joining and leaving of joinable roles"""
        if ctx.subcommand_passed is None:
            await ctx.send(f"Use `{ctx.prefix}help selfrole` for info on how to use this command.")

    @selfrole.command()
    async def list(self, ctx, page=""):
        """Provides a list of all joinable roles"""
        role_id_list = Configuration.getConfigVar(ctx.guild.id, "JOINABLE_ROLES")
        if len(role_id_list)==0:
            await ctx.send("There are currently not selfroles set.")
            return

        rolesPerPage = 20
        roles = ""
        ids = ""
        pages = math.ceil(len(role_id_list)/rolesPerPage)
        if page == "" or not page.isdigit():
            page = 1
        elif int(page) <=1 or int(page) > pages:
            page = 1

        for i in range(rolesPerPage*(int(page)-1),rolesPerPage*int(page)):
            if i < len(role_id_list):
                role = role_id_list[i]
                roles += f"<@&{role}>\n\n"
                ids += str(role) + "\n\n"
            else:
                break

        embed = discord.Embed(title=ctx.guild.name + "'s Joinable roles", color=0x54d5ff)
        embed.add_field(name="\u200b", value=roles, inline=True)
        embed.add_field(name="\u200b", value=ids, inline=True)
        embed.set_footer(text=f"Page {page} of {pages}")
        await ctx.send(embed=embed)


    @selfrole.command()
    async def join(self, ctx, *, rolename):
        """Joins a selfrole group"""
        role = None
        #mention
        if rolename.startswith("<@"):
            roleid = rolename.replace('<','').replace('!','').replace('@','').replace('&','').replace('>','')
            role = discord.utils.get(ctx.guild.roles, id=int(roleid))
        #id
        elif rolename.isdigit():
            role = discord.utils.get(ctx.guild.roles, id=int(rolename))
        #name
        else:
            name = difflib.get_close_matches(rolename,Util.getRoleNameArray(ctx),1,0.4)
            if len(name)>0:
                role = discord.utils.get(ctx.guild.roles, id=Util.getRoleIdDict(ctx)[name[0]])

        if role is None:
                await ctx.send("I cannnot find that role!")
                return

        role_id_list = Configuration.getConfigVar(ctx.guild.id, "JOINABLE_ROLES")
        if role.id in role_id_list and role not in ctx.author.roles:
            await ctx.message.author.add_roles(role, reason=f"{ctx.message.author} Joined role group {role.name}")
            await ctx.send(f"Succesfully joined {role.name}")
        else:
            await ctx.send("That role isn't joinable or you already have joined it.")

    @selfrole.command()
    async def leave(self, ctx, *, rolename):
        """Leaves one of the selfrole groups you are in"""
        role = None
        #mention
        if rolename.startswith("<@"):
            roleid = rolename.replace('<','').replace('!','').replace('@','').replace('&','').replace('>','')
            role = discord.utils.get(ctx.guild.roles, id=int(roleid))
        #id
        elif rolename.isdigit():
            role = discord.utils.get(ctx.guild.roles, id=int(rolename))
        #name
        else:
            name = difflib.get_close_matches(rolename,Util.getRoleNameArray(ctx),1,0.4)
            if len(name)>0:
                role = discord.utils.get(ctx.guild.roles, id=Util.getRoleIdDict(ctx)[name[0]])

        if role is None:
                await ctx.send("I cannnot find that role!")
                return

        role_id_list = Configuration.getConfigVar(ctx.guild.id, "JOINABLE_ROLES")
        if role.id in role_id_list and role in ctx.author.roles:
            await ctx.message.author.remove_roles(role, reason=f"{ctx.message.author} Left role group {role.name}")
            await ctx.send(f"Succesfully left {role.name}")
        else:
            await ctx.send("That role isn't leavable or you don't have the role.")

    async def __local_check(self, ctx):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "utils")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

def setup(bot):
    bot.add_cog(UtilsCog(bot))
