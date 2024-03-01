from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from datetime import datetime
from apiclient import discovery
from google.oauth2 import service_account
from pytz import timezone
import discord
import os.path
import os
import threading

class Logging(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        self.service = discovery.build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = '1zFiOEYIYEKQY_qhAJ_8TtXiucDbYGSTwj_-E8J6HabU'

    async def roster_update_log(self, author_id, log_type):
        # Get DiscordIDs and Logs
        ids = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!O:O")).execute().get('values')
        logs = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=(f"'Deathtrooper Roster Mk.V'!{log_type}:{log_type}")).execute().get('values')
        ids = [''.join([str(elem) for elem in sublist]) for sublist in ids]
        logs = [''.join([str(elem) for elem in sublist]) for sublist in logs]
        # If no logs set to 0
        if logs[ids.index(str(author_id))] == 'N/A':
            logs[ids.index(str(author_id))] = 0
        # Get range and add 1 to logs
        range_name = "'Deathtrooper Roster Mk.V'!" + log_type + str(ids.index(str(author_id)) + 1)
        values = [[int(logs[ids.index(str(author_id))]) + 1],]
        # Request
        body = {'values': values}
        self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_name,valueInputOption='RAW', body=body).execute()
        # Return number of logs
        return int(logs[ids.index(str(author_id))]) + 1

    @commands.hybrid_command(name="logpt")
    async def log_pt(self, ctx: commands.Context, activities: str, attended: str, supervisor: discord.Member = None, notes: str = "None"):
        if ctx.channel.name == ("nco-logs"):
            await ctx.defer()
            # Update Roster
            pt_number = await self.roster_update_log(ctx.author.id, 'W')
            # Send Message
            await ctx.send(f'Host: <@{str(ctx.author.id)}>\nDate: {datetime.now(timezone("EST")).strftime("%#m/%d/%y")}\nPT Number: {str(pt_number)}\nPT Activities: {activities}\nDT Attended: {str(attended)}\nNotes: {notes}')
            # If there is a supervisor, add 1 to column X
            if supervisor is not None:
                await self.roster_update_log(supervisor.id, 'X')
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)
            
    @commands.hybrid_command(name="logtryout")
    async def log_tryout(self, ctx: commands.Context, attended: int, passed: int, supervisor: discord.Member = None, notes: str='None'):
        if ctx.channel.name == ("tryout-logs"):
            await ctx.defer()
            # Get Tryout count
            tryout_number = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!O:T")).execute().get('values')
            tryout_number = [x[5] for x in tryout_number if len(x) == 6 and x[0] == str(ctx.author.id)]
            tryout_number = tryout_number[0]
            # If no tryouts, set to 0
            if tryout_number == 'N/A':
                tryout_number = 0
            # Send Message
            await ctx.send(f'Host: <@{str(ctx.author.id)}>\nSupervisor: {"None" if supervisor is None else supervisor.mention}\nDate: {datetime.now(timezone("EST")).strftime("%#m/%d/%y")}\nTryout Number: {str(int(tryout_number)+1)}\nNumber Attended: {str(attended)}\nNumber Passed: {str(passed)}\nNotes: {notes}')
            # Update Roster
            if attended == 0:
                await self.roster_update_log(ctx.author.id, 'V')
            else:
                await self.roster_update_log(ctx.author.id, "T")
            if supervisor is not None and attended != 0:
                await self.roster_update_log(supervisor.id, "U")
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)
            
    @commands.hybrid_command(name="logpatrol")
    async def log_patrol(self, ctx: commands.Context, route: str, attended: str, notes: str = "None"):
        if ctx.channel.name == ("nco-logs"):
            await ctx.send(f'Host: <@{str(ctx.author.id)}>\nPatrol Route: {route}\nDT Attended: {str(attended)}\nNotes: {notes}')
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)
            
    @commands.hybrid_command(name="logsim")
    async def log_sim(self, ctx: commands.Context, staff: str, activities: str, attended: str, notes: str = "None"):
        if ctx.channel.name == ("nco-logs"):
            await ctx.send(f'Host: {ctx.author.mention}\nDate: {datetime.now(timezone("EST")).strftime("%#m/%d/%y")}\nSIM Number: N/A\nStaff that Assisted: {staff}\nSIM Activities: {activities}\nDT Attended: {str(attended)}\nNotes: {notes}')
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Logging(client))