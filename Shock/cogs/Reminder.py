from __future__ import print_function
from discord.ext import commands
from discord.utils import get
from apiclient import discovery
from google.oauth2 import service_account
import sqlite3 as sl
import discord
import a2s
import asyncio
import os.path
import os
import json
import valve.source.a2s
import requests as req
import re

con = sl.connect('Shock.db', check_same_thread=False)

class MemberIds():
    def __init__(self, community, discord):
        self.comm = str(community)
        self.discord = discord
        
    def __str__(self):
        return self.comm

# Reminder Class
class Reminder(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        self.SERVER_ADDRESS = ('208.103.169.68', 27015)
        self.STEAM_API_KEY = "D5C92FDA0BE4918C15C85559AF5C2137"
        self.to_alert = []
        self.alerted_players = []
        super().__init__()
        
        # Create periodic loop
        self.client.loop.create_task(self.periodic())
        
    # Turn a steamid to a steam community id
    def steamid_to_community_id(self, steamid):
        sid_split = steamid.split(':')
        community_id = int(sid_split[2]) * 2
        if sid_split[1] == '1':
            community_id += 1
        community_id += 76561197960265728
        return community_id
        
    # Get all member steamids
    def get_from_roster(self):
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        service = discovery.build('sheets', 'v4', credentials=credentials)
        spreadsheet_id = '1SJWjZaCGtXs346Xjmm0Z6UCxJVNTOWr79LQYpjCZObg'
        members = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=("'Shock Roster'!D:E")).execute().get('values')
        
        members = [i for i in members if len(i) == 2]
        
        members = [i for i in members if re.search("STEAM_0:.:\d+", i[0])]
        
        return members
        
    async def periodic(self):
        while True:
            # Query zehpyr for online players and send message with amount of players
            with valve.source.a2s.ServerQuerier(self.SERVER_ADDRESS) as server:
                try:
                    players = server.players()
                except Exception as e:
                    print(e)
                    continue

            if len(players["players"]) < 10:
                await asyncio.sleep(600)
                continue

            members = self.get_from_roster()
            player_names = [player["name"] for player in players["players"]]
            member_ids = []
            
            for member in members:
                try:
                    member_ids.append(MemberIds(self.steamid_to_community_id(member[0]), member[1]))
                except Exception as e:
                    continue

            try:
                response = req.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={self.STEAM_API_KEY}&steamids={','.join([str(x) for x in member_ids])}")
                response = response.json()
            except Exception:
                continue                

            timed_in = con.execute("SELECT id FROM shock_timesheets").fetchall()
            timed_in = [str(x[0]) for x in timed_in]
            

            online_shock = [x["steamid"] for x in response['response']['players'] if x["personaname"] in player_names]
            online_discord = []
            
            for shock in online_shock:
                discord_id = [i.discord for i in member_ids if i.comm == shock][0]
                online_discord.append(discord_id)

            # Loop Though To Alert
            for discord_id in self.to_alert:
                # Check if user is not online
                if discord_id not in online_discord:
                    self.to_alert.remove(discord_id)
                # Check if user is timed in
                elif discord_id in timed_in:
                    self.to_alert.remove(discord_id)
                    self.alerted_players.append(discord_id)
                    
            # Loop though alerted plyers
            for discord_id in self.alerted_players:
                # Check if user is not online
                if discord_id not in online_discord:
                    self.alerted_players.remove(discord_id)

            if len(self.to_alert) != 0:
                chnl = await self.client.fetch_channel(922226592263057428)
                await chnl.send(f"{''.join([f'<@{x}>' for x in self.to_alert])} Reminder: You are not timed in! If you are not on your shock job, please ignore this.")

            self.alerted_players += self.to_alert
            self.to_alert.clear()

            # Loop through online discord
            for discord_id in online_discord:
                # Ensure user is not already alerted
                if discord_id not in self.alerted_players:
                    # Add user to alerted if they are timed in and online
                    if discord_id in timed_in and discord_id in online_discord:
                        self.alerted_players.append(discord_id)
                    # Alert user if they have not opt-ed out
                    #elif discord.utils.get(ctx.guild.roles, name="Deathtrooper Secretary") in not ctx.author.roles:
                    else:
                        self.to_alert.append(discord_id)

            await asyncio.sleep(600)
        
# Button Class
class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='xxxx', style=discord.ButtonStyle.grey, custom_id='optOut')
    async def OptedOut(self, interaction: discord.Interaction, button: discord.ui.Button):
        # If user has "xxxx"
        if discord.utils.get(interaction.guild.roles, name="xxxx") in interaction.user.roles:
            # Remove role and send message
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="xxxx"))
            await interaction.response.send_message(content="Removed the `xxxx` Role!", ephemeral = True)
            return
        # Else add role and send message
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name="xxxx"))
        await interaction.response.send_message(content="Gave you the `xxxx` role!", ephemeral = True)

# Setup Function
async def setup(client):
    await client.add_cog(Reminder(client))
#    client.add_view(PersistentView())