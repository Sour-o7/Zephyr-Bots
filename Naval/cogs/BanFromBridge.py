from __future__ import print_function
from discord.ext import commands
import discord
from discord.ext import commands
from pytz import timezone
from datetime import datetime, timedelta
import asyncio

class BanFromBridge(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
        # Variables for methods
        self.current_bans = []
        self.permissions = [
            ["Chief Warrant Officer", "Lieutenant", "Captain", "Deputy Chief", "Chief", "Deputy Director of Naval", "Naval Director"], # Ban up to 168 Hours
            ["Deputy Chief", "Chief", "Deputy Director of Naval", "Naval Director"] # No ban limit
        ]
        
        # Create loop
        self.client.loop.create_task(self.periodic())

    async def periodic(self):
        while True:
            # Loop through current_bans
            for x in self.current_bans:
                now = datetime.now(timezone('US/Eastern'))
                # If ban is expired
                if x[1] < int(now.timestamp()):
                    # Remove x from current_bans
                    self.current_bans.remove(x)
                    # Delete message
                    try:
                        channel = self.client.get_channel(907360244756279336)
                        message = await channel.fetch_message(x[0])
                        await message.delete()
                    except:
                        pass
            await asyncio.sleep(60)

    @commands.hybrid_command(name="banfrombridge")
    async def ban_from_bridge(self, ctx: commands.Context, member: str, hours: int, reason: str):
        # If channel is bridge-blacklist-commands
        if ctx.channel.name == "bridge-blacklist-commands":
            # Check if member can use bfb
            member_roles = [x.name for x in ctx.author.roles]
            if not "Probationary Naval Guard" in member_roles and "Naval Guard" in member_roles:
                # Extend response timeframe
                await ctx.defer()
                
                # If the member is requesting a time above the allowed time
                if (hours == 0 or hours > 168) and not any(x in self.permissions[1] for x in member_roles):
                    hours = 168
                
                if (hours > 24 or hours > 168) and not any (x in self.permissions[0] for x in member_roles):
                    hours = 24

                if hours != 0:

                    # Get ending timestamp
                    time_est = datetime.now(timezone('US/Eastern')) + timedelta(hours = hours)
                    
                    # Send confirmation message
                    await ctx.send(f"<@{ctx.author.id}> has issued a ban on {member} from entering bridge for {hours} hours. Reason Provided: {reason}\n{member} will be eligible for bridge entry on {time_est.strftime('%m/%d/%Y at %I:%M%p EST')}")

                    # Send ban log
                    message = await self.client.get_channel(907360244756279336).send(f'{member} - Reason: {reason} - Expires: {time_est.strftime("%m/%d/%Y at %I:%M%p EST")} `{int(time_est.timestamp())}`')

                    # Add Message to current_bans
                    self.current_bans.append([message.id, int(time_est.timestamp())])

                else:
                    await ctx.send(f"<@{ctx.author.id}> has issued a ban on {member} from entering bridge indefinitely. Reason Provided: {reason}")
                    await self.client.get_channel(907360244756279336).send(f'{member} - Reason: {reason} - Expires: `Never`')
            else:
                await ctx.send('You do not have permission to use this command!', ephemeral=True)
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)

# Setup Function
async def setup(client: commands.Bot) -> None:
    cog_instance = BanFromBridge(client)
    await client.add_cog(cog_instance)
    
    # Fetch all bridge bans after restart
    async for message in client.get_channel(907360244756279336).history(limit=None):
        if not message.content.endswith('`Never`'):
            try:
                ending_timestamp = message.content.split('`')
                cog_instance.current_bans.append([message.id, int(ending_timestamp[-2])])
            except Exception:
                pass