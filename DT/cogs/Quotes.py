from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from datetime import datetime, timedelta
import discord
import threading
import ast

with open('Quotes.txt', 'r') as f:
    global quotes
    quotes = ast.literal_eval(f.read())

class Quotes(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # Send Message into Logging Channel
    async def command_log(self, ctx, content, name):
        log = discord.Embed(
            description=f"Command Used in {ctx.channel.mention}: {name}", color=0x000000
        ).set_author(name=ctx.author, url=None, icon_url=ctx.author.avatar)
        timestamp = datetime.now()+timedelta(hours=7)
        log.timestamp = timestamp
        log.add_field(name="Response", value=content)
        await self.client.get_channel(883495591374635008).send(embed=log)

    @commands.hybrid_group(name="quote")
    async def quote_group(self, ctx: commands.Context):
        return

    @quote_group.command(name="assign")
    async def quote_assign(self, ctx: commands.Context, name: str, quote: str):
        # If author is a secretary or admin
        if discord.utils.get(ctx.guild.roles, name="Deathtrooper Secretary") in ctx.author.roles or ctx.author.guild_permissions.administrator:
            # Add name and quote to quotes dictionary
            quotes[name.lower()] = quote
            # Update file
            with open("Quotes.txt", 'w') as f:
                f.write(str(quotes))
            # Send Messages
            await ctx.send(f"Successfully assigned {name.lower()}'s quote as {quote}")
            await self.command_log(ctx, f"Member: {ctx.author.mention}\nTrigger: {name.lower()}\nQuote: {quote}", "Quote Assign")
        else:
            await ctx.send("Invalid Permissions.")
            
    @quote_group.command(name="remove")
    async def quote_remove(self, ctx: commands.Context, name: str):
        # If author is a secretary or admin
        if discord.utils.get(ctx.guild.roles, name="Deathtrooper Secretary") in ctx.author.roles or ctx.author.guild_permissions.administrator:
            # Remove name from quotes and update file
            try:
                quotes.pop(name.lower())
                with open("Quotes.txt", 'w') as f:
                    f.write(str(quotes))
                # Send Messages
                await ctx.send(f"Successfully removed {name.lower()}'s quote.")
                await self.command_log(ctx, f"Member: {ctx.author.mention}\nTrigger: {name.lower()}", "Quote Remove")
            except ValueError:
                await ctx.send('Invalid Name.')
        else:
            await ctx.send("Invalid Permissions.")

    @commands.Cog.listener()
    async def on_message(self, message):
        # If author is not the bot
        if message.author.id != self.client.user.id:
            # if someone is mentioned
            if message.mentions != []:
                # If the bot was mentioned and it's not sour
                bot = await self.client.fetch_user(self.client.user.id)
                if bot in message.mentions and not message.author.id == 295644243945586688:
                    # Send Message
                    await message.channel.send(f'<@{message.author.id}> https://cdn.discordapp.com/attachments/484438766266613760/764018553203982346/IMG_20200722_190606.png')
            # Check if the message is in quotes
            if message.content.lower() in quotes:
                # Send value associated with key
                await message.channel.send(quotes[message.content.lower()])
            # Check if message contains a wildcard quote
            elif [key for key in quotes if key[2:] in message.content.lower() and key.startswith('??')]:
                # Send Quote
                await message.channel.send(quotes[[key for key in quotes if key[2:] in message.content.lower() and key.startswith('??')][0]])
        
# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Quotes(client))