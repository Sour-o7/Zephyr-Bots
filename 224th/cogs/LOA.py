import discord
from discord.ext import commands
from discord.utils import get

class LOA(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    @commands.hybrid_command(name="loa")
    async def loa(self, ctx: commands.Context, start_date: str, end_date: str, reason: str = "None Provided") -> None:
        # If channel is LOA
        if ctx.channel.name == "loa":
            # Add LOA Role and send message
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="LOA"))
            await ctx.send(f"<@{ctx.author.id}> just went on LOA from the {start_date} till the {end_date}. Reason: {reason}")
        else:
            ctx.send("Use the Correct Channel!", ephemeral = True)
            
    @commands.hybrid_command(name="endloa")
    async def endloa(self, ctx: commands.Context) -> None:
        # If channel is LOA
        if ctx.channel.name == "loa":
            # Remove LOA role and send message
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name="LOA"))
            await ctx.send(f"<@{ctx.author.id}> went off their LOA.")
        else:
            ctx.send("Use the Correct Channel!", ephemeral = True)

# Setup Functi            
async def setup(client: commands.Bot) -> None:
    await client.add_cog(LOA(client))