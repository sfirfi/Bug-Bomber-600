# This cog includes the server utils so self assignable roles and the server
# unlock

import discord
from discord.ext import commands


class ServerutilsCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ServerutilsCog(bot))
