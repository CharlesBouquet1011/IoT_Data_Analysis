from pydantic import BaseModel
from typing import List

class ProcessRequest(BaseModel):
    year: int | None
    month: int | None
    columnList: List[str]