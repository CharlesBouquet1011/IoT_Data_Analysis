import pandas as pd
import os
def open_processed_df(file:str):
    df= pd.read_json(file,orient="index")
    return df

def Ouvre_Json(annee:int):
    """
    Docstring for Ouvre_Json
    Fonction qui renvoie un df à partir de l'année que l'on veut importer
    :param annee: annee que l'on veut importer
    :type annee: int
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.join(script_dir,annee)
    
    list_df=[]
    for root,dirs,files in os.walk(path):
        for file in files:
            tempDf=open_processed_df(file)
            if tempDf.empty or tempDf.isna().all(axis=None):
                continue #on ne veut pas ajouter notre DataFrame s'il n'y a rien dedans
            list_df.append(tempDf)
    df=pd.concat(list_df,axis=0,join='outer')
    return df
