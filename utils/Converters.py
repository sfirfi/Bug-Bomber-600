from discord.ext import commands


class Event(commands.Converter):
    async def convert(self, ctx, argument):
        return self.realConvert(ctx.bot, argument)

    def realConvert(self, bot, argument):
        dbc = bot.DBC
        if isinstance(argument, str):
            argument = dbc.escape(argument)
        dbc.query(f"SELECT * FROM events where ID='{argument}' OR name = '{argument}'")
        event = dbc.fetch_onerow()
        if event is None:
            raise commands.BadArgument(f"Unable to find event `{argument}`")
        dbc.query(f"SELECT * FROM eventchannels where event={event['ID']}")
        channellist = dbc.fetch_rows()
        channels = dict()
        for c in channellist:
            channels[c["name"]] = c
        event["channels"] = channels
        return event