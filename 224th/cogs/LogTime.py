from __future__ import print_function
import discord
from discord.ext import commands
from discord.utils import get
from apiclient import discovery
from google.oauth2 import service_account
from discord.ext import commands
import os.path
import os

class LogTime(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # A function to add 2 strings in format "HH:MM"
    async def maths_handler(self, a, b):
        if a == "":
            a = "0:0"
        timeList = [a, b]
        totalSecs = 0
        for tm in timeList:
            timeParts = [int(s) for s in tm.split(':')]
            totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60
        totalSecs = divmod(totalSecs, 60)[0]
        hours, minutes = divmod(totalSecs, 60)
        return "%d:%02d" % (hours, minutes)
       
    # Update time on spreadsheet
    async def update_time(self, author_id, time):
        # Spreadsheet variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1ndHEHSjsn5-DaP5GWDQeluiSJEy26X9ZGeetat0wdZU'
        
        # Get time and discord id
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'Member List'!G:H")).execute().get('values')
        members = [[i[0], i[1]] if len(i) == 2 else ([i[0], ''] if len(i) == 1 else ['','']) for i in members]

        # Get authors's row number
        row_number = [n[0] for n in members].index(str(author_id))
        # Add time together
        values = [ await self.maths_handler(members[row_number][1], time), ]
        # Request Variables
        range_name = f"'Member List'!H{str(int(row_number) + 1)}:H{str(int(row_number) + 1)}"
        values = [values,]
        body = {'values': values}
        # Send request
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()

    @commands.hybrid_command(name="log")
    async def log_time(self, ctx: commands.Context, hours:int=0, minutes:int=0):
        # If channel is timesheets
        if ctx.channel.name == "timesheets":
            # Send message and store message object
            message = await ctx.send(f"<@{ctx.author.id}> - {hours} hours and {minutes} minutes")
            # Attempt update and reaction
            try:
                await self.update_time(ctx.author.id, f"{hours}:{minutes}")
                await message.add_reaction('<:Accepted:908787795076743248>')
            except Exception as e:
                await message.add_reaction('<:Denied:908787834637393970>')
                await ctx.channel.send(f'<@&671801935052931074><@295644243945586688> There has been an error: {e}')
        else:
            await ctx.send('Please use the correct channel.', ephemeral = True)

# Setup Function
async def setup(client: commands.Bot) -> None:
    await client.add_cog(LogTime(client))