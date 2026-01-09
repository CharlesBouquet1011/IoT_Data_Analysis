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
from cachetools import TTLCache, cached
cache = TTLCache(maxsize=100, ttl=120) #TTL de 120 secondes, max 100 éléments mémorisés cache nécessaire pour accélérer les algos
#peu intéressant d'optimiser comme c'est surtout des essais de différentes méthodes

def open_processed_df(file:str)->pd.DataFrame:
    """
    Docstring for open_processed_df
    Ouvre le fichier spécifié en tant que dataframe

    :param file: chemin du fichier
    :type file: str
    :return: Dataframe correspondant au json choisi
    :rtype: DataFrame
    """
    df= pd.read_json(file,orient="index")
    return df
@cached(cache) #cache pour accès plus rapide
def Ouvre_Json_Util(path)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Util
    Ouvre des JSON globalement, utilisé dans les autres fonctions uniquement

    :param path: Description
    :return: Description
    :rtype: DataFrame
    """
    list_df=[]
    for root,dirs,files in os.walk(path):
        for file in files:
            file=os.path.join(root,file)
            tempDf=open_processed_df(file)
            if (tempDf.empty or tempDf.isna().all(axis=None)) and len(list_df)>0:
                continue #on ne veut pas ajouter notre DataFrame s'il n'y a rien dedans
            list_df.append(tempDf)
    df=pd.concat(list_df,axis=0,join='outer')
    return df

def Ouvre_Tous_Json()->pd.DataFrame:
    """
    Docstring for Ouvre_Tous_Json
    Ouvre toutes les données enregistrées
    :return: Description
    :rtype: DataFrame
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data")
    return Ouvre_Json_Util(path)

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
    
def Ouvre_Json_Mois_Toutes_Annees(mois:int)->pd.DataFrame:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root=os.path.join(script_dir,"Data")
    temp=[Ouvre_Json_Mois(annee,mois) for annee in os.listdir(root)]
    return pd.concat(temp,axis=0,join="outer")

def Ouvre_Json_Cat_Mois_Toutes_Annees(mois:int,categorie:str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root=os.path.join(script_dir,"Data")
    temp=[Ouvre_Json_Mois_Categorie(annee,mois,categorie) for annee in os.listdir(root)]
    return pd.concat(temp,axis=0,join="outer")
def Ouvre_Json_Mois(annee:int,mois:int)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Mois
    Ouvre toutes les catégories du mois sélectionné
    :param annee: année du mois choisi
    :type annee: int
    :param mois: mois choisi (de 1 à 12)
    :type mois: int
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data",str(annee),str(mois))
    return Ouvre_Json_Util(path)

def Ouvre_Json_Mois_Categorie(annee:int,mois:int,Categorie:str)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Mois_Categorie
    Importe dans un Dataframe les données correspondants à l'année, au mois et à la catégorie sélectionnés

    :param annee: année choisie
    :type annee: int
    :param mois: mois choisi (de 1 à 12)
    :type mois: int
    :param Categorie: Catégorie de data (par exemple Confirmed Data Up)
    :type Categorie: str
    :return: le dataframe correspondant aux données sélectionées
    :rtype: DataFrame
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file=os.path.join(script_dir,"Data",str(annee),str(mois),Categorie+".json")
    df=open_processed_df(file)
    return df
@cached(cache) #cache pour accès plus rapide
def Ouvre_Json_Cat_Util(path:str,cat:str)->pd.DataFrame: 
    """
    Docstring for Ouvre_Json_Cat_Util
    Fonction globalement utilisée pour ouvrir des json en fonction d'une catégorie

    :param path: chemin du répertoire où on cherche
    :type path: str
    :param cat: Catégorie choisie
    :type cat: str
    :return: DataFrame des données trouvées
    :rtype: DataFrame
    """
    list_df=[]
    for root,dirs,files in os.walk(path):
        for file in files:
            if cat in file:#on veut que le nom du fichier contienne le nom de la catégorie
                file=os.path.join(root,file)
                tempDf=open_processed_df(file)
                if (tempDf.empty or tempDf.isna().all(axis=None)) and len(list_df)>0:
                    continue #on ne veut pas ajouter notre DataFrame s'il n'y a rien dedans
                list_df.append(tempDf)
    df=pd.concat(list_df,axis=0,join='outer')
    return df

def Ouvre_Json_Categorie(Categorie:str)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Categorie
    Importe dans un Dataframe tous les JSON de la catégorie choisie

    :param Categorie: Catégorie choisie (par exemple Confirmed Data Up)
    :type Categorie: str
    :return: données correspondantes à la catégorie choisie
    :rtype: DataFrame
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data")
    return Ouvre_Json_Cat_Util(path,Categorie)

def Ouvre_Json_Categorie_Annee(annee:int,Categorie:str)->pd.DataFrame:
    """
    Docstring for Ouvre_Json_Categorie_Annee
    Importe en DataFrame tous les json de la catégorie et de l'année choisis

    :param annee: année choisie
    :type annee: int
    :param Categorie: catégorie choisie (exemple Confirmed Data Up)
    :type Categorie: str
    :return: Données correspondantes
    :rtype: DataFrame
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data",str(annee))
    return Ouvre_Json_Cat_Util(path,Categorie)

def Ouvre_Tous_Json_Cat(cat:str)->pd.DataFrame:
    """
    Docstring for Ouvre_Tous_Json_Cat
    
    :param cat: Catégorie
    :type cat: str
    :return: Données correspondantes
    :rtype: DataFrame
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path=os.path.join(script_dir,"Data")
    return Ouvre_Json_Cat_Util(path,cat)

@cached(cache) #cache pour accès plus rapide
def Choose_Open(year:int=None,month:int=None,categories:tuple=None)->pd.DataFrame: 
    #à tester quand je serai branché sur secteur et pas dans un train
    """
    Docstring for Choose_Open
    
    Choisis la meilleure fonction à utiliser en fonction des paramètres fournis
    :param year: année ou None
    :type year: int
    :param month: mois ou None
    :type month: int
    :param categories: Liste des catégories ou None ou liste vide
    :type categories: list
    :return: Description
    :rtype: DataFrame
    """
    try:
        if (year and month and categories):
            temp=[Ouvre_Json_Mois_Categorie(year,month,cat) for cat in categories]
            df=pd.concat(temp,axis=0,join='outer')
            return df
        elif (not year and not month and not categories):
            return Ouvre_Tous_Json() #on a rien donc on ouvre tout
        elif (year and month and not categories):
            return Ouvre_Json_Mois(year,month)
        elif (year and not month and not categories):
            return Ouvre_Json_Annee(year)
        elif (year and not month and categories):
            temp=[Ouvre_Json_Categorie_Annee(year,cat) for cat in categories]
            return pd.concat(temp,axis=0,join="outer")
        elif (not year and not month and categories):
            temp=[Ouvre_Tous_Json_Cat(cat) for cat in categories]
            return pd.concat(temp,axis=0,join="outer")
        elif (not year and month and categories):
            temp=[Ouvre_Json_Cat_Mois_Toutes_Annees(month,categorie) for categorie in categories]
            return pd.concat(temp,axis=0,join="outer")
        elif (not year and month and not categories):
            return Ouvre_Json_Mois_Toutes_Annees(month)
        #normalement tous les cas possibles sont gérés, je ne peux pas avoir month sans avoir year
    except FileNotFoundError:
        print("fichier non trouvé")
        return pd.DataFrame()
    except ValueError:
        print("fichier non trouvé")
        return pd.DataFrame()


if __name__=="__main__":
    df=Ouvre_Json_Mois_Categorie(2025,1,"sd")
    print(df)