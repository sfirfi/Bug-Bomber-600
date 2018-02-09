# This cog includes all the features of the modlog

import discord
from discord.ext import commands


class ModlogCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ModlogCog(bot))
