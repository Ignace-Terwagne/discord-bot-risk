from map_manager import MapManager
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
        map_data_file = shutil.copy("templates/game-data.csv", f"game-data/map-data/map-data-{game_id}.csv" )
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
    def deploy_troups(self, region_name: str, troops: int, game_id: str, discord_id: int):
        ##########################################################
        #           NOT TESTED YET!!!                            #
        ##########################################################
        player_data_file = f"game-data/player-data/player-data-{game_id}.csv"
        map_data_file = f"game-data/map-data/map-data-{game_id}.csv"
        player_data = pd.read_csv(player_data_file)
        map_data = pd.read_csv(map_data_file)
        crud.get_user_by_
        player_data_condition = (player_data["player_id"] == crud.get_user_by_discord_id(discord_id).id)
        available_troops = int(player_data.loc[player_data_condition, "available troops"])
        if troops <= available_troops:
            troops_data = int(map_data.loc[(map_data["region-name"] == region_name), "troops"])
            player_data.loc[(map_data["region-name"] == region_name), "troops"] = troops_data + troops
            if troops == available_troops:
                player_data.loc[player_data_condition, "current phase"] = "attack"
            player_data.loc[player_data_condition, "available troops"] = available_troops - troops
            player_data.to_csv(player_data_file)
            map_data.to_csv(map_data_file)
        else:
            return False
    
