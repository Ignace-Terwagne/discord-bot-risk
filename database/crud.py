from sqlalchemy.orm import Session
from .database import engine
from .  import models

def get_session():
    return Session(bind=engine)

def get_user_by_id(id: int):
    db: Session = get_session()
    user = db.query(models.User).filter(models.User.id == id).first()
    db.close()
    return user

def get_user_by_discord_id(id: int):
    db: Session = get_session()
    user = db.query(models.User).filter(models.User.discord_id == id).first()
    db.close()
    return user

def get_users():
    db: Session = get_session()
    users = db.query(models.User).all()
    db.close()
    return users

def create_user(discord_id: int):
    db: Session = get_session()
    db_user = models.User(discord_id=discord_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

def get_game_by_id(id: int):
    db: Session = get_session()
    game = db.query(models.Game).filter(models.Game.id == id).first()
    db.close()
    return game

def get_game_by_game_id(uuid:int):
    db: Session = get_session()
    game = db.query(models.Game).filter(models.Game.uuid == uuid).first()
    db.close()
    return game

def get_games_by_guild(guild: int,):
    db: Session = get_session()
    games = db.query(models.Game).filter(models.Game.guild == guild).all()
    db.close()
    return games

def get_games():
    db: Session = get_session()
    games = db.query(models.Game).all()
    db.close()
    return games

def create_game(uuid: int, guild: int, channel_id: int):
    db: Session = get_session()
    db_game = models.Game(uuid=uuid, guild=guild, channel_id=channel_id)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    db.close()
    return db_game

def join_game(user_id: int, game_id: int, ):
    
    db = get_session()
    user = db.query(models.User).filter(models.User.id == user_id).first()
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    # return 3 -> the game is full
    # return 2 -> you already joined the game
    # return 1 -> you joined the game
    # return 0 -> an error occurred
    if len(game.users) >= 8:
        return 3
    if user is None or game is None:
        return 0
    if game_id in [user_game.id for user_game in user.games]:
        return 1
    try:
        user.games.append(game)
        db.commit()
        db.close()
        return 2
    except Exception as e:
        db.rollback()
        db.close()
        return 0
def set_game_turn(game_id, user_id: int):
    db = get_session()
    game = db.query(models.Game).filter(models.Game.uuid == game_id)
    game.update({models.Game.user_id_turn : user_id})
    db.commit()
    db.close()
def delete_game(game_id):
    db = get_session()
    game = get_game_by_game_id(game_id)
    db.delete(game)
    db.commit()
    db.close()

def get_players_by_game(game_id: int):
    db = get_session()
    game = db.query(models.Game).filter(models.Game.id == game_id).first()
    
    return game.users


def get_guild_by_id(id : int):
    db = get_session()
    guild = db.query(models.Guild).filter(models.Guild.id == id).first()
    db.close()
    return guild

def get_guild_by_discord_id(discord_id: int):
    db = get_session()
    guild = db.query(models.Guild).filter(models.Guild.discord_id == discord_id).first()
    db.close()
    return guild

def update_guild(discord_id: int, manager_role_id: int = None, game_category_id: int = None, game_count : int = None):
    db = get_session()
    guild = db.query(models.Guild).filter(models.Guild.discord_id == discord_id)
    if manager_role_id: guild.update({models.Guild.manager_role_id: manager_role_id})
    if game_category_id: guild.update({models.Guild.game_category_id: game_category_id})
    if game_count:  guild.update({models.Guild.game_count: game_count})
    db.commit()
    db.close()
    return guild

def create_guild(discord_id: int, manager_role_id: int, game_category_id: int):
    db = get_session()
    guild = models.Guild(discord_id=discord_id, manager_role_id=manager_role_id, game_category_id=game_category_id)
    db.add(guild)
    db.commit()
    db.refresh(guild)
    db.close()