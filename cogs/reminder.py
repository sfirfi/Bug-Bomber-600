# This cog features the reminder functions

import discord
from discord.ext import commands


class ReminderCog:
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ReminderCog(bot))
