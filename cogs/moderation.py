# This cog in includes the mod utils so ban,kick,mute,warn etc

import discord
from discord.ext import commands


class ModerationCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ModerationCog(bot))
