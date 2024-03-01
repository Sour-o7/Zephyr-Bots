from __future__ import print_function
from apiclient import discovery
from google.oauth2 import service_account
from discord.ext import commands
from datetime import datetime
import sqlite3 as sl
import discord
import os.path
import os
import math
import a2s
import asyncio

con = sl.connect('JT.db', check_same_thread=False)
# Timesheet Class
class TimeSheets(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.streak = 0;
        
        # Create Task on client.loop
        self.client.loop.create_task(self.periodic())

    # Periodic Loop
    async def periodic(self):
        # Loop forever with 5 minute delay
        while True:
            # Get player count and add 1 to streak if player count is 0
            try:
                info = a2s.info(self.SERVER_ADDRESS)
                if info.player_count == 0:
                    self.streak += 1
                else: 
                    self.streak = 0
            except Exception as e:
                print(e)
            # If at least 15 minutes have passed
            if self.streak == 4:
                # Get active members from database and purge database
                members = con.execute("SELECT * FROM jt_timesheets").fetchone()
                con.execute("DELETE FROM jt_timesheets")
                con.commit()
                # If at least 1 active member
                if members is not None:
                    await self.client.get_channel(889995136812085289).send('Zephyr count has been 0 for 15 minutes. Purging Active Timesheets.')
            await asyncio.sleep(300)
        
    # Add a and b in HH:MM format and return sum in HH:MM format
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
        
    # Return minutes in HH:MM format
    def convert_time(self, minutes):
        hour = minutes // 60
        minutes %= 60
        return "%d:%02d" % (hour, minutes)

    # Update time on spreadsheet
    async def update_time(self, author_id, time):
        # Google sheets api variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1GkJSo2-9DeHKAY1gYNJsSI9pjr0FU7WYV-9mb72SG6w'
        
        # Get columns i through j and save discordid and time
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'Roster'!I:J")).execute().get('values')
        members = [[i[0], i[1]] if len(i) == 2 else ([i[0], ''] if len(i) == 1 else ['','']) for i in members]
        
        # Calculate member's row number
        row_number = [n[0] for n in members].index(str(author_id))
        # Add times together
        values = [ await self.maths_handler(members[row_number][1], time), ]

        # Variables for request
        values = [values,]
        range_name = f"'Roster'!J{str(int(row_number) + 1)}:J{str(int(row_number) + 1)}"
        body = {'values': values}
        # Request Changes
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()

    # Start Shift 
    @commands.hybrid_command(name="ss")
    async def start_shift(self, ctx: commands.Context):
        # If channel is not ⏱time-logs
        if ctx.channel.name != "⏱time-logs":
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            return
            
        # Extend response timeframe
        await ctx.defer()
        # Check if author is in database
        author = con.execute(f'SELECT * FROM jt_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
        if author is None:
            # Add author to database with current timestamp
            con.execute(f'INSERT INTO jt_timesheets (id, timestamp) values (?, ?)', (ctx.author.id, int(datetime.now().timestamp())))
            con.commit()
            # Send message
            timesheet_embed = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
            await ctx.send(embed=timesheet_embed)
        else:
            # Send error message - Cannot start because of existing one
            timesheet_embed = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot start a shift because you already have a running one!")
            await ctx.send(embed=timesheet_embed)
            
    # End Shift
    @commands.hybrid_command(name="es")
    async def end_shift(self, ctx: commands.Context):
        # If channel is not ⏱time-logs
        if ctx.channel.name != "⏱time-logs":
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            return
            
        # Extend response timeframe
        await ctx.defer()
        
        # Check if author is not in database
        author = con.execute(f'SELECT * FROM jt_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
        if author is None:
            # Send error message - Does not have a current timesheet
            timesheet_embed = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot end a shift because you don't have one started!")
            await ctx.send(embed=timesheet_embed)
            return
            
        # Get time differences from start and now
        time_difference = datetime.now() - datetime.fromtimestamp(author[1])
        author_time = math.floor(time_difference.total_seconds()) // 60

        # Delete author from database
        con.execute(f'DELETE FROM jt_timesheets WHERE id=?', (ctx.author.id,))
        con.commit()

        # Send end shift message
        timesheet_embed = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>, your shift has ended, it lasted {author_time} minutes!")
        sent_message = await ctx.send(embed=timesheet_embed)
        
        # Update time on spreadsheet and react to message
        try:
            await self.update_time(ctx.author.id, self.convert_time(author_time))
            await sent_message.add_reaction('✅')
        except Exception as e:
            print(e)
            await sent_message.add_reaction('❌')
            await ctx.channel.send(f'<@&504897032335523844><@295644243945586688> There has been an error: {e}')


# Setup Function
async def setup(client):
    await client.add_cog(TimeSheets(client))