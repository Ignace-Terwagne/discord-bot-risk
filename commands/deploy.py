import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

sys.path.append("../database")
sys.path.append("../.")
import database.crud as crud
from game_manager import GameManager

gm = GameManager()
class DeployGroup(app_commands.Group):
    @app_commands.command(name="north-america")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_north_america)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)

    @app_commands.command(name="north-america")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_south_america)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
    
    @app_commands.command(name="europe")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_europe)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
        
    @app_commands.command(name="asia")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_asia)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
    
    @app_commands.command(name="africa")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_africa)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
        
    @app_commands.command(name="australia")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_australia)
    async def deploy_America(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)

async def deploy(interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):
    game = crud.get_game_by_channel_id(interaction.channel_id)
    
    data = gm.deploy_troops(territory.value, amount, game.id, interaction.user.id)
    return_code = data[0]
    if return_code == 0:
        interaction.response.send_message("it's not your turn. You cannot perform an action until it is your turn.", ephemeral=True)
    elif return_code == 1:
        interaction.response.send_message("You are currently not in the `deploy phase`. You cannot deploy anymore during this round.", ephemeral=True)
    elif return_code == 2:
        interaction.response.send_message("this territory isn't yours. please select a territory that belongs to you.", ephemral= True)
    elif return_code == 3:
        interaction.response.send_message(f"You don't have this much troops available to send out. You have `{data[2]}` troops available to deploy.", ephemral=True)
    elif return_code == 4:
        available_troops = data[1]
        total_troops = data[2]
        embed = discord.Embed()
        embed.title = "troops deployed"
        embed.add_field(name="territory:", value=territory.name, inline=False)
        embed.add_field(name="total troops on this territory: ", value=total_troops, inline=False)
        embed.add_field(name="available troops left", value=available_troops, inline=False)
        
        interaction.response.send_message(embed=embed)
    
async def setup(bot : commands.Bot):
    bot.tree.add_command(DeployGroup(name="deploy", description="deploy troops"))
    import discord
from discord import app_commands
from discord.ext import commands
import sys
import os

sys.path.append("../database")
sys.path.append("../.")
import database.crud as crud
from game_manager import GameManager

gm = GameManager()
class DeployGroup(app_commands.Group):
    @app_commands.command(name="north-america")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_north_america)
    async def deploy_north_america(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)

    @app_commands.command(name="south-america")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_south_america)
    async def deploy_south_america(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
    
    @app_commands.command(name="europe")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_europe)
    async def deploy_europe(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
        
    @app_commands.command(name="asia")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_asia)
    async def deploy_asia(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
    
    @app_commands.command(name="africa")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_africa)
    async def deploy_africa(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)
        
    @app_commands.command(name="australia")
    @app_commands.describe(territory="territory which you want to deploy troops in", amount="amount of troops you want to deploy")
    @app_commands.choices(territory = gm.territories_australia)
    async def deploy_australia(self, interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):    
        await deploy(interaction, territory, amount)

async def deploy(interaction: discord.Interaction, territory: discord.app_commands.Choice[str], amount: int):
    game = crud.get_game_by_channel_id(interaction.channel_id) 
    if not game:
        await interaction.response.send_message("you cannot use this commmand outside a game.", ephemeral=True)
    
    data = gm.deploy_troops(territory.value, amount, game.uuid, interaction.user.id)
    return_code = data[0]
    if return_code == 0:
        await interaction.response.send_message("it's not your turn. You cannot perform an action until it is your turn.", ephemeral=True)
    elif return_code == 1:
        await interaction.response.send_message("You are currently not in the `deploy phase`. You cannot deploy anymore during this round.", ephemeral=True)
    elif return_code == 2:
        await interaction.response.send_message("this territory isn't yours. please select a territory that belongs to you.", ephemeral= True)
    elif return_code == 3:
        await interaction.response.send_message(f"You don't have this much troops available to send out. You have `{data[1]}` troops available to deploy.", ephemeral=True)
    elif return_code == 4:
        available_troops = data[1]
        total_troops = data[2]
        embed = discord.Embed()
        embed.color = discord.Color.green()
        embed.title = "troops deployed"
        embed.add_field(name="territory:", value=territory.name, inline=False)
        embed.add_field(name="total troops on this territory: ", value=total_troops, inline=False)
        embed.add_field(name="available troops left", value=available_troops, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
async def setup(bot : commands.Bot):
    bot.tree.add_command(DeployGroup(name="deploy", description="deploy troops"))
    