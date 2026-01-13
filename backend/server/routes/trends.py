from data_processing import trends
from fastapi import APIRouter,HTTPException
from server.models.trends import TrendsRequest

router = APIRouter(prefix="/api/trends", tags=["stats"])


@router.post("/")
async def process(data:TrendsRequest):
    if data.month is not None and (data.month < 1 or data.month > 12):
        raise HTTPException(
            status_code=400,
            detail="Mois invalide"
        )


    files=trends(data.year,data.month,tuple(data.categories),data.hopInterval,data.hopValue,data.freq)
    print(files)
    return {"status":"ok","images":files}
