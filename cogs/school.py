import discord
import sys
from discord.ext import commands, tasks
import os
import platform
from datetime import date

def getpath():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')

sys.path.insert(1, getpath())
import database as db
import embed_builder as eb

#----------Schul-Modul----------
class School(commands.Cog):
    """Modul für die Schulfunktionen"""
    def __init__(self, bot):
        self.bot = bot
#-------------------------------


#-----------Wenn hochgefahren-----------
    @commands.Cog.listener()
    async def on_ready(self):
        print("School module loaded.")
        self.notify_homework.start()
        self.notify_exam.start()
#---------------------------------------


#-----------Erstellen von drei Channeln unter der Kategorie Schulinformationen (Nur ausführbar mit Admin Rechten)-----------
    @commands.command(help="Erstellt Channel für die benutzung der Schulfunktionen.")
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        channel_names = ["🔔neuigkeiten🔔", "╔⥤📖hausaufgaben📖⥢", "╚⥤📚termine📚⥢"]
        channels = []
        all_channels = self.bot.get_all_channels()
        for ch in all_channels:
            channels.append(ch.name)
        for name in channel_names:
            if name in channels:
                embed = eb.build_embed(f"Konnte nicht ausgeführt werden.", f"Dieser Befehl wurde vermutlich schonmal ausgeführt.", 
                            [],
                            0xFF1C1C, None, None, None)
                await ctx.send(embed=embed)
                return

        category = await ctx.guild.create_category_channel(name="SETUP CHANNELS")
        for name in channel_names:
            await ctx.guild.create_text_channel(name=name, category=category)

        await category.edit(position=0)
        await ctx.guild.create_role(name="Klassenmanagement", color=0xf5a742)
        await ctx.guild.create_role(name="Notify", color=0xf5a742)
#---------------------------------------------------------------------------------------------------------------------------



#-----------Wenn keine Admin Berechtigungen, wird ein Error ausgegeben-----------
    @setup.error
    async def setup_channels_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embedVar = discord.Embed(title="Keine Berechtigung",
                                     description="Du hast nicht die benötigten Rechte um diesen Befehl auszuführen.",
                                     color=0xff1c1c)
            await ctx.send(embed=embedVar)
#---------------------------------------------------------------------------------

#-----------Setzen von Hausaufgaben (Eintragen in die DB) (Nur mit Klassenmanagement oder Verwalter Rolle)-----------
    @commands.command(help="Setzt einen Klassenarbeitstermin in die Datenbank")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def set_homework(self, ctx, homeworkdate=None, *args):
        string = ""
        task_date = homeworkdate
        if len(args) > 0 and homeworkdate is not None:
            for word in args:
                string += word+" "
            db.database.execute(f'INSERT INTO homework(task, task_date) VALUES("{string}", "{homeworkdate}")')
        else:
            embed = eb.build_embed(f"Keine Eingabe", "Bitte gebe hinter dem Befehl die einzutragenden Hausaufgaben an.",
                            [["Syntax", ".set_hausaufgaben <AUFGABE>", True]],
                            0xFF1C1C, None, None, None)
            await ctx.send(embed=embed)
#----------------------------------------------------------------------------------------------------------------------


#-----------Wenn nicht genügen Berechtigungen, dann Error Ausgabe-----------
    @set_homework.error
    async def set_homework_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = eb.build_embed("Keine Berechtigung", "Du hast nicht die benötigten Rechte um diesen Befehl auszuführen.", 
                            [],
                            0xFF1C1C, None, None, None)
            await ctx.send(embed=embed)

#----------------------------------------------------------------------------


