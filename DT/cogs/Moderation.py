from __future__ import print_function
from discord.ext import commands
from datetime import datetime, timedelta
import discord
import threading

class Moderation(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        # Guild ID
        self.GUILD_ID = 877764629042958336
        
    async def command_log(self, ctx, content, name):
        log = discord.Embed(
            description=f"Command Used in {ctx.channel.mention}: {name}", color=0x000000
        ).set_author(name=ctx.author, url=None, icon_url=ctx.author.avatar)
        timestamp = datetime.now()+timedelta(hours=7)
        log.timestamp = timestamp
        log.add_field(name="Response", value=content)
        await self.client.get_channel(883495591374635008).send(embed=log)
        
    #          #
    # Commands #    
    #          #
    
    # Define command group
    @commands.hybrid_group(name="ban")
    async def ban_group(self, ctx: commands.Context):
        return
        
    @ban_group.command(name="by-id")
    async def ban_by_id(self, ctx: commands.Context, id: str, daysfordeletion: int = 0, reason: str = "None Provided."):
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
            
    @ban_group.command(name="by-user")
    async def ban_by_user(self, ctx: commands.Context, user: discord.Member, daysfordeletion: int = 0, reason: str = "None Provided."):
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

    @commands.hybrid_command(name="purge")
    async def purge(self, ctx: commands.Context, amount = 30):
        # If author has admin or is sour
        if ctx.author.guild_permissions.administrator or ctx.author.id == 295644243945586688:
            # Get messages
            await ctx.defer()
            messages = []
            async for message in ctx.channel.history(limit=amount + 1):
                messages.append(message)
            # Delete Messages
            await ctx.channel.delete_messages(messages)
            # Send confirmation message and audit message
            await ctx.channel.send(f'> {amount} messages have been purged by {ctx.author.mention}')
            await self.command_log(ctx, f"Member: {ctx.author.mention}\nAmount: {amount}\nChannel: {ctx.channel.mention}", "Purge")
        else:
            await ctx.send("Invalid Permissions")

    #        #
    # Events #
    #        #
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Check if guild is DT discord
        if before.guild.id != self.GUILD_ID or before.content == "":
            return
        # Make sure channel topic is not "[Locked.]"
        if before.channel.topic is None:
            before.channel.topic = ""
        if "[Locked.]" not in before.channel.topic:
            # If message was edited
            if before.content != after.content:
                # Send Embed
                message_embed = discord.Embed(
                    description=f"Message edited in {before.channel.mention}", color=0x007B10
                ).set_author(name=before.author, url=None, icon_url=before.author.avatar)
                message_embed.add_field(name="Old Message", value=before.content)
                message_embed.add_field(name="New Message", value=after.content)
                timestamp = before.created_at
                message_embed.timestamp = timestamp
                await self.client.get_channel(879943145452863528).send(embed=message_embed)
                
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Check if guild is DT Discord
        if message.guild.id != self.GUILD_ID:
            return
        # Check if channel topic is not "[Locked]"
        if message.channel.topic is None:
            message.channel.topic = ""
        if "[Locked.]" not in message.channel.topic:
            # If old message context
            if message.content != '':
                # Send Embed
                message_embed = discord.Embed(
                    description=f"Message deleted in {message.channel.mention}", color=0x007B10
                ).set_author(name=message.author, url=None, icon_url=message.author.avatar)
                message_embed.add_field(name="Message", value=message.content)
                timestamp = message.created_at
                message_embed.timestamp = timestamp
                await self.client.get_channel(879943145452863528).send(embed=message_embed)
            # Loop through all attachments in message
            for attachment in message.attachments:
                # Send each file
                try:
                    file = await attachment.to_file(use_cached=True)
                    message_embed_files = discord.Embed(
                        description=f"Attachment above message_embed in {message.channel.mention}", color=0x007B10
                    ).set_author(name=message.author, url=None, icon_url=message.author.avatar)
                    timestamp = message.created_at
                    message_embed_files.timestamp = timestamp
                    await self.client.get_channel(879943145452863528).send(embed=message_embed_files, file=file)
                except:
                    message_embed_files = discord.Embed(
                        description=f"Unknown attachment message_embed in {message.channel.mention}", color=0x007B10
                    ).set_author(name=message.author, url=None, icon_url=message.author.avatar)
                    timestamp = message.created_at
                    message_embed_files.timestamp = timestamp
                    await self.client.get_channel(879943145452863528).send(embed=message_embed_files)
                    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Ensure proper guild
        if before.channel is not None:
            if before.channel.guild.id != self.GUILD_ID:
                return

        elif after.channel is not None:
            if after.channel.guild.id != self.GUILD_ID:
                return

        # Calculate what changed and save proper message to text
        text = ""
        if before.channel is None:
            # Ensure voice state is in guild
            text = f"Joined {after.channel.mention}"
        elif after.channel is None:
            # Ensure voice state is in guild
            text = f"Left {before.channel.mention}"
        elif before.channel != after.channel:
            text = f"{before.channel.mention} => {after.channel.mention}"
        elif before.self_deaf != after.self_deaf:
            if after.self_deaf == True:
                text = f"Deafened themselfs in {after.channel.mention}"
            else:
                text = f"Undeafened themselfs in {after.channel.mention}"
        elif before.self_mute != after.self_mute:
            if after.self_mute == True:
                text = f"Muted themselfs in {after.channel.mention}"
            else:
                text = f"Unmuted themselfs in {after.channel.mention}"
        elif before.self_stream != after.self_stream:
            if after.self_stream == True:
                text = f"Started a stream in {after.channel.mention}"
            else:
                text = f"Ended a stream in {after.channel.mention}"
        elif before.self_video != after.self_video:
            if after.self_video == True:
                text = f"Turned on video in {after.channel.mention}"
            else:
                text = f"Turned off video in {after.channel.mention}"
        
        # Filter out any unsupported actions
        if text != "":
            # Send Embed to channel
            message_embed = discord.Embed(
                description=f"{text}", color=0x0029FF
            ).set_author(name=member, url=None, icon_url=member.avatar)
            timestamp = datetime.now()
            message_embed.timestamp = timestamp
            await self.client.get_channel(880211541583089714).send(embed=message_embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Check if roles were updated
        if before.roles != after.roles:
            text = ""
            # Fetch which roles were changed
            async for entry in before.guild.audit_logs(action=discord.AuditLogAction.member_role_update, limit=1):
                entry = entry
            if entry.before.roles == []:
                text = f"{entry.user.mention} added {entry.changes.after.roles[0].mention} to {entry.target.mention}"
            if entry.after.roles == []:
                text = f"{entry.user.mention} removed {entry.changes.before.roles[0].mention} from {entry.target.mention}"
            # Send Embed
            message_embed = discord.Embed(
                description=f"{text}", color=0x9C0000
            ).set_author(name=entry.user, url=None, icon_url=entry.user.avatar)
            timestamp =  datetime.now()
            message_embed.timestamp = timestamp
            await self.client.get_channel(880304997101875272).send(embed=message_embed)

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        # Check if guild is DT discord
        if channel.guild.id != self.GUILD_ID:
            return
        # Check if channel topic is not "[Locked.]"
        if channel.topic is None:
            channel.topic = ""
        if "[Locked.]" not in channel.topic:
            # Send Embed
            message_embed = discord.Embed(
                description=f"{user.mention} started typing in {channel.mention}", color=0xF6A700
            ).set_author(name=user, url=None, icon_url=user.avatar)
            timestamp = datetime.now()
            message_embed.timestamp = timestamp
            await self.client.get_channel(882777116020707349).send(embed=message_embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction,user):
        # Check if guild is DT Discord
        if reaction.message.guild.id != self.GUILD_ID:
            return
        # Check if topic is not "[Locked.]"
        if reaction.message.channel.topic is None:
            reaction.message.channel.topic = ""
        if "[Locked.]" not in reaction.message.channel.topic:
            # Send Embed
            message_embed = discord.Embed(
                description=f"{user.mention} reacted with {reaction.emoji} in {reaction.message.channel.mention}", color=0xF6A700
            ).set_author(name=user, url=None, icon_url=user.avatar)
            timestamp = datetime.now()
            message_embed.add_field(name="Message Link", value=f"{reaction.message.jump_url}")
            message_embed.timestamp = timestamp
            await self.client.get_channel(883492606510780416).send(embed=message_embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction,user):
        # Check if guild is DT Discord
        if reaction.message.guild.id != self.GUILD_ID:
            return
        # Check if channel topic is not "[Locked.]"
        if reaction.message.channel.topic is None:
            reaction.message.channel.topic = ""
        if "[Locked.]" not in reaction.message.channel.topic:
            # Send Embed
            message_embed = discord.Embed(
                description=f"{user.mention} un-reacted with {reaction.emoji} in {reaction.message.channel.mention}", color=0xF6A700
            ).set_author(name=user, url=None, icon_url=user.avatar)
            timestamp = datetime.now()
            message_embed.add_field(name="Message Link", value=f"{reaction.message.jump_url}")
            message_embed.timestamp = timestamp
            await self.client.get_channel(883492606510780416).send(embed=message_embed)

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Moderation(client))