import discord
import sys
from discord.ext import commands
import os
import platform
import redditeasy
import datetime
import asyncio
from itawiki_api_wrapper import auth, posts
import mal

def getpath():
    config_path = None
    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\scripts\\"
    if platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    return config_path

sys.path.insert(1, getpath())
import database as db


class Fun(commands.Cog, name="Fun", description="Enthält alle Funktionen die zur Unterhaltung dienen."):
    """Modul für die Funfuntionen"""
    def __init__(self, bot):
        self.bot = bot
        self.message = None
        self.vote_channel = None
        self.time = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fun module loaded.")

    @commands.command(help="Erstellt einen Vorschlag mit direktem voting.")
    async def suggestion(self, ctx, *, suggestion):
        emotes = ['👍','👎']
        embedVar = discord.Embed(title='Simplistic - Suggestion', description=f'Vorschlag von {ctx.message.author.mention}', color=discord.Colour.blue())
        embedVar.add_field(name='Vorschlag', value=f'{suggestion}')

        message = await ctx.send(embed=embedVar)

        for emote in emotes:
            await message.add_reaction(emote)


    @commands.command(help="Sucht nach einem Beitrag im ITA-Wiki.")
    async def itasearch(self, ctx, keywords):
        auth.login('marvingrunwald2000@gmail.com', 'ita19b2021')
        result = posts.search(keywords)
        embedVar = discord.Embed(title='ITA-Wiki Search', description=f'Benutzte Keywords: {keywords}')
        embedVar.add_field(name='Titel', value=f'{result["title"]}')
        embedVar.add_field(name='URL', value=f'{result["url"]}')
        await ctx.send(embed=embedVar)

    @commands.command(help="Gibt ein zufälligs Meme von Reddit aus.")
    async def meme(self, ctx):
        post = redditeasy.Subreddit(client_id="tdEFqzh4aZ8Gpw", client_secret="_LbOSNTPnUJq6n7KZpfPUllAme-4JQ", user_agent="Anime Module / TBS Bot")
        output = post.get_post(subreddit="dankmemes")
        formatted_time = datetime.datetime.fromtimestamp(output.created_at).strftime("%d/%m/%Y %I:%M:%S CEST")
        embedVar = discord.Embed(title=output.title, description=f'Redditor: {output.author}', color=0x0000CD)
        embedVar.add_field(name="Upvotes", value=f'{output.score}', inline=True)
        embedVar.add_field(name="Erstellt am", value=f'{formatted_time}', inline=True)
        embedVar.set_image(url=output.content)
        await ctx.send(embed=embedVar)

    @commands.command(help="Gibt einen Beitrag aus einem Subreddit aus.")
    async def reddit(self, ctx, subreddit):
        post = redditeasy.Subreddit(client_id="tdEFqzh4aZ8Gpw", client_secret="_LbOSNTPnUJq6n7KZpfPUllAme-4JQ", user_agent="Anime Module / TBS Bot")
        output = post.get_post(subreddit=subreddit)
        formatted_time = datetime.datetime.fromtimestamp(output.created_at).strftime("%d/%m/%Y %I:%M:%S CEST")
        embedVar = discord.Embed(title=output.title, description=f'Redditor: {output.author}', color=0x0000CD)
        embedVar.add_field(name="Upvotes", value=f'{output.score}', inline=True)
        embedVar.add_field(name="Erstellt am", value=f'{formatted_time}', inline=True)
        embedVar.set_image(url=output.content)
        await ctx.send(embed=embedVar)

    @commands.command(help="Zeigt dir die höchsten User im Bereich Level oder Geld an.")
    async def top(self, ctx, option):
        if option == "level":
            db.database.execute(f'SELECT * FROM userdata ORDER BY lvl DESC LIMIT 5')
            result = db.database.fetchall()
            embedVar = discord.Embed(title="Leaderboard (Top 5)", description='Absteigend nach Level', color=0x0000CD)
            for i in range(len(result)):
                user = await self.bot.fetch_user(result[i][2])
                username = user.name
                embedVar.add_field(name=f"{i + 1}. {username}", value=f'Level: {result[i][3]}', inline=False)
            await ctx.send(embed=embedVar)

        elif option == "money":
            db.database.execute(f'SELECT * FROM userdata ORDER BY money DESC LIMIT 5')
            result = db.database.fetchall()
            embedVar = discord.Embed(title="Leaderboard (Top 5)", description='Absteigend nach Vermögen', color=0x0000CD)
            for i in range(len(result)):
                user = await self.bot.fetch_user(result[i][2])
                username = user.name
                embedVar.add_field(name=f"{i + 1}. {username}", value=f'Vermögen: {result[i][7]}', inline=False)
            await ctx.send(embed=embedVar)

        else:
            await ctx.send("Dieses Leaderboard gibt es nicht. Folgende Leaderboards sind verfügbar: money, level")

    @commands.command(help="Gibt Informationen zu einem Anime aus.")
    async def anime(self, ctx, option, *, keywords=None,):
        if option == 'search':
            result_first = mal.AnimeSearch(keywords, timeout=1)
            result = mal.Anime(result_first.results[0].mal_id, timeout=1)

            genres = ""
            for genre in result.genres:
                genres += genre + ", "

            studios = ""
            for studio in result.studios:
                studios += studio + ", "


            embedVar = discord.Embed(title=f"{result.title_japanese}", description=f'{result.title_english}')
            embedVar.add_field(name='Genres', value=f'{genres[:-2]}', inline=True)
            embedVar.add_field(name='Veröffentlicht', value=f'{result.aired}', inline=True)
            embedVar.add_field(name='Studio', value=f'{studios[:-2]}', inline=True)
            embedVar.add_field(name='Rating', value=f'{result.rating}', inline=True)
            embedVar.add_field(name='Score', value=f'{result.score} / 10', inline=True)
            embedVar.add_field(name='Episoden', value=f'{result.episodes}', inline=True)
            embedVar.add_field(name='URL', value=f'{result.url}', inline=True)
            embedVar.set_thumbnail(url=result.image_url)
            await ctx.send(embed=embedVar)


    @commands.command(help="Erstellt ein zeitlichbegrenztes Voting.")
    @commands.has_permissions(administrator=True)
    async def vote(self, ctx, time: int, *args):
        self.time = time
        emote_array = ['✅', '❎']
        string = ""
        user = ctx.author
        if len(args) > 0:
            for word in args:
                string += word + " "

        embedVar = discord.Embed(title="🗳 Voting", description=f"Erstellt von {user.name}")
        embedVar.add_field(name="\u200b", value=string, inline=False)
        self.message = await ctx.send(embed=embedVar)
        for emote in emote_array:
            await self.message.add_reaction(emote)

        self.vote_channel = ctx.message.channel
        await asyncio.sleep(time)
        await self.vote_result()

    @commands.command(help="Beendet dsa Voting vor dem Zeitlimit.")
    @commands.has_permissions(administrator=True)
    async def vote_result(self):
        cached_message = await self.vote_channel.fetch_message(self.message.id)
        reaction_array = [cached_message.reactions[0].count-1, cached_message.reactions[1].count-1]
        if reaction_array[0] > reaction_array[1]:
            embedVar = discord.Embed(title="Voting Ergebnis", description=f'Die Mehrheit hat für "Ja" gestimmt.',
                                     color=0x00EE00)
            await self.vote_channel.send(embed=embedVar)
            return

        if reaction_array[1] > reaction_array[0]:
            embedVar = discord.Embed(title="Voting Ergebnis", description=f'Die Mehrheit hat für "Nein" gestimmt.',
                                     color=0xFF0000)
            await self.vote_channel.send(embed=embedVar)
            return

        if reaction_array[0] == 0 and reaction_array[1] == 0:
            embedVar = discord.Embed(title="Voting Ergebnis", description=f'Es wurden keine Stimmen abgegeben, daher liegt kein Ergebnis vor.')
            await self.vote_channel.send(embed=embedVar)
            return

        if reaction_array[0] == reaction_array[1]:
            embedVar = discord.Embed(title="Voting Ergebnis", description=f'Das Vorting ist unentschieden.',
                                     color=0xFFA500)
            await self.vote_channel.send(embed=embedVar)
            return

    @commands.command(help="Zeigt das Avatar des gewählten Users.")
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Bitte markiere einen User. - .avatar @USER")
        else:
            embedVar = discord.Embed(title=f"Avatar von {user.name}", color=0x0000CD)
            embedVar.set_image(url=user.avatar_url)
            await ctx.send(embed=embedVar)

def setup(bot):
    bot.add_cog(Fun(bot))