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
import dask_cudf
import cudf

#en forme de procédure pour la lisibilité

def produce_dataset(df:dask_cudf.DataFrame,verbose:bool,undefined_toggle:bool,outlier_toggle:bool,duree,selected_attrs:list,fichier_sortie:str,Type:str):
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
        df=df.dropna(subset=selected_attrs) #on veut trier uniquement sur les attributs renseignés
    #on marque les entrées aberrantes puis on les supprimera dans un 2nd temps
    #sinon on pourrait supprimer des valeurs qui n'étaient pas si aberrantes que ça
    df["outlier"]=False
    if outlier_toggle:
        for attr in selected_attrs:
            if df[attr].dtype.kind in 'if': #if = int ou float, donc on vérifie qu'on a soit i soit f
                #duree peut être soit une durée en temps "7d" soit un nombre de points
                q1, q3 = df[attr].quantile([0.25, 0.75], interpolation="linear").compute() #plus de fenêtre glissante car pas possible sur GPU efficacement
                IQRange=q3-q1   #écart interquartile
                df["outlier"]=(df["outlier"]) | (df[attr]<=(q1-1.5*IQRange)) | (df[attr]>=(q3+1.5*IQRange)) 
        df=df[~ df["outlier"]]
        
    df=df.drop("outlier",axis=1)
    df.to_parquet(fichier_sortie, compression="zstd")    
    print("custom_dataset.parquet generated successfully.") # VERBOSE terminé !
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



def sub_df_by_column(df:dask_cudf.DataFrame,column:str)->dict:
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

def split_df_by_month(df:dask_cudf.DataFrame):
    dic={(int(year),int(month)): sub for (year,month),sub in df.groupby([df.year,df.index.month])}
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
    df=dask_cudf.read_parquet(flat_output_path)
     # TEST 1 : Est-ce que le parquet se lit correctement ?
    print("=== TEST LECTURE PARQUET ===")
    try:
        test = df.head(1).compute()
        print("Lecture parquet: OK")
        print(f"Index type: {test.index.dtype}")
    except Exception as e:
        print(f"Lecture parquet: ERREUR - {e}")
    print("============================")
    df=df.reset_index(drop=True)
    print("=== TEST LECTURE PARQUET ===")
    try:
        test = df.head(1).compute()
        print("reset index: OK")
        print(f"Index type: {test.index.dtype}")
    except Exception as e:
        print(f"Reset Index: ERREUR - {e}")
    print("============================")
    if df["@timestamp"].dtype == 'object' or df["@timestamp"].dtype == 'string':
        df["@timestamp"] = df["@timestamp"].map_partitions(
            cudf.to_datetime,
            meta=('timestamp', 'datetime64[ns]')
        )
    df=addNwkOperator(df) #le merge ici MODIFIE l'index
     # TEST 1 : Est-ce que le parquet se lit correctement ?
    print("=== TEST LECTURE PARQUET ===")
    try:
        test = df.head(1).compute()
        print("nwk operatort: OK")
        print(f"Index type: {test.index.dtype}")
    except Exception as e:
        print(f"nwk operator: ERREUR - {e}")
    print("============================")
    df=addColAdr(df)
     # DEBUG : afficher les types de TOUTES les colonnes
    print("=== TYPES DE COLONNES ===")
    for col in df.columns:
        print(f"{col}: {df[col].dtype}")
    print("=========================")
    print("=== TEST COMPUTE PAR COLONNE ===")
    for col in df.columns:
        try:
            result = df[col].head(1).compute()
            print(f"{col}: OK")
        except Exception as e:
            print(f"{col}: ERREUR - {str(e)[:100]}")
    print("================================")
    # Créer des colonnes temporaires pour grouper par année/mois
    df["_year"] = df["@timestamp"].dt.year.astype('int64')
    df["_month"] = df["@timestamp"].dt.month.astype('int64')

    # Récupérer juste les combinaisons qui existent réellement en persitant le df
    df_persisted = df.persist()  # Garde le df en mémoire GPU
    
    # Utiliser to_pandas directement pour éviter les problèmes de type cudf
    unique_combos = df_persisted[["_year", "_month", "Type"]].drop_duplicates().compute().to_pandas()
    
    # Itérer sur les combinaisons réelles
    for _, row in unique_combos.iterrows():
        year, month, t = int(row["_year"]), int(row["_month"]), str(row["Type"])
        
        # Filtrer le dataframe pour cette combinaison
        subDf = df_persisted[(df_persisted["_year"] == year) & 
                             (df_persisted["_month"] == month) & 
                             (df_persisted["Type"] == t)]
        
        os.makedirs(os.path.join(script_dir,"Data",str(year),str(month)),exist_ok=True)
        outputFile=os.path.join(script_dir,"Data",str(year),str(month),t+".parquet")
        produce_dataset(subDf,True,True,True,rolling_interval,attrList,outputFile,t)

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

    