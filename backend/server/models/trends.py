from pydantic import BaseModel
from typing import List, Literal

class TrendsRequest(BaseModel):
    year:int|None
    month:int|None
    categories:List[str]|None
    hopInterval:Literal["seconds", "minutes", "hours", "days", "weeks"]
    hopValue: int
    freq:Literal["10s", "30s", "min", "5min", "15min","30min","h","D","W","M","Y"]