#-----------Lässt den Bot dir eine priv. Nachricht schreiben mit den Hausaufgaben-----------
    @commands.command(help="Zeigt dir die aktuellen Hausaufgaben.")
    async def homework(self, ctx):
        db.database.execute(f'SELECT task, task_date FROM homework')
        result = db.database.fetchall()
        embed = eb.build_embed("Hausaufgaben", "Dies sind die aktuellen Hausaufgaben. Falls diese nicht korrekt sind, wende dich bitte an das Klassenmanagement.", 
                            [],
                            0xFF1C1C, None, None, None)
        for i in range(len(result)):
            embed.add_field(name="Hausaufgabe", value=result[i][0], inline=True)
            embed.add_field(name="Datum", value=result[i][1], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
        await ctx.message.author.send(embed=embed)
#---------------------------------------------------------------------------------------------


#-------------Löscht aktuell noch alle Hausaufgaben-------------
    @commands.command(help="Löscht eine betimmte Hausaufgabe aus der Datenbank")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def del_homework(self, ctx, *args):
        if len(args) > 0:
            for i in args:
                db.database.execute(f'DELETE FROM homework WHERE h_id = "{i}"')
            db.database.execute(f'SET @num := 0')
            db.database.execute(f'UPDATE homework SET h_id = @num := (@num+1)')
            db.database.execute(f'ALTER TABLE homework AUTO_INCREMENT =1')
        else:
            embed = eb.build_embed(f"Keine Eingabe", "Bitte gebe hinter dem Befehl die einzutragenden Hausaufgaben an.",
                            [["Syntax", ".del_homework <ID>", True]],
                            0xFF1C1C, None, None, None)
            await ctx.send(embed=embed)
#---------------------------------------------------------------


#-----------Gibt der Person die den Befehl ausgeführt hat, die Rolle "Notify"-----------
    @commands.command(help="Gibt dir die Rolle 'Notify'.")
    async def notify_me(self, ctx):
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name="Notify")
        await member.add_roles(role)
#---------------------------------------------------------------------------------------


