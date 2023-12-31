from typing import Optional
import discord
from cairosvg import svg2png
from discord.ext import commands
from discord import app_commands
from map_manager import MapManager
from game_manager import GameManager
from PIL import Image
import database.crud as crud
import database.models as models
from database.database import engine
import datetime
import asyncio
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv, set_key


models.Base.metadata.create_all(bind=engine)
mm = MapManager()
gm = GameManager()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
if not find_dotenv(usecwd=True):
    print("couldn't find .env")
    open(".env", "x")
load_dotenv(".env")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    DISCORD_TOKEN = input("Please enter the discord token: ")
    set_key(".env", "DISCORD_TOKEN", DISCORD_TOKEN)
    print("discord token added")
territories = mm.list_countries()

if not os.path.isdir("maps"):
    os.makedirs("maps")
if not os.path.isdir("game-data"):
    os.makedirs("game-data")
if not os.path.isdir("game-data/map-data"): os.makedirs("game-data/map-data")
if not os.path.isdir("game-data/player-data"): os.makedirs("game-data/player-data")
### CHECKS ###
async def check_manager(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    guild = crud.get_guild_by_discord_id(guild_id)
    if not guild:
        await interaction.response.send_message("this server has not been setup yet. Please use the `/setup` command as an administrator.", ephemeral=True)
        return False
    manager_role_id = guild.manager_role_id
    if manager_role_id in [role.id for role in interaction.user.roles]:
        return True
    else:
        await interaction.response.send_message(
            "You don't have to necessary role to run this command.", ephemeral=True
        )


async def check_admin(interaction: discord.Interaction):
    user = interaction.user
    if not user.guild_permissions.administrator:
        await interaction.response.send_message(
            "You don't have the permission to run this command", ephemeral=True
        )
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
    async def continue_setup(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        self.disable_buttons()
        await setup(interaction, "update")

    @discord.ui.button(label="cancel", style=discord.ButtonStyle.gray)
    async def cancel_setup(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.defer()
        self.disable_buttons()


class JoinGameView(discord.ui.View):
    def __init__(self, game_id):
        super().__init__()
        self.game_id = str(game_id)

    @discord.ui.button(label="join game", style=discord.ButtonStyle.green)
    async def join_game(self, interaction: discord.Interaction, button: discord.Button):
        # check if user is already in database
        user = crud.get_user_by_discord_id(interaction.user.id)
        # if not create a user
        if not user:
            user = crud.create_user(interaction.user.id)
        game = crud.get_game_by_game_id(self.game_id)
        # if the game is not in the database, something is wrong
        if not game:
            await interaction.response.send_message(
                "an error occured while joining the game. Please trying again later.",
                ephemeral=True,
            )
        confirmation = crud.join_game(user.id, game.id)
        if confirmation == 0:
            await interaction.response.send_message(
                "An error occured while joining the game. Please try again later.",
                ephemeral=True,
            )
        elif confirmation == 1:
            await interaction.response.send_message(
                "You have already joined this game", ephemeral=True
            )
        elif confirmation == 2:
            await interaction.response.send_message(
                "you have joined the game!", ephemeral=True
            )
        elif confirmation == 3:
            await interaction.response.send_message(
                "This game is full", ephemeral=True
            )


################################################
async def setup(interaction: discord.Interaction, action):
    check_permissions = True
    check_database = True
    manager_role = None
    game_category = None
    embed = discord.Embed(title="setup 1/5", timestamp=datetime.datetime.now())
    embed.add_field(
        name=":white_check_mark: INITIALIZATION",
        value="starting the setup",
        inline=False,
    )
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await asyncio.sleep(1)

    # create the manager role. This will be the role that users
    # need to pas the check_manager() function.
    embed.title = "setup 2/5"
    try:
        manager_role = await interaction.guild.create_role(
            name="game-manager",
            mentionable=False,
            color=discord.Color.blue(),
            reason="setup game configuration",
        )
        embed.add_field(
            name=":white_check_mark: ROLE SETUP", 
            value=f"created <@&{manager_role.id}>"
        )
    except discord.Forbidden:
        check = False
        embed.add_field(
            name=":warning: ROLE SETUP",
            value=f"Missing permissions: 'manage roles",
            inline=False,
        )
    await message.edit(embed=embed)
    await asyncio.sleep(1)

    # create the category for the games, so the private channels
    # don't get created at random over the entire server.
    embed.title = "setup 3/5"
    try:
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = False
        overwrite.send_messages= True
        game_category = await interaction.guild.create_category(
            name="games", overwrites={interaction.guild.default_role: overwrite,
                                      bot.user: discord.PermissionOverwrite(view_channel=True)}
        )
        embed.add_field(
            name=":white_check_mark: CATEGORY SETUP",
            value=f"created the category `games` with the necessary permissions",
            inline=False,
        )
    except discord.Forbidden:
        check_permissions = False
        embed.add_field(
            name=" :warning: CATEGORY SETUP",
            value=f"Missing permissions: `manage channels`",
            inline=False,
        )
    await message.edit(embed=embed)
    await asyncio.sleep(1)

    # check if the server was successfully registered in the database.
    # If not, the data will not be saved and the server will be in a loop
    # with the setup menu forever.
    embed.title = "setup 4/5"

    # first check if the permissions were granted. check_permissions is True by default,
    # but if something fails in the setup process due to discord.Forbidden,
    # it gets set to False.
    if check_permissions:
        # if the permissions were granted, a new record will be added to the database or an existing record will be updated with the new data.
        await message.edit(embed=embed)
        if action == "create":
            crud.create_guild(interaction.guild_id, manager_role.id, game_category.id)
        else:
            crud.update_guild(interaction.guild_id, manager_role.id, game_category.id)

        # after the creation of the new record, there will be a check if the guild is synced correctly.
        guild = crud.get_guild_by_discord_id(interaction.guild_id)
        if guild:
            embed.add_field(
                name=":white_check_mark: DATABASE SYNC",
                value="the server is successfully registered in the database",
                inline=False,
            )
            await message.edit(embed=embed)
            await asyncio.sleep(1)
            embed.title="setup 5/5"
            embed.add_field(
                name=":white_check_mark: ALL DONE",
                value=f"The server is successfully configured and registed. you can change the name and position from the role and the category that were generated. To start a game, a user needs to have the role <@&{manager_role.id}> Have fun! ",
                inline=False
            )
            await message.edit(embed=embed)
        else:
            await manager_role.delete()
            await game_category.delete()
            embed.add_field(
                name=" :warning: DATABASE SYNC",
                value="the server is not found in our database. The data from this setup is not saved",
                inline=False
            )
            embed.add_field(
                name=":warning: DATABASE ERROR",
                value=f"There was an internal error in the database, which caused your server not to be registered successfully. Please try the `/setup` command again in a few minutes.",
                inline=False,
            )
        await message.edit(embed=embed)
    else:
        # If one or more permissions were not granted, the script will undo
        # the setup so far. This way, when they run the script again,
        # it won't make duplicates of categories and roles in the server.
        if manager_role:
            await manager_role.delete()
        if game_category:
            await game_category.delete()
        embed.add_field(
            name=":warning: MISSING PERMISSIONS",
            value=f"Please give the missing permissions and rerun the command.",
            inline=False,
        )
        await message.edit(embed=embed)

async def send_map(game_id, channel: discord.TextChannel):
    mm.create_image(game_id)
    file = discord.File("temp_img.png")
    await channel.send(file=file)
#########################################################
#                       BOT COMMANDS                    #
#########################################################
@bot.event
async def on_ready():
    print("bot is ready")
    try:
        loaded = await bot.load_extension("commands.deploy")
        synced = await bot.tree.sync()
        
        for i in synced:
            print(f"SYNCED {i}")
    except Exception as e:
        print(e)


@bot.event
async def on_guild_join(guild: discord.Guild):
    admins = [
        member for member in guild.members if member.guild_permissions.administrator
    ]
    owner = guild.owner
    for admin in admins:
        try:
            await admin.send(
                "Thank you for inviting me to your server! Please use `/setup` to configure the settings for your servers. This action can only be done by a member of the guild with the administrator permissions. Have fun!"
            )
        except discord.Forbidden:
            pass





# this command sets up the bot and applies the server specific configuration.
@bot.tree.command(name="setup")
async def setup_command(interaction: discord.Interaction):
    if await check_admin(interaction):
        guild = crud.get_guild_by_discord_id(interaction.guild_id)
        if guild:
            await interaction.response.send_message(
                "This server is already registered in the system. If you continue with the configuration process, it will override the existing settings",
                view=SetupOVerwriteView(),
            )
        else:
            await setup(interaction, "create")
            return


# assigns the manager role to a member of the guild. only these people can pass the check_manager() function
@bot.tree.command(name="add-manager")
@app_commands.describe(
    member="member",
)
async def add_manager(interaction: discord.Interaction, member: discord.Member):
    if await check_admin(interaction):
        manager_role_id: int = crud.get_guild_by_discord_id(
            interaction.guild.id
        ).manager_role_id
        print(manager_role_id)
        manager_role = interaction.guild.get_role(manager_role_id)
        await member.add_roles(manager_role)
        await interaction.response.send_message(f"The role <@&{manager_role_id}> was added to <@{member.id}>",ephemeral=True)


# initiates a game
@bot.tree.command(name="start-game")
async def start_game(interaction: discord.Interaction):
    if await check_manager(interaction):
        await interaction.response.send_message("preparing game...", ephemeral=True)
        
        guild = crud.get_guild_by_discord_id(interaction.guild_id)
        category = discord.utils.get(interaction.guild.categories, id=guild.game_category_id)
        channel = await interaction.guild.create_text_channel(name=f"game-#{guild.game_count+1}", category=category,)
        
        game_id, game = gm.register_game(guild.id, channel_id=channel.id)
        await channel.edit(topic=f"game_id: {game_id}")
        view = JoinGameView(game_id=game_id)
        timer = datetime.datetime.now() + datetime.timedelta(minutes=2)
        timer = int(timer.timestamp())
        message = await interaction.channel.send(f"the game is starting <t:{timer}:R>", view=view)
        await asyncio.sleep(10)
        for i in view.children:
            i.disabled = True
        players, colors_players = gm.initiate_game_data(game_id)
        if len(players) <= 1:
            await message.edit(content=f"The game was cancelled due to an insufficient number of players.", view=None)
            await gm.delete_game(game_id, interaction)
            return
        await message.edit(content=f"the game started", view=view)
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = True
        mention_string = ''
        embed = discord.Embed(title=f"Welcome to the game!")
        for e, player in enumerate(players):
            emoji = gm.colors_dict[colors_players[e]][0]
            discord_id = player.discord_id
            embed.add_field(name=f"{emoji} player {e+1}", value=f"<@{discord_id}>", inline=False)
            mention_string +=  f'<@{discord_id}>'
            member = interaction.guild.get_member(discord_id)
            await channel.set_permissions(target=member,overwrite=overwrite)
        embed.set_footer(text=f"game-id: {game_id}")
        await channel.send(content=mention_string, embed=embed)
        await send_map(game_id, channel)
        await gm.start(game_id, interaction)
        
## ---> continue here


## game commands ##
        
@bot.tree.command(name="my-games")
async def get_my_games(interaction: discord.Interaction):
    user = crud.get_user_by_discord_id(interaction.user.id)
    embed = discord.Embed()
    for e, game in enumerate(user.games):
        embed.add_field(name=f"game {e+1}", value=f"{game.uuid} | {game.created_at}", inline=False)
        
    await interaction.response.send_message(embed=embed)
    
    
    
#################################
#       ONLY FOR TESTING        #
#################################

@bot.tree.command(name="cleanup-games")
async def cleanup_games(interaction: discord.Interaction):
    channels = [channel for channel in interaction.guild.channels if channel.name.startswith("game-")]
    await interaction.response.send_message(f"deleted `{len(channels)}` channels")
    
    for channel in channels:
        await channel.delete()
    
        
bot.run(DISCORD_TOKEN)
