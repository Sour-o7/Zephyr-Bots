from __future__ import print_function
from discord.ext import commands
from discord.utils import get
import discord
import threading

# Button Class
class PersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def button_roles(self, interaction, button):
#        print(interaction.user.roles)
        if button.custom_id == "Discord Member":
            if discord.utils.get(interaction.guild.roles, name="Discord Member") in interaction.user.roles:
                await interaction.response.send_message(content="You already have that role, stupid!", ephemeral = True)
                return
            else:
                await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name=button.custom_id))
                await interaction.response.send_message(content=f"Gave you the {button.custom_id} role!", ephemeral = True)
        elif not discord.utils.get(interaction.guild.roles, name="Discord Member") in interaction.user.roles:
            await interaction.response.send_message(content="Please agree to the rules first!", ephemeral = True)
            return
        elif discord.utils.get(interaction.guild.roles, name=button.custom_id) in interaction.user.roles:
            await interaction.user.remove_roles(discord.utils.get(interaction.guild.roles, name=button.custom_id))
            await interaction.response.send_message(content=f"Removed the {button.custom_id} Role!", ephemeral = True)
            return
        await interaction.user.add_roles(discord.utils.get(interaction.guild.roles, name=button.custom_id))
        await interaction.response.send_message(content=f"Gave you the {button.custom_id} role!", ephemeral = True)

    @discord.ui.button(custom_id = "Discord Member")
    async def discord_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "Game-Night Notifications")
    async def game_notifications(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "Deathtrooper Applicant")
    async def deathtrooper_applicant(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "ARC Representative Applicant")
    async def arc_rep_applicant(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "Fleet Representative Applicant")
    async def fleet_rep_applicant(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "Event Notifications")
    async def event_notifications(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)
        
    @discord.ui.button(custom_id = "Activity Notifications")
    async def activity_notifications(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.button_roles(interaction, button)


# Setup Function
async def setup(client: commands.Bot) -> None:
    client.add_view(PersistentView())