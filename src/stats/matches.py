import json
import pandas as pd
import numpy as np
import streamlit as st

from copy import copy
from statsbombpy import sb
from typing import List

from stats.competitions import get_matches_df

from models.player_stats import PlayerStats
from typing import Literal


def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


@st.cache_resource(ttl=3600)
def get_lineups(match_id: int) -> str:
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ["cards", "positions"]
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient="records")
    return to_json(data_final)


@st.cache_resource(ttl=3600)
def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json(
        [
            {k: v for k, v in event.items() if v is not np.nan}
            for event in full_events.sort_values(by="minute").to_dict(orient="records")
        ]
    )


@st.cache_resource(ttl=3600)
def get_team_players(match_id: int, team: str) -> list:
    data = sb.lineups(match_id=match_id)
    team_data = data[team]
    return team_data["player"].tolist()


@st.cache_resource(ttl=3600)
def get_match_df(match_id: int) -> pd.DataFrame:
    return sb.events(match_id=match_id)


MATCH_TIME_MAP = Literal["whole_match", "first_half", "second_half", "overtime"]


@st.cache_resource(ttl=3600)
def get_players_stats(match_id: int, time: MATCH_TIME_MAP = "whole_match") -> str:
    # Get all players names in the match
    events = get_match_df(match_id)

    print(time)

    # Get the unique players
    players = events["player"].dropna().unique()

    # Get the stats for each player
    players_stats = {}
    for player in players:
        players_stats[player] = get_single_player_stats(match_id, player, time)

    return to_json(players_stats)


@st.cache_resource(ttl=3600)
def get_single_player_stats(
    match_id, player_name, time: MATCH_TIME_MAP = "whole_match"
) -> str:
    """
    Returns the consolidated statistics of a specific player in a match.

    Parameters:
        match_id (int): ID of the match (provided by StatsBomb).
        player_name (str): Full name of the player.
        time (str): Time of the match to consider (whole_match, first_half, second_half, overtime).

    Returns:
        dict: Consolidated statistics of the player.

    Raises:
        PlayerStatsError: If any issue occurs while fetching or calculating the statistics.
    """
    try:
        # Load match events
        events = sb.events(match_id=match_id)

        # Filter events based on the time
        if time == "first_half":
            events = events[events["minute"] <= 45]
        elif time == "second_half":
            events = events[events["minute"] > 45]
        elif time == "overtime":
            events = events[events["minute"] > 90]

        # Validate if events were loaded
        if events.empty:
            raise Exception("No events found for the match")

        # Filter events for the specific player
        player_events = events[events["player"] == player_name]

        # Check if the player is present in the events
        if player_events.empty:
            raise Exception("Player not found in the match events")

        # Consolidate statistics
        stats = {
            "passes_completed": player_events[
                (player_events["type"] == "Pass")
                & (player_events["pass_outcome"].isna())
            ].shape[0],
            "passes_attempted": player_events[player_events["type"] == "Pass"].shape[0],
            "shots": player_events[player_events["type"] == "Shot"].shape[0],
            "shots_on_target": player_events[
                (player_events["type"] == "Shot")
                & (player_events["shot_outcome"] == "On Target")
            ].shape[0],
            "fouls_committed": player_events[
                player_events["type"] == "Foul Committed"
            ].shape[0],
            "fouls_won": player_events[player_events["type"] == "Foul Won"].shape[0],
            "tackles": player_events[player_events["type"] == "Tackle"].shape[0],
            "interceptions": player_events[
                player_events["type"] == "Interception"
            ].shape[0],
            "dribbles_successful": player_events[
                (player_events["type"] == "Dribble")
                & (player_events["dribble_outcome"] == "Complete")
            ].shape[0],
            "dribbles_attempted": player_events[
                player_events["type"] == "Dribble"
            ].shape[0],
        }
        stats = PlayerStats(**stats)

    except Exception as e:
        # Return empty stats if any error occurs
        stats = PlayerStats(
            **{
                "passes_completed": 0,
                "passes_attempted": 0,
                "shots": 0,
                "shots_on_target": 0,
                "fouls_committed": 0,
                "fouls_won": 0,
                "tackles": 0,
                "interceptions": 0,
                "dribbles_successful": 0,
                "dribbles_attempted": 0,
            }
        )

    return stats.model_dump_json()


@st.cache_data(ttl=3600, show_spinner=False)
def get_teams(competition_id, season_id, match_id) -> List[str]:
    matches = get_matches_df(competition_id, season_id)
    match = matches[matches["match_id"] == match_id]
    home_team = match["home_team"].values[0]
    away_team = match["away_team"].values[0]
    return home_team, away_team


