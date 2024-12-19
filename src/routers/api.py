import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models.player_stats import PlayerStats
from models.match_summary import MatchSummary

from tools.football import (
    get_specialist_comments_about_match,
    retrieve_match_details,
    get_lineups,
    get_players_stats,
    COMMENTARY_STYLES,
)

from stats.matches import MATCH_TIME_MAP

app = FastAPI()


# --------------------------
# Endpoints
# --------------------------
@app.get("/match_summary", response_model=MatchSummary)
def match_summary(
    competition_id: int = 9,
    season_id: int = 27,
    match_id: int = 3890477,
    style: COMMENTARY_STYLES = "formal",
) -> MatchSummary:
    """
    Generate a match summary based on the match details and lineups.
    The match summary can be generated with a specialist commentary style.

    Args:
        competition_id: The competition ID.
        season_id: The season ID.
        match_id: The match ID.
        style: The specialist commentary style (formal, funny or technical).

    Returns:
        MatchSummary: The match summary.
    """

    try:
        match_id = int(match_id)
        match_details = retrieve_match_details(competition_id, season_id, match_id)
        lineups = get_lineups(match_id)
        match_summary = get_specialist_comments_about_match(
            match_details=match_details, lineups=lineups, style=style
        )
        if not match_summary:
            raise HTTPException(
                status_code=404, detail="Could not generate match summary"
            )
        return {"match_id": match_id, "summary": match_summary}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid match_id")


@app.get("/player_stats", response_model=PlayerStats)
def player_stats(
    competition_id: int = 9,
    season_id: int = 27,
    match_id: int = 3890477,
    player_name: str = "Kohr",
    time: MATCH_TIME_MAP = "whole_match",
) -> PlayerStats:
    """
    Get the player stats for a specific player in a match.

    Args:
        competition_id: The competition ID.
        season_id: The season ID.
        match_id: The match ID.
        player_name: The player's name.
        time: The match time (whole_match, first_half, second_half or overtime).

    Returns:
        PlayerStats: The player's stats.
    """

    try:
        match_id = int(match_id)
        player_name = str(player_name)
        player_stats = get_players_stats(
            competition_id=competition_id,
            season_id=season_id,
            match_id=match_id,
            player_name=player_name,
            time=time,
        )

        try:
            return json.loads(player_stats)
        except ValueError:
            raise HTTPException(
                status_code=404, detail="Could not retrieve player stats"
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid match_id or player_name")
