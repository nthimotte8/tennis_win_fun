from sqlalchemy import (
    create_engine,
    Column,
    String,
    Date,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import pandas as pd

Base = declarative_base()


class Tournoi(Base):
    __tablename__ = "tournois"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tourney_id = Column(String, unique=True, nullable=True)
    tourney_name = Column(String, nullable=False)
    surface = Column(String)
    draw_size = Column(Integer)
    tourney_level = Column(String)
    tourney_date = Column(Date)
    tourney_start_date = Column(Date)


class Joueur(Base):
    __tablename__ = "joueurs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    hand = Column(String)
    ht = Column(Integer)
    ioc = Column(String)

    __table_args__ = (UniqueConstraint('name', 'ioc', name='_name_ioc_uc'),)


class DbNeon:
    def __init__(self, db_url: str = "sqlite:///tennis.db"):
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, future=True)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def write_players(self, df: pd.DataFrame):
        """
        Insert players from a DataFrame into the joueurs table,
        avoiding duplicates on (name, ioc).
        """
        df = df[["name", "hand", "ht", "ioc"]].drop_duplicates()

        with self.session_scope() as session:
            for _, row in df.iterrows():
                exists = session.query(Joueur).filter_by(name=row["name"], ioc=row["ioc"]).first()
                if not exists:
                    player = Joueur(
                        name=row["name"],
                        hand=row["hand"],
                        ht=row["ht"],
                        ioc=row["ioc"],
                    )
                    session.add(player)

        print(f"{len(df)} joueurs insérés ou ignorés.")

    def write_tourney(self, df: pd.DataFrame):
        """
        Insert tournaments from a DataFrame into the tournois table,
        avoiding duplicates on tourney_id.
        Converts dates to proper datetime.date objects.
        """
        expected_cols = [
            "tourney_id",
            "tourney_name",
            "surface",
            "draw_size",
            "tourney_level",
            "tourney_date",
            "tourney_start_date",
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        # Convert dates
        df['tourney_date'] = pd.to_datetime(df['tourney_date'], format="%Y%m%d", errors='coerce').dt.date
        df['tourney_start_date'] = pd.to_datetime(df['tourney_start_date'], errors='coerce').dt.date

        with self.session_scope() as session:
            for _, row in df.iterrows():
                exists = session.query(Tournoi).filter_by(tourney_id=row["tourney_id"]).first()
                if not exists:
                    tourney = Tournoi(
                        tourney_id=row["tourney_id"],
                        tourney_name=row["tourney_name"],
                        surface=row["surface"],
                        draw_size=row["draw_size"],
                        tourney_level=row["tourney_level"],
                        tourney_date=row["tourney_date"],
                        tourney_start_date=row["tourney_start_date"],
                    )
                    session.add(tourney)

        print(f"{len(df)} tournois insérés ou ignorés.")
