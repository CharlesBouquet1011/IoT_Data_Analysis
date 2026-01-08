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
Docstring for backend.data_processing.stats.paquets
"""
from preprocessing.useData import Choose_Open #pour executer ce fichier or du serveur, rajouter ... devant le module
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from numpy import ndarray
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")

def GatewayList(annee:int=None,mois:int=None)->ndarray:
    df=Choose_Open(annee,mois,["Join Request"])
    gateway=df["GW_EUI"].unique()
    return gateway

def GetListValues(caracteristique:str,annee:int=None,mois:int=None)->ndarray:
    """
    Docstring for GetList
    Renvoie la liste de toutes les valeurs possibles d'une colonne caracteristique
    :param caracteristique: la colonne du DataFrame
    :param annee: Description
    :type annee: int
    :param mois: Description
    :type mois: int
    :return: Description
    :rtype: ndarray[_AnyShape, dtype[Any]]
    """
    if caracteristique=="GW_EUI": ##cas spécial, on a cette caractéristique que dans les paquets Join Request,
        #ça fonctionne probablement sans ce if mais je préfère ne pas prendre de risque
        return GatewayList(annee,mois)
    df=Choose_Open(annee,mois)
    liste=df[caracteristique].unique()
    liste.sort()
    return liste


def _proportionCaraCat(caracteristique:str,valeurCaracteristique,alias:str,annee:int=None,mois:int=None,categorie:str=None,repartitions:list=None):
    """
    Docstring for _proportionCaraCat
    Renvoie la répartition d'une caractéristique selon plusieurs catégories

    :param caracteristique: La colonne du DatFrame concernée
    :type caracteristique: str
    :param valeurCaracteristique: La valeur concernée pour déterminer son pourcentage
    :param alias: Description
    :type alias: str
    :param annee: Description
    :type annee: int
    :param mois: Description
    :type mois: int
    :param categorie: Description
    :type categorie: str
    :param repartitions: Description
    :type repartitions: list
    """
    df=Choose_Open(annee,mois,[categorie])
    nombre=len(df[df[caracteristique]==valeurCaracteristique])
    tot=len(df)
    taux=nombre/tot 
    repartitions.append({"categorie":categorie,alias:taux})

def ColumnsList(annee:int=None,mois:int=None)->list:
    df=Choose_Open(annee,mois)
    return df.columns.values.tolist()

def RepartitionCaracteristiqueParCategorie(caracteristique:str,alias:str,annee:int=None,mois:int=None)->dict:
    """
    Docstring for RepartitionCaracteristiqueParCategorie
    Crée des histogrammes de répartition par valeur et par catégorie, chaque valeur de la caractéristique (colonne du DataFrame)
    est un fichier différent avec chaque caractéristique sur chaque fichier

    :param caracteristique:  intitulé de la caractéristique tel que présent dans le paquet
    :type caracteristique: str
    :param alias: nom couramment utilisé de la caractéristique
    :type alias: str
    :param annee: Description
    :type annee: int
    :param mois: Description
    :type mois: int
    :return: Description
    :rtype: list[str]
    """
    plot_files={}
    for valeurCaracteristique in GetListValues(caracteristique,annee,mois):
        repartitions=[]
        #{nomImage:cheminImage}
        plot_file=os.path.join(plot_dir,f"Repartition_{alias.replace("/","-")}_Categories_{str(valeurCaracteristique).replace("/","-")}.webp")
        [_proportionCaraCat(caracteristique,valeurCaracteristique,alias,annee,mois,categorie,repartitions) for categorie in categories] #plots
        df=pd.DataFrame(repartitions).set_index("categorie")
        df.plot(kind='bar',legend=False)
        plt.ylabel("Taux")
        plt.xlabel(alias)
        plt.title(f"Proportion {caracteristique}={valeurCaracteristique} par categorie")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(plot_file)
        plot_files[f"{caracteristique}={valeurCaracteristique}"]=plot_file
        plt.close()
    return plot_files
        

def _proportionCaracteristique(annee,mois,repartitions,caracteristique,nomCaracteristique,valeurCaracteristique):
    df=Choose_Open(annee,mois)
    nombre=len(df[df[caracteristique]==valeurCaracteristique])
    tot=len(df)  
    taux=nombre/tot
    repartitions.append({nomCaracteristique:valeurCaracteristique,"taux":taux})  

def RepartitionCaracteristiqueGlobale(caracteristique:str,alias:str,annee:int=None,mois:int=None)->dict:
    """
    Docstring for RepartitionCaracteristiqueGlobale
    Crée des histogrammes de répartition par valeur selon la caractéristique (colonne du DataFrame) indiquée

    :param caracteristique: intitulé de la caractéristique tel que présent dans le paquet
    :type caracteristique: str
    :param alias: Nom couramment utilisé de la caractéristique
    :type alias: str
    :param annee: Description
    :type annee: int
    :param mois: Description
    :type mois: int
    :return: nom et chemin du fichier créé
    :rtype: dict
    """
    repartitions=[]
    plot_file=os.path.join(plot_dir,f"Repartition_{alias}_Globale.webp")
    [_proportionCaracteristique(annee,mois,repartitions,caracteristique,alias,gw) for gw in GetListValues(caracteristique,annee,mois)] #plots
    df=pd.DataFrame(repartitions).set_index(alias)
    df.plot(kind='bar',legend=False)
    nom=f"Proportion {alias} globale"
    plt.ylabel("Taux")
    plt.title(nom)
    plt.xlabel(alias)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}

def plotHistogramGlobal(caracteristique:str,alias:str,annee:int=None,mois:int=None):
    plot_file=os.path.join(plot_dir,f"Histogramme_{alias}_Global.webp")
    df=Choose_Open(annee,mois)
    df.hist(column=caracteristique,legend=True)
    nom=f"Histogramme {alias} globale"
    plt.ylabel("nombre d'occurrences")
    plt.title(nom)
    plt.xlabel(alias)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}
def plotHistogrammeParType(caracteristique:str,alias:str,annee:int|None=None,mois:int|None=None):
    plot_file=os.path.join(plot_dir,f"Histogramme_{alias}_Categorie.webp")
    df=Choose_Open(annee,mois)
    df.hist(column=caracteristique,legend=True,by="Type",
            figsize=(16, 8),      # Plus large et plus haut
            layout=(2, 4),        # 2 lignes, 4 colonnes = 8 subplots
            sharex=True
            )
    nom=f"Histogrammes {alias} par type de paquet"
    plt.ylabel("nombre d'occurrences")
    plt.suptitle(nom)
    plt.xlabel(alias)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}
if __name__=="__main__":
    execution={"GW_EUI":"gateway","Bandwidth":"BW","SF":"Spreading Factor","codr":"coding rate","freq":"Sous Bande"}
    plotHistogramGlobal("lsnr","SNR")
    plotHistogrammeParType("lsnr","SNR")
    for caracteristique,alias in execution.items():

        RepartitionCaracteristiqueParCategorie(caracteristique,alias)
        RepartitionCaracteristiqueGlobale(caracteristique,alias)
