from discord.ext import commands
from utils import permissions
import os

class MaintenanceCog:
    """Cog for all things related to bot operation"""
    def __init__(self, bot):
        self.bot = bot


    async def __local_check(self, ctx:commands.Context):
        if type(ctx.message.channel) is discord.channel.TextChannel:
            return await permissions.hasPermission(ctx, "fun")
        else:
            return ctx.bot.config.getboolean('Settings','allow_dm_commands')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        cogs = []
        cog = cog.lower()
        for c in ctx.bot.cogs:
            cogs.append(c.replace('Cog', '').lower())

        if cog in cogs:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f'**{cog}** has been reloaded')
        else:
            await ctx.send(f"I can't find that cog.")

    @commands.command(hidden=True)
    async def miniupdate(self, ctx,):
        pass

    @commands.command(hidden=True)
    async def load(self, ctx, cog: str):
        if os.path.isfile(f"cogs/{cog}.py"):
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f"**{cog}** has been loaded!")
        else:
            await ctx.send(f"I can't find that cog.")

    @commands.command(hidden=True)
    async def unload(self, ctx, cog:str):
        cogs = []
        cog = cog.lower()
        for c in ctx.bot.cogs:
            cogs.append(c.replace('Cog', '').lower())

        if cog in cogs:
            self.bot.unload_extension(f"cogs.{cog}")
            await ctx.send(f'**{cog}** has been unloaded')
        else:
            await ctx.send(f"I can't find that cog.")





def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
