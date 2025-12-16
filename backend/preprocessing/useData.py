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
By Charles Bouquet
Docstring for preprocessing.useData
Sert à importer les données enregistrées en json dans le système de fichiers
erreurs soulevées: ValueError pour toutes les fonctions sauf Ouvre_Json_Mois_Categorie: FileNotFoundError 
Pour chaque fonction, on suppose que le fichier cherché existe, ça revient à l'utilisateur des fonctions de faire un try except au cas où
Fonctions:
open_processed_df:
    ouvre juste un df en fonction de comment il a été enregistré
Ouvre_Json_Util:
    Code réutilisé à plusieurs endroits pour ouvrir plusieurs JSON et concaténer les DF
Ouvre_Json_Annee:
    Ouvre tous les JSON d'une année donnée (quel que soit le mois et le type de paquet)
Ouvre_Json_Mois:
    Ouvre tous les JSON d'un mois donné (quel que soit le mois et le type de paquet)
Ouvre_Json_Mois_Categorie:
    Ouvre le JSON spécifié (d'un mois précis et d'un type de paquet précis)
Ouvre_Json_Cat_Util:
    Code réutilisé dans les deux fonctions suivantes pour ouvrir les JSON d'un chemin et d'une catégorie donnée
Ouvre_Json_Categorie:
    Renvoie un Dataframe à partir de tous les JSON de la Catégorie correspondante (quels que soient les mois ou les années)
Ouvre_Json_Categorie_Annee:
    Renvoie un Dataframe à partir de tous les JSON de l'année et de la Catégorie correspondante (quel que soit le mois)
"""

import pandas as pd
import os
def open_processed_df(file:str):
    df= pd.read_json(file,orient="index")
    return df

def Ouvre_Json_Util(path)->pd.DataFrame:
    list_df=[]
    for root,dirs,files in os.walk(path):
        for file in files:
            file=os.path.join(root,file)
            tempDf=open_processed_df(file)
            if tempDf.empty or tempDf.isna().all(axis=None):
                continue #on ne veut pas ajouter notre DataFrame s'il n'y a rien dedans
            list_df.append(tempDf)
    df=pd.concat(list_df,axis=0,join='outer')
    return df

def Ouvre_Json_Annee(annee:int)->pd.DataFrame:
    """
    Docstring for Ouvre_Json
    Ouvre toutes les catégories de l'année sélectionnée
    Fonction qui renvoie un df à partir de l'année que l'on veut importer
    :param annee: annee que l'on veut importer
    :type annee: int
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data",str(annee))
    return Ouvre_Json_Util(path)
    


def Ouvre_Json_Mois(annee:int,mois:int)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Mois
    Ouvre toutes les catégories du mois sélectionné
    :param annee: Description
    :type annee: int
    :param mois: Description
    :type mois: int
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data",str(annee),str(mois))
    return Ouvre_Json_Util(path)

def Ouvre_Json_Mois_Categorie(annee:int,mois:int,Categorie:str)->pd.DataFrame:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file=os.path.join(script_dir,"Data",str(annee),str(mois),Categorie+".json")
    df=open_processed_df(file)
    return df

def Ouvre_Json_Cat_Util(path:str,cat:str)->pd.DataFrame: #à tester
    list_df=[]
    for root,dirs,files in os.walk(path):
        for file in files:
            if cat in file:#on veut que le nom du fichier contienne le nom de la catégorie
                file=os.path.join(root,file)
                tempDf=open_processed_df(file)
                if tempDf.empty or tempDf.isna().all(axis=None):
                    continue #on ne veut pas ajouter notre DataFrame s'il n'y a rien dedans
                list_df.append(tempDf)
    df=pd.concat(list_df,axis=0,join='outer')
    return df

def Ouvre_Json_Categorie(Categorie:str)->pd.DataFrame:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data")
    return Ouvre_Json_Cat_Util(path,Categorie)

def Ouvre_Json_Categorie_Annee(annee:int,Categorie:str)->pd.DataFrame:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data",str(annee))
    return Ouvre_Json_Cat_Util(path,Categorie)


if __name__=="__main__":
    df=Ouvre_Json_Mois_Categorie(2025,1,"sd")
    print(df)