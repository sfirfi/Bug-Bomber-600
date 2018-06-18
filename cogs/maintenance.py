import asyncio
from subprocess import Popen
import subprocess

from discord.ext import commands
import discord
import os
import subprocess


class MaintenanceCog:
    """Cog for all things related to bot operation"""
    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx:commands.Context):
        if str(ctx.message.author.id) in self.bot.config['Settings']['admins']:
            return True
        else:
            return False

    @commands.command(hidden=True)
    async def reload(self, ctx, *, cog: str):
        cogs = []
        cog = cog.lower()
        for c in ctx.bot.cogs:
            cogs.append(c.replace('Cog', '').lower())

        if cog in cogs:
            self.bot.unload_extension(f"cogs.{cog}")
            self.bot.load_extension(f"cogs.{cog}")
            await ctx.send(f'**{cog}** has been reloaded.')
        else:
            await ctx.send(f"I can't find that cog.")

    @commands.command()
    async def pull(self, ctx):
        """Pulls from github so an upgrade can be performed without full restart"""
        async with ctx.typing():
            p = Popen(["git pull origin master"], cwd=os.getcwd(), shell=True, stdout=subprocess.PIPE)
            while p.poll() is None:
                await asyncio.sleep(1)
            out, error = p.communicate()
            await ctx.send(f"Pull completed with exit code {p.returncode}```yaml\n{out.decode('utf-8')}```")

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
            await ctx.send(f'**{cog}** has been unloaded.')
        else:
            await ctx.send(f"I can't find that cog.")





def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
