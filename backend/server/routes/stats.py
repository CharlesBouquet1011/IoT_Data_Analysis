from data_processing import packetMain,ColumnsList
from fastapi import APIRouter,HTTPException
from server.models.stats.processing import ProcessRequest

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/ColumnList")
async def listeOfColumns(annee:int |None = None,mois:int|None =None):
    liste=ColumnsList(annee,mois)
    return {"status":"ok","liste":liste}

@router.post("/")
async def process(data:ProcessRequest):
    if data.month is not None and (data.month < 1 or data.month > 12):
        raise HTTPException(
            status_code=400,
            detail="Mois invalide"
        )

    
    if not data.columnList:
        raise HTTPException(
            status_code=400,
            detail="Aucune colonne sélectionnée"
        )
    
    try:
        files=packetMain(data.columnList,data.year,data.month)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pas de données pour annee:{data.year}, mois ={data.month}")
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Pas de données pour annee:{data.year}, mois ={data.month}")
    return {"status":"ok","images":files}
    