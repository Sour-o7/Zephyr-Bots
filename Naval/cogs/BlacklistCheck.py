from __future__ import print_function
from discord.ext import commands
from apiclient import discovery
from google.oauth2 import service_account
from discord.ext import commands
import discord
import os.path
import os
import re

class BlackListCheck(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'naval_keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes = scopes)
        self.service = discovery.build('sheets', 'v4', credentials = credentials)
        
    async def fetch_blacklists(self):
        spreadsheet_id = '11Dg2XJ6V9B1Vct3tAiy5Cak6Hdt0pn1RWpcDcrGhqmI'
        
        # Get Non-Revoked Naval Blacklists
        naval_blacklists = self.service.spreadsheets().values().get(spreadsheetId = spreadsheet_id, range = "'Naval Blacklist'!B:N").execute().get('values')
        naval_blacklists = list(filter(None, naval_blacklists))
        naval_blacklists = [x[1][4] for x in enumerate(naval_blacklists) if x[1][12] != "REVOKED"]
        
        # Get Accepted Shock Blacklists
        shock_blacklists = self.service.spreadsheets().values().get(spreadsheetId = spreadsheet_id, range = "'SHOCK Blacklist'!B:N").execute().get('values')
        shock_blacklists = list(filter(None, shock_blacklists))   
        shock_blacklists = [x[1][4] for x in enumerate(shock_blacklists) if x[1][12] == "Accepted"]

        # Combine blacklists and remove duplicates
        both = naval_blacklists + shock_blacklists
        output = []
        [output.append(x) for x in both if x not in output]
        
        return output

    @commands.Cog.listener()
    async def on_message(self, message):
        # If sent message is from a bot
        if message.author.bot:
            return
        # If Channel is tryout-log
        if message.channel.name == "tryout-log":
            # Get blacklists from fetch_blacklists
            blacklists = await self.fetch_blacklists()
            # Get SteamIDs from message
            SteamIDs = re.findall("STEAM_0:.:\d+", message.content)
            # Check if there are any blacklisted steamids
            flagged = [x for x in SteamIDs if x in blacklists]
            if flagged:
                # Send Message
                await message.channel.send(f'<@{message.author.id}> {", ".join(flagged)} is marked as blacklisted! Please verify this information before continuing!')

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(BlackListCheck(client))