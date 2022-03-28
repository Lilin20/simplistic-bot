import discord
import sys
from discord.ext import commands
import os


def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')


sys.path.insert(1, getpath())
import database as db

#Discord.py method that builds an embed with multiple fields
def build_embed(title, description, fields, color, footer, thumbnail, author):
    embed = discord.Embed(title=title, description=description, color=color)
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])
    if footer != None:
        embed.set_footer(text=footer)
    if thumbnail != None:
        embed.set_thumbnail(url=thumbnail)
    if author != None:
        embed.set_author(name=author[0], url=author[1], icon_url=author[2])
    return embed
    