#-------------Listet alle 2 Stunden im Zusammenhang mit der Methode "Notify_homework" die aktuellen Hausaufgaben-------------
    # Automatic
    async def show_homework(self):
        db.database.execute(f'SELECT task, task_date FROM homework ORDER BY task_date ASC')
        result = db.database.fetchall()
        embed = eb.build_embed("Hausaufgaben", "Dies sind die aktuellen Hausaufgaben. Falls diese nicht korrekt sind, wende dich bitte an das Klassenmanagement.", 
                            [],
                            0xFF1C1C, None, None, None)
        for i in range(len(result)):
            embed.add_field(name="Hausaufgabe", value=result[i][0], inline=True)
            embed.add_field(name="Datum", value=result[i][1], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
        return embed

    @tasks.loop(hours=4)
    async def notify_homework(self):
        db.database.execute(f'SELECT task, task_date FROM homework')
        result = db.database.fetchall()
        if not result:
            return
        channel = discord.utils.get(self.bot.get_all_channels(), name="╔⥤📖hausaufgaben📖⥢")
        if channel == None:
            print("Den Befehl 'Setup' ausführen!")
            return
        guild = self.bot.guilds[0]
        role = discord.utils.get(guild.roles, name="Notify")
        await channel.purge(limit=5)
        await channel.send(role.mention)
        await channel.send(embed=await self.show_homework())
#-----------------------------------------------------------------------------------------------------------------------------


#-------------Bot sendet dem ersteller der Nachricht eine priv. Nachricht mit den aktuellen Klausuren/Tests-------------
    @commands.command(help="Gibt die aktuellen Klassenarbeiten/Tests aus.")
    async def exam(self, ctx):
        db.database.execute(f'SELECT test, test_date FROM classtest')
        result = db.database.fetchall()
        embed = eb.build_embed("Klausuren/Tests", "Dies sind die aktuellen Klausuren/Tests. Falls diese nicht korrekt sind, wende dich bitte an das Klassenmanagement.", 
                            [],
                            0xFF1C1C, None, None, None)
        for i in range(len(result)):
            embed.add_field(name="Klausuren/Tests", value=result[i][0], inline=True)
            embed.add_field(name="Datum", value=result[i][1], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
        await ctx.message.author.send(embed=embed)
#-----------------------------------------------------------------------------------------------------------------------


#-------------Nur mit den Rollen "Klassenmanagement" und "Verwalter" können Klausuren oder Tests gesetzt werden-------------
    @commands.command(help="Setzt einen beliebigen Klassenarbeits-/Testtermin in die Datenbank")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def set_exam(self, ctx, examdate=None, *args):
        string = ""
        test_date = examdate
        if len(args) > 0 and examdate is not None:
            for word in args:
                string += word + " "
            db.database.execute(f'INSERT INTO classtest(test, test_date) VALUES("{string}", "{test_date}")')
        else:
            embed = eb.build_embed(f"Keine Eingabe", "Bitte gebe hinter dem Befehl die einzutragenden Klausuren/Tests an.",
                            [["Syntax", ".set_exam <Datum/Fach/Inhalt>", True]],
                            0xFF1C1C, None, None, None)
            await ctx.send(embed=embed)
#---------------------------------------------------------------------------------------------------------------------------


#-------------Nur mit den Rollen "Klassenmanagement" und "Verwalter" können Klausuren oder Tests gelöscht werden-------------
    @commands.command(help="Löscht einen beliebigen Termin aus der Datenbank.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def del_exam(self, ctx, *args):
        if len(args) > 0:
            for i in args:
                db.database.execute(f'DELETE FROM classtest WHERE c_id = "{i}"')
            db.database.execute(f'SET @num := 0')
            db.database.execute(f'UPDATE classtest SET c_id = @num := (@num+1)')
            db.database.execute(f'ALTER TABLE classtest AUTO_INCREMENT =1')
        else:
            embed = eb.build_embed(f"Keine Eingabe", "Bitte gebe hinter dem Befehl die zu löschenden Klausur/Test-ID's an.",
                            [["Syntax", ".del_exam <ID>", True]],
                            0xFF1C1C, None, None, None)
            await ctx.send(embed=embed)



#----------------------------------------------------------------------------------------------------------------------------


#-------------Fragt alle 2 Stunden die Datenbank nach neuen Klausuren/Tests ab und erstellt für diese dann ein Embed das in Zusammenhang mit der unteren Methode alle 2 Stunden ausgegeben wird-------------
    async def show_exam(self):
        db.database.execute(f'SELECT test, test_date FROM classtest')
        result = db.database.fetchall()
        embed = eb.build_embed("Klausuren/Tests", "Dies sind die aktuellen Klausuren/Tests. Falls diese nicht korrekt sind, wende dich bitte an das Klassenmanagement.", 
                            [],
                            0xFF1C1C, None, None, None)
        for i in range(len(result)):
            embed.add_field(name="Klausuren/Tests", value=result[i][0], inline=True)
            embed.add_field(name="Datum", value=result[i][1], inline=True)
            embed.add_field(name="\u200b", value="\u200b")
        return embed

    @tasks.loop(hours=4)
    async def notify_exam(self):
        db.database.execute(f'SELECT test, test_date FROM classtest')
        result = db.database.fetchall()
        if not result:
            return
        channel = discord.utils.get(self.bot.get_all_channels(), name="╚⥤📚termine📚⥢")
        if channel == None:
            print("Den Befehl 'Setup' ausführen!")
            return
        guild = self.bot.guilds[0]
        role = discord.utils.get(guild.roles, name="Notify")
        await channel.purge(limit=5)
        await channel.send(role.mention)
        await channel.send(embed=await self.show_exam())
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


#-------------News-------------
    @commands.command(help="Sendet eine Neuigkeit in den dafür vorgesehenen Channel.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def news(self, ctx, title, *args):
        string = ""
        news_date = date.today().strftime("%d.%m.%Y")
        if len(args) > 0:
            for word in args:
                string += word + " "
            db.database.execute(f'INSERT INTO news(news, news_date) VALUES("{string}", "{news_date}")')
            embedVar = discord.Embed(title=title,
                                     description=string,
                                     color=0xff1c1c)
            #embedVar.add_field(name="Test", value=string, inline=True)
            #embedVar.add_field(name="\u200b", value="\u200b")
            embedVar.set_thumbnail(url=self.bot.user.avatar_url)
            embedVar.set_footer(text=f"Neuigkeit gepostet von {ctx.message.author.name}")
            channel = discord.utils.get(self.bot.get_all_channels(), name="🔔neuigkeiten🔔")
            message = await channel.send(embed=embedVar)
            await message.publish()

        else:
            embedVar = discord.Embed(title="Keine Eingabe",
                                     description="Bitte gebe hinter dem Befehl die einzutragenen Neuigkeiten an.",
                                     color=0xff1c1c)
            embedVar.add_field(name="Syntax", value=".news <Überschrift> <Neuigkeit>")
            await ctx.send(embed=embedVar)
#------------------------------


#-------------Deletet bestimmte News-------------
    @commands.command(help="Löscht eine Neuigkeit aus der Datenbank.")
    @commands.has_any_role("Klassenmanagement", "Verwalter")
    async def del_news(self, ctx, *args):
        if len(args) > 0:
            for i in args:
                db.database.execute(f'DELETE FROM news WHERE n_id = "{i}"')
            db.database.execute(f'SET @num := 0')
            db.database.execute(f'UPDATE news SET n_id = @num := (@num+1)')
            db.database.execute(f'ALTER TABLE news AUTO_INCREMENT =1')
        else:
            embedVar = discord.Embed(title="Keine Eingabe",
                                     description="Bitte gebe hinter dem Befehl die zu löschende Neuigkeiten-ID an.",
                                     color=0xff1c1c)
            embedVar.add_field(name="Syntax", value=".del_news <ID>")
            await ctx.send(embed=embedVar)
#---------------------------------------------------------------

def setup(bot):
    bot.add_cog(School(bot))
