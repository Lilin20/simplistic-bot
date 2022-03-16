import discord
import sys
from discord.ext import commands, tasks
import os
import platform
import random
import asyncio


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


class Casino(commands.Cog):
    """Modul für die Casinofunktionen"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Casino module loaded.")


    @commands.command(help="Lässt dich Roulette spielen mit maximal 4 Feldern.")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def roulette(self, ctx, bet: int, *args):
        db.database.execute(f'SELECT * FROM userdata WHERE d_id = {ctx.message.author.id}')
        result = db.database.fetchall()
        current_money = result[0][7]
        if current_money < bet:
            await ctx.send("Du hast nicht genug Geld um ein Spiel 'Roulette' zu spielen.")
            return
        if current_money < len(args) * bet:
            await ctx.send("Du hast nicht genug Geld um ein Spiel 'Roulette' zu spielen.")
            return
        if bet <=0:
            await ctx.send("Zu wenig oder gar kein Einsatz eingegeben.")
            return
        if bet >150:
            await ctx.send("Der maximale Einsatz beträgt 150.")
            return
        if len(args) <= 0:
            await ctx.send("Bitte wähle die Felder aus auf denen du Chips platzieren willst (4 Felder max.)")
            return
        if len(args) >= 5:
            await ctx.send("Bitte lege deine Chips nur auf 4 Felder.")
            return

        red = [2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36]
        black = [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35]
        landed_ball = random.randint(0, 36)
        betted_fields = args
        winnings = 0
        for field in betted_fields:
            db.database.execute(f'UPDATE userdata SET money = money - {bet} WHERE d_id = {ctx.message.author.id}')
        for field in betted_fields:
            if int(field) == landed_ball:
                winnings += (bet * 35)
        if winnings == 0:
            embed = eb.build_embed("Simplistic - Gamble", "Roulette",  [["Verlorener Betrag", f"{bet * len(betted_fields)}", False]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)

        elif winnings > 0:
            embed = eb.build_embed("Simplistic - Gamble", "Roulette",  [["Gewonnener Betrag", f"{winnings}", False]], 0x00FF00, None, None, None)
            await ctx.send(embed=embed)

        db.database.execute(f'UPDATE userdata SET money = money + {winnings} WHERE d_id = {ctx.message.author.id}')

    @roulette.error
    async def roulette_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cd = round(error.retry_after)
            minutes = str(cd // 60)
            seconds = str(cd % 60)

            embed = eb.build_embed("Cooldown", " ", [["Achting", f"Wir wissen das deine Spielsucht dich dazu treibt mehr Geld zu verdienen.\nMach mal eine Pause:\n \n {self.leadingZero(minutes)}:{self.leadingZero(seconds)}.", True]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)

    @commands.command(help="Startet eine Runde 'Higher or Lower'")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hol(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Zu wenig oder gar kein Einsatz eingegeben.")
            return
        if amount > 250:
            await ctx.send("Du hast das maximale Einsatzlimit überschritten. 1 - 250")
            return
        db.database.execute(f'SELECT * FROM userdata WHERE d_id = {ctx.message.author.id}')
        result = db.database.fetchall()
        current_money = result[0][7]
        if current_money < amount:
            await ctx.send("Du hast nicht genug Geld um ein Spiel 'Higher or Lower' zu spielen.")
            return

        bot_number = random.randint(1, 50)
        player_number = random.randint(1, 50)
        while bot_number == player_number:
            bot_number = random.randint(2, 49)
        await ctx.send(f'{ctx.message.author.mention} du hast die Nummer {player_number} bekommen. Higher or Lower?')
        while True:
            try:
                msg = await self.bot.wait_for('message', timeout=30.0)
            except asyncio.TimeoutError:
                await ctx.send('Du hast das Spiel nicht beendet.')
                return

            if msg.author.id == ctx.message.author.id:
                if msg.content == "higher" or msg.content == "Higher":
                    if bot_number > player_number:
                        embedVar = discord.Embed(title="Simplistic - Gamble", description=f"Higher or Lower", color=0x00ff00)
                        embedVar.add_field(name="User", value=ctx.message.author.mention)
                        embedVar.add_field(name="Zahl vom Bot", value=bot_number, inline=False)
                        embedVar.add_field(name="Gewonnener Betrag", value=amount, inline=False)
                        await ctx.send(embed=embedVar)
                        db.database.execute(f"UPDATE userdata SET money = money + {amount} WHERE d_id = {ctx.message.author.id}")
                        return
                    else:
                        embedVar = discord.Embed(title="Simplistic - Gamble", description=f"Higher or Lower", color=discord.Colour.red())
                        embedVar.add_field(name="User", value=ctx.message.author.mention)
                        embedVar.add_field(name="Zahl vom Bot", value=bot_number, inline=False)
                        embedVar.add_field(name="Verlorener Betrag", value=amount, inline=False)
                        await ctx.send(embed=embedVar)
                        db.database.execute(f"UPDATE userdata SET money = money - {amount} WHERE d_id = {ctx.message.author.id}")
                        return

                if msg.content == "lower" or msg.content == "Lower":
                    if bot_number < player_number:
                        embedVar = discord.Embed(title="Simplistic - Gamble", description=f"Higher or Lower", color=0x00ff00)
                        embedVar.add_field(name="User", value=ctx.message.author.mention)
                        embedVar.add_field(name="Zahl vom Bot", value=bot_number, inline=False)
                        embedVar.add_field(name="Gewonnener Betrag", value=amount, inline=False)
                        await ctx.send(embed=embedVar)
                        db.database.execute(f"UPDATE userdata SET money = money + {amount} WHERE d_id = {ctx.message.author.id}")
                        return
                    else:
                        embedVar = discord.Embed(title="Simplistic - Gamble", description=f"Higher or Lower", color=discord.Colour.red())
                        embedVar.add_field(name="User", value=ctx.message.author.mention)
                        embedVar.add_field(name="Zahl vom Bot", value=bot_number, inline=False)
                        embedVar.add_field(name="Verlorener Betrag", value=amount, inline=False)
                        await ctx.send(embed=embedVar)
                        db.database.execute(f"UPDATE userdata SET money = money - {amount} WHERE d_id = {ctx.message.author.id}")
                        return

    @hol.error
    async def hol_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cd = round(error.retry_after)
            minutes = str(cd // 60)
            seconds = str(cd % 60)

            embed = eb.build_embed("Cooldown", " ", [["Achting", f"Wir wissen das deine Spielsucht dich dazu treibt mehr Geld zu verdienen.\nMach mal eine Pause:\n \n {self.leadingZero(minutes)}:{self.leadingZero(seconds)}.", True]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)

    def leadingZero(self, time: str):
        if len(time) > 1:
            return time

        return "0" + time


def setup(bot):
    bot.add_cog(Casino(bot))