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
        print("Cases module loaded.")

    '''@commands.Cog.listener()
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def on_message(self, message):
        # Die Chance das ein User eine Case bekommt beträgt 5% pro Nachricht
        if random.randint(1, 100) <= 10:
            db.database.execute(f"UPDATE userdata SET cases = cases + 1 WHERE d_id = {message.author.id}")
            #Embed that shows the user that he got a case
            embed = discord.Embed(title="Simplistic - Cases", description="Du hast eine Case erhalten!", color=0x00ff00)
            embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            embed.set_footer(text="Schlüssel können im Keyshop erworben werden.")
            await message.channel.send(embed=embed)'''

    @commands.command()
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def givecase(self, ctx, user:discord.Member, amount:int):
        user_id = user.id
        db.database.execute(f"UPDATE userdata SET cases = cases + {amount} WHERE d_id = {user_id}")
        await ctx.send("Kisten wurden erfolgreich gesendet.")

    @commands.command()
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def inventory(self, ctx):
        user = ctx.message.author
        db.database.execute(f"SELECT inventory_slot_one, inventory_slot_two, inventory_slot_three FROM userdata WHERE d_id = {user.id}")
        result = db.database.fetchall()
        await ctx.send(embed=eb.build_embed("Inventory", f"Inventory von {user.mention}", [["Slot 1", result[0][0], True], ["Slot 2", result[0][1], True], ["Slot 3", result[0][2], True]], 0x00ff00, None, None))

        


   

def setup(bot):
    bot.add_cog(Cases(bot))