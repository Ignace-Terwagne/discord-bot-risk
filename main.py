from typing import Optional
import discord
from cairosvg import svg2png
from discord.ext import commands
from discord import app_commands
from map_manager import MapManager
from PIL import Image
import database.crud as crud
import database.models as models
from database.database import engine
import datetime
import asyncio
import os
from dotenv import load_dotenv, dotenv_values


models.Base.metadata.create_all(bind=engine)
mm = MapManager()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
territories= mm.list_countries()
if not os.path.isdir("maps"):
    os.makedirs("maps")
    
### CHECKS ###
async def check_manager(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    manager_role_id = crud.get_guild_by_discord_id(guild_id).manager_role_id
    if manager_role_id in [role.id for role in interaction.user.roles]:
        return True
    else:
        await interaction.response.send_message("You don't have to necessary role to run this command.", ephemeral=True)
    
async def check_admin(interaction: discord.Interaction):
    user = interaction.user
    if not user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have the permission to run this command", ephemeral=True)
        return False
    else:
        return True
    
#################VIEWS##########################
class SetupOVerwriteView(discord.ui.View):
    def __init__(self):
        super().__init__()
    def disable_buttons(self):
        for i in self.children:
            i.disabled = True
    @discord.ui.button(label="continue", style=discord.ButtonStyle.danger)
    async def continue_setup(self, interaction: discord.Interaction, button: discord.Button):
        self.disable_buttons()
        await setup(interaction, "update")
    @discord.ui.button(label="cancel", style=discord.ButtonStyle.gray)
    async def cancel_setup(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        self.disable_buttons()
        
        

class JoinGameView(discord.ui.View):
    def __init__(self, map_id):
        super().__init__()
        self.map_id = str(map_id)
        
    @discord.ui.button(label="join game", style=discord.ButtonStyle.green)
    async def join_game(self, interaction: discord.Interaction, button: discord.Button):
        #check if user is already in database
        user = crud.get_user_by_discord_id( interaction.user.id)
        # if not create a user
        if not user:
            user = crud.create_user( interaction.user.id)
        game = crud.get_game_by_uuid( self.map_id)
        # if the game is not in the database, something is wrong
        if not game:
            await interaction.response.send_message("an error occured while joining the game. Please trying again later.", ephemeral=True)
        confirmation = crud.join_game( user.id, game.id)
        if confirmation == 0:
            await interaction.response.send_message("An error occured while joining the game. Please try again later.", ephemeral=True)
        elif confirmation == 1:
            await interaction.response.send_message("You have already joined this game", ephemeral=True)
        elif confirmation == 2:
            await interaction.response.send_message("you have joined the game!", ephemeral=True)
################################################
async def setup(interaction: discord.Interaction,action):
    check = True
    manager_role = None
    game_channel = None
    embed = discord.Embed(title="setup 1/4", timestamp=datetime.datetime.now())
    embed.add_field(name=":white_check_mark: INITIALIZATION", value="starting the setup", inline=False)
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await asyncio.sleep(1)
    embed.title = "setup 2/4"
    try:
        manager_role = await interaction.guild.create_role(name="game-manager", mentionable=False, color=discord.Color.blue(), reason="setup game configuration")
        embed.add_field(name=":white_check_mark: ROLE SETUP", value=f"created <@&{manager_role.id}>")
    except discord.Forbidden:
        check = False
        embed.add_field(name=":warning: ROLE SETUP", value=f"Missing permissions: 'manage roles", inline=False)
    await message.edit(embed=embed)
    await asyncio.sleep(1)
    embed.title = "setup 3/4"
    try:
        game_channel = await interaction.guild.create_text_channel(name="games")
        embed.add_field(name=":white_check_mark: CHANNEL SETUP", value=f"created channel <#{game_channel.id}>", inline=False)
    except discord.Forbidden:
        check = False
        embed.add_field(name=" :warning: CHANNEL SETUP", value=f"Missing permissions: `manage channels`", inline=False)
    await message.edit(embed=embed)
    await asyncio.sleep(1)
    embed.title = "setup 4/4"
    if check:
        embed.add_field(name=":white_check_mark: ALL DONE", value=f"Your server has been successfully configured. You can change the name, color and category from the text-channel and role. Have fun!", inline=False)
        await message.edit(embed=embed)
        if action == 'create':
            crud.create_guild(interaction.guild_id, manager_role.id, game_channel.id)
        else:
            crud.update_guild(interaction.guild_id, manager_role.id, game_channel.id)
    else:
        print(manager_role)
        print(game_channel)
        if manager_role:
            await manager_role.delete()
        if game_channel:
            await game_channel.delete()
        embed.add_field(name=":warning: MISSING PERMISSIONS", value=f"Please give the missing permissions and rerun the command.", inline=False)
        await message.edit(embed=embed)

@bot.event
async def on_ready():
    print("bot is ready")
    try:
        synced = await bot.tree.sync()
        for i in synced:
            print(f"SYNCED {i}")
    except Exception as e:
        print(e)
         
@bot.event
async def on_guild_join(guild : discord.Guild):
    admins = [member for member in guild.members if member.guild_permissions.administrator]
    owner = guild.owner
    for admin in admins:
        try:
            await admin.send('Thank you for inviting me to your server! Please use `/setup` to configure the settings for your servers. This action can only be done by a member of the guild with the administrator permissions. Have fun!')
        except discord.Forbidden:
            pass
        
async def send_map(map_id, channel: discord.TextChannel):
    filepath = f"./maps/map-{map_id}.svg"
    svg2png(url=filepath, write_to="temp_img.png")
    image = Image.open("temp_img.png")
    width, height = image.size
    background = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    background.paste(image, (0,0), image)
    background.save("temp_img.png")
    file = discord.File("temp_img.png")
    await channel.send(file=file)
    await channel.send(f"`map_id: {map_id}`")
    
#this command sets up the bot and applies the server specific configuration.
@bot.tree.command(name="setup")
async def setup_command(interaction:discord.Interaction):
    if check_admin(interaction):
        guild = crud.get_guild_by_discord_id(interaction.guild_id)
        if guild:
            await interaction.response.send_message("This server is already registered in the system. If you continue with the configuration process, it will override the existing settings", view=SetupOVerwriteView())
        else:
            await setup(interaction, "create")
            return

#assigns the manager role to a member of the guild. only these people can pass the check_manager() function
@bot.tree.command(name="add-manager")
@app_commands.describe(member="member", )
async def add_manager(interaction: discord.Interaction, member: discord.Member):
    if await check_admin(interaction):
        manager_role_id : int = crud.get_guild_by_discord_id(interaction.guild.id).manager_role_id
        print(manager_role_id)
        manager_role = interaction.guild.get_role(manager_role_id)
        await member.add_roles(manager_role)
        await interaction.response.send_message(f"The role <@&{manager_role_id}> was added to <@{member.id}>", ephemeral=True)
    
#initiates a game
@bot.tree.command(name="start-game")
async def start_game(interaction: discord.Interaction):
    if await check_manager(interaction):
        await interaction.response.send_message("preparing game...", ephemeral=True)
        map_id = mm.create_map()
        crud.create_game( str(map_id), interaction.guild_id)
        view = JoinGameView(map_id=map_id)
        timer = datetime.datetime.now() + datetime.timedelta(minutes=2)
        timer = int(timer.timestamp())
        message = await interaction.channel.send(f'the game is starting <t:{timer}:R>',view=view)
        await asyncio.sleep(120)
        for i in view.children:
            i.disabled = True
        await message.edit(content=f'the game started',view=view)


## ---> continue here



## game commands ##
@bot.tree.command(name="my-games")
async def get_my_games(interaction: discord.Interaction):
    user = crud.get_user_by_discord_id(interaction.user.id)
    await interaction.response.send_message(f"{user.games}")
bot.run(DISCORD_TOKEN)