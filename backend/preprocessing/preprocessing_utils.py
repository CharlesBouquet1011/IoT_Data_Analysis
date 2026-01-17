# Copyright 2025 Charles Bouquet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Fichier regroupant toutes les fonctions utiles au preprocessing des donnes

By Charles Bouquet
"""
from .flatten_datas import flatten_datas
#from .query_elk import download_data
from datetime import datetime
from .txtUtils import write_log_removed
from .RawParsing import addColAdr
from .netId import addNwkOperator
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg') #backend non interactif
import matplotlib.pyplot as plt
#en forme de procédure pour la lisibilité

def produce_dataset(df:pd.DataFrame,verbose:bool,undefined_toggle:bool,outlier_toggle:bool,duree,selected_attrs:list,fichier_sortie:str,Type:str):
    """
    

    Entrées:
    df: le DataFrame à nettoyer
    verbose: log ou non
    undefined_toggle: vire ou non les paquets ayant des champs vides
    outlier_toggle: vire ou non les paquets qui ont des valeurs aberrantes
    duree: soit nombre de points pour la fenêtre glissante du calcul d'écart interquartile soit durée pour le faire (pour prendre en compte la potentielle saisonnalité des données)
    selected_attrs: la liste des attributs concernés par le nettoyage des outliers
    fichier_sortie: chemin du fichier de sortie
    """
    if verbose:  print("Producing custom dataset") 

    
    if verbose: print(f"Selected attributes: {selected_attrs}") # VERBOSE affichage des attributs sélectionnés
    if undefined_toggle:
        initial_count = len(df)
        df.dropna(inplace=True,axis=0,subset=selected_attrs,how="any") #on veut trier uniquement sur les attributs renseignés
        if verbose: 
            message=f"{Type}: Removed {initial_count - len(df)} packets with undefined values from {initial_count} initial packets.\n it is {(initial_count-len(df))*100/initial_count} % \n\n"
            print(f"durée = {duree}") # VERBOSE affichage du contenu de la variable durée
            print(message) # VERBOSE affichage du nombre de paquets supprimés car attribut non défini
            write_log_removed(message)
    #on marque les entrées aberrantes puis on les supprimera dans un 2nd temps
    #sinon on pourrait supprimer des valeurs qui n'étaient pas si aberrantes que ça
    df["outlier"]=False
    print(df.head)
    print(f"Index name: {df.index.name}")
    if outlier_toggle:
        for attr in selected_attrs:
            if pd.api.types.is_numeric_dtype(df[attr]):
                #duree peut être soit une durée en temps "7d" soit un nombre de points
                print("durée :",duree)
                q1=df[attr].rolling(duree).quantile(0.25) #premier quartile  (fenêtre glissante)
                q3=df[attr].rolling(duree).quantile(0.75)#dernier quartile (fenêtre glissante)
                IQRange=q3-q1   #écart interquartile
                df["outlier"]=(df["outlier"]) | (df[attr]<=(q1-1.5*IQRange)) | (df[attr]>=(q3+1.5*IQRange)) 
        df=df[~ df["outlier"]]
        
    if verbose: print(f"Remaining packets after processing: {len(df)}") # VERBOSE sauvegarde du dataset
    df.reset_index(inplace=True)
    df=addColAdr(df)
    df=addNwkOperator(df) #le merge ici MODIFIE l'index
    df.drop("outlier",axis=1,inplace=True)
    print(f"Colonnes avant sauvegarde: {df.columns.tolist()}")
    df.to_parquet(fichier_sortie, engine="pyarrow", compression="zstd") #il faudra readJson avec orient="index"
    print("custom_dataset.json generated successfully.") # VERBOSE terminé !
    return df #au cas où



def plot_timeSeries(df:pd.DataFrame,attrs:list,begin=None,end=None):
    """
    Le nom est explicite
    """
    t=datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    
    CurrentDir = os.path.dirname(os.path.abspath(__file__))
    plotDir=os.path.join(CurrentDir,"Export",t)
    os.makedirs(plotDir)
    if begin is not None:
        subset=df.loc[begin:]
        if end is not None:
            subset=subset.loc[:end]
    else:
        subset=df.loc[:end]
    #on garde que les valeurs dans l'intervalle si le début et la fin sont définies
    for attr in attrs:
        plt.figure()
        subset[attr].plot()
        plt.savefig(os.path.join(plotDir,attr))

def calcul_Gte_Lt(year:int,month:int):
    """
    Prend en paramètre l'année et le mois concerné (des entiers)
    """
    premierJour= datetime(year,month,1,0,0,0) #premier jour du mois
    #calcul du mois suivant
    if month==12:
        month=1
        year+=1
    else:
        month+=1
    DernierJour=datetime(year,month,1,0,0,0)
    return premierJour.isoformat(),DernierJour.isoformat()



def sub_df_by_column(df:pd.DataFrame,column:str)->dict:
    """
    Docstring for sub_df_by_column
    Renvoie les sous DataFrame du DataFrame filtré par valeur d'une colonne

    :param df: le Dataframe concerné
    :type df: pd.DataFrame
    :param column: Description
    :type column: str
    """
    groupe=df.groupby(column)
    return {Cat:val for Cat, val in groupe}

def split_df_by_month(df:pd.DataFrame):
    dic={(int(year),int(month)): sub for (year,month),sub in df.groupby([df.index.year,df.index.month])}
    return dic

def prepare_data(rolling_interval,attrList:list,file):
    """
    Crée des répertoires contenant les données rangées
    """
    #gte,lt=calcul_Gte_Lt(year,month)
    #file=download_data(gte,lt,year,month)
    script_dir = os.path.dirname(os.path.abspath(__file__))

    flat_output_path=os.path.join(script_dir,"flattened","flat.parquet")
    os.makedirs(os.path.join(script_dir,"flattened"),exist_ok=True)
    flatten_datas(file,flat_output_path)
    df=pd.read_parquet(flat_output_path)
    df["@timestamp"]=pd.to_datetime(df["@timestamp"],errors="coerce",utc=True)
    df.set_index("@timestamp",inplace=True)
    for (year,month),monthlyDf in split_df_by_month(df).items():
        file=flat_output_path
        
        dfs=sub_df_by_column(monthlyDf,"Type")
        for Type,subDf in dfs.items():
            os.makedirs(os.path.join(script_dir,"Data",str(year),str(month)),exist_ok=True)
            outputFile=os.path.join(script_dir,"Data",str(year),str(month),Type+".parquet")
            produce_dataset(subDf,False,True,True,rolling_interval,attrList,outputFile,Type)

def open_df_flattened(fichier:str)->pd.DataFrame:
    """
    Docstring for open_df
    
    :param fichier: chemin du fichier flattened
    :type fichier: str
    :return: dataframe correspondant à ce fichier
    :rtype: DataFrame
    """

    dfs = []
    for chunk in pd.read_json(fichier, lines=True, chunksize=100_000):
        dfs.append(chunk)
    df = pd.concat(dfs, ignore_index=True)
    df["@timestamp"]=pd.to_datetime(df["@timestamp"],errors="coerce",utc=True)
    df.set_index("@timestamp",inplace=True)
    return df


if __name__=="__main__":
    #tests
    #lancer le script EN TANT QUE MODULE, sinon ça ne fonctionnera pas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file=os.path.join(script_dir,"Raw","raw.json")
    prepare_data(30,["BitRate","rssi","lsnr"],file)

    