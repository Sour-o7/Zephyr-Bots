from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from apiclient import discovery
from google.oauth2 import service_account
import discord
import os.path
import os
import threading
import time

class Logs(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        super().__init__()  # this is now required in this context.
        
    # General function for updating logs on spreadsheet
    async def update_logs(self, author_id, activity_type):
        # Column letters for each type of log
        column_reference = {
            'Escort': 'E',
            'Security': 'F',
            'Mercenary': 'G',
            'Fugitive': 'H',
            'Patrol': 'I'
        }
        # Get log column for specified activity
        log_column = column_reference[activity_type]

        # Variables for google sheets api
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1RHxuIb3w-ZC1o70lx_X9qY8Iho2eeUFBddBHgIIVwNk'

        # Get columns E-M (Logs and DiscordID)
        rows = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=('Roster!E:M')).execute().get('values')
        rows = [x if len(x) == 9 else [[""]*9] for x in rows ]

        # Get author's row number
        row_number = [n[-1] for n in rows].index(str(author_id))

        # Add 1 to cell corresponding to activity type
        values = [[int(rows[row_number][list(column_reference.values()).index(log_column)]) + 1],]

        # Variables for google sheets request
        range_name = f"Roster!{log_column}{str(int(row_number) + 1)}"
        body = {'values': values}
        # Send request
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()
        
    # Define parent command for logs
    @commands.hybrid_group(name="log")
    async def log_command(self, ctx: commands.Context) -> None:
        return
        
    @log_command.command(name="escort")
    async def LogEscort(self, ctx: commands.Context, person: str, time: str, notes: str="None"):
        # Send Message
        await ctx.send(f"Name: {ctx.author.mention}\nType: Escort\nPerson: {person}\nTime: {time}\nNotes: {notes}")
        # Attempt to update logs
        try:
            await self.update_logs(ctx.author.id, "Escort")
        except Exception as e:
            await ctx.channel.send(e)
            
    @log_command.command(name="security")
    async def LogSecurity(self, ctx: commands.Context, location: str, time: str, incidents: str):
        # Send Message
        await ctx.send(f"Name: {ctx.author.mention}\nType: Security\nLocation: {location}\nTime: {time}\nincidents: {incidents}")
        # Attempt to update logs
        try:
            await self.update_logs(ctx.author.id, "Security")
        except Exception as e:
            await ctx.channel.send(e)
            
    @log_command.command(name="mercenary")
    async def LogMercenary(self, ctx: commands.Context, organizer: str, activity_type: str, time: str, incidents: str):
        # Send Message
        await ctx.send(f"Name: {ctx.author.mention}\nType: Mercenary\nOrganizer: {organizer}\nActivity Type: {activity_type}\nTime: {time}\nIncidents: {incidents}")
        # Attempt to update logs
        try:
            await self.update_logs(ctx.author.id, "Mercenary")
        except Exception as e:
            await ctx.channel.send(e)
            
    @log_command.command(name="fugitive")
    async def LogFugitive(self, ctx: commands.Context, fugitive: str, time: str, notes: str="None"):
        # Send Message
        await ctx.send(f"Name: {ctx.author.mention}\nType: Fugitive\nFugitive: {fugitive}\nAproxx Time: {time}\nNotes: {notes}")
        # Attempt to update logs
        try:
            await self.update_logs(ctx.author.id, "Fugitive")
        except Exception as e:
            await ctx.channel.send(e)
            
    @log_command.command(name="patrol")
    async def LogPatrol(self, ctx: commands.Context, where: str, time: str, notes: str="None"):
        # Send Message
        await ctx.send(f"Name: {ctx.author.mention}\nType: Patrol\nWhere: {where}\nTime: {time}\nNotes: {notes}")
        # Attempt to update logs
        try:
            await self.update_logs(ctx.author.id, "Patrol")
        except Exception as e:
            await ctx.channel.send(e)

# Setup function
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Logs(client))