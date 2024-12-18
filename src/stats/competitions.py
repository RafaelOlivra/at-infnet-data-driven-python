from statsbombpy import sb
import pandas as pd

import json


def get_competitions() -> str:
    return json.dumps(sb.competitions().to_dict(orient="records"))


def get_matches(competition_id: int, season_id: int) -> str:
    return json.dumps(
        get_matches_df(competition_id, season_id).to_dict(orient="records")
    )


def get_matches_df(competition_id: int, season_id: int) -> pd.DataFrame:
    return sb.matches(competition_id=competition_id, season_id=season_id)
