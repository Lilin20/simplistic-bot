import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure
import os
import configparser
import platform
import scripts.database as db
import scripts.uuid_gen as uuid_gen

c_parser = configparser.ConfigParser()
c_parser.read(os.path.dirname(os.path.realpath(__file__))+"/config/config.ini")

# Information zum Bot

description = """ -Discord Bot """
version = "0.1"
maintenance = False

# Intents
intents = discord.Intents.default()
intents.members = True

# Object
bot = commands.Bot(command_prefix=".", case_insensitive=True, description=description, intents=intents, help_command=None, activity=discord.Streaming(name="WIP", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"))


# Event - Startup


@bot.event
async def on_ready():
    print("""
   ▄████████   ▄▄▄▄███▄▄▄▄      ▄███████▄  ▄█       
  ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███ ███       
  ███    █▀  ███   ███   ███   ███    ███ ███       
  ███        ███   ███   ███   ███    ███ ███       
▀███████████ ███   ███   ███ ▀█████████▀  ███       
         ███ ███   ███   ███   ███        ███       
   ▄█    ███ ███   ███   ███   ███        ███▌    ▄ 
 ▄████████▀   ▀█   ███   █▀   ▄████▀      █████▄▄██ 
                                          ▀         
    """)

    guild = None
    for guilds in bot.guilds:
        guild = guilds
    print(f"Successfully connected to '{guild}' using {platform.system()} as hosting OS")

    members = await guild.fetch_members(limit=None).flatten()
    print("Checking for new members...")
    for member in members:
        db.database.execute(f'SELECT d_id FROM userdata WHERE d_id = "{member.id}"')
        result = db.database.fetchall()
        joined = member.joined_at.strftime("%d.%m.%Y")
        if not result:
            db.database.execute(f'INSERT INTO userdata (uid, d_id, lvl, warns, msg, join_date, money, xp, growth) VALUES ("{uuid_gen.generator.build()}", {member.id}, 1, 0, 0, "{joined}", 0, 0, 0.25)')

    print("Done.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        embedVar = discord.Embed(title="Befehl unbekannt", description=f'**{ctx.message.content}**', color=0xff1c1c)
        await ctx.send(embed=embedVar)

@bot.command(help="Lädt ein Modul neu.")
@has_permissions(administrator=True)
async def reload(ctx, extension):
    if ctx.message.author.guild_permissions.administrator:
        bot.unload_extension(f'cogs.{extension}')
        bot.load_extension(f'cogs.{extension}')
        await ctx.send(f"Successfully reloaded the '{extension}' module!")

for filename in os.listdir(os.path.dirname(os.path.realpath(__file__))+"/cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_member_join(member):
    db.database.execute(f'SELECT d_id FROM userdata WHERE d_id = "{member.id}"')
    result = db.database.fetchall()
    joined = member.joined_at.strftime("%d.%m.%Y")
    if not result:
        db.database.execute(
            f'INSERT INTO userdata (uid, d_id, lvl, warns, msg, join_date, money, xp, growth) VALUES ("{uuid_gen.generator.build()}", {member.id}, 0, 0, 0, "{joined}", 0, 0, 0.25)')

@bot.event
async def on_member_remove(member):
    db.database.execute(f'DELETE FROM userdata WHERE d_id = "{member.id}"')


bot.run(c_parser.get('Bot', 'token'))
