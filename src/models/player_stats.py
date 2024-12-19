from pydantic import BaseModel


class PlayerStats(BaseModel):
    passes_completed: int
    passes_attempted: int
    shots: int
    shots_on_target: int
    fouls_committed: int
    fouls_won: int
    tackles: int
    interceptions: int
    dribbles_successful: int
    dribbles_attempted: int
