from discord.ext import commands
from utils import permissions


class MaintenanceCog:
    """Cog for all things related to bot operation"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        return await permissions.hasPermission(ctx, "maintenance")

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        self.bot.unload_extension(f"cogs.{cog}")
        self.bot.load_extension(f"cogs.{cog}")
        await ctx.send(f'**{cog}** has been reloaded')

    @commands.command(hidden=True)
    async def miniupdate(self, ctx,):
        pass



def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
