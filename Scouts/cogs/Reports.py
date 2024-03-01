from __future__ import print_function
from discord.ext import commands
from datetime import datetime
from pytz import timezone
import discord

class Reports(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
    @commands.hybrid_command(name="report")
    async def report(self, ctx: commands.Context, scout: str, offense: str):
        # Send messages
        await self.client.get_channel(720319493750128842).send(f'<@{ctx.author.id}> has submitted a report.\n**Date:** {datetime.now(timezone("EST")).strftime("%b %#d, %Y %#I:%M:%S %p")}\n**Scout In Question:** {scout}\n**Offense:** {offense}\n<@&691104806210633740>')
        await ctx.send('Report Filed Successfully', ephemeral = True)

    @commands.hybrid_command(name="closereport")
    async def closereport(self, ctx: commands.Context, reporter: discord.Member, status: str, notes: str):
        # Get author's roles
        author_roles = [x.name for x in ctx.author.roles]
        # If IA Member
        if "Internal Affairs" in author_roles:
            # Send Messages
            await reporter.send(f"> Your report has been {status} by <@{ctx.author.id}>.\n{notes}\n\nIf you have any questions or concerns, please contact <@{ctx.author.id}>")
            await ctx.send(f"{reporter.mention}'s report has been closed.")
        else:
            await ctx.send("Invalid Permissions", ephemeral = True)

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Reports(client))