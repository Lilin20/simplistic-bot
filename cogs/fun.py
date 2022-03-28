import discord
import sys
from discord.ext import commands
import os
import redditeasy
import datetime
import asyncio

def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb


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
        embed = eb.build_embed(f"Simplistic - Suggestion", f"Vorschlag von {ctx.message.author.mention}",
                            [["Vorschlag", suggestion, True]],
                            0xFF0000, None, None, None)

        message = await ctx.send(embed=embed)

        for emote in emotes:
            await message.add_reaction(emote)

    @commands.command(help="Gibt ein zufälligs Meme von Reddit aus.")
    async def meme(self, ctx):
        post = redditeasy.Subreddit(client_id="INSERT CLIENT ID", client_secret="INSERT CLIENT SECRET", user_agent="Anime Module / TBS Bot")
        output = post.get_post(subreddit="dankmemes")
        formatted_time = datetime.datetime.fromtimestamp(output.created_at).strftime("%d/%m/%Y %I:%M:%S CEST")
    
        embed=eb.build_embed(f"{output.title}", f"Redditor: {output.author}", 
                            [["Upvotes", f"{output.score}", True],
                            ["Erstellt am", f"{formatted_time}", True]],
                            0xFF0000, None, None, None)
        embed.set_image(url=output.content)

        await ctx.send(embed=embed)

    @commands.command(help="Zeigt dir die höchsten User im Bereich Level oder Geld an.")
    async def top(self, ctx, option):
        if option == "level":
            db.database.execute(f'SELECT * FROM userdata ORDER BY lvl DESC LIMIT 5')
            result = db.database.fetchall()
            embedVar = discord.Embed(title="Leaderboard (Top 5)", description='Absteigend nach Level', color=0x0000CD)
            embed = eb.build_embed(f"Leaderboard (Top 5)", f"Absteigend nach Level", 
                            [],
                            0x0000CD, None, None, None)
            for i in range(len(result)):
                user = await self.bot.fetch_user(result[i][2])
                username = user.name
                embed.add_field(name=f"{i + 1}. {username}", value=f'Level: {result[i][3]}', inline=False)
                

            await ctx.send(embed=embed)

        elif option == "money":
            db.database.execute(f'SELECT * FROM userdata ORDER BY money DESC LIMIT 5')
            result = db.database.fetchall()
            embed = eb.build_embed(f"Leaderboard (Top 5)", f"Absteigend nach Vermögen", 
                            [],
                            0x0000CD, None, None, None)
            for i in range(len(result)):
                user = await self.bot.fetch_user(result[i][2])
                username = user.name
                embed.add_field(name=f"{i + 1}. {username}", value=f'Vermögen: {result[i][7]}', inline=False)
            await ctx.send(embed=embed)

        elif option == "messages":
            db.database.execute(f'SELECT * FROM userdata ORDER BY msg DESC LIMIT 5')
            result = db.database.fetchall()
            embed = eb.build_embed(f"Leaderboard (Top 5)", f"Absteigend nach Nachrichten",
                            [],
                            0x0000CD, None, None, None)
            for i in range(len(result)):
                user = await self.bot.fetch_user(result[i][2])
                username = user.name
                embed.add_field(name=f"{i + 1}. {username}", value=f'Nachrichten: {result[i][5]}', inline=False)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Dieses Leaderboard gibt es nicht. Folgende Leaderboards sind verfügbar: money, level")

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
            embed = eb.build_embed(f"Voting Ergebnis", f"Die Mehrheit hat für 'Ja' gestimmt.", 
                            [],
                            0x00EE00, None, None, None)
            await self.vote_channel.send(embed=embed)
            return

        if reaction_array[1] > reaction_array[0]:
            embed = eb.build_embed(f"Voting Ergebnis", f"Die Mehrheit hat für 'Nein' gestimmt.", 
                            [],
                            0xFF0000, None, None, None)
            await self.vote_channel.send(embed=embed)
            return

        if reaction_array[0] == 0 and reaction_array[1] == 0:
            embed = eb.build_embed(f"Voting Ergebnis", f"Es wurden keine Stimmen abgegeben, daher liegt kein Ergebnis vor.", 
                            [],
                            0xFF0000, None, None, None)
            await self.vote_channel.send(embed=embed)
            return

        if reaction_array[0] == reaction_array[1]:        
            embed = eb.build_embed(f"Voting Ergebnis", f"Das Voting ist unentschieden.", 
                            [],
                            0xFFA500, None, None, None)

            await self.vote_channel.send(embed=embed)
            return

    @commands.command(help="Zeigt das Avatar des gewählten Users.")
    async def avatar(self, ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Bitte markiere einen User. - .avatar @USER")
        else:
            embed = eb.build_embed(f"Avatar von {user.name}", "", 
                            [],
                            0x0000CD, None, None, None)
            embed.set_image(url=user.avatar_url)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Fun(bot))
