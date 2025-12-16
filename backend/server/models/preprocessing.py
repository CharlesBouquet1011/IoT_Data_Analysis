from pydantic import BaseModel
from typing import List, Literal

class PreprocessRequest(BaseModel):
    year: int
    month: int
    rollingIntervalType: Literal["nb", "Duree"]
    rollingInterval: str | int
    attrList: List[str]
