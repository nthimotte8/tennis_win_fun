import os
from typing import List

import pandas as pd

from tennis_win_fun.build_historic.models import DbNeon


class BuildHistoric:
    """
    Class to build all historic data from csv files.
    """

    def __init__(self, db=None):
        """
        Initialize the BuildHistoric class.
        :param db: Database handler instance, if None will create DbNeon instance internally
        """
        self.dossier_csv = "../tennis_win_fun/tennis_win_fun/historic_data"
        self.all_cols = [
            "tourney_id",
            "tourney_name",
            "surface",
            "draw_size",
            "tourney_level",
            "tourney_date",
            "match_num",
            "winner_id",
            "winner_seed",
            "winner_entry",
            "winner_name",
            "winner_hand",
            "winner_ht",
            "winner_ioc",
            "winner_age",
            "loser_id",
            "loser_seed",
            "loser_entry",
            "loser_name",
            "loser_hand",
            "loser_ht",
            "loser_ioc",
            "loser_age",
            "score",
            "best_of",
            "round",
            "minutes",
            "w_ace",
            "w_df",
            "w_svpt",
            "w_1stIn",
            "w_1stWon",
            "w_2ndWon",
            "w_SvGms",
            "w_bpSaved",
            "w_bpFaced",
            "l_ace",
            "l_df",
            "l_svpt",
            "l_1stIn",
            "l_1stWon",
            "l_2ndWon",
            "l_SvGms",
            "l_bpSaved",
            "l_bpFaced",
            "winner_rank",
            "winner_rank_points",
            "loser_rank",
            "loser_rank_points",
        ]

        self.match_cols = [
            "tourney_id",
            "winner_seed",
            "winner_entry",
            "winner_name",
            "loser_seed",
            "loser_entry",
            "loser_name",
            "score",
        ]

        self.tournament_cols = [
            "tourney_id",
            "tourney_name",
            "surface",
            "draw_size",
            "tourney_level",
            "tourney_date",
        ]
        self.player_cols = [
            "winner_name",
            "winner_hand",
            "winner_ht",
            "winner_ioc",
            "winner_age",
            "loser_name",
            "loser_hand",
            "loser_ht",
            "loser_ioc",
            "loser_age",
        ]

        if db is None:
            self.db = DbNeon(db_url=os.getenv("DATABASE_URL", "sqlite:///tennis.db"))
        else:
            self.db = db

    def get_historic_from_csv(self, gender: str = "wta") -> pd.DataFrame:
        """
        Read and concatenate all historic data from CSV files in the specified directory.

        Parameters
        ----------
        gender : str
            The gender category, e.g., "wta" or "atp".

        Returns
        -------
        pd.DataFrame
            A DataFrame containing all historic data concatenated from CSV files.
        """
        dir_csv = os.path.abspath(os.path.join(self.dossier_csv, gender))

        if not os.path.exists(dir_csv):
            raise FileNotFoundError(f"Le dossier {dir_csv} est introuvable.")

        csv_files = [f for f in os.listdir(dir_csv) if f.endswith(".csv")]

        if not csv_files:
            raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {dir_csv}.")

        dataframes = [
            pd.read_csv(os.path.join(dir_csv, f), dtype=str) for f in csv_files
        ]
        df_concatene = pd.concat(dataframes, ignore_index=True)

        return df_concatene

    def build_tourney(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build a DataFrame containing tournament information.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing match data.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing tournament information.
        """
        missing_cols = set(self.tournament_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Les colonnes suivantes sont manquantes dans le DataFrame: {missing_cols}"
            )

        df_tourney = df[self.tournament_cols].drop_duplicates().reset_index(drop=True)
        df_tourney["tourney_start_date"] = pd.to_datetime(
            df_tourney["tourney_date"], format="%Y%m%d", errors="coerce"
        )

        return df_tourney

    def build_players(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build a DataFrame with all unique players (winner and loser), without age.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing match data.

        Returns
        -------
        pd.DataFrame
            A DataFrame with unique players (id, name, etc.) excluding age.
        """
        player_cols = [col for col in self.player_cols if "age" not in col]

        winner_cols = [col for col in player_cols if col.startswith("winner_")]
        loser_cols = [col for col in player_cols if col.startswith("loser_")]

        df_winner = df[winner_cols].copy()
        df_winner.columns = [col.replace("winner_", "") for col in df_winner.columns]

        df_loser = df[loser_cols].copy()
        df_loser.columns = [col.replace("loser_", "") for col in df_loser.columns]

        df_players = pd.concat(
            [df_winner, df_loser], ignore_index=True
        ).drop_duplicates()

        return df_players.reset_index(drop=True)

    def _load_and_build_players(self, gender: str) -> pd.DataFrame:
        print(f"Chargement et construction des joueurs pour {gender.upper()}...")
        df = self.get_historic_from_csv(gender)
        return self.build_players(df)

    def _load_and_build_tourney(self, gender: str) -> pd.DataFrame:
        print(f"Chargement et construction des tournois pour {gender.upper()}...")
        df = self.get_historic_from_csv(gender)
        return self.build_tourney(df)

    def run(self, genders=None):
        """
        Run the historic data building process for specified genders.

        Parameters
        ----------
        genders : list
            List of gender strings to process (e.g., ["wta", "atp"]).
        """
        if genders is None:
            genders = ["wta", "atp"]
        print("Début de la construction des données historiques...")

        players_dfs = []
        tourney_dfs = []

        for gender in genders:
            df_players = self._load_and_build_players(gender)
            players_dfs.append(df_players)

            df_tourney = self._load_and_build_tourney(gender)
            tourney_dfs.append(df_tourney)

        print("Concaténation des données joueurs...")
        df_players_all = pd.concat(players_dfs).drop_duplicates().reset_index(drop=True)
        print(f"Nombre total de joueurs uniques : {len(df_players_all)}")

        print("Concaténation des données tournois...")
        df_tourney_all = pd.concat(tourney_dfs).drop_duplicates().reset_index(drop=True)
        print(f"Nombre total de tournois uniques : {len(df_tourney_all)}")

        print("Écriture des données dans la base...")
        self.db.write_players(df_players_all)
        self.db.write_tourney(df_tourney_all)

        print("Processus terminé avec succès.")

    def run_match_historic(self, genders: List[str] = None):
        """
        Run the historic match data building process.
        This method is intended to be implemented to handle match data processing.

        Parameters
        ----------
        genders: str
        available values are "wta" and "atp".
        default is ["wta", "atp"].

        Returns
        -------
        None
        """

        if genders is None:
            genders = ["wta", "atp"]
        print("Début de la construction des données historiques...")

        matchs_dfs = []

        for gender in genders:
            df = self.get_historic_from_csv(gender)
            matchs_dfs.append(df)

        # concatenate all match data
        print("Concaténation des données de matchs...")
        df_matchs_all = pd.concat(matchs_dfs, ignore_index=True)
        print(f"Nombre total de matchs : {len(df_matchs_all)}")

        # keep only the columns that are needed for the match data
        df_matchs_all = (
            df_matchs_all[self.match_cols].drop_duplicates().reset_index(drop=True)
        )

        # Read the players and tournaments from the database
        df_players = self.db.read_players()
        df_tourney = self.db.read_tourneys()

        # select id cols to join
        df_players = df_players[["id", "name", "ioc"]]
        df_tourney = df_tourney[["id", "tourney_id"]]
        # join players and tournaments to the match data
        df_matchs_all = df_matchs_all.merge(
            df_players, left_on="winner_name", right_on="name", how="left"
        )
        # rename columns to avoid confusion
        df_matchs_all.rename(columns={"id": "winner_id"}, inplace=True)
        df_matchs_all = df_matchs_all.merge(
            df_players, left_on="loser_name", right_on="name", how="left"
        )
        df_matchs_all.rename(columns={"id": "loser_id"}, inplace=True)
        df_matchs_all = df_matchs_all.merge(df_tourney, on="tourney_id", how="left")

        # write the match data to the database
        self.db.write_matches(df_matchs_all)
