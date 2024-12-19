from pydantic import BaseModel


class MatchSummary(BaseModel):
    match_id: int
    summary: str
