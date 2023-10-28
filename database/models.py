from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    games = relationship("Game", secondary="user_game_association", back_populates="users")

class Game(Base):
    __tablename__= "games"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True)
    guild = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now())
    status = Column(Boolean, default=True)
    users = relationship("User", secondary="user_game_association", back_populates="games")
    
class User_Game_Association(Base):
    __tablename__ = "user_game_association"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))

class Guild(Base):
    __tablename__ = "guilds"
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(Integer, unique=True)
    manager_role_id = Column(Integer, unique=True)
    game_channel_id = Column(Integer, unique=True)
    games = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now())

    
    