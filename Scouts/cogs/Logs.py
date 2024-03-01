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
import re


class Logs(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
    async def log_logs(self, author_id, log_range, rank_group, new_values):
        # Google Sheets API Variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        secret_file = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1BBesk4pnC1wNHUwVDAWwZHKB_paANOB0-uBk2grWaIo'

        # Get range D through M
        ids = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=(rank_group + 'D:M')).execute().get('values')
        # Get range log_range column:column
        append = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=(log_range.replace('$', "")[:-1] + log_range[-5])).execute().get('values')
        append = [''.join([str(elem) for elem in sublist]) for sublist in append]
        # Get name and discordid
        ids = [[x[0],x[9]] for x in ids if len(x) == 10]
        # range = log_range where $ is the row below the end of append
        range_name = log_range.replace('$', str(len(append)+1))
        # Name associated with discordid, current time in EST
        values = [ids[[i[1] for i in ids].index(str(author_id))][0], datetime.now(timezone('US/Eastern')).strftime('%#m/%#d/%Y')]
        # Add new_values to values
        values.extend(new_values)
        # Format for request
        values = [ values, ]
        body = {
            "majorDimension": "ROWS",
            'values': values
        }
        service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name,valueInputOption='USER_ENTERED', body=body).execute()

    # Group for commands
    @commands.hybrid_group(name="log")
    async def log_group(self, ctx: commands.Context) -> None:
        return
        
    @log_group.command(name="tryout")
    async def log_tryout(self, ctx: commands.Context, participants: str, passed: str, steamid: str, supervisor: str = "None", notes: str = "None"):
        # If channel is not scout-logs and not officer-logs
        if ctx.channel.name != "scout-logs" and ctx.channel.name != "officer-logs":
            await ctx.send('Please use the correct channel.', ephemeral = True)
            return

        # Extend response timeframe
        await ctx.defer()

        author_roles = [x.name for x in ctx.author.roles]
        # Set attended to true if someone attended
        if participants.lower() == "none" or participants.lower() == "n/a" or participants.lower() == "0":
            attended = False
        else:
            attended = True
        # Send Message and update roster if author has permission
        try:
            if "Scout Officer" in author_roles or "Scout Lieutenant" in author_roles or "Scout Commander" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nActivity: Tryout\nParticipants: {participants}\nPassed: {passed}\nSteamID(s): {steamid}\nNotes: {notes}\nSupervisor: {supervisor}")
                await self.log_logs(ctx.author.id, 'Logs!A$:C$', "Officer Roster!", [str(attended)])
            elif "Officer In Training" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nActivity: Tryout\nParticipants: {participants}\nPassed: {passed}\nSteamID(s): {steamid}\nNotes: {notes}\nSupervisor: {supervisor}")
                await self.log_logs(ctx.author.id, 'Logs!A$:C$', "SGT Roster!", [str(attended)])
            else:
                await ctx.send("Invalid Permissions!", ephemeral=True)
        except Exception as e:
            await ctx.channel.send(f'An error has occurred. {e}')
        
    @log_group.command(name="ptsim")
    async def log_PTSIM(self, ctx: commands.Context, activity: str, participants: str, promotions: str='None'):
        # If channel is not scout-logs and not officer-logs
        if ctx.channel.name != "scout-logs" and ctx.channel.name != "officer-logs":
            await ctx.send('Please use the correct channel.', ephemeral = True)
            return

        # Extend response timeframe
        await ctx.defer()

        author_roles = [x.name for x in ctx.author.roles]
        # Send Message and update roster if author has permission
        try:
            if "Scout Officer" in author_roles or "Scout Lieutenant" in author_roles or "Scout Commander" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nActivity: {activity}\nParticipants: {participants}\nPromotions: {promotions}")
                await self.log_logs(ctx.author.id, 'Logs!D$:G$', "Officer Roster!", [activity,"TRUE"])
            elif "Scout Sergeant" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nActivity: {activity}\nParticipants: {participants}\nPromotions: {promotions}")
                await self.log_logs(ctx.author.id, 'Logs!D$:G$', "SGT Roster!", [activity,"TRUE"])
            else:
                await ctx.send("Invalid Permissions!", ephemeral=True)
        except Exception as e:
            await ctx.channel.send(f'An error has occurred. {e}')
            
    @log_group.command(name="other")
    async def log_other(self, ctx: commands.Context, logtype: str, line1: str, line2: str, line3: str):
        # If channel is not scout-logs and not officer-logs
        if ctx.channel.name != "scout-logs" and ctx.channel.name != "officer-logs":
            await ctx.send('Please use the correct channel.', ephemeral = True)
            return
        # Extend response timeframe
        await ctx.defer()
        
        author_roles = [x.name for x in ctx.author.roles]
        # Send Message and update roster if author has permission
        try:
            if "Scout Officer" in author_roles or "Scout Lieutenant" in author_roles or "Scout Commander" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nLog Type: {logtype}\n{line1}\n{line2}\n{line3}")
                await self.log_logs(ctx.author.id, 'Logs!K$:M$', "Officer Roster!", [logtype])
            elif "Scout Sergeant" in author_roles:
                await ctx.send(f"Name: <@{ctx.author.id}>\nLog Type: {logtype}\n{line1}\n{line2}\n{line3}")
                await self.log_logs(ctx.author.id, 'Logs!K$:M$', "SGT Roster!", [logtype])
            else:
                await ctx.send(f"Name: <@{ctx.author.id}>\nLog Type: {logtype}\n{line1}\n{line2}\n{line3}")
                await self.log_logs(ctx.author.id, 'Logs!K$:M$', "Enlisted Roster!", [logtype])
        except Exception as e:
            await ctx.channel.send(f'An error has occurred. {e}')

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Logs(client))