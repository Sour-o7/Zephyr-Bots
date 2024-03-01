from __future__ import print_function
from discord.ext import commands
import discord

class MemberLeave(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if discord.utils.get(member.guild.roles, name="Jump Trooper") in member.roles:
            await self.client.get_channel(683787869839425631).send(f'<@&683787371988385807> <@{member.id}>({member.display_name}) has left the discord.')

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(MemberLeave(client))