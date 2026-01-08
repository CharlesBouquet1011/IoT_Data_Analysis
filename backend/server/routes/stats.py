from data_processing import RepartitionCaracteristiqueGlobale,RepartitionCaracteristiqueParCategorie,Repartition_ADR_Cat,nombreDevices,ColumnsList,RepartitionAdrGlobale
from fastapi import APIRouter,HTTPException
import os
from server.models.stats.processing import ProcessRequest

router = APIRouter(prefix="/api/stats", tags=["stats"])
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(script_dir)
image_dir=os.path.join(parent_dir,"Images")
data_dir=os.path.join(parent_dir,"preprocessing","Data")
raw_data_dir=os.path.join(parent_dir,"preprocessing","Raw")


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
    aliases={"Bandwidth":"Bandwidth","Coding_rate":"Coding Rate","GW_EUI": "Id Gateway","SF":"Spreading Factor","freq":"sous bande",
             "modu":"modulation","adr":"Adaptive Data Rate"
             }
    files={}
    for column in data.columnList:
        dictionnaireCat={}
        alias=aliases[column] #pas de gestion pour voir s'il envoit un truc dedans ou pas, pas le temps, personne va modifier le javascript pour un projet comme ça
        if column=="adr": #fonction spéciale
            dictionnaireCat.update(Repartition_ADR_Cat(data.year,data.month))
            dictionnaireCat.update(RepartitionAdrGlobale(data.year,data.month))
        else:
            dictionnaireCat.update(RepartitionCaracteristiqueGlobale(column,alias,data.year,data.month))
            dictionnaireCat.update(RepartitionCaracteristiqueParCategorie(column,alias,data.year,data.month))
        files[column]=dictionnaireCat
    print(files)
    return {"status":"ok","images":files}
    