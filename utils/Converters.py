from discord.ext import commands


class Event(commands.Converter):
    async def convert(self, ctx, argument):
        dbc = ctx.bot.DBC
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
        dbc.query(f"SELECT * FROM submissions where event={event['ID']}")
        event["submittions"] = dict()
        submissions = dbc.fetch_rows()
        event["totalsubmissions"] = 0
        for s in submissions:
            event["totalsubmissions"] = event["totalsubmissions"] + s["count"]
            event["submittions"][s["user"]] = s
        if "closingTime" in event.keys():
            event["closingTime"] = event["endtime"] - event["closingTime"]
        return event

    def convert2(self, bot, argument):
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
        dbc.query(f"SELECT * FROM submissions where event={event['ID']}")
        event["submittions"] = dict()
        submissions = dbc.fetch_rows()
        event["totalsubmissions"] = 0
        for s in submissions:
            event["totalsubmissions"] = event["totalsubmissions"] + 1
        if "closingtime" in event.keys():
            event["closingtime"] = event["endtime"] - event["closingtime"]
        return event