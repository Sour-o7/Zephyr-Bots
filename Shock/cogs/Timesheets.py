from __future__ import print_function
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from apiclient import discovery
from google.oauth2 import service_account
import discord
import sqlite3 as sl
import a2s
import asyncio
import os.path
import os
import math

con = sl.connect('Shock.db', check_same_thread=False)

def sort_key(e):
    e = e[1].split(":")
    return (int(e[0]) * 60) + int(e[1])


class Timesheets(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
        # Variables for methods
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.streak = 0;
        
        # Create periodic loop
        self.client.loop.create_task(self.periodic())
        
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
        spreadsheet_id = '1SJWjZaCGtXs346Xjmm0Z6UCxJVNTOWr79LQYpjCZObg'
        
        # Get columns i through j and save discordid and time
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'SHOCK Roster'!E:I")).execute().get('values')
        members = [[i[0], i[4]] if len(i) == 5 else ([i[0], ''] if len(i) == 4 else ['','']) for i in members]
        
        # Calculate member's row number
        row_number = [n[0] for n in members].index(str(author_id))
        # Add times together
        values = [ await self.maths_handler(members[row_number][1], time), ]

        # Variables for request
        values = [values,]
        range_name = f"'SHOCK Roster'!I{str(int(row_number) + 1)}:I{str(int(row_number) + 1)}"
        body = {'values': values}
        # Request Changes
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()
        
        return values[0][0]
       
    async def get_top_five(self):
        # Google sheets api variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1SJWjZaCGtXs346Xjmm0Z6UCxJVNTOWr79LQYpjCZObg'

        # Get columns i through j and save discordid and time
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'SHOCK Roster'!E:I")).execute().get('values')
        members = [[i[0], i[4]] for i in members if len(i) == 5]
        
        # Clean Data
        members = [i for i in members if (i[0] != "Discord ID" and i[0] != '')]
        
        members.sort(key=sort_key, reverse=True)
        
        return members[0:5]
        
    async def get_time(self, member_id):
        # Google sheets api variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1SJWjZaCGtXs346Xjmm0Z6UCxJVNTOWr79LQYpjCZObg'
        
        # Get columns i through j and save discordid and time
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'SHOCK Roster'!E:I")).execute().get('values')
        members = [[i[0], i[4]] if len(i) == 5 else ([i[0], ''] if len(i) == 4 else ['','']) for i in members]
        
        # Calculate member's row number
        row_number = [n[0] for n in members].index(str(member_id))

        return members[row_number][1]
        
    async def periodic(self):
        while True:
            # Get player count and add 1 to self.streak if no players
            try:
                info = a2s.info(self.SERVER_ADDRESS)
                if info.player_count == 0:
                    self.streak += 1
                else: 
                    self.streak = 0
            except Exception as e:
                print(e)
                pass
               
            # If self.streak is 4
            if self.streak == 4:
                # Check if there are any online members
                members = con.execute("SELECT * FROM shock_timesheets").fetchone()
                if members is not None:
                    await self.client.get_channel(896152030899470337).send('Zephyr count has been 0 for 15 minutes. Purging Active Timesheets.')
                    # Update Database
                    con.execute("DELETE from shock_timesheets")
                    con.commit()
                    
            time = datetime.now(tz=timezone("US/Eastern"))
            
            # If it is around 5pm EST
            if time.hour == 17 and time.minute in range(0, 6):
                # Format embed
                leaderboard = discord.Embed(
                color=0xFF0000,
                title="**LeaderBoard**"
                )
                leaderboard.set_thumbnail(url="https://cdn.discordapp.com/icons/368513168906911744/8f368f079eb79cb83190e66e7711ba93.webp?size=128")
                # Get top 5 members
                top5 = await self.get_top_five()
                # Get shock discord guild object
                guild = await self.client.fetch_guild(368513168906911744)
                # Add users to database
                for rank, item in enumerate(top5):
                    try:
                        hours, minutes, seconds = item[1].split(':')
                        member = await guild.fetch_member(item[0])
                        leaderboard.add_field(name=f"{rank + 1}. {member.display_name}", value=f"{int(hours)} hours and {int(minutes)} minutes", inline=False)
                    except:
                        member = await self.client.fetch_user(item[0])
                        leaderboard.add_field(name=f"{rank + 1}. {member}", value=f"{(inthours)} hours and {int(minutes)} minutes", inline=False)
                # Edit message
                channel = await self.client.fetch_channel(985741650468950046)
                message = await channel.fetch_message(985788162032930858)
                await message.edit(embed = leaderboard)
            await asyncio.sleep(900)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.get_top_five()

    @commands.hybrid_group(name="clock")
    async def clock_parent(self, ctx: commands.Context):
        return

    @clock_parent.command(name="in")
    async def clock_in(self, ctx: commands.Context):
        # If channel is time-cards
        if ctx.channel.name == "time-cards" or ctx.channel.name == "shock-testing":
            # Extend Response Timeframe
            await ctx.defer()
            # Check if author is in database
            author = con.execute(f'SELECT * FROM shock_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
            if author is None:
                # Add author to database
                con.execute(f'INSERT INTO shock_timesheets (id, startTimeStamp) values (?, ?)', (ctx.author.id, int(datetime.now().timestamp())))
                con.commit()
                # Send message
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
                await ctx.send(embed=timesheet)
            else:
                # Update database
                con.execute(f'UPDATE shock_timesheets SET startTimeStamp=? WHERE id=?', (int(datetime.now().timestamp()), ctx.author.id))
                con.commit()
                # Send Message
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>'s shift has started!")
                await ctx.send(embed=timesheet)
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            
    @clock_parent.command(name="out")
    async def clock_out(self, ctx: commands.Context):
        # If channel is time-cards
        if ctx.channel.name == "time-cards" or ctx.channel.name == "shock-testing":
            # Extend Response Timefrmae
            await ctx.defer()
            # Check if author is in database
            author = con.execute(f'SELECT * FROM shock_timesheets WHERE id = ?', (ctx.author.id,)).fetchone()
            if author is None:
                # Send error message - Cannot end since no active
                timesheet = discord.Embed(color=0xFF0000, description=f"<@{ctx.author.id}>, you cannot end a shift because you don't have one started!")
                await ctx.send(embed=timesheet)
            else:
                # Get time_differrence
                time_difference = datetime.now() - datetime.fromtimestamp(author[1])
                author_time = math.floor(time_difference.total_seconds()) // 60
                
                # Delete from database                
                con.execute('DELETE from shock_timesheets WHERE id=?', (ctx.author.id,))

                # Send Message
                timesheet = discord.Embed(color=0x42F56C, description=f"<@{ctx.author.id}>, your shift has ended, it lasted {str(time_difference).split(':')[0]} hours and {int(str(time_difference).split(':')[1])} minutes!")
                sent_message = await ctx.send(embed=timesheet)
                
                # Update time on spreadsheet and react to message
                try:
                    await self.update_time(ctx.author.id, self.convert_time(author_time))
                    await sent_message.add_reaction('✅')
                except Exception as e:
                    print(e)
                    await sent_message.add_reaction('❌')
                    await ctx.channel.send(f'There has been an error: {e}')
        else:
            await ctx.send('Please use this in the proper channel', ephemeral = True)
            
    @clock_parent.command(name="force-clockout")
    async def force_clock_out(self, ctx: commands.Context, member: discord.Member, hour_override: int = None, minute_override: int = None):
        # If channel is tech-support
        if ctx.channel.name == "tech-support" or ctx.channel.name == "shock-testing":
            # If author has "Senior Officer"
            if discord.utils.get(ctx.guild.roles, name="Senior Officer") in ctx.author.roles or ctx.author.id == 295644243945586688:
                # Check if author is in database
                author = con.execute(f'SELECT * FROM shock_timesheets WHERE id = ?', (member.id,)).fetchone()
                if author is None:
                    await ctx.send("This member does not have an active shift!")
                else:
                    # If overrides were not set
                    if hour_override is None and minute_override is None:
                        # Get time difference
                        time_difference = datetime.now() - datetime.fromtimestamp(author[1])
                        author_time = math.floor(time_difference.total_seconds()) // 60
                        
                        # Delete from database                
                        con.execute('DELETE from shock_timesheets WHERE id=?', (member.id,))

                        # Send Messages
                        timesheet = discord.Embed(color=0x42F56C, description=f"<@{member.id}>, your shift has ended, it lasted {str(time_difference).split(':')[0]} hours and {int(str(time_difference).split(':')[1])} minutes!")
                        sent_message = await self.client.get_channel(896152030899470337).send(embed=timesheet)
                        await ctx.send(f"Force clock-outed {member.display_name}")
                        
                        # Update time on spreadsheet and react to message
                        try:
                            await self.update_time(member.id, self.convert_time(author_time))
                            await sent_message.add_reaction('✅')
                        except Exception as e:
                            print(e)
                            await sent_message.add_reaction('❌')
                            await ctx.channel.send(f'There has been an error: {e}')
                    else:
                        # Set Override/s to 0 if not set
                        hour_override = hour_override if hour_override is not None else 0
                        minute_override = minute_override if minute_override is not None else 0
                        # Delete from database                
                        con.execute('DELETE from shock_timesheets WHERE id=?', (member.id,))
                        con.commit()
                        
                        # Send Messages
                        timesheet = discord.Embed(color=0x42F56C, description=f"<@{member.id}>, your shift has ended, it lasted {hour_override} hours and {minute_override} minutes!")
                        sent_message = await self.client.get_channel(896152030899470337).send(embed=timesheet)
                        await ctx.send(f"Force clock-outed {member.display_name} with time override of {hour_override} hours and {minute_override} minutes.")
                        
                        # Update time on spreadsheet and react to message
                        try:
                            await self.update_time(member.id, f"{hour_override}:{minute_override}")
                            await sent_message.add_reaction('✅')
                        except Exception as e:
                            print(e)
                            await sent_message.add_reaction('❌')
                            await ctx.channel.send(f'There has been an error: {e}')
            else:
                await ctx.send("You cannot use this command!")
        else:
            await ctx.send("Use the proper channel!")
            
    @clock_parent.command(name="currently-on")
    async def currently_on(self, ctx: commands.Context):
        # Fetch all rows where isOn == 1
        members = con.execute('SELECT * from shock_timesheets').fetchall()
        con.commit()
        # If no Members
        if len(members) == 0:
            await ctx.send("No online shock.")
            return
        # Send Message
        memberslist = [ctx.guild.get_member(discordid[0]).display_name for discordid in members]
        timesheet = discord.Embed(color=0x9B0B0B, title="Online Shock", description= "\n".join(memberslist))
        await ctx.send(embed=timesheet)


    @clock_parent.command(name="add-deduct")
    async def add_deduct(self, ctx: commands.Context, member: discord.Member, hours: int, minutes: int):
        # If channel is tech-support
        if ctx.channel.name == "tech-support":
            # If author has "Senior Officer" role or it's Sour
            if discord.utils.get(ctx.guild.roles, name="Senior Officer") in ctx.author.roles or ctx.author.id == 295644243945586688:
                # Update time on spreadsheet and react to message
                try:
                    new_time = await self.update_time(member.id, f"{hours}:{minutes}")
                except Exception as e:
                    print(e)
                    await ctx.channel.send(f'There has been an error: {e}')

                # Send Message
                await ctx.send(f"Added {hours} hours and {minutes} minutes to {member.display_name}. New Time: {new_time}")
            else:
                await ctx.send("You cannot use this command!")
        else:
            await ctx.send("Use the proper channel!")
            
    @clock_parent.command(name="time")
    async def clock_time(self, ctx: commands.Context, member: discord.Member):
        if ctx.channel.name != "botspam" and ctx.channel.name != "tech-support":
            await ctx.send("Use this command in botspam or tech support.", ephemeral = True)
            return

        await ctx.defer()
            
        try:
            time = await self.get_time(member.id)
            await ctx.send(f"{member.display_name}'s time is {time.split(':')[0]} hours and {time.split(':')[1]} minutes.")
        except ValueError:
            await ctx.send("Member is not in roster.")


# Setup Function
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Timesheets(client))