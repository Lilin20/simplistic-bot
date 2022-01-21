import discord
import sys
from discord.ext import commands
import os
import platform


def getpath():
    config_path = None
    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\scripts\\"
    if platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    return config_path

sys.path.insert(1, getpath())
import database as db


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Moderation module loaded.")

    @commands.command(help="Kickt den gewählten User vom Server.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        await user.kick(reason=reason)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='User gekickt', value=f'{user}', inline=True)
        embedVar.add_field(name='Gekickt von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für den Kick', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Bannt den gewähöten Uer vom Server.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        await user.ban(reason=reason)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='User gebannt', value=f'{user}', inline=True)
        embedVar.add_field(name='Gebannt von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für den Bann', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Zeigt dir deine aktuellen Verwarnungen an.")
    async def warns(self, ctx):
        user_id = ctx.message.author.id
        db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user_id}')
        result = db.database.fetchall()
        user_table_id = result[0][0]
        db.database.execute(f'SELECT * FROM warns WHERE user_id = {user_table_id}')
        warns = db.database.fetchall()
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'Hier ist eine Liste von deinen aktuellen Verwarnungen.', color=0xFE9A2E)
        for warn in warns:
            embedVar.add_field(name='Verwarnung', value=f'{warn[1]}', inline=False)
            embedVar.add_field(name='ID', value=f'{warn[0]}')
            embedVar.add_field(name='Zeitstempel', value=f'{warn[3]}')
            embedVar.add_field(name='\u200b', value='\u200b', inline=False)

        await ctx.send(embed=embedVar)

    @commands.command(help="Entfernt eine Verwarnung vom gewählten User.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def warn_remove(self, ctx, user: discord.Member = None, warn_id = None):
        if user is None:
            await ctx.send('Bitte gib einen Nutzer an.')
            return
        if warn_id is None:
            await ctx.send('Bitte gib eine Warn-ID an.')
            return
        db.database.execute(f'UPDATE userdata SET warns = warns - 1 WHERE d_id = {user.id}')
        db.database.execute(f'DELETE FROM warns WHERE warn_id = {warn_id}')
        await ctx.send(f'Verwarnung mit der ID {warn_id} wurde entfernt.')

    @commands.command(help="Verwarnt einen gewählten User.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def warn(self, ctx, user: discord.Member, *, reason=None):
        user_id = user.id
        db.database.execute(f'UPDATE userdata SET warns = warns + 1 WHERE d_id = {user_id}')
        db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user_id}')
        result = db.database.fetchall()
        user_table_id = result[0][0]

        '''Add a new entry to the table names warns and add the reason in the coloumn warn_info'''
        db.database.execute(f'INSERT INTO warns (user_id, warn_info) VALUES ({user_table_id}, "{reason}")')


        if result[0][4] >= 3:
            #await user.ban(reason="User gebannt aufgrund zuvieler Verwarnungen.")
            embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0xFF0000)
            embedVar.add_field(name='User gebannt', value=f'{user}', inline=True)
            embedVar.add_field(name='Gebannt von',
                               value=f'Simplistic - Auto Bann', inline=True)
            embedVar.add_field(name='Grund für den Bann', value=f'User gebannt aufgrund zuvieler Verwarnungen.', inline=False)
            await ctx.send(embed=embedVar)
            return
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0xFE9A2E)
        embedVar.add_field(name='User wurde verwarnt!', value=f'{user}', inline=True)
        embedVar.add_field(name='Verwarnt von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für die Verwarnung', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Entbannt den gewählten User.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def unban(self, ctx, user: discord.Member, *, reason=None):
        await ctx.guild.unban(user)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='User entbannt', value=f'{user}', inline=True)
        embedVar.add_field(name='Entbannt von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für den Entbann', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Entfernt x Anzahl von Nachrichten.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='Nachrichten gelöscht', value=f'{amount}', inline=True)
        embedVar.add_field(name='Gelöscht von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        await ctx.send(embed=embedVar)
    
    @commands.command(help="Gibt einen User die Rolle 'Muted'.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await user.add_roles(role)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='User gemutet', value=f'{user}', inline=True)
        embedVar.add_field(name='Gemutet von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für den Mute', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Entfernt einem User die Rolle 'Muted'")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def unmute(self, ctx, user: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await user.remove_roles(role)
        embedVar = discord.Embed(title="Simplistic - Moderation", description=f'\u200b', color=0x00EE00)
        embedVar.add_field(name='User entmutet', value=f'{user}', inline=True)
        embedVar.add_field(name='Entmutet von', value=f'{ctx.message.author.name}#{ctx.message.author.discriminator}', inline=True)
        embedVar.add_field(name='Grund für den Entmute', value=f'{reason}', inline=False)
        await ctx.send(embed=embedVar)

    @commands.command(help="Sendet dem User eine Hilfeseite.")
    @commands.has_permissions(add_reactions=True, embed_links=True)
    async def help(self, ctx, *cog):
        """Gets all cogs and commands of mine."""
        try:
            if not cog:
                halp = discord.Embed(title='Auflistung von Modulen und sonstigen Befehlen',
                                     description='Um genauere Hilfe zu erhalten: .help <MODUL>')
                cogs_desc = ''
                for x in self.bot.cogs:
                    cogs_desc += ('{} - {}'.format(x, self.bot.cogs[x].__doc__) + '\n')
                halp.add_field(name='Module', value=cogs_desc[0:len(cogs_desc) - 1], inline=False)
                cmds_desc = ''
                for y in self.bot.walk_commands():
                    if not y.cog_name and not y.hidden:
                        cmds_desc += ('{} - {}'.format(y.name, y.help) + '\n')
                halp.add_field(name='Sonstige Befehle', value=cmds_desc[0:len(cmds_desc) - 1], inline=False)
                await ctx.message.add_reaction(emoji='✉')
                await ctx.message.author.send('', embed=halp)
            else:
                if len(cog) > 1:
                    halp = discord.Embed(title='Error!', description='Das sind zu viele Angaben!',
                                         color=discord.Color.red())
                    await ctx.message.author.send('', embed=halp)
                else:
                    found = False
                    for x in self.bot.cogs:
                        for y in cog:
                            if x == y:
                                halp = discord.Embed(title=cog[0] + '- Befehls auflistung',
                                                     description=self.bot.cogs[cog[0]].__doc__)
                                for c in self.bot.get_cog(y).get_commands():
                                    if not c.hidden:
                                        halp.add_field(name=c.name, value=c.help, inline=False)
                                found = True
                    if not found:
                        halp = discord.Embed(title='Error!', description='Unbekanntes Modul. Vielleich falsch geschrieben? "' + cog[0] + '"?',
                                             color=discord.Color.red())
                    else:
                        await ctx.message.add_reaction(emoji='✉')
                    await ctx.message.author.send('', embed=halp)
        except:
            pass

def setup(bot):
    bot.add_cog(Moderation(bot))
