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

class Roster(commands.GroupCog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

        # Dictionaries

        self.rank_dictionary = {
            'Colonel':              ["Deathtrooper N.C.O.", "Deathtrooper Officer", "Colonel"],
            'Lieutenant Colonel':   ["Deathtrooper N.C.O.", "Deathtrooper Officer", "Lieutenant Colonel"],
            'Major':                ["Deathtrooper N.C.O.", "Deathtrooper Officer", "Major"],
            'Captain':              ["Deathtrooper N.C.O.", "Deathtrooper Officer", "Captain"],
            '1st Lieutenant':       ["Deathtrooper N.C.O.", "Deathtrooper Officer", "1st Lieutenant"],
            '2nd Lieutenant':       ["Deathtrooper N.C.O.", "Deathtrooper Officer", "2nd Lieutenant"],
            'Sergeant Major':       ["Deathtrooper N.C.O.", "Sergeant Major"],
            'Master Sergeant':      ["Deathtrooper N.C.O.", "Master Sergeant"],
            'Sergeant First Class': ["Deathtrooper N.C.O.", "Sergeant First Class"],
            'Staff Sergeant':       ["Deathtrooper N.C.O.", "Staff Sergeant"],
            'Sergeant':             ["Deathtrooper N.C.O.", "Sergeant"],
            'Corporal':             ["Corporal"],
            'Lance Corporal':       ["Lance Corporal"],
            'Private First Class':  ["Private First Class"],
            'Private':              ["Private", "Battalion Applicant"],
            'Trainee':              []
        }
        # Rank: [Max Promotion Rank, Demotion Perms (Aka 2LT+), Tryout Perms, Revoke Blacklist Perms]
        self.rank_permissions = {
            "Commander":                        ["Colonel",               True,  True,  True],
            "Colonel":                          ["Colonel",               True,  True,  True],
            "Deathtrooper Astromech Developer": ["Lieutenant Colonel",    True,  True,  True],
            "Lieutenant Colonel":               ["Captain",               True,  True,  True],
            "Major":                            ["1st Lieutenant",        True,  True,  False],
            "Captain":                          ["Sergeant Major",        True,  True,  False],
            "1st Lieutenant":                   ["Master Sergeant",       True,  True,  False],
            "2nd Lieutenant":                   ["Sergeant First Class",  True,  True,  False],
            "Sergeant Major":                   ["Corporal",              False, True,  False],
            "Master Sergeant":                  ["Lance Corporal",        False, True,  False],
            "Sergeant First Class":             ["Private First Class",   False, False, False]
        }

        self.dt_roles = ["Deathtrooper Officer", "Deathtrooper N.C.O.", "Deathtrooper Enlisted", "Event Notifications", "Activity Notifications", "Report Notifications", "Tryout Supervision Program", "(VII) Director", "(VI) Chief", "(V) Warrant Officer", "(IV) Petty Officer", "(III) Veteran Agent", "(II) Agent", "(I) Probationary Agent",  "Flight Trained", "E.B.D.", "D.N.P.", "Leave Of Absence"]
        self.dt_roles_wildcard = ["B.B.", "X.B.", "E.B.", "Battalion", "Purge", "Probation", "Instructor"]
        # Todo: Battalion Roles
        
        self.battalion_ranks = {
            'P.A. (I)':     ["(I) Probationary Agent", "$ Enlisted"],
            'A. (II)':      ["(II) Agent",             "$ Enlisted"],
            'V.A. (III)':   ["(III) Veteran Agent",    "$ Enlisted"],
            'P.O. (IV)':    ["(IV) Petty Officer",     "$ Enlisted", "$ Officer"],
            'W.O. (V)':     ["(V) Warrant Officer",    "$ Enlisted", "$ Officer"],
            'C. (VI)':      ["(VI) Chief",             "$ Enlisted", "$ Officer", "$ High Command"],
            'D. (VII)':     ["(VII) Director",         "$ Enlisted", "$ Officer", "$ High Command"],
            'V.B.O. (VII)': [],
            'B.O. (VIII)':  [],
            'C.B.O. (IX)':  [],
            'N/A':          []
        }
        
        self.battalion_acronyms = {
            'B.B.': 'Beskar Battalion',
            'X.B.': 'Xonolite Battalion',
            'N/A': 'N/A',
            'C.B.': 'N/A',
            'V.B.': 'N/A',
            'B.O.': 'N/A'
        }
        
        # Roster Variables
        scopes = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/spreadsheets"]
        tokens = os.path.join(os.getcwd(), 'keys.json')
        credentials = service_account.Credentials.from_service_account_file(tokens, scopes=scopes)
        self.service = discovery.build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = '1zFiOEYIYEKQY_qhAJ_8TtXiucDbYGSTwj_-E8J6HabU'
        

#                            #
#   Roster Update Methods    #
#                            #
        
    def roster_enlist(self, member_id, member_name, member_steamid):
        
        # Calcuate destination
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!D:AB")).execute().get('values')
        row_number = [[n[0], n[1]] if len(n) >= 2 else ["", ""] for n in members].index(["","Trainee"])
        # Unhide row
        request_bodyf = {
            "requests": [
                {
                    'updateDimensionProperties': {
                        "range": {
                        "dimension": 'ROWS',
                        "startIndex": row_number,
                        "endIndex": row_number + 1,
                        },
                        "properties": {
                        "hiddenByUser": False,
                        },
                        "fields": 'hiddenByUser',
                    }
                }
            ],
        }
        # Fill values
        request_bodyv = {
            'valueInputOption': 'RAW',
            "data": [
                {
                    "range": f"'Deathtrooper Roster Mk.V'!D{row_number + 1}:AB{row_number + 1}",
                    "values": [
                        [member_name, "Trainee", "N/A", "N/A", datetime.now(timezone('US/Eastern')).strftime("%#d/%#m/%Y"), datetime.now(timezone('US/Eastern')).strftime("%#d/%#m/%Y"), "A", "", "", member_steamid, member_steamid, str(member_id), *[""] * 4, *["N/A"] * 9]
                    ],
                }
            ],
        }
        # Requests
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_bodyv).execute()    
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_bodyf).execute()        
        
    def roster_remove(self, member_id, reason):
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!D:AB")).execute().get('values')
        row_number = [n[11] if len(n) >= 12 else "" for n in members].index(str(member_id))
        before = members[row_number][1]
        end_row = [n[1] if len(n) >= 2 else "" for n in members]
        end_row = [index for index, value in enumerate(end_row) if value == before]
        # Hide row
        request_body_format = {
            "requests": [
                {
                    'updateDimensionProperties': {
                        "range": {
                        "dimension": 'ROWS',
                        "startIndex": row_number,
                        "endIndex": row_number + 1,
                        },
                        "properties": {
                        "hiddenByUser": True,
                        },
                        "fields": 'hiddenByUser',
                    }
                }
            ],
        }
        # Fill row will blank values
        request_body_value = {
            'valueInputOption': 'USER_ENTERED',
            "data": [
                {
                    "range": f"'Deathtrooper Roster Mk.V'!D{row_number + 1}:AB{row_number + 1}",
                    "values": [
                        ["", before, *[""] * 23]
                    ],
                }
            ],
        }
        # Add Name, Rank, SteamID, DiscordID, Reason, and Date for "Purge and Removal List"
        request_body_value_removal = {
            "majorDimension": "ROWS",
            "values": [
                [members[row_number][0], members[row_number][1], members[row_number][9], members[row_number][11], reason, datetime.now(timezone('US/Eastern')).strftime("%#d/%#m/%Y")]
            ],
        }
        # If row is not at the bottom, move to bottom
        if end_row[-1] != row_number:
            request_body_format["requests"].append({
                "moveDimension": {
                    "source": {
                    "dimension": "ROWS",
                    "startIndex": row_number,
                    "endIndex": row_number+1
                    },
                    "destinationIndex": end_row[-1]+1
                }
            })
        # Requests
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()    
        self.service.spreadsheets().values().append(spreadsheetId=self.spreadsheet_id, range="'Purge and Removal List Mk.V'!D27:I66", valueInputOption="USER_ENTERED", body=request_body_value_removal).execute()
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_format).execute()
        # Return SteamID and Rank
        return members[row_number][9], members[row_number][1]        

    def roster_promotion_demotion(self, member_id, rank, is_demotion = False):
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!D:AB")).execute().get('values')
        row_number = [n[11] if len(n) >= 12 else "" for n in members].index(str(member_id))
        before = members[row_number][1]
        try:
            destination_index = [[n[0], n[1]] if len(n) >= 2 else "" for n in members].index(["", rank])
        except ValueError:
            raise Exception("Not Enough Space")
            return
        end_row = [n[1] if len(n) >= 2 else "" for n in members]
        end_row = [idx for idx, val in enumerate(end_row) if val == before]
        request_body_format = {
            "requests": [
                # Set empty note value
                {
                    "updateCells": {
                        "range": {
                            "startRowIndex": row_number,
                            "endRowIndex": row_number + 1,
                            "startColumnIndex": 8,
                            "endColumnIndex": 9
                        },
                        "rows": [
                            {
                                "values": [
                                    {
                                        "note": ""
                                    }
                                ]
                            }
                        ],
                        "fields": "note"
                    }
                },                
                # Hide old row
                {
                    'updateDimensionProperties': {
                        "range": {
                        "dimension": 'ROWS',
                        "startIndex": row_number,
                        "endIndex": row_number + 1,
                        },
                        "properties": {
                        "hiddenByUser": True,
                        },
                        "fields": 'hiddenByUser',
                    }
                },
                # Unhide new row
                {
                    'updateDimensionProperties': {
                        "range": {
                        "dimension": 'ROWS',
                        "startIndex": destination_index,
                        "endIndex": destination_index + 1,
                        },
                        "properties": {
                        "hiddenByUser": False,
                        },
                        "fields": 'hiddenByUser',
                    }
                }
            ],
        }
        request_body_value = {
            'valueInputOption': 'USER_ENTERED',
            "data": [
                # Set old row to empty strings
                {
                    "range": f"'Deathtrooper Roster Mk.V'!D{row_number + 1}:AB{row_number + 1}",
                    "values": [
                        ["",before, *[""]*23]
                    ],
                },
                # Transfer old data to new row
                {
                    "range": f"'Deathtrooper Roster Mk.V'!D{destination_index + 1}:AB{destination_index + 1}",
                    "values": [
                        members[row_number]
                    ],
                },
                # Update rank and promotion date
                {
                    "range": f"'Deathtrooper Roster Mk.V'!D{destination_index + 1}:I{destination_index + 1}",
                    "values": [
                        [members[row_number][0], rank, *members[row_number][2:5], datetime.now(timezone('US/Eastern')).strftime("%#d/%#m/%Y")]
                    ],
                }
            ],
        }
        # If row is not at bottom, move to bottom
        if end_row[-1] != row_number:
            request_body_format["requests"].append({
                "moveDimension": {
                    "source": {
                    "dimension": "ROWS",
                    "startIndex": row_number,
                    "endIndex": row_number + 1
                    },
                    "destinationIndex": end_row[-1]+1
                }
            })
        # If demotion, add demotion note
        if is_demotion:
            request_body_format["requests"].append({
                "updateCells": {
                    "range": {
                        "startRowIndex": destination_index,
                        "endRowIndex": destination_index + 1,
                        "startColumnIndex": 8,
                        "endColumnIndex": 9
                    },
                    "rows": [
                        {
                            "values": [
                                {
                                    "note": "Demotion Date"
                                }
                            ]
                        }
                    ],
                    "fields": "note"
                }
            })
        # Requests
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_format).execute()

    def roster_battalion_promotion_demotion(self, member, rank, battalion):
        #SLASH COMMAND SHOULD HAVE OPTIONS NOT ROLE SELECT RESPONSE WILL BE IN "Acronym : Role" ID FORMAT
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Deathtrooper Roster Mk.V'!D:O")).execute().get('values')
        row_number = [n[11] if len(n) >= 12 else "" for n in members].index(str(member.id))
        member_roles = ":".join([x.name for x in member.roles])
        member_rank_list = re.findall("\([IXV]+\)[^:]+", member_roles)
        output = f"{battalion}{rank}"
        print(member_roles)
        print(member_rank_list)
        # Check if member is a battalion overseer
        if "Overseer" in member_rank_list:
            if "(IX) Chief Battalion Overseer" in member_rank_list:
                output += " | C.B.O. (IX)"
            elif "(VIII) Battalion Overseer" in member_rank_list:
                output += " | B.O. (VIII)" 
            elif "(VII) Vice Battalion Overseer" in member_rank_list:
                output += " | V.B.O. (VII)"

        # If member in no battalion
        elif rank == "N/A" or battalion == "N/A":
            output = "N/A"
        # Update cell
        request_body_value = {
            'valueInputOption': 'RAW',
            "data": [
                {
                    "range": f"'Deathtrooper Roster Mk.V'!F{row_number+1}:F{row_number+1}",
                    "values": [
                        [output]
                    ],
                }
            ],
        }
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()
        # Return Old Battalion
        return members[row_number][2].split(" | ")[0]
    
    def roster_update_user_into(self, member_id, info_type, value):
        #INFO TYPE SHOULD BE ROSTER COLUMN
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=(f"'Deathtrooper Roster Mk.V'!D:O")).execute().get('values')
        column_to_number = {'D': 0, 'M': 9, 'O': 11}
        row_number = [n[11] if len(n) >= 12 else "" for n in members].index(str(member_id))
        print(row_number)
        print(info_type)
        # Set cell to value
        request_body_value = {
            'valueInputOption': 'RAW',
            "data": [
                {
                    "range": f"'Deathtrooper Roster Mk.V'!{info_type.split(':')[0]}{row_number + 1}:{info_type.split(':')[0]}{row_number + 1}",
                    "values": [
                        [value]
                    ],
                }
            ],
        }
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()
        # Return old value
        return members[row_number][column_to_number[info_type.split(':')[0]]]
    
    def roster_add_blacklist(self, member_id, name, steamid, reason):
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=(f"'Blacklists Mk.V'!D:H")).execute().get('values')
        destination_index = [n[0] if len(n) > 0 else "" for n in members]
        # Unhide row
        request_body_format = {
            "requests": [
                {
                    'updateDimensionProperties': {
                        "range": {
                        "sheetId": 1319964729,
                        "dimension": 'ROWS',
                        "startIndex": len(destination_index),
                        "endIndex": len(destination_index)+1,
                        },
                        "properties": {
                        "hiddenByUser": False,
                        },
                        "fields": 'hiddenByUser',
                    }
                }
            ],
        }
        # Update values
        request_body_value = {
            'valueInputOption': 'RAW',
            "data": [
                {
                    "range": f"'Blacklists Mk.V'!D{len(destination_index)+1}:H{len(destination_index)+1}",
                    "values": [
                        [name, steamid, member_id, reason, datetime.now(timezone('US/Eastern')).strftime("%#d/%#m/%Y")]
                    ],
                }
            ],
        }
        # Requests
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()    
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_format).execute()
    
    def roster_remove_blacklist(self, steamid):
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=("'Blacklists Mk.V'!D:H")).execute().get('values')
        row_number = [n[1] if len(n) >= 3 else "" for n in members].index(str(steamid))
        # Hide row and move to bottom
        request_bodyf = {
            "requests": [
                {
                    'updateDimensionProperties': {
                        "range": {
                        "sheetId": 1319964729,
                        "dimension": 'ROWS',
                        "startIndex": row_number,
                        "endIndex": row_number + 1,
                        },
                        "properties": {
                        "hiddenByUser": True,
                        },
                        "fields": 'hiddenByUser',
                    }
                },
                {
                    "moveDimension": {
                        "source": {
                        "sheetId": 1319964729, 
                        "dimension": "ROWS",
                        "startIndex": row_number,
                        "endIndex": row_number + 1
                        },
                        "destinationIndex": len(members) + 1
                    }
                }
            ],
        }
        # Set values to empty
        request_bodyv = {
            'valueInputOption': 'USER_ENTERED',
            "data": [
                {
                    "range": f"'Blacklists Mk.V'!D{row_number+1}:H{row_number+1}",
                    "values": [
                        ["","","","",""]
                    ],
                }
            ],
        }
        # Request
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_bodyv).execute()    
        self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_bodyf).execute()
        # Return name
        return members[row_number][0]
    
    def roster_update_blacklist(self, steamid, type_column, new_value):
        #INFO TYPE SHOULD BE ROSTER COLUMN
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=(f"'Blacklists Mk.V'!D:H")).execute().get('values')
        column_to_number = {'D': 0, 'E': 1, 'F': 2, 'G': 3}
        try:
            row_number = [n[1] if len(n) >= 5 else "" for n in members].index(str(steamid))
        except ValueError:
            return None
        # Update cell to new value
        request_body_value = {
            'valueInputOption': 'RAW',
            "data": [
                {
                    "range": f"'Blacklists Mk.V'!{type_column}{row_number+1}:{type_column}{row_number+1}",
                    "values": [
                        [new_value]
                    ],
                }
            ],
        }
        # Request
        self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=request_body_value).execute()
        # Return Name and old value
        return members[row_number][0], members[row_number][column_to_number[type_column]]

    def roster_fetch_blacklist(self):
        members = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=(f"'Blacklists Mk.V'!D9:H")).execute().get('values')
        # Return steamid and discord id
        return [[member[1], member[2]] for member in members if len(member) >= 5]

