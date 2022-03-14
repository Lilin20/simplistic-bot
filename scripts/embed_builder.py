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

#Discord.py method that builds an embed with multiple fields
def build_embed(title, description, fields, color, footer, thumbnail):
    embed = discord.Embed(title=title, description=description, color=color)
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])
    if footer != None:
        embed.set_footer(text=footer)
    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)
    return embed
    