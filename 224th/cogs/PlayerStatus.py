from __future__ import print_function
import discord
from discord.ext import commands
import discord
import a2s
import asyncio

# Player Status Class
class PlayerStatus(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)

        # Create Task on client loop
        client.loop.create_task(self.periodic())
    async def periodic(self):
        # Loop forever
        while True:
            # Ping Zephyr and set status to "x/110 Zephyr Roleplay"
            try:
                info = a2s.info(self.SERVER_ADDRESS)
                await self.client.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{info.player_count}/{info.max_players} Zephyr Roleplay"))
            # If error, set status to idle
            except Exception as e:
                print(e)
                await self.client.change_presence(status=discord.Status.idle)
            # Wait 5 minutes
            await asyncio.sleep(300)

# Setup Function
async def setup(client):
    await client.add_cog(PlayerStatus(client))