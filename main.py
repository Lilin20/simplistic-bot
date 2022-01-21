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

@bot.command(help="Zeigt Informationen zum Bot aus.")
async def about(ctx):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send(file=discord.File('logo_long.png'))

        dev_list = [await bot.fetch_user("232109327626797056"), await bot.fetch_user("305035025202806787"), await bot.fetch_user("427073776811769857"), await bot.fetch_user("630399208108851217")]
        embedVar = discord.Embed(title="Marvin G.", description="iLLness LiLin#6101", color=discord.Colour.random())
        embedVar.add_field(name="Über Marvin", value="Marvin war für die programmierung des Bots zuständig. Durch Ihn konnten wir das Drohnenskript von Python 2.7 auf Python 3.9 umschreiben.")
        embedVar.set_thumbnail(url=dev_list[0].avatar_url)
        await ctx.send(embed=embedVar)

        embedVar = discord.Embed(title="Mirco L.", description="Mirco#1028", color=discord.Colour.random())
        embedVar.add_field(name="Über Mirco", value="Mirco war für den Bot zuständig. Er programmierte das Profilmodul sowie das Schulmodul. Dank Ihm konnten wir eine neue Datenbanklösung verwenden.")
        embedVar.set_thumbnail(url=dev_list[1].avatar_url)
        await ctx.send(embed=embedVar)

        embedVar = discord.Embed(title="Kevin D.", description="K3vin#7507", color=discord.Colour.random())
        embedVar.add_field(name="Über Kevin", value="Kevin war, im großen und ganzen, für die Backend-Programmierung der App zuständig. Er hat die App, so wie sie heute aussieht, designed und hat die Verbindung mit Datenbanken eingebaut.")
        embedVar.set_thumbnail(url=dev_list[2].avatar_url)
        await ctx.send(embed=embedVar)

        embedVar = discord.Embed(title="Justin S.", description="jstn#7940", color=discord.Colour.random())
        embedVar.add_field(name="Über Justin", value="Justin war für den Kartei-/Informationsbereich der App verantwortlich. Außerdem hat er die Sqlite3 Datenbank aufgesetzt und die Projektdokumentation sowie Präsentation verwaltet.")
        embedVar.set_thumbnail(url=dev_list[3].avatar_url)
        await ctx.send(embed=embedVar)

        embedVar = discord.Embed(title='Simplistic - Allround Discord-Bot', description="Not just a normal school bot.")
        embedVar.add_field(name="Version", value=f'0.23.11 Out of testing!', inline=False)
        embedVar.add_field(name="Über Simplistic", value="Nach langer Überlegung sind wir zu dem Entschluss gekommen diesen Bot zu erstellen. Der Bot entstand im laufe der Projekttage der ITA-Oberstufe. Wir legen hohen Wert auf wiederverwendbarkeit. Deswegen fiel die entscheidung einen Schulbot mit normalen Botfeatures zu erstellen. Doch das war uns zu wenig. Neben den Bot arbeitet ein anderes Team an einer App die es jemanden ermöglicht z.B. Hausaufgaben und Klassenarbeiten zu sichten. Diese App ist aber noch stark in bearbeitung.", inline=False)
        await ctx.send(embed=embedVar)

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
