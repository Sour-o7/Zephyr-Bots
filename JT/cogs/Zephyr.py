from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from apiclient import discovery
from google.oauth2 import service_account
import os.path
import os
import json
import valve.source.a2s
import a2s
import requests as req
import discord

class Zephyr(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.STEAM_API_KEY = "D5C92FDA0BE4918C15C85559AF5C2137"
        super().__init__()
        
    # Turn a steamid to a steam community id
    def steamid_to_community_id(self, steamid):
        sid_split = steamid.split(':')
        community_id = int(sid_split[2]) * 2
        if sid_split[1] == '1':
            community_id += 1
        community_id += 76561197960265728
        return community_id
        
    # Turn a steam community id to a steam id
    def community_id_to_steamid(self, community_id):
        steamid = []
        steamid.append('STEAM_0:')
        steamidacct = int(community_id) - 76561197960265728
        if steamidacct % 2 == 0:
            steamid.append('0:')
        else:
            steamid.append('1:')
        steamid.append(str(steamidacct // 2))
        return ''.join(steamid)
        
    # Get all member's rank, name, and steamid
    def get_from_roster(self):
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1GkJSo2-9DeHKAY1gYNJsSI9pjr0FU7WYV-9mb72SG6w'
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("Roster!C:H")).execute().get('values')
        # Return a 2d array where each row contains a string (rank + name) and steamid
        members = [[i[0] + " " + i[2], i[5]] for i in members if len(i) == 6]
        return members
        
    @commands.hybrid_command(name="zephyr")
    async def zephyr(self, ctx: commands.Context):
        # Query zehpyr for online players and send message with amount of players
        with valve.source.a2s.ServerQuerier(self.SERVER_ADDRESS) as server:
            info = server.info()
            try:
                players = server.players()
            except Exception as e:
                print(e)
                players = "Unable to fetch players"
        message = await ctx.send(f"{info['player_count']}/{info['max_players']} {info['server_name']}")

        # If fetching players is unsuccessful
        if players == "Unable to fetch players":
            await message.edit(content=f"{info['player_count']}/{info['max_players']} {info['server_name']}\nUnable to fetch players.")
            return

        # Get all JT SteamIDs
        members = self.get_from_roster()

        online_players = "\nActive JT. (Note: Just because someone is listed here does not mean they are on their whitelist. They are just on Zephyr.)"
        player_names = [player["name"] for player in players["players"]]
        members_community_ids = []
                
        # Loop through members and save their community_ids to members_community_ids
        for member in members:
            try:
                members_community_ids.append(f"{self.steamid_to_community_id(member[1])}")
            except Exception as e:
                continue

        # Check if there is at least 1 online JT
        if members_community_ids:
            # Get steam usernames for members_community_ids
            response = req.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.STEAM_API_KEY}&steamids={','.join(members_community_ids)}")
            response = response.json()

            # Loop through all steam names and add them to online_players if they are on zephyr
            for x in response['response']['players']:
                if x["personaname"] in player_names:
                    online_players = online_players + f'\n{members[[i for x, i in members].index(self.community_id_to_steamid(x["steamid"]))][0]}'

            # If there are no online JT
            if online_players == "\nActive JT. (Note: Just because someone is listed here does not mean they are on their whitelist. They are just on Zephyr.)":
                online_players = "\nNo online JT."

            # Edit message to include online_players
            await message.edit(content=f"{info['player_count']}/{info['max_players']} {info['server_name']}\n{online_players}")

# Setup Function
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Zephyr(client))