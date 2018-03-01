
# creates a connection to the DB
from discord.ext import commands

# Receives a permissions and the roles of a user
# Checks if any of the roles has the needed Permission
async def hasPermission(ctx, cog):
    conn = ctx.bot.DBC
    for crole in ctx.author.roles:
        conn.query(f"SELECT id, permission FROM permissions where role_id='{crole.id}' AND (permission = '*' OR permission = '{cog}.*' OR permission = '{cog}.{ctx.command}');")
        if len(conn.fetch_rows()) is not 0:
            return True

    return await ctx.bot.is_owner(ctx.author)

#recives a role and a permission and checks if the role has that permission
def roleHasPermission(ctx, role, permission):
    conn = ctx.bot.DBC
    conn.query(f"SELECT id, permission FROM permissions where role_id='{role.id}' AND permission = '{permission}'")
    if len(conn.fetch_rows()) is not 0:
        return True

    return False


def listPermissions(ctx, role):
    conn = ctx.bot.DBC
    perms = ""
    conn.query(f"SELECT permission FROM permissions where role_id='{role.id}' ORDER BY permission;")
    for perm in conn.fetch_rows():
        perms += f"{perm['permission']}\n"
    return perms

def verifyPermission(ctx, permission):
    perms = list()
    perms.append('*')
    bot = ctx.bot
    for cog in bot.cogs:
        perms.append(f"{formatPermission(cog)}.*")

    for command in bot.all_commands:
        perms.append(f"{formatPermission(str(bot.all_commands.get(command).cog_name))}.{command}")

    if permission in perms:
        return True
    else:
        return False

def addPermission(ctx, role, permission):
    conn = ctx.bot.DBC
    if verifyPermission(ctx, permission):
        if(roleHasPermission(ctx, role, permission)):
            return "The role already has that permission"
        else:
            conn.query(f"INSERT INTO permissions (role_id,permission) VALUES ('{role.id}','{permission}')")
            return ":wrench: The permission was succesfully added."
    else:
        return "This Permission doesn't seem to exist."

def rmvPermission(ctx, role, permission):
    conn = ctx.bot.DBC
    if verifyPermission(ctx, permission):
        if(roleHasPermission(ctx, role, permission)):
            conn.query(f"DELETE FROM permissions WHERE role_id='{role.id}' AND permission='{permission}'")
            return ":wrench: The permission was succesfully removed"
        else:
            return "The role doesn't has that permission."
    else:
        return "This Permission doesn't seem to exist"

def formatPermission(permission):
    return permission.replace('Cog', '').replace('Server','').lower()

def owner_only():
    async def predicate(ctx):
        return ctx.bot.is_owner(ctx.author)
    return commands.check(predicate)
