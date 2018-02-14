# This cog in includes the mod utils so ban,kick,mute,warn etc
from discord.ext import commands
from utils import permissions


class ModerationCog:
    def __init__(self, bot):
        self.bot = bot

    # The kick command isn't finished yet, it currently is a way to test
    # the Permissions system
    @commands.command(name='kick')
    async def kick(self, ctx):
        if permissions.hasPermission(ctx.author.roles, 'moderation.kick'):
            await ctx.send('valid')
        else:
            await ctx.send('invalid')


def setup(bot):
    bot.add_cog(ModerationCog(bot))
