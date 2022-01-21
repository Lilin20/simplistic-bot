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


class Profile(commands.Cog):
    """Modul für die Profilfunktionen"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Profile module loaded.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('.'):
            return
        if message.author == self.bot.user:
            return
        if message.content.startswith("https") or message.content.startswith("http"):
            return
        else:
            xp_to_give = len(message.content) - message.content.count(" ")
            db.database.execute(f'UPDATE userdata SET msg = msg + 1 WHERE d_id = {message.author.id}')
            db.database.execute(f'UPDATE userdata SET xp = xp + {xp_to_give} WHERE d_id = {message.author.id}')
            db.database.execute(f'SELECT * FROM userdata WHERE d_id = {message.author.id}')
            result = db.database.fetchall()
            try:
              fetched_xp, fetched_growth, fetched_level = result[0][8], result[0][9], result[0][3]
            except IndexError:
              print(result)
              print("Unknown Error")
            calculate_xp = 50 * (1+fetched_growth) ** int(fetched_level)
            if fetched_xp >= calculate_xp:
                db.database.execute(f'UPDATE userdata SET lvl = lvl + 1 WHERE d_id = {message.author.id}')
                db.database.execute(f'UPDATE userdata SET xp = 0 WHERE d_id = {message.author.id}')
                db.database.execute(f'UPDATE userdata SET growth = growth + 0.05 WHERE d_id = {message.author.id}')
                db.database.execute(f'UPDATE userdata SET money = money + 50 WHERE d_id = {message.author.id}')
                embedVar = discord.Embed(title="Level Up!", description=f'{message.author.name} hat ein neues Level erreicht!', color=0x0000CD)
                embedVar.set_thumbnail(url="https://i.redd.it/5ej93xbz1jo51.gif")
                embedVar.set_author(name=message.author, url=" ",icon_url=message.author.avatar_url)
                await message.channel.send(embed=embedVar, delete_after=5)

    @commands.command(help="Zeigt dein Profil oder as Profil von einem anderen User an.")
    async def profile(self, ctx, *args:discord.Member):
        if len(args) > 0:
            for i in args:
                db.database.execute(f'SELECT * FROM userdata WHERE d_id = {i.id}')
                result = db.database.fetchall()

                embedVar = discord.Embed(title=i.display_name, description=result[0][10], color=0x0000CD)
                embedVar.set_thumbnail(url=i.avatar_url)
                embedVar.add_field(name="💬 Messages", value=result[0][5], inline=True)
                embedVar.add_field(name="⚡ Level", value=result[0][3], inline=True)
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                embedVar.add_field(name="💴 Money", value=result[0][7], inline=True)
                embedVar.add_field(name="ID", value=result[0][2], inline=True)
                embedVar.add_field(name="So oft wurde dir Geld geklaut", value=result[0][11], inline=False)
                embedVar.add_field(name="Entwichene Raubversuche", value=result[0][12], inline=True)
                embedVar.add_field(name="Gearbeitete Stunden", value=result[0][13], inline=True)
                #embedVar.add_field(name="\u200b", value="\u200b", inline=True)

                role_mention = []
                for role in i.roles:
                    if role.name != "@everyone":
                        role_mention.append(role.mention)
                role_string = ", ".join(role_mention)
                embedVar.add_field(name="Roles", value=role_string, inline=False)

                embedVar.add_field(name="\u200b", value="\u200b")
                embedVar.add_field(name="\u200b", value="\u200b")
                embedVar.set_footer(text=f"📅 Beitritt am: {result[0][6]}")

        else:
            user = ctx.author
            user_id = ctx.author.id
            db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user_id}')
            result = db.database.fetchall()
            embedVar = discord.Embed(title=ctx.author.display_name, description=result[0][10], color=0x0000CD)
            embedVar.set_thumbnail(url=ctx.author.avatar_url)
            embedVar.add_field(name="💬 Messages", value=result[0][5], inline=True)
            embedVar.add_field(name="⚡ Level", value=result[0][3], inline=True)
            embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="💴 Money", value=result[0][7], inline=True)
            embedVar.add_field(name="ID", value=result[0][2], inline=True)
            embedVar.add_field(name="So oft wurde dir Geld geklaut", value=result[0][11], inline=False)
            embedVar.add_field(name="Entwichene Raubversuche", value=result[0][12], inline=True)
            embedVar.add_field(name="Gearbeitete Stunden", value=result[0][13], inline=True)
            #embedVar.add_field(name="\u200b", value="\u200b")

            role_mention = []
            for role in user.roles:
                if role.name != "@everyone":
                    role_mention.append(role.mention)
            role_string = ", ".join(role_mention)
            embedVar.add_field(name="Roles", value=role_string, inline=False)

            embedVar.add_field(name="\u200b", value="\u200b")
            embedVar.add_field(name="\u200b", value="\u200b")
            embedVar.set_footer(text=f"📅 Beitritt am: {result[0][6]}")

        await ctx.send(embed=embedVar)

    @commands.command(help="Setzt einen beliebigen Status für dein Profil.")
    async def set_status(self, ctx, *args):
        string = ""
        user_id = ctx.author.id
        if len(args) > 0:
            for word in args:
                string += word+" "
        db.database.execute(f'UPDATE userdata SET description = "{string}" WHERE d_id = "{user_id}"')


def setup(bot):
    bot.add_cog(Profile(bot))