@st.cache_data(ttl=3600, show_spinner=False)
def get_goals_df(match_id, team="", shot_type="") -> pd.DataFrame:
    events = get_match_df(match_id)
    goals = events[events["shot_outcome"] == "Goal"]

    # Check for own goals
    own_goals = events[events["type"] == "Own Goal Against"]
    own_goals = own_goals[["team", "player", "minute"]]
    own_goals["shot_type"] = "Own Goal"
    goals = pd.concat([goals, own_goals])

    if shot_type:
        goals = goals[goals["shot_type"] == shot_type]

    if team:
        goals = goals[goals["team"] == team]
    return goals


@st.cache_data(ttl=3600, show_spinner=False)
def get_match_score_details(competition_id, season_id, match_id) -> dict:

    # Get goals for open play and penalties
    goals = get_goals_df(match_id)
    teams = get_teams(competition_id, season_id, match_id)

    # Remove own goals from the goals DataFrame
    own_goals = goals[goals["shot_type"] == "Own Goal"]
    goals = goals[goals["shot_type"] != "Own Goal"]

    # Add [OG] to the player name for own goals
    own_goals["player"] = own_goals["player"].apply(lambda x: f"{x} [OG]")

    # Get player name and time for each goal
    home_team_player_goals = goals[goals["team"] == teams[0]][["player", "minute"]]
    alway_team_player_goals = goals[goals["team"] == teams[1]][["player", "minute"]]

    # Add own goals to the other team
    home_team_player_goals = pd.concat(
        [home_team_player_goals, own_goals[own_goals["team"] == teams[1]]]
    )
    home_team_player_goals["team"] = teams[0]
    alway_team_player_goals = pd.concat(
        [alway_team_player_goals, own_goals[own_goals["team"] == teams[0]]]
    )
    alway_team_player_goals["team"] = teams[1]
    goals = pd.concat([home_team_player_goals, alway_team_player_goals])

    # Penalty goals are counted after the minute 120
    penalty_goals = goals[goals["minute"] >= 120]
    open_play_goals = goals[goals["minute"] < 120]

    home_team_player_goals_text = ""
    for i, row in home_team_player_goals.iterrows():
        home_team_player_goals_text += f"{row['player']} ({row['minute']}'), "
    home_team_player_goals_text = home_team_player_goals_text[:-2]

    alway_team_player_goals_text = ""
    for i, row in alway_team_player_goals.iterrows():
        alway_team_player_goals_text += f"{row['player']} ({row['minute']}'), "
    alway_team_player_goals_text = alway_team_player_goals_text[:-2]

    # Get total goals for each team
    open_play_goals = open_play_goals.groupby("team").size()
    penalty_goals = penalty_goals.groupby("team").size()

    home_team_open_play_goals = (
        open_play_goals[teams[0]] if teams[0] in open_play_goals else 0
    )
    home_team_penalty_goals = (
        penalty_goals[teams[0]] if teams[0] in penalty_goals else 0
    )

    # [!] Second team may not be present in the goals DataFrame
    if len(teams) == 2:
        alway_team_open_play_goals = (
            open_play_goals[teams[1]] if teams[1] in open_play_goals else 0
        )
        alway_team_penalty_goals = (
            penalty_goals[teams[1]] if teams[1] in penalty_goals else 0
        )
    else:
        alway_team_open_play_goals = 0
        alway_team_penalty_goals = 0

    return {
        "home_team_name": str(teams[0]),
        "home_team_open_play": int(home_team_open_play_goals),
        "home_team_penalty": int(home_team_penalty_goals),
        "home_team_player_goals": str(home_team_player_goals_text),
        "alway_team_name": str(teams[1]),
        "alway_team_open_play": int(alway_team_open_play_goals),
        "alway_team_penalty": int(alway_team_penalty_goals),
        "alway_team_player_goals": str(alway_team_player_goals_text),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_match_stats_summary(match_id: int, stats_map: dict = None) -> dict:
    events = get_match_df(match_id)

    # Define the default stats map
    if stats_map is None:
        stats_map = {
            "⚽ Shots": "Shot",
            "🅿️ Pass": "Pass",
            "❌ Fouls": {"type": "Foul Committed"},
            "🏳️ Corners": {"pass_type": "Corner"},
            "🟨 Yellow": {
                "foul_committed_card": "Yellow Card",
                "bad_behavior_card": "Yellow Card",
            },
            "🟥 Red": {
                "foul_committed_card": "Red Card",
                "bad_behavior_card": "Red Card",
            },
        }

    # Get stats for each team
    teams = events["team"].unique()
    stats = {}

    for team in teams:
        team_events = events[events["team"] == team]
        team_stats = {}
        for stat_name, stat_type in stats_map.items():
            if isinstance(stat_type, dict):
                stat = 0
                for key, value in stat_type.items():
                    # Check if the key exists in the DataFrame
                    if key in team_events.columns:
                        stat += len(team_events[team_events[key] == value])
            else:
                stat = len(team_events[team_events["type"] == stat_type])
            team_stats[stat_name] = stat
        stats[team] = team_stats

    return stats
