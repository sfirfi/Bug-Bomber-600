import discord
from discord.ext import commands


class ReminderCog:
    """This cog features the reminder functions"""
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(ReminderCog(bot))
