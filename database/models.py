from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from .database import Base
import datetime
user_game = Table('user_game', Base.metadata, 
                  Column('user_id', Integer, ForeignKey('users.id')),
                  Column('game_id', Integer, ForeignKey('games.id')))
                  
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(Integer, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    games = relationship("Game", secondary=user_game, back_populates="users")

class Game(Base):
    __tablename__= "games"
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True)
    guild = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.now())
    status = Column(Boolean, default=True)
    users = relationship("User", secondary=user_game, back_populates="games")
    
class Guild(Base):
    __tablename__ = "guilds"
    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(Integer, unique=True)
    manager_role_id = Column(Integer, unique=True)
    game_category_id = Column(Integer, unique=True)
    games = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.now())
    
    