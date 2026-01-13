from data_processing import RepartitionCaracteristiqueGlobale,RepartitionCaracteristiqueParCategorie,Proportion_ADR_Cat,nombreDevices,ColumnsList,RepartitionAdrGlobale,plotHistogramGlobal,plotHistogrammeParType
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
    aliases={"Bandwidth":"Bandwidth","Coding_rate":"Coding Rate","GW_EUI": "Id Gateway","SF":"Spreading Factor","freq":"sous bande",
             "modu":"modulation","adr":"Adaptive Data Rate",
             "BitRate":"BitRate","Airtime":"Durée de vol","lsnr":"SNR","rssi":"Puissance du signal reçu","size":"taille du paquet",
             "rfch":"RF Chain"
             }
    files={}
    histogrammes=set(["BitRate","Airtime","lsnr","rssi","size"])#métriques qui doivent être analysées par histogramme
    try:
        for column in data.columnList:
            dictionnaireCat={}
            alias=aliases[column] #pas de gestion pour voir s'il envoit un truc dedans ou pas, pas le temps, personne va modifier le javascript pour un projet comme ça
            if column=="adr": #fonction spéciale
                dictionnaireCat.update(Proportion_ADR_Cat(data.year,data.month))
                dictionnaireCat.update(RepartitionAdrGlobale(data.year,data.month))
            elif column in histogrammes:
                dictionnaireCat.update(plotHistogrammeParType(column,alias,data.year,data.month))
                dictionnaireCat.update(plotHistogramGlobal(column,alias,data.year,data.month))
            else:
                dictionnaireCat.update(RepartitionCaracteristiqueGlobale(column,alias,data.year,data.month))
                dictionnaireCat.update(RepartitionCaracteristiqueParCategorie(column,alias,data.year,data.month))
            files[column]=dictionnaireCat
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pas de données pour annee:{data.year}, mois ={data.month}")
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Pas de données pour annee:{data.year}, mois ={data.month}")
    return {"status":"ok","images":files}
    