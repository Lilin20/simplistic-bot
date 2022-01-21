import discord
import sys
from discord.ext import commands
import os
import platform
import ardrone


def getpath():
    config_path = None
    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\scripts\\"
    if platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/scripts"
    return config_path

sys.path.insert(1, getpath())
import database as db


class Drone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.drone = None
        self.emoji_list = ['⬆️','⬇️','⬅️','➡️','⏫','⏬','⏸','🚁','❌','📷','🎧']

    @commands.Cog.listener()
    async def on_ready(self):
        print("Drone module loaded.")

    @commands.command()
    async def reset(self, ctx):
        self.drone.halt()
        self.drone = ardrone.ARDrone()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        channel = discord.utils.get(self.bot.get_all_channels(), name='piloting')
        channel_id = channel.id

        if user == self.bot.user:
            return
        if reaction.emoji == self.emoji_list[0]:
            self.drone.move_up()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[1]:
            self.drone.move_down()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[2]:
            self.drone.turn_left()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[3]:
            self.drone.turn_right()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[4]:
            self.drone.move_forward()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[5]:
            self.drone.move_backward()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[6]:
            self.drone.hover()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[7]:
            self.drone.takeoff()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[8]:
            self.drone.land()
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[9]:
            self.drone.image.save("droneView.png")
            await channel.send(file=discord.File('droneView.png'))
            await reaction.remove(user)
        if reaction.emoji == self.emoji_list[10]:
            self.drone.event_yawdance()
            await reaction.remove(user)

    @commands.command()
    async def initialize(self, ctx):
        self.drone = ardrone.ARDrone()
        embedVar = discord.Embed(title="Cockpit", description='ARDrone-Rewritten', color=0x0000CD)
        embedVar.add_field(name="Steuerung", value="Die Drohne wird über 'Reactions' gesteuert.")
        embedVar.add_field(name=":arrow_left:", value="Nach links drehen.", inline=False)
        embedVar.add_field(name=":arrow_right:", value="Nach rechts drehen.", inline=True)
        embedVar.add_field(name=":arrow_up:", value="Nach oben fliegen.", inline=True)
        embedVar.add_field(name=":arrow_down:", value="Nach unten fliegen.", inline=True)
        embedVar.add_field(name=":arrow_double_up:", value="Nach vorne fliegen.", inline=True)
        embedVar.add_field(name=":arrow_double_down:", value="Nach hinten fliegen.", inline=True)
        embedVar.add_field(name=":pause_button:", value="Aktuelle Aktion stoppen.", inline=True)
        embedVar.add_field(name=":helicopter:", value="Lässt die Drohne abheben.", inline=True)
        embedVar.add_field(name=":x:", value="Lässt die Drohne landen.", inline=True)
        embedVar.add_field(name=":camera:", value="Macht ein Bild von der Drohnenkamera.", inline=True)
        embedVar.add_field(name=":headphones:", value="Lässt die Drohne tanzen.", inline=True)
        message = await ctx.send(embed=embedVar)
        for emote in self.emoji_list:
            await message.add_reaction(emote)

    @commands.command()
    async def takeoff(self, ctx):
        self.drone.takeoff()

    @commands.command()
    async def land(self, ctx):
        self.drone.land()

    @commands.command()
    async def left(self, ctx):
        self.drone.turn_left()

    @commands.command()
    async def right(self, ctx):
        self.drone.turn_right()

    @commands.command()
    async def up(self, ctx):
        self.drone.move_up()

    @commands.command()
    async def down(self, ctx):
        self.drone.move_down()

    @commands.command()
    async def hover(self, ctx):
        self.drone.hover()

    @commands.command()
    async def get_image(self, ctx):
        self.drone.image.save("test123.png")
        await ctx.send(file=discord.File('test123.png'))

    @commands.command()
    async def dance(self, ctx):
        self.drone.event_yawdance()



def setup(bot):
    bot.add_cog(Drone(bot))
