from __future__ import print_function
from discord.ext import commands
import discord

class RankSelfAssignment(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()
        
        # Rank: [Max Promotion Rank, Can Demote]
        self.rank_permissions = {
            "Jump Trooper Commander": ["Sergeant Major",        True],
            "Colonel":                ["Sergeant Major",        True],
            "Lieutenant Colonel":     ["Sergeant Major",        True],
            "Major":                  ["Sergeant Major",        True],
            "Captain":                ["Sergeant Major",        True],
            "1st Lieutenant":         ["Master Sergeant",       True],
            "2nd Lieutenant":         ["Sergeant First Class",  True],
            "Sergeant Major":         ["Corporal",              False],
            "Master Sergeant":        ["Lance Corporal",        False],
            "Sergeant First Class":   ["Private First Class",   False],
            "Zephyr Staff":           ["Corporal",              False]
        }

        # Rank: [Associated Role 1, Associated Role 2, ..]
        self.rank_dictionary = {
            'Jump Trooper Commander':   [],
            'Colonel':                  [],
            'Lieutenant Colonel':       [],
            'Major':                    [],
            'Captain':                  [],
            '1st Lieutenant':           [],
            '2nd Lieutenant':           [],
            'Sergeant Major':           ["Jump Trooper", "Jump Sergeant", "Sergeant Major"],
            'Master Sergeant':          ["Jump Trooper", "Jump Sergeant", "Master Sergeant"],
            'Sergeant First Class':     ["Jump Trooper", "Jump Sergeant", "Sergeant First Class"],
            'Staff Sergeant':           ["Jump Trooper", "Jump Sergeant", "Staff Sergeant"],
            'Sergeant':                 ["Jump Trooper", "Jump Sergeant", "Sergeant"],
            'Corporal':                 ["Jump Trooper", "JT Enlisted",   "Corporal"],
            'Lance Corporal':           ["Jump Trooper", "JT Enlisted",   "Lance Corporal"],
            'Private First Class':      ["Jump Trooper", "JT Enlisted",   "Private First Class"],
            'Private':                  ["Jump Trooper", "JT Enlisted",   "Private"],
            'JT Enlisted':              ["Trainee"]
        }
        
    @commands.hybrid_command(name="rsa")
    async def rank_self_assignment(self, ctx: commands.Context, rank: str, promoter: discord.Member):

        # If channel is not 📝rank-self-assignment
        if ctx.channel.name != "📝rank-self-assignment":
            await ctx.send("Use the correct channel", ephemeral = True)
            return
        
        # Get all of the Author's roles and Promoter's roles
        promoter_roles = [x.name for x in promoter.roles]
        author_roles = [x.name for x in ctx.author.roles]
        
        # If promoter can not promote
        if not any(x in promoter_roles for x in list(self.rank_permissions)):
            await ctx.send(f"{promoter.mention} cannot promote!")
            return

        # If author is being promoted to TRA
        if rank == "Trainee":
            await ctx.send(f"{ctx.author.mention} was promoted by {promoter.mention} to {rank}")
            
            # Add roles in roles_to_add to author
            roles_to_add = ["Jump Trooper", "JT Enlisted", "Trainee"]
            roles_to_add = [discord.utils.get(ctx.guild.roles, name = role_name) for role_name in roles_to_add]
            await ctx.author.add_roles(*roles_to_add)
            return

        # Get list of self.rank_dictionary (All ranks)
        ranks = list(self.rank_dictionary)
        
        # Get Author's and Promoter's rank
        promoter_rank = [x for x in promoter_roles if x in ranks][-1]
        author_rank = [x for x in author_roles if x in ranks][-1]
    
        # Check if Promoter can promote to Rank
        if ranks.index(self.rank_permissions[promoter_rank][0]) <= ranks.index(rank):
        
            # If Author is the current Rank
            if rank == author_rank:
                await ctx.send(f'{ctx.author.mention} is already a {rank}!')
                
            # Check if the new Rank is a demotion from Current Rank
            elif ranks.index(rank) > ranks.index(author_rank):
            
                # If Promoter is not allowed to demote or they can not demote the Author's rank
                if not self.rank_permissions[promoter_rank][1] or not ranks.index(self.rank_permissions[promoter_rank][0]) <= ranks.index(author_rank):
                    await ctx.send(f"{promoter.mention} cannot demote from {author_rank}!")
                    return

                # Send Message
                await ctx.send(f"{ctx.author.mention} was demoted by {promoter.mention} to {rank}")
                
                # Calculate roles to remove and add
                roles_to_remove = self.rank_dictionary[author_rank]
                roles_to_add = self.rank_dictionary[rank]
                roles_to_remove = [discord.utils.get(ctx.guild.roles, name = x) for x in roles_to_remove if x not in roles_to_add]
                roles_to_add = [discord.utils.get(ctx.guild.roles, name = x) for x in roles_to_add]
                
                # Add and remove roles
                await ctx.author.remove_roles(*roles_to_remove)
                await ctx.author.add_roles(*roles_to_add)

            # Check if author is the correct rank for promotion
            elif ranks[ranks.index(rank)+1] == author_rank:
            
                # Send Message
                await ctx.send(f"{ctx.author.mention} was promoted by {promoter.mention} to {rank}")
                
                # Calculate roles to add and remove
                roles_to_remove = self.rank_dictionary[author_rank]
                roles_to_add = self.rank_dictionary[rank]
                roles_to_remove = [discord.utils.get(ctx.guild.roles, name = x) for x in roles_to_remove if x not in roles_to_add]
                roles_to_add = [discord.utils.get(ctx.guild.roles, name = x) for x in roles_to_add]
                
                # Add and remove roles
                await ctx.author.remove_roles(*roles_to_remove)
                await ctx.author.add_roles(*roles_to_add)
            else:
                await ctx.send(f'This trooper must be a {ranks[ranks.index(rank)+1]} to be promoted to {rank}!')
        else:
            await ctx.send(f"{promoter.mention} can only promote up to {self.rank_permissions[promoter_rank][0]}")

# Setup Function          
async def setup(client: commands.Bot) -> None:
    await client.add_cog(RankSelfAssignment(client))