#                    #
#   Command Events   #
#                    #


    @commands.hybrid_command(name="enlist")
    async def enlist(self, ctx: commands.Context, member: discord.Member, name: str, steamid: str, notes: str = "None."):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
            
        author_roles = [x.name for x in ctx.author.roles]
        
        # If author is not in rank_permissions
        if not any(x in author_roles for x in list(self.rank_permissions)):
            await ctx.send("You cannot host tryouts!", ephemeral = True)
            return
            
        ranks = list(self.rank_dictionary)
        author_rank = [x for x in author_roles if x in ranks][-1]
        
        # If author can host tryouts
        if self.rank_permissions[author_rank][2]:
        
            # If new member is blacklisted
            blacklist_steam_discord = self.roster_fetch_blacklist()
            if steamid in blacklist_steam_discord[0] or member.id in blacklist_steam_discord[1]:
                await ctx.send("This person is blacklisted!")
                return
            
            # Send Message
            await ctx.send(f"Host: {ctx.author.mention}\nPerson Accepted: {member.mention}\nSteamID: {steamid}\nNew Rank: TRA\nNotes: {notes}")
            
            # Add them to roster
            try:
                self.roster_enlist(member.id, name, steamid)
            except Exception as e:
                await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                pass
                
            # Give roles
            await member.add_roles(discord.utils.get(ctx.guild.roles, name="Deathtrooper Enlisted"))
            await member.add_roles(discord.utils.get(ctx.guild.roles, name="Trainee"))
        else:
            await ctx.send("You cannot host tryouts!", ephemeral = True)

    @commands.hybrid_command(name="promotion-demotion")
    async def promotion_demotion(self, ctx: commands.Context, trooper: discord.Member, rank: str, reason: str):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
            
        ranks = list(self.rank_dictionary)
        member_roles = [x.name for x in trooper.roles]
        author_roles = [x.name for x in ctx.author.roles]
        # If author can not promote
        if not any(x in author_roles for x in list(self.rank_permissions)):
            await ctx.send("You cannot promote!", ephemeral = True)
            return

        member_rank = [x for x in member_roles if x in ranks][-1]
        author_rank = [x for x in author_roles if x in ranks][-1]
        
        try:
            # If author can promote to rank
            if ranks.index(self.rank_permissions[author_rank][0]) <= ranks.index(rank):
                # If author has required roles for promotion
                if ranks[ranks.index(rank)+1] == member_rank:
                    # Send Message
                    await ctx.send(f"Officer: {ctx.author.mention}\nPerson Promoted: {trooper.mention}\nOld Rank: {ranks[ranks.index(rank)+1]}\nNew Rank: {rank}\nReason: {reason}")
                    # Add and remove roles
                    roles_to_add = self.rank_dictionary[rank]
                    roles_to_add = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_add]
                    await trooper.add_roles(*roles_to_add)
                    await trooper.remove_roles(discord.utils.get(ctx.guild.roles, name=ranks[ranks.index(rank) + 1]))
                    # Update Roster
                    try:
                        self.roster_promotion_demotion(trooper.id, rank)
                    except Exception as e:
                        await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                        pass
                # If going to rank would be a demotion
                elif ranks.index(rank) > ranks.index(member_rank):
                    # If author can demote and author can demote member's rank
                    if self.rank_permissions[author_rank][1] and ranks.index(self.rank_permissions[author_rank][0]) <= ranks.index(member_rank):
                        # Send Message
                        await ctx.send(f"Officer: {ctx.author.mention}\nPerson Demoted: {trooper.mention}\nOld Rank: {member_rank}\nNew Rank: {rank}\nReason: {reason}")
                        # Add and Remove Roles
                        roles_to_remove = self.rank_dictionary[member_rank]
                        roles_to_add = self.rank_dictionary[rank]
                        roles_to_remove = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_remove if x not in roles_to_add]
                        roles_to_add = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_add]
                        await trooper.remove_roles(*roles_to_remove)
                        await trooper.add_roles(*roles_to_add)
                        # Update Roster
                        try:
                            self.roster_promotion_demotion(trooper.id, rank, True)
                        except Exception as e:
                            await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                            pass
                    else:
                        await ctx.send("You cannot demote troopers!", ephemeral = True)
                elif rank == member_rank:
                    await ctx.send(f'{trooper} is already a {rank}!', ephemeral = True)
                else:
                    await ctx.send(f'This trooper must be a {ranks[ranks.index(rank)+1]} to be promoted to {rank}!', ephemeral = True)
            else:
                await ctx.send(f"You can only promote/demote up to {self.rank_permissions[author_rank][0]}", ephemeral = True)
        except IndexError:
            await ctx.send("This member is not apart of the regiment!", ephemeral = True)            

    @commands.hybrid_command(name="remove")
    async def remove(self, ctx: commands.Context, member: discord.Member, reason: str, notes: str="None"):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        # Extend response time
        await ctx.defer()
        ranks = list(self.rank_dictionary)
        roles = ranks + self.dt_roles
        for role in ctx.guild.roles:
            if any(wildcard in role.name for wildcard in self.dt_roles_wildcard):
                roles.append(role.name)
        print(roles)
        member_roles = [x.name for x in member.roles]
        author_roles = [x.name for x in ctx.author.roles]
        # If author has any roles in rank_permissions
        if any(x in author_roles for x in list(self.rank_permissions)):
            # If member is in regiment
            member_rank = [x for x in member_roles if x in ranks][-1]
            author_rank = [x for x in author_roles if x in ranks][-1]
            if member_rank:
                # If author can remove
                if self.rank_permissions[author_rank][1]:
                    # If author can remove member's rank
                    if ranks.index(self.rank_permissions[author_rank][0]) <= ranks.index(member_rank):
                        # Update roster
                        try:
                            steamid, rank = self.roster_remove(member.id, reason)
                        except Exception as e:
                            await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                            pass
                        # Send Message
                        await ctx.send(f"Person Removed: {member.mention}\nOld Rank: {rank}\nSteamID: {steamid}\nReason: {reason}\nNotes: {notes}")
                        # Remove Roles
                        roles_to_remove = [x for x in member_roles if x in roles]
                        roles_to_remove = [discord.utils.get(ctx.guild.roles, name=name_) for name_ in roles_to_remove]

                        await member.remove_roles(*roles_to_remove)
                    else:
                        await ctx.send(f"You can only remove up to {self.rank_permissions[author_rank][0]}", ephemeral = True)
                else:
                    await ctx.send("You cannot remove!", ephemeral = True)
            else:
                await ctx.send("This member is not in the regiment!", ephemeral = True)
        else:
            await ctx.send("You cannot remove!", ephemeral = True)

    @commands.hybrid_command(base="roster", name="update-info")
    async def update_info(self, ctx: commands.Context, member: discord.Member, type: str, value: str, notes: str = "None"):
        # Chcek if channel is roster changes
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        author_roles = [x.name for x in ctx.author.roles]
        # Check if author has role in rank_permissions
        if not any(x in author_roles for x in list(self.rank_permissions)):
            await ctx.send("You must be at least 2nd Lieutenant to edit roster components", ephemeral = True)
            return

        # Check if member is in regiment
        if discord.utils.get(ctx.guild.roles, name="Deathtrooper Enlisted") in member.roles:
            # Check if author can update info
            ranks = list(self.rank_dictionary)
            author_rank = [x for x in author_roles if x in ranks][-1]
            if self.rank_permissions[author_rank][1]:
                # Update info and send message
                try:
                    old_value = self.roster_update_user_into(member.id, type, value)
                    await ctx.send(f"Person Updated: {member.mention}\nType: {type.split(':')[1]}\nOld Value: {old_value}\nNew Value: {value}\nNotes: {notes}")
                except Exception as e:
                    await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                    pass
            else:
                await ctx.send("You must be at least a 2nd Lieutenant to edit roster components!", ephemeral = True)
        else:
            await ctx.send("This member is not in the regiment!", ephemeral = True)

    @commands.hybrid_command(name="unit-promotion-demotion")
    async def unit_promotion_demotion(self, ctx: commands.Context, trooper: discord.Member, unit: str, rank: str, reason: str):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral=True)
            return
        print(ctx.author.roles)
        roles_of_interest = ["Commander", "Colonel", "Lieutenant Colonel" ,f"Lead {unit} Instructor", f"{unit} Instructor", f"{unit} Trained", "@everyone"]
        author_roles = [x.name for x in ctx.author.roles]
        author_rank = [x for x in author_roles if x in roles_of_interest][-1]
        trooper_roles = [x.name for x in trooper.roles]
        trooper_rank = [x for x in trooper_roles if x in roles_of_interest[3:7]][-1]
        rank = rank.replace('xxx', unit)
        # If promotion
        if roles_of_interest.index(rank) < roles_of_interest.index(trooper_rank):
            # If rank in guild roles
            if rank in [x.name for x in ctx.guild.roles]:
                # If author can promote to role
                if roles_of_interest.index(author_rank) < roles_of_interest.index(rank):
                    # Send Message
                    await ctx.send(f"Officer: {ctx.author.mention}\nPerson Promoted: {trooper.mention}\nOld Unit Rank: {trooper_rank if trooper_rank != '@everyone' else 'N/A'}\nNew Unit Rank: {rank}\nReason: {reason}")
                    # Add roles
                    for index, role in enumerate(roles_of_interest[3:6]):
                        if index >= roles_of_interest[3:6].index(rank) and role in [x.name for x in ctx.guild.roles]:
                            await trooper.add_roles(discord.utils.get(ctx.guild.roles, name=role))
                else:
                    await ctx.send("You cannot promote to this rank!", ephemeral=True)
            else:
                await ctx.send("This rank does not exist.", ephemeral=True)
        # If Demotion or Removal
        elif roles_of_interest.index(rank) > roles_of_interest.index(trooper_rank):
            # If Author can demote from role
            if roles_of_interest.index(author_rank) < roles_of_interest.index(trooper_rank):
                # If Demotion
                if rank in [x.name for x in ctx.guild.roles]:
                    # Send Message
                    await ctx.send(f"Officer: {ctx.author.mention}\nPerson Demoted: {trooper.mention}\nOld Unit Rank: {trooper_rank if trooper_rank != '@everyone' else 'N/A'}\nNew Unit Rank: {rank.replace('xxx', unit)}\nReason: {reason}")
                    # Remove Roles
                    for index, role in enumerate(roles_of_interest[3:6]):
                        if index < roles_of_interest[3:6].index(rank) and role in [x.name for x in ctx.guild.roles]:
                                await trooper.remove_roles(discord.utils.get(ctx.guild.roles, name=role))
                # If Removal
                else:
                    # Send Message
                    await ctx.send(f"Officer: {ctx.author.mention}\nPerson Removed: {trooper.mention}\nOld Unit Rank: {trooper_rank if trooper_rank != '@everyone' else 'N/A'}\nNew Unit Rank: N/A\nReason: {reason}")
                    # Remove Roles
                    for index, role in enumerate(roles_of_interest[3:6]):
                        if role in [x.name for x in ctx.guild.roles]:                                
                            await trooper.remove_roles(discord.utils.get(ctx.guild.roles, name=role))
            else:
                await ctx.send("You cannot demote this person!", ephemeral=True)
        else:
            await ctx.send(f"{trooper.mention} is already a {rank}", hidden=True)

