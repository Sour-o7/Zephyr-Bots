from __future__ import print_function
from discord.ext import commands
from discord.ext import commands
from pytz import timezone
from datetime import datetime
import discord

class Reports(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    @commands.hybrid_command(name="report")
    async def report(self, ctx: commands.Context, offender: str, reason:str):
        # If channel is reports
        if ctx.channel.name == "reports":
            # Send Messages
            embed = discord.Embed(timestamp=datetime.now(timezone('US/Eastern')), colour=0x001183, description=f"**Reporter:** {ctx.author.display_name}\n**Offender:** {offender}\n**Reason:**   {reason}")
            await ctx.send(content=f"Thank you {ctx.author.mention}, your report has been sent in!", embed=embed)
            await self.client.get_channel(527291868850159637).send(content=f"<@&520397357368737792> A report has been sent in!", embed=embed)
        else:
            await ctx.send("Use the correct channel!", ephemeral=True)

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Reports(client))