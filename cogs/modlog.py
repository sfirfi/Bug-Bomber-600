import asyncio
import datetime
import time

import discord
from discord.embeds import EmptyEmbed
from discord.ext import commands
from discord.ext.commands import BadArgument
from discord.raw_models import RawMessageDeleteEvent, RawMessageUpdateEvent

from cogs.serveradmin import Serveradmin
from utils import permissions, Configuration, BugLog
from utils.DatabaseConnector import LoggedMessage, LoggedAttachment


class ModlogCog:
    """This cog includes all the features of the modlog"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return await permissions.hasPermission(ctx, "modlog")

    @Serveradmin.configure.command()
    async def minorLogChannel(self, ctx, channel: discord.TextChannel):
        """Sets the logging channel for minor logs (edit/delete)"""
        if channel is None:
            raise BadArgument("Missing channel")
        permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
        if permissions.read_messages and permissions.send_messages and permissions.embed_links:
            old = Configuration.getConfigVar(ctx.guild.id, "MINOR_LOGS")
            Configuration.setConfigVar(ctx.guild.id, "MINOR_LOGS", channel.id)
            await ctx.send(f"{channel.mention} will now be used for minor logs")
            if old == 0:
                await ctx.send(f"Caching recent messages for logging...")
                await self.buildCache(ctx.guild)
                await ctx.send("Caching complete")
        else:
            await ctx.send(
                f"I cannot use {channel.mention} for logging, I do not have the required permissions in there (read_messages, send_messages and embed_links).")

    @Serveradmin.disable.command(name="minorLogChannel")
    async def disableMinorLogChannel(self, ctx):
        """Disables minor logs (edit/delete)"""
        Configuration.setConfigVar(ctx.guild.id, "MINOR_LOGS", 0)
        await ctx.send("Minor logs have been disabled.")

    @Serveradmin.configure.command()
    async def joinLogChannel(self, ctx, channel: discord.TextChannel):
        """Sets the logging channel for join/leave logs"""
        permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
        if permissions.read_messages and permissions.send_messages:
            Configuration.setConfigVar(ctx.guild.id, "JOIN_LOGS", channel.id)
            await ctx.send(f"{channel.mention} will now be used for join logs.")
        else:
            await ctx.send(
                f"I cannot use {channel.mention} for logging, I do not have the required permissions in there (read_messages, send_messages).")

    @Serveradmin.disable.command(name="joinLogChannel")
    async def disablejoinLogChannel(self, ctx):
        """Disables join/leave logs"""
        Configuration.setConfigVar(ctx.guild.id, "JOIN_LOGS", 0)
        await ctx.send("Join logs have been disabled.")

    @Serveradmin.configure.command()
    async def modLogChannel(self, ctx, channel: discord.TextChannel):
        """Sets the logging channel for modlogs (mute/kick/ban/...)"""
        permissions = channel.permissions_for(ctx.guild.get_member(self.bot.user.id))
        if permissions.read_messages and permissions.send_messages:
            Configuration.setConfigVar(ctx.guild.id, "MOD_LOGS", channel.id)
            await ctx.send(f"{channel.mention} will now be used for mod logs.")
        else:
            await ctx.send(
                f"I cannot use {channel.mention} for logging, I do not have the required permissions in there (read_messages, send_messages)")

    @Serveradmin.disable.command(name="modLogChannel")
    async def disablemodLogChannel(self, ctx):
        """Disables the modlogs (mute/kick/ban/...)"""
        Configuration.setConfigVar(ctx.guild.id, "MOD_LOGS", 0)
        await ctx.send("Mod logs have been disabled.")

    async def buildCache(self, guild: discord.Guild):
        start = time.perf_counter()
        BugLog.info(f"Populating modlog with missed messages during downtime for {guild.name} ({guild.id}).")
        newCount = 0
        editCount = 0
        count = 0
        for channel in guild.text_channels:
            if channel.permissions_for(guild.get_member(self.bot.user.id)).read_messages:
                async for message in channel.history(limit=250, reverse=False):
                    if message.author.bot:
                        continue
                    logged = LoggedMessage.get_or_none(messageid=message.id)
                    if logged is None:
                        LoggedMessage.create(messageid=message.id, author=message.author.id,
                                             content=self.bot.aes.encrypt(message.content), timestamp=message.created_at.timestamp(),
                                             channel=channel.id)
                        for a in message.attachments:
                            LoggedAttachment.create(id=a.id, url=self.bot.aes.encrypt(a.url), isImage=(a.width is not None or a.width is 0),
                                                    messageid=message.id)
                        newCount = newCount + 1
                    elif self.bot.aes.decrypt(logged.content) != message.content:
                        logged.content = self.bot.aes.encrypt(message.content)
                        logged.save()
                        editCount = editCount + 1
                    count = count + 1
        BugLog.info(f"Discovered {newCount} new messages and {editCount} edited in {guild.name} (checked {count}) in {time.perf_counter() - start }s.")

    async def on_ready(self):
        for guild in self.bot.guilds:
            if Configuration.getConfigVar(guild.id, "MINOR_LOGS") is not 0:
                await self.buildCache(guild)

    async def on_message(self, message: discord.Message):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        if not hasattr(message.channel, "guild") or message.channel.guild is None:
            return
        if Configuration.getConfigVar(message.guild.id, "MINOR_LOGS") is 0 or message.author.bot:
            return
        for a in message.attachments:
            LoggedAttachment.create(id=a.id, url=self.bot.aes.encrypt(a.url), isImage=(a.width is not None or a.width is 0),
                                    messageid=message.id)
        LoggedMessage.create(messageid=message.id, author=message.author.id, content=self.bot.aes.encrypt(message.content),
                             timestamp=message.created_at.timestamp(), channel=message.channel.id)

    async def on_member_update(self, before, after):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        for role in before.roles:
            if not role in after.roles:
                channelid = Configuration.getConfigVar(before.guild.id, "MINOR_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":pencil2: ``{role.name}`` has been removed from {before.name}#{before.discriminator} (`{before.id}`)")
        for role in after.roles:
            if not role in before.roles:
                channelid = Configuration.getConfigVar(before.guild.id, "MINOR_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":pencil2: ``{role.name}`` has been added to {before.name}#{before.discriminator} (`{before.id}`)")
        if before.nick != after.nick:
            if before.nick is None:
                channelid = Configuration.getConfigVar(before.guild.id, "MINOR_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":name_badge: {before.name}#{before.discriminator} (`{before.id}`) has added nickname ``{after.nick}``.")
            elif after.nick is None:
                channelid = Configuration.getConfigVar(before.guild.id, "MINOR_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":name_badge: {before.name}#{before.discriminator} (`{before.id}`) has removed their nickname, was previously ``{before.nick}``.")
            else:
                channelid = Configuration.getConfigVar(before.guild.id, "MINOR_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":name_badge: {before.name}#{before.discriminator} (`{before.id}`) has changed their nickname from `{before.nick}` to `{after.nick}`.")


    async def on_raw_message_delete(self, data: RawMessageDeleteEvent):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        message = LoggedMessage.get_or_none(messageid=data.message_id)
        if message is not None:
            channel: discord.TextChannel = self.bot.get_channel(data.channel_id)
            user: discord.User = self.bot.get_user(message.author)
            hasUser = user is not None
            channelid = Configuration.getConfigVar(channel.guild.id, "MINOR_LOGS")
            if channelid is not 0:
                logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                if logChannel is not None:
                    embed = discord.Embed(timestamp=datetime.datetime.utcfromtimestamp(time.time()),
                                          description=self.bot.aes.decrypt(message.content))
                    embed.set_author(name=user.name if hasUser else message.author,
                                     icon_url=user.avatar_url if hasUser else EmptyEmbed)
                    embed.set_footer(text=f"Sent in #{channel.name}")
                    await logChannel.send(
                        f":wastebasket: Message by {user.name if hasUser else message.author} (`{user.id}`) in {channel.mention} has been removed.",
                        embed=embed)

    async def on_raw_message_edit(self, event: RawMessageUpdateEvent):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        message = LoggedMessage.get_or_none(messageid=event.message_id)
        if message is not None and "content" in event.data:
            channel: discord.TextChannel = self.bot.get_channel(int(event.data["channel_id"]))
            user: discord.User = self.bot.get_user(message.author)
            hasUser = user is not None
            channelid = Configuration.getConfigVar(channel.guild.id, "MINOR_LOGS")
            if channelid is not 0:
                logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                if logChannel is not None:
                    if message.content == event.data["content"]:
                        # prob just pinned
                        return
                    embed = discord.Embed(timestamp=datetime.datetime.utcfromtimestamp(time.time()))
                    embed.set_author(name=user.name if hasUser else message.author,
                                     icon_url=user.avatar_url if hasUser else EmptyEmbed)
                    embed.set_footer(text=f"Sent in #{channel.name}")
                    if self.bot.aes.decrypt(message.content) is "":
                        oldMessage = "---There was no message data before, this probably is the edit of an attachment.---"
                    else:
                        oldMessage = self.bot.aes.decrypt(message.content)

                    embed.add_field(name="Before", value=(oldMessage[:1000] + '...') if len(oldMessage) > 1020 else oldMessage, inline=False)
                    embed.add_field(name="After", value=(event.data["content"][:1000] + '...') if len(event.data["content"]) > 1020 else event.data["content"], inline=False)
                    await logChannel.send(
                        f":pencil: Message by {user.name} (`{user.id}`) in {channel.mention} has been edited",
                        embed=embed)
                    message.content = self.bot.aes.encrypt(event.data["content"])
                    message.save()

    async def on_member_join(self, member: discord.Member):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        channelid = Configuration.getConfigVar(member.guild.id, "JOIN_LOGS")
        if channelid is not 0:
            logChannel: discord.TextChannel = self.bot.get_channel(channelid)
            if logChannel is not None:
                dif = (datetime.datetime.utcnow() - member.created_at)
                minutes, seconds = divmod(dif.days * 86400 + dif.seconds, 60)
                hours, minutes = divmod(minutes, 60)
                age = (f"{dif.days} days") if dif.days > 0 else f"{hours} hours, {minutes} mins."
                await logChannel.send(
                    f":inbox_tray: {member.display_name}#{member.discriminator} (`{member.id}`) has joined, account created {age} ago.")

    async def on_member_remove(self, member: discord.Member):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target == member:
                channelid = Configuration.getConfigVar(member.guild.id, "MOD_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":boot: {member} (`{member.id}`) has been kicked.")
            else:
                channelid = Configuration.getConfigVar(member.guild.id, "JOIN_LOGS")
                if channelid is not 0:
                    logChannel: discord.TextChannel = self.bot.get_channel(channelid)
                    if logChannel is not None:
                        await logChannel.send(f":outbox_tray: {member} (`{member.id}`) has left the server.")


    async def on_member_ban(self, guild, user):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        channelid = Configuration.getConfigVar(guild.id, "MOD_LOGS")
        if channelid is not 0:
            logChannel: discord.TextChannel = self.bot.get_channel(channelid)
            if logChannel is not None:
                await logChannel.send(
                    f":rotating_light: {user.display_name}#{user.discriminator} (`{user.id}`) has been banned from the server.")

    async def on_member_unban(self, guild, user):
        while not self.bot.startup_done:
            await asyncio.sleep(1)
        channelid = Configuration.getConfigVar(guild.id, "MOD_LOGS")
        if channelid is not 0:
            logChannel: discord.TextChannel = self.bot.get_channel(channelid)
            if logChannel is not None:
                await logChannel.send(
                    f":rotating_light: {user.display_name}#{user.discriminator} (`{user.id}`) has been unbanned from the server.")

def setup(bot):
    bot.add_cog(ModlogCog(bot))
