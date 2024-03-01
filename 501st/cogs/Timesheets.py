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

con = sl.connect('501st.db', check_same_thread=False)

# Timesheet Class
class TimeSheets(commands.Cog):
    def __init__(self, client) -> None:
        super().__init__()
        self.client = client
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.streak = 0;
        
        # Create Task on client loop
        client.loop.create_task(self.periodic())

    # Periodic Loop
    async def periodic(self):
        while True:
            # Get player count and add 1 to streak if no players
            try:
                info = a2s.info(self.SERVER_ADDRESS)
                if info.player_count == 0:
                    self.streak += 1
                else: 
                    self.streak = 0
            except Exception as e:
                print(e)
            # If player count is 0 for at least 15 minutes
            if self.streak == 4:
                # Check if there are any online 501st and purge database
                members = con.execute("SELECT * FROM i501st_timesheets").fetchone()
                con.execute("DELETE FROM i501st_timesheets")
                con.commit()
                # If there are any online 501st
                if members is not None:
                    await self.client.get_channel(1098311650160939048).send('Zephyr count has been 0 for 15 minutes. Purging Active Timesheets.')
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
    async def update_time(self, author_id, rank_group, time):
        # Google sheets api variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1mUcVHxni-LFqU0YmD-z08tKvlQMhFdw6RHbLyuOpEts'

        # Officers/Lieutenants: B:E
        # NCO: G:J
        # Enlisted: L:O
        
        
        # Get discordid and time
        
        # Name, Rank, Id, Time
        # 0     1     2   3
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=(f"Timesheets!{rank_group}")).execute().get('values')
        members = [[i[2], i[3]] if len(i) == 4 else ([i[2], ''] if len(i) == 3 else ['','']) for i in members]
        
        # Calculate member's row number
        row_number = [n[0] for n in members].index(str(author_id))
        # Add times
        values = [ await self.maths_handler(members[row_number][1], time), ]
        # Variables for request
        range_name = f"Timesheets!{rank_group[-1]}{str(int(row_number) + 1)}"
        values = [values,]
        body = {'values': values}
        # Request Changes
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()

    @commands.hybrid_command(name="ss")
    async def start_shift(self, ctx: commands.Context):
        # If channel is time-log
        if ctx.channel.name == "time-log":
            # Extend response timeframe
            await ctx.defer()
            
            # Check if author is not in database
            author = con.execute(f'SELECT * FROM i501st_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
            if author is None:
                # Add author id into database and current timestamp
                con.execute(f'INSERT INTO i501st_timesheets (id, timestamp) values (?, ?)', (ctx.author.id, int(datetime.now().timestamp())))
                con.commit()
                # Send message
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
                await ctx.send(embed=timesheet)
            else:
                # Overwrite timestamp to current timestamp
                con.execute(f'UPDATE i501st_timesheets SET timestamp=? WHERE id=?', (int(datetime.now().timestamp()), ctx.author.id))
                con.commit()
                # Send Message
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
                await ctx.send(embed=timesheet)
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            
    @commands.hybrid_command(name="es")
    async def end_shift(self, ctx: commands.Context, notes: str = "None"):
        # If channel is not time-log
        if ctx.channel.name != "time-log":
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            return
            
        # Extend response timeframe
        await ctx.defer()
        
        # Check if author is not in database
        author = con.execute(f'SELECT * FROM i501st_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
        if author is None:
            # Send error message - Can't end since none exists
            timesheet = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot end a shift because you don't have one started!")
            await ctx.send(embed=timesheet)
        else:
            author_roles = [x.name for x in ctx.author.roles]
            
            # Get time difference of start shift and now
            time_difference = datetime.now() - datetime.fromtimestamp(author[1])
            author_time = math.floor(time_difference.total_seconds()) // 60
            
            # Delete member from database
            con.execute(f'DELETE FROM i501st_timesheets WHERE id=?', (ctx.author.id,))
            con.commit()
            
            # Send message
            timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>, your shift has ended, it lasted {author_time} minutes!\nNotes: {notes}")
            message = await ctx.send(embed=timesheet)
            
            # Update time
            try:
                if "Higher Ups" in author_roles:
                    await self.update_time(ctx.author.id, "B:E", self.convert_time(author_time))
                elif "Sergeants" in author_roles:
                    await self.update_time(ctx.author.id, "G:J", self.convert_time(author_time))
                elif "Troopers" in author_roles:
                    await self.update_time(ctx.author.id, "L:O", self.convert_time(author_time))
                await message.add_reaction('<:CheckMark:491376406442278914>')
            except Exception as e:
                print(e)
                await message.add_reaction('<:WrongMark:491376501774745633>')
                await ctx.channel.send(f'<@&756275251498844281><@295644243945586688> There has been an error: {e}')
            

# Setup Function
async def setup(client):
    await client.add_cog( TimeSheets(client) )