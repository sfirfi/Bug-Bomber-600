import asyncio
import datetime
import json

import discord
import time
from discord.ext import commands
from collections import deque

from cogs.fun import FunCog
from utils import permissions, BugLog, Util
from utils.Converters import Event


class EventsCog:
    """This cog includes all the features of the modlog"""
    def __init__(self, bot):
        self.bot:commands.Bot = bot
        self.events = dict()
        self.eventChannels = dict()
        bot.DBC.query("SELECT * FROM events WHERE started = 1 AND ended = 0")
        eventlist = bot.DBC.fetch_rows()
        for e in eventlist:
            event = Event().realConvert(bot, e['ID'])
            self.events[event['name']] = event
            for name, c in event["channels"].items():
                self.eventChannels[name] = c
        bot.loop.create_task(eventsChecker(self))
        self.active = True
        self.processing = [] #stopDoubleVotes!
        self.approved = deque(maxlen=20)

    def __unload(self):
        self.active = False #mark as terminated for the checking loop to terminate cleanly

    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "events")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')
    
    @commands.group(name='event')
    @commands.guild_only()
    async def eventCommand(self, ctx: commands.Context):
        """Allows to manage events"""
        if ctx.invoked_subcommand is None:
            await ctx.send("TODO: add explanations")

    @eventCommand.command()
    async def create(self, ctx: commands.Context, name: str, duration: int, durationtype: str,  closingtime: int, closingtimetype: str):
        """Creates a new event"""
        duration = Util.convertToSeconds(duration, durationtype)
        closingtime = Util.convertToSeconds(closingtime, closingtimetype)
        dbc = self.bot.DBC
        name = dbc.escape(name)
        dbc.query("INSERT INTO events (name, duration, closingTime) VALUES ('%s', %d, %d)" % (name, duration, closingtime))
        id = dbc.connection.insert_id()
        await ctx.send(f"Event `{name}` created with ID `{id}`")

    @eventCommand.command()
    async def info(self, ctx: commands.Context, event:Event):
        info = ""
        for key, item in event.items():
            info = f"{info}\n{key}: {item}"
        await ctx.send(info)

    @eventCommand.command()
    async def setDuration(self, ctx: commands.Context, event: Event, duration: int, durationtype: str, closingtime: int, closingtimetype: str):
        newDuration = Util.convertToSeconds(duration, durationtype)
        newClosing = Util.convertToSeconds(closingtime, closingtimetype)
        dbc = self.bot.DBC
        dbc.query('UPDATE events set duration=%d, closingTime=%d WHERE ID=%d' % (newDuration, newClosing, event["ID"]))
        await ctx.send(f"Event {event['name']} duration is now {duration} {durationtype} and submissions will be closed {closingtime} {closingtimetype} in advance")

    @eventCommand.command()
    async def start(self, ctx: commands.Context, event: Event):
        dbc = self.bot.DBC
        dbc.query('UPDATE events set started=1, endtime=%s, closingTime=%s WHERE ID=%d' % (time.time() + event["duration"], time.time() + event["duration"] - event["closingTime"], event["ID"]))
        event = await Event().convert(ctx, event['ID'])
        for name, c in event["channels"].items():
            channel:discord.TextChannel = self.bot.get_channel(c["channel"])
            everyone = None
            for role in channel.guild.roles:
                if role.id == channel.guild.id:
                    everyone = role
                    break
            type = c["type"]
            if type == 0:
                await channel.set_permissions(everyone, read_messages=True)
            elif type == 1 or type == 2:
                await channel.set_permissions(everyone, read_messages=True, send_messages=True)
            self.eventChannels[name] = c
        self.events[event['name']] = event
        await ctx.send(f"{event['name']} has been started!")
        await self.updateScoreboard('Post Pick-Up Hug / Fight Strings!')

    @eventCommand.command()
    async def addChannel(self, ctx: commands.Context, event:Event, channel: discord.TextChannel, codename: str, type: int):
        self.bot.DBC.query("INSERT INTO eventchannels (channel, event, type, name) VALUES (%d, %d, %d, '%s')" % (channel.id, event["ID"], type, codename))
        await ctx.send("Channel assigned")

    @eventCommand.command()
    async def updateBoard(self, ctx: commands.Context, event: Event):
        await self.updateScoreboard(event["ID"])

    positiveID = 418865687365287956
    negativeID = 418865725449437205

    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if "Post Pick-Up Hug / Fight Strings!" in self.events and (message.channel.id == self.eventChannels["hugSubmissions"]["channel"] or message.channel.id == self.eventChannels["fightSubmissions"]["channel"]):
            if not '{0}' in message.content or not '{1}' in message.content:
                reply = await message.channel.send(f"{message.author.mention}: Invalid submission, please make sure it contains both ` {0} ` and ` {1} `")
                await asyncio.sleep(10)
                await message.delete()
                await reply.delete()
            else:
                content = self.bot.DBC.escape(message.content)
                positive = None
                negative = None
                for emoji in self.bot.emojis:
                    if emoji.id == self.positiveID:
                        positive = emoji
                    elif emoji.id == self.negativeID:
                        negative = emoji
                await message.add_reaction(positive)
                await message.add_reaction(negative)

                eventID = self.events['Post Pick-Up Hug / Fight Strings!']["ID"]
                self.bot.DBC.query("INSERT INTO submissions (event, user, submission, message) VALUES (%d, %d, '%s', %d)" % (eventID, message.author.id, content, message.id))
                await self.updateScoreboard('Post Pick-Up Hug / Fight Strings!')

    async def on_raw_reaction_add(self, emoji: discord.PartialEmoji, message_id, channel_id, user_id):
        while message_id in self.processing:
            await asyncio.sleep(1)
        self.processing.append(message_id)
        try:
            message: discord.Message = await self.bot.get_channel(channel_id).get_message(message_id)
        except discord.NotFound:
            #already processed
            pass
        else:
            if "Post Pick-Up Hug / Fight Strings!" in self.events and (message.channel.id == self.eventChannels["hugSubmissions"]["channel"] or message.channel.id == self.eventChannels["fightSubmissions"]["channel"]):
                positiveCount = 0
                negativeCount = 0
                for reaction in message.reactions:
                    async for user in reaction.users():
                        if user == message.author:
                            await message.remove_reaction(reaction.emoji, message.author)
                            reply = await message.channel.send(f"Voting on your own submission is not allowed {message.author.mention}!")
                            await asyncio.sleep(10)
                            await reply.delete()
                        if 396322114208137217 in message.author.roles:
                            await message.remove_reaction(reaction.emoji, message.author)
                            reply = await message.channel.send(f"Test dummies are not allowed to vote {message.author.mention}!")
                            await asyncio.sleep(10)
                            await reply.delete()
                    if not isinstance(reaction.emoji, str) and reaction.emoji.id == self.positiveID:
                        positiveCount = reaction.count
                    elif not isinstance(reaction.emoji, str) and reaction.emoji.id == self.negativeID:
                        negativeCount = reaction.count
                    else:
                        await message.remove_reaction(reaction.emoji, message.author)
                if negativeCount > 3:
                    try:
                        await message.author.send(f"I'm sorry but the folowing submission has been denied:```\n{message.content}```")
                    except Exception as e:
                        #user probably doesn't allow DMs
                        pass
                    await message.delete()
                elif positiveCount > 3:
                    self.approved.append(message.id)
                    content = self.bot.DBC.escape(message.content)
                    eventID = self.events['Post Pick-Up Hug / Fight Strings!']["ID"]
                    self.bot.DBC.query("UPDATE submissions SET points=1 WHERE event=%d AND message=%d" % (eventID, message.id))
                    if message.channel.id == self.eventChannels["hugSubmissions"]["channel"]:
                        self.bot.DBC.query('INSERT INTO hugs (hug, author) VALUES ("%s", "%d")' % (content, message.author.id))
                        await BugLog.logToBotlog(message=f"New hug added: ```\n ID: {self.bot.DBC.connection.insert_id()}\nText: {content}\nAuthor: {message.author.name}#{message.author.discriminator}```")
                        FunCog.hugs.append(content)
                        try:
                            await message.author.send(f"Congratulation, your hug suggestion ```{content}``` has been added to the list!")
                        except Exception:
                            pass
                    elif message.channel.id == self.eventChannels["fightSubmissions"]["channel"]:
                        self.bot.DBC.query('INSERT INTO fights (fight, author) VALUES ("%s", "%d")' % (content, message.author.id))
                        await BugLog.logToBotlog(message=f"New fight added: ```\n ID: {self.bot.DBC.connection.insert_id()}\nText: {content}\nAuthor: {message.author.name}#{message.author.discriminator}```")
                        FunCog.fights.append(content)
                        try:
                            await message.author.send(f"Congratulation, your fight suggestion ```{content}``` has been added to the list!")
                        except Exception:
                            pass
                    await self.updateScoreboard('Post Pick-Up Hug / Fight Strings!')
                    await message.delete()
                self.processing.remove(message_id)

    async def on_raw_message_delete(self, message_id, channel_id):
        if message_id in self.approved:
            BugLog.info("Caught a submision before it fell into the void!")
            return
        self.bot.DBC.query(f"DELETE FROM submissions WHERE message = {message_id} AND points = 0")
        await self.updateScoreboard('Post Pick-Up Hug / Fight Strings!')


    async def on_raw_message_edit(self, message_id, data):
        self.bot.DBC.query(f"SELECT * from submissions WHERE message = {message_id}")
        if self.bot.DBC.fetch_onerow() is not None:
            for name, c in self.eventChannels.items():
                try:
                    message: discord.Message = await self.bot.get_channel(c["channel"]).get_message(message_id)
                except Exception:
                    #wrong channel
                    pass
                else:
                    reply = await message.channel.send(f"{message.author.mention}: You edited your submission, as such all previous votes are no longer valid")
                    for reaction in message.reactions:
                        async for user in reaction.users():
                            if user != self.bot.user:
                                await message.remove_reaction(reaction.emoji, user)
                    await asyncio.sleep(10)
                    await reply.delete()
                    break


    async def updateScoreboard(self, event):
        event = Event().realConvert(self.bot, event)
        self.bot.DBC.query('SELECT count(*) as score, user from submissions WHERE event = %d AND points > 0 GROUP BY user ORDER BY score DESC' % (event["ID"]))
        originaltop = self.bot.DBC.fetch_rows()
        top = originaltop[:5]
        desc = ""
        count = 0
        indicators = [
            ":first_place: ",
            ":second_place: ",
            ":third_place: ",
            "\n4th place: ",
            "5th place: "
        ]
        for entry in top:
            if count >= len(originaltop):
                break
            desc = f"{desc}\n{indicators[count]}: <@{entry['user']}>: {entry['score']}"
            count = count + 1
        if len(desc) == 0:
            desc = "No participants so far :disappointed: "
        self.bot.DBC.query('SELECT count(*) as total from submissions WHERE event = %d' % (event["ID"]))
        total = self.bot.DBC.fetch_onerow()["total"]
        self.bot.DBC.query('SELECT count(*) as accepted from submissions WHERE event = %d AND points > 0' % (event["ID"]))
        accepted = self.bot.DBC.fetch_onerow()["accepted"]
        embed = discord.Embed(title=f"{event['name']} leaderboard", colour=discord.Colour(0xfe9d3d),
                              description=desc,
                              timestamp=datetime.datetime.utcfromtimestamp(time.time()))
        footer = "This event is in progress"
        if time.time() > event["closingTime"]:
            footer = "Submissions are now closed but you can still vote"
        if event["ended"] == 1:
            footer = "This event has ended"
        embed.set_footer(text=footer)
        embed.add_field(name="Total submissions", value=total)
        embed.add_field(name="Approved", value=accepted)
        if event["leaderboard"] is None:
            message = await self.bot.get_channel(int(self.bot.config["Events"]["scoreboardChannel"])).send(embed=embed)
            self.bot.DBC.query(
                'UPDATE events SET leaderboard=%d WHERE ID = %d' % (
                message.id, event["ID"]))
            event["leaderboard"] = message.id
        else:
            message:discord.Message = await self.bot.get_channel(int(self.bot.config["Events"]["scoreboardChannel"])).get_message(event["leaderboard"])
            await message.edit(embed=embed)






