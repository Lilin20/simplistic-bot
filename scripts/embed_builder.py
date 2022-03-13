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

def build_embed(title: str, description: str, color, field_amount: int, key_listDict: dict):
    embedVar = discord.Embed(title=title, description=description, color=color)
    for field in range(field_amount+1):
        for key in key_listDict:
            if key_listDict[key][2] == True:
                embedVar.add_field(name=key_listDict[key][0], value=key_listDict[key][1], inline=True)
            else:
                embedVar.add_field(name=key_listDict[key][0], value=key_listDict[key][1], inline=False)
    return embedVar