# Group Commands

    @commands.hybrid_group(name="battalion")
    async def battalion_group(self, ctx: commands.Context):
        return
        
    @battalion_group.command(name="update")
    async def battalion_update(self, ctx: commands.Context, member: discord.Member, battalion: str, rank: str, reason: str):
        # If channel is not roster-changes
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        # If member is not in DT
        if not discord.utils.get(ctx.guild.roles, name="Deathtrooper Enlisted") in member.roles:
            await ctx.send("This member is not in the regiment!", ephemeral = True)
            return
        
        await ctx.defer()
        before = self.roster_battalion_promotion_demotion(member, rank, battalion)
        after = f'{battalion}{rank}'
        after = "N/A" if after == "N/AN/A" else after
        
        old_battalion = self.battalion_acronyms[before[0:4]]
        new_battalion = self.battalion_acronyms[battalion]
        # If nothing changed
        if before != after:
            # Same battalion
            if before[0:4] == after:
                # Add and remove roles
                roles_to_add = self.battalion_ranks[rank]
                roles_to_remove = self.battalion_ranks["N/A" if before.split("|")[0][4:] == "" else before.split("|")[0][4:]]
                roles_to_add = [rank.replace("$", new_battalion) for rank in roles_to_add]
                roles_to_remove = [rank.replace("$", old_battalion) for rank in roles_to_remove]
                roles_to_remove = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_remove if x not in roles_to_add]
                roles_to_add = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_add]
                await member.remove_roles(*roles_to_remove)
                await member.add_roles(*roles_to_add)
                # Send Message
                await ctx.send(f"Officer: {ctx.author.mention}\nPerson Updated:{member.mention}\nOld Battalion Rank: {before}\nNew Battalion Rank: {after}\nReason: {reason}")
            else:
                # Add and remove roles
                roles_to_add = self.battalion_ranks[rank]
                roles_to_remove = self.battalion_ranks["N/A" if before.split("|")[0][4:] == "" else before.split("|")[0][4:]]
                for role in ctx.author.roles:
                    if old_battalion in role.name and role.name not in roles_to_remove:
                        roles_to_remove.append(role.name)
                # Replace $ to battalion
                roles_to_remove = [rank.replace("$", old_battalion) for rank in roles_to_remove]
                roles_to_add = [rank.replace("$", new_battalion) for rank in roles_to_add]
                # Turn role from string into object
                roles_to_remove = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_remove if x not in roles_to_add]
                roles_to_add = [discord.utils.get(ctx.guild.roles, name=x) for x in roles_to_add if x != ""]
                await member.remove_roles(*roles_to_remove)
                await member.add_roles(*roles_to_add)
                # Send message
                await ctx.send(f"Officer: {ctx.author.mention}\nPerson Updated: {member.mention}\nOld Battalion Rank: {before}\nNew Battalion Rank: {after}\nReason: {reason}")
        else:
            await ctx.send(f"The member is already apart of the battalion at the selected rank!", ephemeral = True)

    @commands.hybrid_group(name="blacklist")
    async def blacklist_group(self, ctx: commands.Context):
        return

    @blacklist_group.command(name="add")
    async def blacklist_add(self, ctx: commands.Context, name: str, steamid: str, discordid: int, reason: str, notes: str = "None"):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        ranks = list(self.rank_dictionary)
        author_roles = [x.name for x in ctx.author.roles]
        # Check if author has a role in rank_permissions
        if any(x in author_roles for x in list(self.rank_permissions)):
            # Check if author has blacklist permissions
            author_rank = [x for x in author_roles if x in ranks][-1]
            if self.rank_permissions[author_rank][1]:
                # Send Message
                await ctx.send(f"Person Blacklisted: {name}\nSteamID: {steamid}\nReason: {reason}\nNotes: {notes}")
                # Update Roster
                try:
                    self.roster_add_blacklist(discordid, name, steamid, reason)
                except Exception as e:
                    await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                    pass
            else:
                await ctx.send("You must be at least a 2nd Lieutenant to blacklist people!", ephemeral = True)
        else:
            await ctx.send("You must be at least 2nd Lieutenant to blacklist people!", ephemeral = True)

    @blacklist_group.command(name="revoke")
    async def blacklist_revoke(self, ctx: commands.Context, steamid: str, reason: str, notes: str = "None"):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        # Check if author has role in rank_permissions
        ranks = list(self.rank_dictionary)
        author_roles = [x.name for x in ctx.author.roles]
        if any(x in author_roles for x in list(self.rank_permissions)):
            # Check if author can revoke blacklists
            author_rank = [x for x in author_roles if x in ranks][-1]
            if self.rank_permissions[author_rank][3]:
                # Remove Blacklist from Roster
                try:
                    name = self.roster_remove_blacklist(steamid)
                except Exception as e:
                    await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}')
                    pass
                # Send Message
                await ctx.send(f"Blacklist Revoked: {name}\nSteamID: {steamid}\nReason: {reason}\nNotes: {notes}")
            else:
                await ctx.send("You must be at least a Lieutenant Colonel to unblacklist people!", ephemeral = True)
        else:
            await ctx.send("You must be at least a Lieutenant Colonel to unblacklist people!", ephemeral = True)

    @blacklist_group.command(name="update")
    async def updateblacklist(self, ctx: commands.Context, steamid: str, type: str, value: str, notes: str = "None"):
        if ctx.channel.name != "roster-changes":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
            
        # Check if author has role in rank_permissions
        author_roles = [x.name for x in ctx.author.roles]
        if any(x in author_roles for x in list(self.rank_permissions)):
            ranks = list(self.rank_dictionary)
            author_rank = [x for x in author_roles if x in ranks][-1]
            # Check if author has blacklist permissions
            if self.rank_permissions[author_rank][1]:
                # Update blacklist and send message
                try:
                    name, oldvalue = self.roster_update_blacklist(steamid, type.split(":")[0], value)
                    await ctx.send(f"Blacklist Updated: {name}\nType: {type.split(':')[1]}\nOld Value: {oldvalue}\nNew Value: {value}\nNotes: {notes}")
                except Exception as e:
                    await ctx.send(f'An Error has occurred. Please contact Sour with all relevent details. {e}', ephemeral = True)
                    pass
            else:
                await ctx.send("You must be at least a 2nd Lieutenant to edit roster components!", ephemeral = True)
        else:
            await ctx.send("You must be at least 2nd Lieutenant to edit roster components", ephemeral = True)

#                      #
#   Event Listeners    #
#                      #

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # If not DT Discord
        if member.guild.id != 877764629042958336:
            return
        # Send Left Message
        await self.client.get_channel(878047082030698528).send(f'{member.mention} has left the discord.')
        # If member was in DT
        if discord.utils.get(member.guild.roles, name="Deathtrooper Enlisted") in member.roles:
            # Remove from roster and send message in roster-changes
            steamid, rank = self.roster_remove(member.id, "Left the discord")
            await self.client.get_channel(878076047940272158).send(f"Person Removed: {member.mention}\nOld Rank: {rank}\nSteamID: {steamid}\nReason: Left the discord")

# Setup Function
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Roster(client))