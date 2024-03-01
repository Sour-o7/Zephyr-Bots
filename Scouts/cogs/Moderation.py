from __future__ import print_function
from discord.ext import commands
import discord

class Ban(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # Define Command Group
    @commands.hybrid_group(name="ban")
    async def ban_parent(self, ctx: commands.Context):
        return
        
    # Ban by ID
    @ban_parent.command(name="by-id")
    async def banbyid(self, ctx: commands.Context, id: int, reason: str = "None Provided", daysfordeletion: int = 0):
        # If ban permissions
        if ctx.author.guild_permissions.ban_members:
            user = None
            # Limit daysfordeletion to 0 - 7
            if daysfordeletion > 7:
                daysfordeletion = 7
            elif daysfordeletion < 1:
                daysfordeletion=0
            # Fetch user by ID
            try:
                user = await self.client.fetch_user(id)
            except Exception as e:
                await ctx.send('This is not a valid user ID!')
                return
            # Ban user and send message.
            await ctx.guild.ban(user, reason=reason, delete_message_days=daysfordeletion)
            await ctx.send(f"Banned {user} for `{reason}`")
        else:
            await ctx.send('Invalid Permissions')
    
    # Ban by user
    @ban_parent.command(name="by-user")
    async def banbyuser(self, ctx: commands.Context, user: discord.Member, reason: str = "None Provided", daysfordeletion: int = 0):
        # If ban permissions
        if ctx.author.guild_permissions.ban_members:
            # Limit daysfordeletion to 0 - 7
            if daysfordeletion > 7:
                daysfordeletion = 7
            elif daysfordeletion < 1:
                daysfordeletion = 0
            # Ban user and send message
            await ctx.guild.ban(user, reason=reason, delete_message_days = daysfordeletion)
            await ctx.send(f"Banned {user} for `{reason}`")
        else:
            await ctx.send('Invalid Permissions')
            
    # Kick user
    @commands.hybrid_command(name="kick")
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = "None Provided"):
        # If kick permissions
        if ctx.author.guild_permissions.kick_members:
            # Kick user and send message
            await ctx.guild.kick(member, reason=reason)
            await ctx.send(f"Kicked {member} for `{reason}`")
        else:
            await ctx.send('Invalid Permissions')

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Ban(client))