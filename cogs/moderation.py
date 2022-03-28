import discord
import sys
from discord.ext import commands
import os

def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb


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
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User gekickt", f'{user}', True],
                            ["Gekickt von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für den Kick", f'{reason}', False]],
                            0x00EE00, None, None, None)

        await ctx.send(embed=embed)

    @commands.command(help="Bannt den gewähöten Uer vom Server.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        await user.ban(reason=reason)
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User gebannt", f'{user}', True],
                            ["Gebannt von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für den Bann", f'{reason}', False]],
                            0x00EE00, None, None, None)
        await ctx.send(embed=embed)

    @commands.command(help="Zeigt dir deine aktuellen Verwarnungen an.")
    async def warns(self, ctx):
        user_id = ctx.message.author.id
        db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user_id}')
        result = db.database.fetchall()
        user_table_id = result[0][0]
        db.database.execute(f'SELECT * FROM warns WHERE user_id = {user_table_id}')
        warns = db.database.fetchall()
        embed = eb.build_embed(f"Simplistic - Moderation", f"Hier ist eine Liste von deinen aktuellen Verwarnungen.", 
                            [],
                            0xFE9A2E, None, None, None)
        for warn in warns:
            embed.add_field(name='Verwarnung', value=f'{warn[1]}', inline=False)
            embed.add_field(name='ID', value=f'{warn[0]}')
            embed.add_field(name='Zeitstempel', value=f'{warn[3]}')
            embed.add_field(name='\u200b', value='\u200b', inline=False)
            

        await ctx.send(embed=embed)

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
            await user.ban(reason="User gebannt aufgrund zuvieler Verwarnungen.")
            embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User gebannt", f'{user}', True],
                            ["Gebannt von", f'Simplistic - Auto Bann', True],
                            ["Grund für den Bann", f'User gebannt aufgrund zuvieler Verwarnungen', False]],
                            0xFF0000, None, None, None)
            await ctx.send(embed=embed)
            return
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User wurde verwarnt!", f'{user}', True],
                            ["Verwarnt von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für die Verwarnung", f'{reason}', False]],
                            0xFE9A2E, None, None, None)
        await ctx.send(embed=embed)

    @commands.command(help="Entbannt den gewählten User.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def unban(self, ctx, user: discord.Member, *, reason=None):
        await ctx.guild.unban(user)
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User entbannt", f'{user}', True],
                            ["Entbannt von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für die Entbannung", f'{reason}', False]],
                            0xFE9A2E, None, None, None)
        await ctx.send(embed=embed)

    @commands.command(help="Entfernt x Anzahl von Nachrichten.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["Nachrichten gelöscht", f'{amount}', True],
                            ["Gelöscht von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True]],
                            0x00EE00, None, None, None)
        await ctx.send(embed=embed, delete_after=5)
    
    @commands.command(help="Gibt einen User die Rolle 'Muted'.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def mute(self, ctx, user: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await user.add_roles(role)
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User gemutet", f'{user}', True],
                            ["Gemutet von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für den Mute", f'{reason}', False]],
                            0x00EE00, None, None, None)
        await ctx.send(embed=embed)

    @commands.command(help="Entfernt einem User die Rolle 'Muted'")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def unmute(self, ctx, user: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await user.remove_roles(role)
        embed = eb.build_embed(f"Simplistic - Moderation", f"\u200b", 
                            [["User entmutet", f'{user}', True],
                            ["Entmutet von", f'{ctx.message.author.name}#{ctx.message.author.discriminator}', True],
                            ["Grund für den Entmute", f'{reason}', False]],
                            0x00EE00, None, None, None)
        await ctx.send(embed=embed)

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