def setup(bot):
    bot.add_cog(EventsCog(bot))


async def eventsChecker(cog: EventsCog):
    await cog.bot.wait_until_ready()
    while not cog.bot.is_closed():
        now = time.time()
        ended = []
        for name, event in cog.events.items():
            if now > event["endtime"]:
                ended.append(event)
            if now > event["closingTime"]:
                for name, c in event["channels"].items():
                    channel:discord.TextChannel = cog.bot.get_channel(c["channel"])
                    everyone = None
                    for role in channel.guild.roles:
                        if role.id == channel.guild.id:
                            everyone = role
                            break
                    if c["type"] == 1:
                        await channel.set_permissions(everyone, send_messages=False)
        for event in ended:
            for name, c in event["channels"].items():
                channel: discord.TextChannel = cog.bot.get_channel(c["channel"])
                everyone = None
                for role in channel.guild.roles:
                    if role.id == channel.guild.id:
                        everyone = role
                        break
                if c["type"] == 2:
                    await channel.set_permissions(everyone, send_messages=False)
                if c["type"] == 0 or c["type"] == 1:
                    await channel.set_permissions(everyone, read_messages=False)
            cog.bot.DBC.query(f"UPDATE events SET ended = 1 WHERE ID = {event['ID']}")
            cog.events[event["name"]]["ended"] = 1
            await cog.updateScoreboard(event["name"])
            del cog.events[event["name"]]
            await BugLog.logToBotlog(f"Event ended: {event['name']}")
        await asyncio.sleep(5)
