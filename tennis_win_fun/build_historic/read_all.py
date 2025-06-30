import os

import pandas as pd


class BuildHistoric:
    """
    Class to build all historic data from csv files.
    """

    def __init__(self):
        """
        Initialize the BuildHistoric class.
        """
        self.dossier_csv = "../historic_data"
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

        self.tournemant_cols = [
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
        # Construire le chemin absolu vers le dossier
        dir_csv = os.path.abspath(os.path.join(self.dossier_csv, gender))

        if not os.path.exists(dir_csv):
            raise FileNotFoundError(f"Le dossier {dir_csv} est introuvable.")

        # Lister les fichiers CSV
        csv_files = [f for f in os.listdir(dir_csv) if f.endswith(".csv")]

        if not csv_files:
            raise FileNotFoundError(f"Aucun fichier CSV trouvé dans {dir_csv}.")

        # Lire et concaténer les DataFrames
        dataframes = [pd.read_csv(os.path.join(dir_csv, f)) for f in csv_files]
        df_concatene = pd.concat(dataframes, ignore_index=True)

        return df_concatene

    def build_tourney(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Build a DataFrame containing tournament information.
        One with all tourney information and one with the tourney id and date
        tourney_date looks like 20230101
        Parameters
        ----------
        df : pd.DataFrame
        DataFrame containing match data.

        Returns
        pd.DataFrame
            A DataFrame containing tournament information.

        """
        # check if all columns are present in the DataFrame
        missing_cols = set(self.tournemant_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Les colonnes suivantes sont manquantes dans le DataFrame: {missing_cols}"
            )
        # Create a DataFrame with tournament information
        df_tourney = df[self.tournemant_cols].drop_duplicates().reset_index(drop=True)
        # Convert tourney_date to datetime format
        df_tourney["tourney_start_date"] = pd.to_datetime(
            df_tourney["tourney_date"], format="%Y%m%d"
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
        # Colonnes à utiliser (sans celles contenant "age")
        player_cols = [col for col in self.player_cols if "age" not in col]

        # Séparer les colonnes winner et loser
        winner_cols = [col for col in player_cols if col.startswith("winner_")]
        loser_cols = [col for col in player_cols if col.startswith("loser_")]

        # Créer DataFrame pour winners
        df_winner = df[winner_cols].copy()
        df_winner.columns = [col.replace("winner_", "") for col in df_winner.columns]

        # Créer DataFrame pour losers
        df_loser = df[loser_cols].copy()
        df_loser.columns = [col.replace("loser_", "") for col in df_loser.columns]

        # Concaténer et supprimer les doublons
        df_players = pd.concat(
            [df_winner, df_loser], ignore_index=True
        ).drop_duplicates()

        return df_players
