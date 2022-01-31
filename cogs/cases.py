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


class Cases(commands.Cog):
    """Modul für die Economyfunktionen"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cases module loaded.")

    @commands.command()
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def inventory(self, ctx):
        user = ctx.message.author
        db.database.execute(f"SELECT inventory_slot_one, inventory_slot_two, inventory_slot_three FROM userdata WHERE d_id = {user.id}")
        result = db.database.fetchall()
        print(result)
        embedVar = discord.Embed(title='Inventory', description=f'Inventory von {user.mention}', color=discord.Colour.blue())
        embedVar.add_field(name='Slot 1', value=f'{result[0][0]}')
        embedVar.add_field(name='Slot 2', value=f'{result[0][1]}')
        embedVar.add_field(name='Slot 3', value=f'{result[0][2]}')
        await ctx.send(embed=embedVar)


   

def setup(bot):
    bot.add_cog(Cases(bot))