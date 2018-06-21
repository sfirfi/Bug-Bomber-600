# This cog includes the fun comments so !hug, fight, cat etc
import asyncio
from datetime import datetime

import discord
import time
from discord.ext import commands
from discord.ext.commands import BucketType, BadArgument
import random

from utils import permissions, BugLog
from utils.Database import SQLDB
from utils import Util
from utils import Configuration

import configparser
import imgurpython

# Extra stuff for the commands
from utils.DatabaseConnector import LoggedAttachment, LoggedMessage


class FunExtras:

    async def catImg():
        html = await Util.grepFromWeb('https://thecatapi.com/api/images/get?format=html')
        html = html.split('src="')
        url = html[1].replace('"></a>', '').replace('http', 'https')
        return url

    async def dogImg():
        while True:
            url = await Util.grepJsonFromWeb('http://random.dog/woof.json')
            if not url['url'].endswith(('mp4', 'webm')):
                return url['url']

    async def foxImg():
        html = await Util.grepFromWeb('http://www.thedailyfox.org/random')
        html = html.split('<img src="')
        html = html[1].split('"')
        url = html[0]
        return url

    async def lizardImg():
        url = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/lizard')
        return url['url']

    async def nekoImg():
        url = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/neko')
        return url['url']

    async def patImg():
        url = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/pat')
        return url['url']

    async def imgurImg(search):
        config = configparser.ConfigParser()
        config.read('config.ini')
        client_id = config['Credentials']['imgur_client_id']
        client_secret = config['Credentials']['imgur_client_secret']
        imgur = imgurpython.ImgurClient(client_id, client_secret)
        galleryItems = imgur.gallery_search(search, window='all')
        images = []
        for i in galleryItems:
            if type(i) is imgurpython.imgur.models.gallery_image.GalleryImage and not i.link.endswith(('.mp4','.webm')) and not i.link.startswith("http://"):
                images.append(i)

        if len(images) >0:
            url = images[random.randint(0, len(images)-1)].link
            return url
        else:
            return None

