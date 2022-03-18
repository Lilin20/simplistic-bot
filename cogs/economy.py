import discord
import sys
from discord.ext import commands
import os
import platform
import random

def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb


class Economy(commands.Cog):
    """Modul für die Economyfunktionen"""
    def __init__(self, bot):
        self.bot = bot
        self.message = None
        self.vote_channel = None
        self.time = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Economy module loaded.")

    @commands.command(help="Gibt dir einen Daily-Reward.")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        db.database.execute(f'UPDATE userdata SET money = money + 150 WHERE d_id = {ctx.message.author.id}')
        embed = eb.build_embed("Simplistic - Economy", "Daily Reward abgeholt!",  [["Erhaltenes Geld", 150, True]], 0x00FF00, None, None, None)
        await ctx.send(embed=embed)

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cd = round(error.retry_after)
            minutes = str(cd // 60)
            seconds = str(cd % 60)

            embed = eb.build_embed("Cooldown", " ", [["Achting", f"Du hast bereits deine tägliche Summe an Geld abgeholt.\nBitte warte:\n \n {self.leadingZero(minutes)}:{self.leadingZero(seconds)}.", True]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)

    @commands.command(help="Gibt dir Geld für gearbeitete Stunden.")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):
        calculated_money = random.randrange(10, 150, 10)
        worked_hours = int(calculated_money / 10)
        db.database.execute(f'UPDATE userdata SET worked_hours = worked_hours + {worked_hours} WHERE d_id = {ctx.message.author.id}')
        db.database.execute(f'UPDATE userdata SET money = money + {calculated_money} WHERE d_id = {ctx.message.author.id}')

        embed=eb.build_embed(f"Simplistic - Jobcenter", f"Du hast Geld erhalten!", 
                            [["Arbeitsstunden", worked_hours, True],
                            ["Erhaltenes Geld", calculated_money, True]],
                            0x00ff00, None, None, None)

        await ctx.send(embed=embed)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cd = round(error.retry_after)
            minutes = str(cd // 60)
            seconds = str(cd % 60)

            embed = eb.build_embed("Cooldown", " ", [["Achting", f"Du brauchst erstmal eine Pause. Die Arbeit war anstrengend.\nMach mal eine Pause:\n \n {self.leadingZero(minutes)}:{self.leadingZero(seconds)}.", True]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)


    @commands.command(help="Raubt den gewählten User aus.")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def rob(self, ctx, user: discord.Member):
        chance = random.randrange(0, 100)
        if chance <= 10:
            # Bestohlener User
            db.database.execute(f'SELECT * FROM userdata WHERE d_id = {user.id}')
            result = db.database.fetchall()
            money = result[0][7]
            if money <= 0:
                await ctx.send("Ausgewählter User hat zu wenig Geld.")
                return
            money = (money / 100) * 10
            db.database.execute(f'UPDATE userdata SET money = money - {money} WHERE d_id = {user.id}')
            db.database.execute(f'UPDATE userdata SET robbed_success = robbed_success + 1 WHERE d_id = {user.id}')

            # Zum Räuber
            db.database.execute(f'UPDATE userdata SET money = money + {money} WHERE d_id = {ctx.message.author.id}')

            embed=eb.build_embed(f"Simplistic - Economy", f"Ein User wurde ausgeraubt!", 
                            [["Räuber", ctx.message.author.display_name, True],
                            ["Opfer", user.display_name, True],
                            ["Erbeuteter Betrag", int(money), False]],
                            0xFF0000, None, None, None)
            await ctx.send(embed=embed)

        else:
            db.database.execute(f'UPDATE userdata SET robbed_fail = robbed_fail + 1 WHERE d_id = {user.id}')
            await ctx.send(f"{user.name} konnte deinen Raubversuch entgehen")

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            cd = round(error.retry_after)
            minutes = str(cd // 60)
            seconds = str(cd % 60)

            embed = eb.build_embed("Cooldown", " ", [["Achting", f"Deine kriminelle Energie ist zu schwach für den nächsten Raubzug.\nMach mal eine Pause:\n \n {self.leadingZero(minutes)}:{self.leadingZero(seconds)}.", True]], 0xFF0000, None, None, None)
            await ctx.send(embed=embed)

    def leadingZero(self, time: str):
        if len(time) > 1:
            return time

        return "0" + time



def setup(bot):
    bot.add_cog(Economy(bot))