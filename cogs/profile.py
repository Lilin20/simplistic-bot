import discord
import sys
from discord.ext import commands
import os
import platform

def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb


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
                db.database.execute(f'UPDATE userdata SET growth = growth + 0.025 WHERE d_id = {message.author.id}')
                db.database.execute(f'UPDATE userdata SET money = money + 50 WHERE d_id = {message.author.id}')
                embed = eb.build_embed("Level Up!", f'{message.author.name} hat ein neues Level erreicht!', [["Level", f"{fetched_level + 1}", True]], 0x0000CD, None, "https://i.redd.it/5ej93xbz1jo51.gif", [message.author.name, " ", message.author.avatar_url])
                await message.channel.send(embed=embed, delete_after=5)

    @commands.command(help="Zeigt dein Profil oder as Profil von einem anderen User an.")
    async def profile(self, ctx, *args:discord.Member):
        if len(args) > 0:
            for i in args:
                db.database.execute(f'SELECT * FROM userdata WHERE d_id = {i.id}')
                result = db.database.fetchall()

                role_mention = []
                for role in i.roles:
                    if role.name != "@everyone":
                        role_mention.append(role.mention)
                role_string = ", ".join(role_mention)

                embed=eb.build_embed(f"{i.display_name}", f"{result[0][10]}", 
                    [["💬 Messages", result[0][5], True], 
                    ["⚡ Level", result[0][3], True],
                    ["💴 Money", result[0][7], True], 
                    ["ID", result[0][2], True],
                    ["So oft wurde dir Geld geklaut", result[0][11], False],
                    ["Entwichene Raubversuche", result[0][12], True],
                    ["Gearbeitete Stunden", result[0][13], True],
                    ["Roles", role_string, False],
                    ["\u200b", "\u200b", False]],
                    0x00ff00, f"📅 Beitritt am: {result[0][6]}", i.avatar_url, None)

        else:
            db.database.execute(f'SELECT * FROM userdata WHERE d_id = {ctx.author.id}')
            result = db.database.fetchall()
            try:
              fetched_xp, fetched_growth, fetched_level = result[0][8], result[0][9], result[0][3]
            except IndexError:
              print(result)
            calculate_xp = 50 * (1+fetched_growth) ** int(fetched_level)
            calculated_percentage = int(((fetched_xp - 0) * 100) / (int(calculate_xp) - 0))
            calculated_blues = calculated_percentage // 10
            xp_bar = ""

            for blues in range(calculated_blues):
                xp_bar += "🟦"
            
            for whites in range(10-calculated_blues):
                xp_bar += "⬜"

            user = ctx.author
            user_id = ctx.author.id
            db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user_id}')
            result = db.database.fetchall()

            role_mention = []
            for role in user.roles:
                if role.name != "@everyone":
                    role_mention.append(role.mention)
            role_string = ", ".join(role_mention)

            embed=eb.build_embed(f"{ctx.author.display_name}", f"{result[0][10]}", 
                [["💬 Messages", result[0][5], True], 
                ["⚡ Level", result[0][3], True],
                ["Progress", xp_bar, True], 
                ["💴 Money", result[0][7], False], 
                ["ID", result[0][2], True],
                ["So oft wurde dir Geld geklaut", result[0][11], False],
                ["Entwichene Raubversuche", result[0][12], True],
                ["Gearbeitete Stunden", result[0][13], True],
                ["Roles", role_string, False],
                ["\u200b", "\u200b", False]],
                0x00ff00, f"📅 Beitritt am: {result[0][6]}", ctx.author.avatar_url, None)

        await ctx.send(embed=embed)

    @commands.command(help="Setzt einen beliebigen Status für dein Profil.")
    async def set_status(self, ctx, *args):
        string = ""
        user_id = ctx.author.id
        if len(args) > 0:
            for word in args:
                string += word+" "
        db.database.cursor.execute(f'UPDATE userdata SET description = %s WHERE d_id = %s', (string, user_id))


def setup(bot):
    bot.add_cog(Profile(bot))