#A ctual cog
class FunCog:
    config = configparser.ConfigParser()
    config.read('config.ini')
    hugs = []
    fights = []
    async def __local_check(self, ctx: commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "fun")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

    @commands.command(name='hug', aliases=['huh','hugh'])
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['hug'], BucketType.user)
    async def hug(self, ctx: commands.Context, friend: discord.Member):
        """Hugs a person."""
        if friend == ctx.author:
            await ctx.send("You must be really lonely if you need to hug yourself, have one from me instead!")
            ctx.command.reset_cooldown(ctx)
        elif friend == self.bot.user:
            await ctx.send("Thanks for the hug!")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.hugs[random.randint(0, len(FunCog.hugs)-1)].format(friend.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['fight'], BucketType.user)
    async def fight(self, ctx: commands.Context, victim: discord.Member):
        """Fights a person."""
        if victim == ctx.author:
            await ctx.send("How would you even do that?")
            ctx.command.reset_cooldown(ctx)
        elif victim == self.bot.user:
            await ctx.send("You sure you want to do that? <:GhoulBan:417535190051586058>")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send(FunCog.fights[random.randint(0, len(FunCog.fights)-1)].format(victim.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['pet'], BucketType.user)
    async def pet(self, ctx: commands.Context, pet: discord.Member):
        """Pets a person."""
        if pet == ctx.author:
            await ctx.send("Petting yourself, how would you even do that?")
            ctx.command.reset_cooldown(ctx)
        elif pet == self.bot.user:
            await ctx.send("<a:typing:393881558169288716>")
            ctx.command.reset_cooldown(ctx)
        else:
            await ctx.send("{0}: {1} pets you".format(pet.mention, ctx.author.name))

    @commands.command()
    @commands.guild_only()
    async def summon(self, ctx, *, target: str):
        """Summons a person."""
        try:
            member = await commands.MemberConverter().convert(ctx, target)
        except BadArgument as ex:
            await ctx.send(f"**I have summoned the one known as {target}!**")
            await asyncio.sleep(5)
            await ctx.send("Be prepared as there is no stopping this summoning!")
            await asyncio.sleep(5)
            await ctx.send("The summoning will be complete soon!")
            await asyncio.sleep(5)
            await ctx.send("_Please note that 'soon' in bot time is not always considered the same as 'soon' in human time_")
            await asyncio.sleep(5)
            await ctx.send("Have a nice day!")
        else:
            if member == ctx.author:
                await ctx.send("Summoning yourself? That's cheating!")
                ctx.command.reset_cooldown(ctx)
            else:
                await ctx.send(f"{member.name} is already a member of this server, do the ping youself, lazy humans.")

    @commands.command()
    @commands.cooldown(1, config['Cooldowns']['img'], BucketType.user)
    async def img(self, ctx: commands.context, *, search):
        """Sends a img for the given search term. The terms [cat,dog,fox,lizard, neko] will random generate, other terms will spit out a Imgur img."""
        search = search.lower().strip()
        imgFunctions = {
            'cat': FunExtras.catImg,
            'dog': FunExtras.dogImg,
            'fox': FunExtras.foxImg,
            'lizard': FunExtras.lizardImg,
            'neko': FunExtras.nekoImg,
            'pat': FunExtras.patImg
        }
        image = imgFunctions.get(search, None)
        if image is not None:
            url = await image()
        else:
            url = await FunExtras.imgurImg(search)

        if url is not None:
            try:
                embed = discord.Embed(color=0x3dede6)
                embed.set_image(url=url)
                await ctx.send(embed=embed)
            except TimeoutError:
                await ctx.send("Oops! I fell asleep... sorry.")
        else:
            await ctx.send("I can't find a Image for that search term.")
        
            
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, config['Cooldowns']['ahug'], BucketType.user)
    async def ahug(self, ctx: commands.Context, member: discord.Member = None):
        """Sends an anime hug gif."""
        img = await Util.grepJsonFromWeb('https://nekos.life/api/v2/img/hug')
        embed = discord.Embed(color=0xe59400)
        if member is not None :
        
            if member.id is not ctx.message.author.id:
             try: embed.add_field(name=f"**{ctx.author.name} gives {member.name} an Anime hug.** :hearts:", value="\u200b")
                except TimeoutError:
                    await ctx.send("Oops! I fell asleep... sorry."
             else:
                embed.add_field(name=f"**{ctx.bot.user.name} gives {member.name} an Anime hug.** :hearts:", value="\u200b")

        embed.set_image(url=img['url'])
        await ctx.send(embed=embed)

    @commands.command()
    async def quote(self, ctx: commands.Context, messageid: int):
        """Quotes the requested message."""
        async with ctx.typing():
            try:
                message = LoggedMessage.get(messageid=messageid)
                embed = discord.Embed(colour=discord.Color(0xd5fff),
                                        timestamp=datetime.utcfromtimestamp(message.timestamp))
                user = await ctx.bot.get_user_info(message.author)
                embed.set_author(name=user.name, icon_url=user.avatar_url)
                embed.set_footer(text=f"Sent in #{self.bot.get_channel(message.channel).name} | Quote requested by {ctx.author.display_name} | {messageid}")
                attachmentsraw = LoggedAttachment.select().where(LoggedAttachment.messageid == messageid)
                attachments = []
                for attachmentraw in attachmentsraw:
                    attachments.append(attachmentraw)
                if attachments != [] and attachments != None:
                    if len(attachments) == 1 and attachments[0].isImage:
                        embed.set_image(url=self.bot.aes.decrypt(attachments[0].url))
                    else:
                        for attachment in attachments:
                            embed.add_field(name="Attachment link", value=self.bot.aes.decrypt(attachment.url))
                if message.content is not None and message.content is not "":
                    embed.description = self.bot.aes.decrypt(message.content)
                await ctx.send(embed=embed)
                await ctx.message.delete()
            except LoggedMessage.DoesNotExist:
                    dmessage = None
                    for server in ctx.bot.guilds:
                        for txtchannel in server.text_channels:
                            try:
                                dmessage = await txtchannel.get_message(messageid)
                                embed = discord.Embed(colour=discord.Color(0xd5fff),
                                        timestamp=datetime.utcfromtimestamp(dmessage.created_at.timestamp()))
                                embed.set_author(name=dmessage.author.name, icon_url=dmessage.author.avatar_url)
                                embed.set_footer(text=f"Sent in #{dmessage.channel.name} | Quote Requested by {ctx.author.display_name} | {dmessage.id}")
                                if dmessage.attachments != []:
                                    if len(dmessage.attachments) == 1:
                                        embed.set_image(url=dmessage.attachments[0].url)
                                    else:
                                        for attachment in dmessage.attachments:
                                            embed.add_field(name="Attachment link", value=attachment.url)
                                if dmessage.content is not None:
                                    embed.description = dmessage.content
                                await ctx.send(embed=embed)
                                await ctx.message.delete()
                                for a in dmessage.attachments:
                                    LoggedAttachment.get_or_create(id=a.id, url=self.bot.aes.encrypt(a.url),
                                                                        isImage=(a.width is not None or a.width is 0),
                                                                        messageid=dmessage.id)
                                LoggedMessage.create(messageid=messageid, content=self.bot.aes.encrypt(dmessage.content),
                                                                        author=dmessage.author.id,
                                                                        timestamp=dmessage.created_at.timestamp(),
                                                                        channel=dmessage.channel.id)
                            except discord.Forbidden:
                                pass
                            except discord.NotFound:
                                pass
                            except TimeoutError:
                                await ctx.send("Oops! I fell asleep... sorry.")
                    if dmessage is None:
                        await ctx.send("Sorry, I couldn't find that message anywhere")

    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if self.bot.user in message.mentions and ("👈" in message.content or "👉" in message.content or 'poke' in message.content):
            muted = discord.utils.get(message.guild.roles, id=Configuration.getConfigVar(message.guild.id, "MUTE_ROLE"))
            if muted is not None:
                await message.author.add_roles(muted)
                await message.channel.send(f"{message.author.mention} I do **NOT** appreciate being poked.")
                await asyncio.sleep(2)
                await message.channel.send(f"Please don't do that again!")
                await asyncio.sleep(13)
                await message.author.remove_roles(muted)
                await asyncio.sleep(5*60)
                await message.channel.send(f"__pokes :point_right:{message.author.mention}:point_left:__")


    def __init__(self, bot):
        self.bot:commands.Bot = bot
        conn: SQLDB = self.bot.DBC
        config = bot.config
        #loading hugs
        conn.query("SELECT * FROM hugs")
        hugs = conn.fetch_rows()
        FunCog.hugs = []
        for hug in hugs:
            FunCog.hugs.append(hug["hug"])
        if len(FunCog.hugs) == 0:
            hugs = Util.fetchFromDisk("fun-info")["hugs"]
            for hug in hugs:
                FunCog.hugs.append(hug)
                conn.query('INSERT INTO hugs (hug, author) VALUES ("%s", "%d")' % (hug, 114407765400748041))


        #loading fights
        conn.query("SELECT * FROM fights")
        fights = conn.fetch_rows()
        FunCog.fights = []
        for fight in fights:
            FunCog.fights.append(fight["fight"])
        if len(FunCog.fights) == 0:
            fights = Util.fetchFromDisk("fun-info")["fights"]
            for fight in fights:
                FunCog.fights.append(fight)
                conn.query('INSERT INTO fights (fight, author) VALUES ("%s", "%d")' % (fight, 114407765400748041))




def setup(bot):
    bot.add_cog(FunCog(bot))
