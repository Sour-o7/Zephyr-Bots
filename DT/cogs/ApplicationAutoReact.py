from __future__ import print_function
from discord.ext import commands
import discord


class ApplicationAutoReact(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) != discord.channel.DMChannel and type(message.channel) != discord.channel.GroupChannel:
            if message.channel.name == "arc-representative-applications" or message.channel.name == "fleet-representative-applications":
                await message.add_reaction(r"<:PositiveOne:880321561884753941>")
                await message.add_reaction(r"<:NeutralOne:880321613235630101>")
                await message.add_reaction(r"<:NegativeOne:880321676846440451>")

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(ApplicationAutoReact(client))