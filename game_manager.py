from map_manager import MapManager
from discord import app_commands
import pandas as pd
import shutil
from database import crud
import random
import uuid
import discord
import os

mm = MapManager()



class GameManager():
    def __init__(self):
        self.colors_dict = { "blue"  : [":blue_square:","#55acee"],
               "red"    : [":red_square:","#78b159"],
               "purple" : [":purple_square:","#aa8ed6"],
               "yellow" : [":yellow_square:","#fdcb58"],
               "green"  : [":green_square:","#78B159"],
               "brown"  : [":brown_square:","#c1694f"],
               "orange" : [":orange_square:","#f4900c"],
               "black"  : [":black_square:","#31373d"]
               }
        self.territories_north_america = [
            app_commands.Choice(name="Alaska", value="alaska"),
            app_commands.Choice(name="Northwest Territory", value="northwest_territory"),
            app_commands.Choice(name="Alberta", value="alberta"),
            app_commands.Choice(name="Western United States", value="western_united_states"),
            app_commands.Choice(name="Eastern United States", value="eastern_united_states"), 
            app_commands.Choice(name="Central America", value="central_america"), 
            app_commands.Choice(name="Quebec", value="quebec"),
            app_commands.Choice(name="Greenland", value="greenland"),
            app_commands.Choice(name="Ontario", value="ontario"),
        ]
        self.territories_south_america = [
            app_commands.Choice(name="Venezuela", value="venezuela"), 
            app_commands.Choice(name="Brazil", value="brazil"), 
            app_commands.Choice(name="Argentina", value="argentina"),
            app_commands.Choice(name="Peru", value="peru"),
            
        ]
        self.territories_africa = [
            app_commands.Choice(name="Madagascar", value="madagascar"), 
            app_commands.Choice(name="North africa", value="north_africa"),
            app_commands.Choice(name="East africa", value="east_africa"), 
            app_commands.Choice(name="Congo", value="congo"), 
            app_commands.Choice(name="South africa", value="south_africa"),
            app_commands.Choice(name="Egypt", value="egypt"),
        ]
        self.territories_europe = [
            app_commands.Choice(name="Iceland", value="iceland"), 
            app_commands.Choice(name="Great britain", value="great_britain"), 
            app_commands.Choice(name="Scandinavia", value="scandinavia"),
            app_commands.Choice(name="Ukraine", value="ukraine"), 
            app_commands.Choice(name="Southern europe", value="southern_europe"), 
            app_commands.Choice(name="Western europe", value="western_europe"), 
            app_commands.Choice(name="Northern europe", value="northern_europe"),
        ]
        self.territories_australia = [
            app_commands.Choice(name="New guinea", value="new_guinea"),
            app_commands.Choice(name="Eastern australia", value="eastern_australia"), 
            app_commands.Choice(name="Indonesia", value="indonesia"),
            app_commands.Choice(name="Western australia", value="western_australia"),  
        ]
        self.territories_asia = [ 
            app_commands.Choice(name="Japan", value="japan"), 
            app_commands.Choice(name="Yakursk", value="yakursk"), 
            app_commands.Choice(name="Kamchatka", value="kamchatka"), 
            app_commands.Choice(name="Siberia", value="siberia"), 
            app_commands.Choice(name="Ural", value="ural"), 
            app_commands.Choice(name="Afghanistan", value="afghanistan"), 
            app_commands.Choice(name="Middle east", value="middle_east"), 
            app_commands.Choice(name="India", value="india"), 
            app_commands.Choice(name="Siam", value="siam"), 
            app_commands.Choice(name="China", value="china"), 
            app_commands.Choice(name="Mongolia", value="mongolia"), 
            app_commands.Choice(name="Irkutsk", value="irkutsk"),
        ]
