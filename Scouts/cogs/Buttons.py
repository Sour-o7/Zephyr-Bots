from __future__ import print_function
from discord.ext import commands
import discord

# Button Class
class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='PT/SIM Annoucement', style=discord.ButtonStyle.grey, custom_id='PTSIM')
    async def Attention_Scouts(self, interaction: discord.Interaction, button: discord.ui.Button):
        # If user has "Scout Enlisted" role
        if discord.utils.get(interaction.guild.roles, name="Scout Enlisted") in interaction.user.roles:
            # If user already has "Attention Scouts!"
            if discord.utils.get(interaction.guild.roles, name="Attention Scouts!") in interaction.user.roles:
                # Remove role and send message
                await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="Attention Scouts!"))
                await interaction.response.send_message(content="Removed the `Attention Scouts!` Role!", ephemeral = True)
                return
            # Else Add role and send message
            await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name="Attention Scouts!"))
            await interaction.response.send_message(content="Gave you the `Attention Scouts!` role!", ephemeral = True)
        else:
            await interaction.response.send_message(content="You have to be a scout in order to get this role!", ephemeral = True)

    @discord.ui.button(label='Retired Scout Trooper', style=discord.ButtonStyle.grey, custom_id='Retired')
    async def Retired_Scouts(self, interaction: discord.Interaction, button: discord.ui.Button):
        # If user has "Retired Scout Trooper"
        if discord.utils.get(interaction.guild.roles, name="Retired Scout Trooper") in interaction.user.roles:
            # Remove role and send message
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name="Retired Scout Trooper"))
            await interaction.response.send_message(content="Removed the `Retired Scout Trooper` Role!", ephemeral = True)
            return
        # Else add role and send message
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name="Retired Scout Trooper"))
        await interaction.response.send_message(content="Gave you the `Retired Scout Trooper` role!", ephemeral = True)

# Setup Function
async def setup(client: commands.Bot) -> None:
    client.add_view(PersistentView())