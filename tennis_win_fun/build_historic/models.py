from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Tournoi(Base):
    __tablename__ = "tournois"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tourney_id = Column(String, unique=True, nullable=True)  # nullable et unique
    tourney_name = Column(String, nullable=False)
    surface = Column(String)
    draw_size = Column(Integer)
    tourney_level = Column(String)
    tourney_date = Column(Date)
    tourney_start_date = Column(Date)


class Joueur(Base):
    __tablename__ = "joueurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    hand = Column(String)
    ht = Column(Integer)
    ioc = Column(String)
