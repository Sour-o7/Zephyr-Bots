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
    async def report(self, ctx: commands.Context, deathtrooper: str, reason: str, type: str, evidence: discord.Attachment = None):

        reporter = '' if type == "Anonymous" else f'`Trooper Reporting:`{ctx.author.name} ; <@{str(ctx.author.id)}> ; {str(ctx.author.id)}\n'
        ping = '' if type != "HighCommandOnly" else '\n<@&878039331208585246>'
        date = datetime.now(timezone("EST")).strftime("%#m/%d/%y")
        time = datetime.now(timezone("EST")).strftime("%#I:%M %p")
        # If Not High Command Only
        if(type != "HighCommandOnly"):
            await self.client.get_channel(879221853292482610).send(f'{reporter}`Trooper Reported:` {deathtrooper}\n`Date:` {date}\n`Time:` {time}\n`Reason:` {reason}\n<@&878039331208585246>')
        # Send Message to High Command Channel
        await self.client.get_channel(879222225377579038).send(f'`Type:`{type}\n`Trooper Reporting:` {ctx.author.name} ; <@{str(ctx.author.id)}> ; {str(ctx.author.id)}\n`Trooper Reported:` {deathtrooper}\n`Date:` {date}\n`Time: `{time}\n`Reason:` {reason}{ping}')
        await ctx.send('Report Filed Successfully', ephemeral = True)
        # Send evidence
        if evidence is not None:
            if type != "HighCommandOnly":
                evidence_file = await evidence.to_file()
                await self.client.get_channel(879221853292482610).send(file = evidence_file)
            evidence_file = await evidence.to_file()
            await self.client.get_channel(858945446013698059).send(file = evidence_file)
# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Reports(client))