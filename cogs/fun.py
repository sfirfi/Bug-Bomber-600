# This cog includes the fun comments so !hug, fight, cat etc

import discord
from discord.ext import commands


class FunCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(FunCog(bot))