#############################################################
#                      MANAGEMENT                           #
#############################################################
    def register_game(self,guild_id: int, channel_id: int):
        game_id = str(uuid.uuid4())
        mm.create_map(game_id)
        game = crud.create_game(game_id, guild_id, channel_id)
        guild = crud.get_guild_by_id(guild_id)
        if guild:
            crud.update_guild(guild.discord_id, game_count=guild.game_count + 1)
            return str(game_id), game
        else:
            return None 
    def initiate_game_data(self,game_id):
        def divide_countries(players: list[int]):
            regions = mm.list_countries() # retrieves a list with the 42 named regions of the risk field
            random.shuffle(players)
            random.shuffle(regions)
            sets = {}
            regions_per_player = len(regions) // len(players)
            remainders = len(regions) % len(players)
            for player in players:
                player_regions = []
                for x in range(regions_per_player):
                    player_regions.append(regions.pop())
                if remainders > 0:
                    player_regions.append(regions.pop())
                    remainders -= 1
                sets[player] = player_regions
            return sets
    
        game = crud.get_game_by_game_id(game_id)
        players = crud.get_players_by_game(game.id)
        if not players:
            return [], []
        player_count = len(players)
        troops_per_player = 40 - (player_count - 2)*5
        player_ids = [player.id for player in players]
        print(player_ids)
        map_data_file = shutil.copy("templates/map-data.csv", f"game-data/map-data/map-data-{game_id}.csv" )
        player_data_file = f"game-data/player-data/player-data-{game_id}.csv"
        sets = divide_countries(player_ids)
        map_data = pd.read_csv(map_data_file)
        player_data_list : list[list] = []
        colors_players = list(self.colors_dict)[:len(players)]
        for i, player_id in enumerate(sets):
            for region in sets[player_id]:
                condition = (map_data["region-name"] == region)
                map_data.loc[condition, "player-id"] = player_id
                map_data.loc[condition, "color"] = colors_players[i]
                map_data.loc[condition, "troops"] = 1
                mm.update_country(game_id, region, colors_players[i])
            player_data_list.append([player_id, colors_players[i],len(sets[player_id]), troops_per_player, "deploy"])
        player_data = pd.DataFrame(player_data_list, columns=["player_id", "color", "territories", "available troops", "current phase"])
        player_data.to_csv(player_data_file, index=False)
        map_data.to_csv(map_data_file, index=False)
        return players, colors_players

    async def start(self, game_id: int, interaction: discord.Interaction):
        game = crud.get_game_by_game_id(game_id)
        guild = interaction.guild
        if game:
            channel = guild.get_channel(game.channel_id)
            player_data = self.get_player_data(game_id)
            first_player = player_data.iloc[0]
            print(player_data)
            print(type(first_player["player_id"]))
            user = crud.get_user_by_id(int(first_player["player_id"]))
            discord_id = user.discord_id
            user_id = user.id
            crud.set_game_turn(game_id, user_id)
            embed = discord.Embed()
            embed.title = "Round 0"
            embed.add_field(name="", value="In this round all players will need to deploy their available troops over the different territories. Alternately everyone will deploy their troops using the `/deploy` command.", inline=False)
            embed.add_field(name="turn: ",value=f"<@{discord_id}>")
            embed.add_field(name="available troops: ", value=first_player["available troops"], inline=False)
            embed.add_field(name="current phase:", value=first_player["current phase"], inline=False)
            message = await channel.send(embed=embed)
            
    async def delete_game(self, game_id: int, interaction: discord.Interaction):
        game = crud.get_game_by_game_id(game_id)
        crud.delete_game(game_id)
        interaction.guild.get_channel(game.channel_id).delete()
        os.remove(f"game-data/map-data/map-data-{game_id}")
        os.remove(f"game-data/player-data/player-data-{game_id}")
        os.remove(f"maps/map-{game_id}")
    
    async def next_player(self, game_id: int, interaction: discord.Interaction):
        game = crud.get_game_by_game_id(game_id)
        game_channel = interaction.guild.get_channel(game.channel_id)
        current_player = game.user_id_turn
        
        player_data = self.get_player_data()
        pass
        game_channel.send()
#############################################################
#                      DATA RETRIEVING                      #
#############################################################
    def get_player_data(self, game_id : int):
        player_data = pd.read_csv(f"game-data/player-data/player-data-{game_id}.csv")
        print(player_data)
        return player_data
    
#############################################################
#                      GAME ACTIONS                         #
#############################################################
    def deploy_troops(self, region_name: str, troops: int, game_id: str, discord_id: int):
        # return codes:
        # 0 -> it's not your turn
        # 1 -> you're not in the correct phase
        # 2 -> this territory doesn't belong to you
        # 3 -> you don't have enough available troops
        # 4 -> troops deployed successfully
        
        
        # TESTED and working: still need to switch automatically on round 0
        player_data_file = f"game-data/player-data/player-data-{game_id}.csv"
        map_data_file = f"game-data/map-data/map-data-{game_id}.csv"
        player_data = pd.read_csv(player_data_file)
        map_data = pd.read_csv(map_data_file)
        
        player = crud.get_user_by_discord_id(discord_id)
        game = crud.get_game_by_game_id(game_id)
        player_data_condition = (player_data["player_id"] == player.id)
        # if it's not the players turn, return and abort the deployment
        if game.user_id_turn != player.id:
            return 0, None, None
        
        # if it is the players turn, but he is not in the right phase (deploy), return and abort the deployment
        if player_data.loc[player_data_condition, "current phase"].iloc[0] != "deploy":
            return 1, None, None
        
        # if it is the players turn and he is in the right phase, but the region is not his, return and abort the deployment
        target_condition = map_data.loc[(map_data["region-name"] == region_name), "player-id"].iloc[0]
        print(target_condition)
        if target_condition != player.id:
            return 2, None, None
        
        available_troops = int(player_data.loc[player_data_condition, "available troops"])
        
        # if all the conditions are met, but the player doesn't have enough available troops, return and abort the deployment
        if troops > available_troops:
            return 3, available_troops
        
        # if all the conditions are met, deploy the troops and update the game-data.
        if troops <= available_troops:
            troops_data = int(map_data.loc[(map_data["region-name"] == region_name), "troops"])
            total_troops = troops_data + troops 
            map_data.loc[(map_data["region-name"] == region_name), "troops"] = total_troops
            if troops == available_troops and game.round != 0:
                player_data.loc[player_data_condition, "current phase"] = "attack"
            available_troops -= troops
            player_data.loc[player_data_condition, "available troops"] = available_troops
            player_data.to_csv(player_data_file)
            map_data.to_csv(map_data_file)
            return 4, available_troops, total_troops
            
    
