from discord.ext import commands
from utils import permissions


class MaintenanceCog:
    """Cog for all things related to bot operation"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return await permissions.hasPermission(ctx, "maintenance")

    @permissions.owner_only()
    @commands.command()
    async def admincheck(self, ctx):
        await ctx.send('valid')



def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
