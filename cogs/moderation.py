from discord.ext import commands
from utils import permissions


class ModerationCog:
    """This cog includes the mod utils so ban, kick, mute, warn, etc"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return permissions.hasPermission(ctx.author.roles, "moderation", ctx.command)

    # The kick command isn't finished yet, it currently is a way to test
    # the Permissions system
    @commands.command(name='kick')
    async def kick(self, ctx):
        await ctx.send('valid')


def setup(bot):
    bot.add_cog(ModerationCog(bot))
