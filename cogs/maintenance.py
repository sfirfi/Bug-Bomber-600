import asyncio
from subprocess import Popen
import subprocess
from utils import Configuration
import configparser
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import traceback

from discord.ext import commands
import discord
import os
import subprocess


class MaintenanceCog:
    """Cog for all things related to bot operation"""
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.sessions = set()

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def eval_enabled(self):
        return self.bot.config.getboolean('Settings','evalCommand')

    async def __local_check(self, ctx:commands.Context):
        if str(ctx.message.author.id) in self.bot.config['Settings']['admins']:
            return True
        else:
            return False

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

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
    
    @commands.command(hidden=True)
    async def restart(self, ctx):
        """Restarts the bot"""
        await ctx.send("Restarting...")
        await self.bot.logout()
        await self.bot.close()


    @commands.command(hidden=True)
    async def pull(self, ctx):
        """Pulls from github so an upgrade can be performed without full restart"""
        async with ctx.typing():
            p = Popen(["git pull"], cwd=os.getcwd(), shell=True, stdout=subprocess.PIPE)
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

    @commands.command(pass_context=True, hidden=True, name='eval')
    @commands.check(eval_enabled)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        if "token" in body:
            await ctx.send("No token stealing allowed.")
            return

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    





def setup(bot):
    bot.add_cog(MaintenanceCog(bot))
