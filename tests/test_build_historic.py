from unittest.mock import patch

import pandas as pd
import pytest

from tennis_win_fun.build_historic.historic_launcher import BuildHistoric



@pytest.fixture
def bh(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///tennis.db")
    return BuildHistoric()


@pytest.fixture
def mock_df():
    data = {
        "tourney_id": ["2023-001", "2023-002"],
        "tourney_name": ["Open A", "Open B"],
        "surface": ["Hard", "Clay"],
        "draw_size": [32, 64],
        "tourney_level": ["G", "G"],
        "tourney_date": [20230101, 20230201],
        "winner_name": ["Alice", "Clara"],
        "winner_hand": ["R", "L"],
        "winner_ht": [170, 175],
        "winner_ioc": ["FRA", "USA"],
        "winner_age": [25.0, 22.0],
        "loser_seed": [1, 2],
        "loser_name": ["Bea", "Diana"],
        "loser_hand": ["L", "R"],
        "loser_ht": [168, 172],
        "loser_ioc": ["ESP", "GBR"],
        "loser_age": [26.0, 23.0],
    }
    return pd.DataFrame(data)


def test_build_tourney_with_mock(bh, mock_df):
    df_tourney = bh.build_tourney(mock_df)
    assert "tourney_id" in df_tourney.columns
    assert "tourney_start_date" in df_tourney.columns
    assert pd.api.types.is_datetime64_any_dtype(df_tourney["tourney_start_date"])
    assert len(df_tourney) == 2


def test_build_players_with_mock(bh, mock_df):
    df_players = bh.build_players(mock_df)
    assert not df_players.empty
    assert set(["name", "hand", "ht", "ioc"]).issubset(df_players.columns)
    assert "age" not in df_players.columns
    assert len(df_players) == 4  # 2 winners + 2 losers


def test_build_tourney_missing_columns(bh, mock_df):
    df_incomplet = mock_df.drop(columns=["surface"])
    with pytest.raises(ValueError, match="Les colonnes suivantes sont manquantes"):
        bh.build_tourney(df_incomplet)


def test_get_historic_from_csv_mocked(bh, mock_df):
    with patch("pandas.read_csv", return_value=mock_df):
        with patch("os.listdir", return_value=["file1.csv", "file2.csv"]):
            with patch("os.path.exists", return_value=True):
                df = bh.get_historic_from_csv("wta")
                assert isinstance(df, pd.DataFrame)
                assert len(df) == 4  # 2 fichiers * 2 lignes
