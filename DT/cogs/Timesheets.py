from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from datetime import datetime
from apiclient import discovery
from google.oauth2 import service_account
from pytz import timezone
import plotly.express as px
import plotly.io as pio
import pandas as pd
import discord
import os.path
import os
import threading
import asyncio
import sqlite3 as sl
import time
import math
import a2s
import io

con = sl.connect('DT.db', check_same_thread=False)
class Timesheets(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
        self.streak = 0;
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.data_dictionary = dict(
        Time = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM", "9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM" ,"11PM"],
        Troopers = [*[0]*24]
        )
        
        client.loop.create_task(self.periodic())
        
    def converttime(self, minutes):
        hour = minutes // 60
        minutes %= 60
        return "%d:%02d" % (hour, minutes)
        
    async def maths_handler(self, a, b):
        if a == "N/A":
            a = "0:0"
        timeList = [a, b]
        totalSecs = 0
        for tm in timeList:
            timeParts = [int(s) for s in tm.split(':')]
            totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60
        totalSecs = divmod(totalSecs, 60)[0]
        hours, minutes = divmod(totalSecs, 60)
        return "%d:%02d" % (hours, minutes)
       
    async def periodic(self):
        while True:
            # Add 1 to streak if player count is 0 otherwise set to 0
            try:
                info = a2s.info(self.SERVER_ADDRESS)
                if info.player_count == 0:
                    self.streak += 1
                else: 
                    self.streak = 0
            except Exception as e:
                print(e)
                pass
            # If server has 0 for at least 15 minutes
            if self.streak == 4:
                # Purge database and send message if someone was online
                members = con.execute("SELECT * FROM deathtrooper_timesheets").fetchone()
                con.execute("DELETE FROM deathtrooper_timesheets")
                con.commit()
                if members is not None:
                    await self.client.get_channel(878075861012717618).send('Zephyr count has been 0 for 15 minutes. Purging Active Timesheets.')
            # Get EST datetime
            time = datetime.now(tz=timezone("US/Eastern"))
            # If the minute is currently between 55 and 60
            if time.minute in range(55, 60):
                # Get DT online and set the count to the hour
                self.data_dictionary["Troopers"][time.hour] = len(con.execute("SELECT * FROM deathtrooper_timesheets").fetchall())
                # If midnight
                if time.hour == 23:
                    # -- Make Graph -- #
                    # Turn Dict to DataFrame
                    scope = pio.kaleido.scope
                    df = pd.DataFrame(self.data_dictionary)
                    # Create Figure from DataFrame
                    fig = px.area(df, x="Time", y="Troopers", title=time.strftime("%#m/%d/%y"), width=1200, height=800)
                    # Update Settings
                    fig.update_layout(
                        margin=dict(l=25, r=20, t=75, b=20),
                        paper_bgcolor="#404240",
                        plot_bgcolor="#515251",
                        font_color="#FFFFFF",
                        font_size=24
                    )
                    # Set Line Colour
                    fig['data'][0]['line']['color']="#008c0c"
                    # Turn Figure to Image Byte Array
                    # Tirm Byte Array into file and output to channel
                    # Send graph and reset times
                    await self.client.get_channel(1005624623230103653).send(file=discord.File(fp=io.BytesIO(fig.to_image(format="png")), filename='graph.png'))
                    self.data_dictionary["Troopers"] = [*[0]*24]
                    scope._shutdown_kaleido()
            await asyncio.sleep(300)
        
    async def roster_update_time(self, member_id, time):
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1zFiOEYIYEKQY_qhAJ_8TtXiucDbYGSTwj_-E8J6HabU'
        # Get DiscordID and time
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!O:AB")).execute().get('values')
        members = [[i[0], i[10], i[11], i[12], i[13]] if (len(i) == 14 and i[0] != "") else ['','', ''] for i in members]
        
        row_number = [n[0] for n in members].index(str(member_id))
        members[row_number][2] = members[row_number][2] if members[row_number][2] != "N/A" else 0
        members[row_number][4] = members[row_number][4] if members[row_number][4] != "N/A" else 0
        # Add time
        values = [[await self.maths_handler(members[row_number][1], time), int(members[row_number][2])+1, await self.maths_handler(members[row_number][3], time), int(members[row_number][4])+1],]
        range_name = f"'Deathtrooper Roster Mk.V'!Y{str(int(row_number) + 1)}:AB{str(int(row_number) + 1)}"
        body = {'values': values}
        # Format cells
        request_body_format = {
            "requests": [
                {
                    # Format Total Time Cell
                    "repeatCell": {
                        "range": {
                        "startRowIndex": row_number,
                        "endRowIndex": row_number + 1,
                        "startColumnIndex": 24,
                        "endColumnIndex": 25
                        },
                        "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                            "type": "DATE",
                            "pattern": "[hh]:mm"
                            }
                        }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    },
                    # Format Monthly Time cell
                    "repeatCell": {
                        "range": {
                        "startRowIndex": row_number,
                        "endRowIndex": row_number + 1,
                        "startColumnIndex": 26,
                        "endColumnIndex": 27
                        },
                        "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                            "type": "DATE",
                            "pattern": "[hh]:mm"
                            }
                        }
                        },
                        "fields": "userEnteredFormat.numberFormat"
                    }
                }
            ]
        }
        # Send Requests
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body_format).execute()
        
    @commands.hybrid_group(name="time")
    async def time_group(self, ctx: commands.Context):
        return

    @time_group.command(name="in")
    async def time_in(self, ctx: commands.Context):
        if ctx.channel.name == "time-logs":
            await ctx.defer()
            # Check if author is in database
            author = con.execute(f'SELECT * FROM deathtrooper_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
            if author is None:
                # Insert into database
                con.execute(f'INSERT INTO deathtrooper_timesheets (id, timestamp) values (?, ?)', (ctx.author.id, int(datetime.now().timestamp())))
                con.commit()
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
                # Send Message
                await ctx.send(embed=timesheet)
            else:
                timesheet = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot start a shift because you already have a running one!")
                await ctx.send(embed=timesheet)
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            
    @time_group.command(name="out")
    async def time_out(self, ctx: commands.Context):
        if ctx.channel.name == "time-logs":
            await ctx.defer()
            # Check if author in database
            author = con.execute(f'SELECT * FROM deathtrooper_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
            if author is None:
                timesheet = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot end a shift because you don't have one started!")
                await ctx.send(embed=timesheet)
            else:
                # Get time time_difference
                time_difference = datetime.now() - datetime.fromtimestamp(author[1])
                time_difference = math.floor(time_difference.total_seconds()) // 60
                # Remove from database
                con.execute(f'DELETE FROM deathtrooper_timesheets WHERE id=?', (ctx.author.id,))
                con.commit()
                # Send Timesheet
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>, your shift has ended, it lasted {time_difference} minutes!")
                message = await ctx.send(embed=timesheet)
                # Update Roster
                try:
                    await self.roster_update_time(ctx.author.id, self.converttime(time_difference))
                    await message.add_reaction('✅')
                except Exception as e:
                    print(e)
                    # If not deathtrooper medic
                    if "Deathtrooper Medic" not in [r.name for r in ctx.author.roles]:
                        await message.add_reaction('❌')
                        await ctx.channel.send(f'<@&504897032335523844><@295644243945586688> There has been an error: {e}')
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            
    @time_group.command(name="list")
    async def time_list(self, ctx: commands.Context):
        # Get everyone from database
        members = con.execute('SELECT * from deathtrooper_timesheets').fetchall()
        # If no online members
        if len(members) == 0:
            await ctx.send("No online DT.")
            return
        # Send message with members    
        members_list = [ctx.guild.get_member(discord_id[0]).display_name for discord_id in members]
        timesheet = discord.Embed(color=0x9B0B0B, title="Online DT", description= "\n".join(members_list))
        await ctx.send(embed=timesheet)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Remove member from database
        member_db = con.execute(f'SELECT * FROM deathtrooper_timesheets WHERE id = ?', (member.id,)).fetchone()
        if member_db is not None:
            con.execute(f'DELETE FROM deathtrooper_timesheets WHERE id=?', (member.id,))
            con.commit()

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Timesheets(client))