from __future__ import print_function
from discord.ext import commands
import discord
import os.path
import os
import threading

#JumpTrooper Version 2.0.0
#9/25/2022

client = commands.Bot(command_prefix="++", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Online")
    # Load cogs
    if client.extensions == {}:
        print("Loading Cogs...")
        for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                await client.load_extension("cogs." + f[:-3])
                print(f"Loaded {f[:-3]}")
        print("Loaded All Cogs")
client.run('TOKEN')
