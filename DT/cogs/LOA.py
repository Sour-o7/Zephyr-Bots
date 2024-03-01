from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from apiclient import discovery
from google.oauth2 import service_account
import discord
import os.path
import os
import threading
import asyncio

class LOA(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    async def roster_loa(self, author_id, new_value):
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1zFiOEYIYEKQY_qhAJ_8TtXiucDbYGSTwj_-E8J6HabU'
        # Get Discord IDs
        ids = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!O:O")).execute().get('values')
        ids = [''.join([str(elem) for elem in sublist]) for sublist in ids]
        # Get author's row number and turn into range
        range_name = "'Deathtrooper Roster Mk.V'!K" + str((ids.index(str(author_id))+1))
        # Update cell value
        values = [
            [
                new_value
            ],
        ]
        body = {
            'values': values
        }
        # Request
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='RAW', body=body).execute()

    @commands.hybrid_command(name="loa")
    async def loa(self, ctx: commands.Context, end_date: str, reason: str):
        if ctx.channel.name != ("loa"):
            await ctx.send('Please use the correct channel.', ephemeral = True)
            return

        # Check if author is a trainee
        role = discord.utils.get(ctx.guild.roles, name="Trainee")
        if role in ctx.author.roles:
            # Send message and react with ✅
            message = await ctx.send(f'<@{ctx.author.id}> has requested to go on a LOA until {end_date} with the reason {reason}. React with ✅ to approve this LOA. This request will expire in 10 minutes.')
            await message.add_reaction('✅')

            def check(reaction, user):
                officer = discord.utils.get(ctx.guild.roles, name="Deathtrooper Officer")
                return officer in user.roles and str(reaction.emoji) == '✅'
            # Await reaction with timeout of 600 seconds and check if reaction is ✅ and user is an officer
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=600.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f'No Reaction within 10 minutes, LOA Denied <@{ctx.author.id}>')
            # Request was approved
            else:
                # Send Message and Give Roles
                response = await ctx.send(f"<@{str(ctx.author.id)}> has gone on LOA until {end_date}, Reason: {reason}")
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Leave Of Absence"))
                # Update Roster and add reaction
                await self.roster_loa(ctx.author.id, end_date)
                await response.add_reaction('<a:ICSeal:845123520887521281>')
        else:
            # Send Message and add roles
            response = await ctx.send(f"<@{str(ctx.author.id)}> has gone on LOA until {end_date}, Reason: {reason}")
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name="Leave Of Absence"))
            # Update Roster and react
            await self.roster_loa(ctx.author.id, end_date)
            await response.add_reaction('<a:ICSeal:845123520887521281>')            

    @commands.hybrid_command(name="offloa")
    async def offloa(self, ctx: commands.Context):
        if ctx.channel.name == ("loa"):
            # Send message and remove roles
            response = await ctx.send(f"<@{str(ctx.author.id)}> has come off LOA, and has returned to duty!")
            await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, name="Leave Of Absence"))
            # Update Roster and React
            await self.roster_loa(ctx.author.id, "")
            await response.add_reaction('<a:ICSeal:845123520887521281>')
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(LOA(client))