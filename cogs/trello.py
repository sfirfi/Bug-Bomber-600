import asyncio
import datetime
import traceback
from concurrent.futures import CancelledError

import discord
import time
import math
from discord.ext import commands
from utils import permissions, BugLog
from utils import Util
from utils import Configuration

class TrelloCog: 
    """This cog includes the ability to allow Bug Hunters to submit to Trello."""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            if ctx.guild.id == self.bot.config["Settings"]["trelloGuild"]:
                return await permissions.hasPermission(ctx, "trello")
            else:
                return False
        else:
            return False

    @commands.command()
    @commands.guild_only()
    async def submit(self, ctx, *, submit = ""):
        channel= ctx.bot.get_channel(456331168246398976)
        
        if(submit != ""):
            try:
                await channel.send(submit)
            except:
                await ctx.send("I wasn't able to send a message in the trello channel. Maybe check the permissions.")
        else: 
            await ctx.send("There's nothing there, and I can't just add to Trello.")
            
def setup(bot):
    bot.add_cog(TrelloCog(bot))
