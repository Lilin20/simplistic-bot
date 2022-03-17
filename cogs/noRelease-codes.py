import discord
import sys
from discord.ext import commands
import os
import platform
import random


def getpath():
    config_path = None
    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\scripts\\"
    if platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    return config_path

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb


class Cases(commands.Cog):
    """Modul für die Economyfunktionen"""
    def __init__(self, bot):
        self.bot = bot
        self.rarities = ["Common", "Uncommon", "Rare", "Super Rare", "Legendary", "Mythical", "Godly"]
        self.chances = [80, 20, 10, 2.5, 1, 0.5, 0.2]

    def get_rarity(self):
        return random.choices(self.rarities, self.chances, k=1)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Special module loaded. Name: noRelease-codes - Remove this when bot gets released. (Only for TBS)")

    @commands.command()
    async def redeem(self, ctx, code):
        db.database.execute(f"SELECT * FROM codes WHERE code = '{code}'")
        result = db.database.fetchall()
        if len(result) == 0:
            await ctx.send("Dieser Code existiert nicht.")
        else:
            if result[0][2] == 0:
                await ctx.send("Dieser Code ist nicht mehr gültig.")
                return
            else:
                db.database.execute(f"UPDATE codes SET uses = uses - 1 WHERE code = '{code}'")
                db.database.execute(f'UPDATE userdata SET money = money + {result[0][3]} WHERE d_id = {ctx.author.id}')
                await ctx.author.send(f"Der Code wurde erfolgreich eingelöst! Du hast {result[0][3]} Coins erhalten.")

def setup(bot):
    bot.add_cog(Cases(bot))