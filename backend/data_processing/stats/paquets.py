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
import numpy as np
from .adr import Proportion_ADR_Cat,RepartitionAdrGlobale

categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")

def GatewayList(df:pd.DataFrame,annee:int=None,mois:int=None)->ndarray:
    df=df[df["Type"]=="Join Request"]
    gateway=df["GW_EUI"].unique()
    return gateway

def GetListValues(df:pd.DataFrame,caracteristique:str,annee:int=None,mois:int=None)->ndarray:
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
        return GatewayList(df,annee,mois)
    liste=df[caracteristique].unique()
    
    valides = [x for x in liste if x is not None and pd.notna(x)] #ce qu'on peut sort
    nones = [x for x in liste if x is None or pd.isna(x)] # NA (on ne peut pas sort)
    
    valides.sort()
    return valides + nones
    
def _RepartitionCaraCat(df,caracteristique:str,valeurCaracteristique,alias:str,annee:int=None,mois:int=None,categorie:str=None,repartitions:list=None):
    """
    Docstring for _proportionCaraCat
    Renvoie la répartition selon les types de paquets dans une caractéristique

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
    dfCat=df[df["Type"]==categorie]
    nombre=len(dfCat[dfCat[caracteristique]==valeurCaracteristique])
    tot=len(df[df[caracteristique]==valeurCaracteristique])
    if tot!=0:
        taux=nombre/tot 
    else:
        taux=0
    repartitions.append({"categorie":categorie,alias:taux})
def _proportionCaraCat(df:pd.DataFrame,caracteristique:str,valeurCaracteristique,alias:str,annee:int=None,mois:int=None,categorie:str=None,repartitions:list=None):
    """
    Docstring for _proportionCaraCat
    Renvoie la proportion de paquets d'une catégorie qui correspondent à cette caractéristique

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
    df=df[df["Type"]==categorie]
    nombre=len(df[df[caracteristique]==valeurCaracteristique])
    tot=len(df)
    if categorie == "Confirmed Data Down":
        print(df[[caracteristique]].value_counts(dropna=False))
    if tot!=0:
        taux=nombre/tot 
    else:
        taux=0
        print(caracteristique,"==",valeurCaracteristique,"=0")

    repartitions.append({"categorie":categorie,alias:taux})

def ColumnsList(annee:int=None,mois:int=None)->list:
    df=Choose_Open(annee,mois)
    return df.columns.values.tolist()

def RepartitionCaracteristiqueParCategorie(dftot:pd.DataFrame,caracteristique:str,alias:str,annee:int=None,mois:int=None)->dict:
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
    if caracteristique=="Operator":
        dftot=dftot[~(dftot["Type"].isin(["Join Accept","Confirmed Data Down","Unconfirmed Data Down","Join Accept"]))]#on drop le downlink + Join Request
        cats=["Confirmed Data Up","Proprietary","RFU","Unconfirmed Data Up"]
    else:
        cats=categories
    for valeurCaracteristique in GetListValues(dftot,caracteristique,annee,mois):
        repartitions=[]
        ul=set(["Confirmed Data Up","Join Request","Unconfirmed Data Up"])
        dl=set(["Confirmed Data Down","Join Accept","Unconfirmed Data Down"])
        #{nomImage:cheminImage}
        plot_file=os.path.join(plot_dir,f"Proportion_Paquets_{alias.replace("/","-")}={str(valeurCaracteristique).replace("/","-")}.webp")
        [_proportionCaraCat(dftot,caracteristique,valeurCaracteristique,alias,annee,mois,categorie,repartitions) for categorie in cats] #plots 
        df=pd.DataFrame(repartitions).set_index("categorie")
        couleurs=["skyblue" if cat in ul else "salmon" if cat in dl else "grey" for cat in df.index.str.strip()]
        plt.figure()
        plt.bar(np.arange(len(df)), df[alias], color=couleurs)
        plt.xticks(np.arange(len(df)), df.index, rotation=45, ha='right')
        plt.ylabel("Proportion")
        plt.ylim(top=min(df.max().max(),1))
        plt.xlabel(alias)
        plt.title(f"Proportion of Packets where {caracteristique}={valeurCaracteristique} by category")
        plt.tight_layout()
        plt.savefig(plot_file)
        plot_files[f"Proportion_{caracteristique}={valeurCaracteristique}"]=plot_file
        plt.close()
        repartitions=[]
        plot_file=os.path.join(plot_dir,f"Repartition_Type_Paquets_{alias.replace("/","-")}={str(valeurCaracteristique).replace("/","-")}.webp")
        [_RepartitionCaraCat(dftot,caracteristique,valeurCaracteristique,alias,annee,mois,categorie,repartitions) for categorie in cats] #plots
        df=pd.DataFrame(repartitions).set_index("categorie")
        couleurs=["skyblue" if cat in ul else "salmon" if cat in dl else "grey" for cat in df.index.str.strip()]
        plt.figure()
        plt.bar(np.arange(len(df)), df[alias], color=couleurs)
        plt.xticks(np.arange(len(df)), df.index, rotation=45, ha='right')
        plt.ylabel("Rate")
        plt.xlabel(alias)
        plt.title(f"Packet Type distribution where {caracteristique}={valeurCaracteristique}")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(plot_file)
        plot_files[f"Repartition_{caracteristique}={valeurCaracteristique}"]=plot_file
        plt.close()
    return plot_files
        

def _proportionCaracteristique(df:pd.DataFrame,annee,mois,repartitions,caracteristique,nomCaracteristique,valeurCaracteristique):
    nombre=len(df[df[caracteristique]==valeurCaracteristique])
    tot=len(df)  
    if caracteristique=="Operator":
        print("packet number : ", nombre)
    taux=nombre/tot
    repartitions.append({nomCaracteristique:valeurCaracteristique,"taux":taux})  

def RepartitionCaracteristiqueGlobale(dftot:pd.DataFrame,caracteristique:str,alias:str,annee:int=None,mois:int=None)->dict:
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
    if caracteristique=="Operator":
        dftot=dftot[~(dftot["Type"].isin(["Join Accept","Confirmed Data Down","Unconfirmed Data Down","Join Accept"]))]#on drop le downlink + Join Request

    [_proportionCaracteristique(dftot,annee,mois,repartitions,caracteristique,alias,gw) for gw in GetListValues(dftot,caracteristique,annee,mois)] #plots
    df=pd.DataFrame(repartitions).set_index(alias)
    df.index = df.index.map(lambda x: str(x)[:20] + '...' if len(str(x)) > 20 else str(x))
    # Somme par ligne
    row_sums = df.sum(axis=1)

    # Réorganiser les lignes selon l'ordre décroissant des sommes
    df = df.reindex(row_sums.sort_values(ascending=False).index)
    df.plot(kind='bar',legend=False)
    nom=f"Global {alias} proportion"
    plt.ylabel("Taux")
    plt.title(nom)
    plt.xlabel(alias)
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()

    plot_files = {nom:plot_file}
    #2e graphique (demandé par les profs pour mieux visualiser)
    #aidé par IA comme je ne savais pas du tout faire ça
    plot_file_detail = os.path.join(plot_dir, f"Repartition_Globale_{alias}_Detaillee_Par_Type.webp")
    
   
    total_paquets = len(dftot)
    # création d'un DataFrame dont les lignes sont les valeurs caractéristiques et les colonnes sont les types de paquets
    pivot_data = dftot.groupby([caracteristique, 'Type']).size().unstack(fill_value=0)
    
    # Normalisation
    pivot_normalized = pivot_data/total_paquets
    pivot_normalized.index = pivot_normalized.index.map(
        lambda x: str(x)[:20] + '...' if len(str(x)) > 20 else str(x)
    )
    row_sums = pivot_normalized.sum(axis=1)

    # trie par ordre décroissant de présence
    pivot_normalized = pivot_normalized.reindex(row_sums.sort_values(ascending=False).index)
    #couleurs choisies par IA
    type_colors = {
        "Confirmed Data Up": "#3498db",      # Bleu
        "Unconfirmed Data Up": "#5dade2",    # Bleu clair
        "Join Request": "#85c1e9",           # Bleu très clair
        "Confirmed Data Down": "#e74c3c",    # Rouge
        "Unconfirmed Data Down": "#ec7063",  # Rouge clair
        "Join Accept": "#f1948a",            # Rouge très clair
        "Proprietary": "#95a5a6",            # Gris
        "RFU": "#bdc3c7"                     # Gris clair
    }
    type_hatches = {
    "Confirmed Data Up": "///",
    "Unconfirmed Data Up": "\\\\\\",
    "Join Request": "xxx",
    "Confirmed Data Down": "---",
    "Unconfirmed Data Down": "...",
    "Join Accept": "++",
    "Proprietary": "oo",
    "RFU": "**"
} #motifs de hachures
    colors = [type_colors.get(cat, '#34495e') for cat in pivot_normalized.columns]
    hatches = [type_hatches.get(cat, "") for cat in pivot_normalized.columns]

    #création du graphique
    ax = pivot_normalized.plot(
        kind='bar', 
        stacked=True, 
        color=colors,
        figsize=(12, 6)
    )
    # Application des hachures
    for container, hatch in zip(ax.containers, hatches):
        for bar in container:
            bar.set_hatch(hatch)
    nom_detail = f"Global distribution of packets by {alias}"
    plt.ylabel("Proportion")
    plt.title(nom_detail)
    plt.xlabel(alias)
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.legend(title='Packet type', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    plt.tight_layout()
    plt.savefig(plot_file_detail, bbox_inches='tight')  # bbox_inches pour inclure la légende
    plt.close()
    plot_files[nom_detail] = plot_file_detail
    
    return plot_files

def plotHistogramGlobal(df:pd.DataFrame,caracteristique:str,alias:str,annee:int=None,mois:int=None):
    plot_file=os.path.join(plot_dir,f"Histogramme_{alias}_Global.webp")
    axes=df.hist(column=caracteristique,legend=True, #df.hist renvoie une liste des ax (les plots)
            density=True,
            bins="auto", #densité de proba en histogramme avec un découpage intelligent
            )
    nom=f"Global {alias} histogram"
    for ax in axes.flatten():
        ax.set_xlabel(alias)       # axe X
        ax.set_ylabel("Proportion")# axe Y
    plt.suptitle(nom)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}
def plotHistogrammeParType(df:pd.DataFrame,caracteristique:str,alias:str,annee:int|None=None,mois:int|None=None):
    plot_file=os.path.join(plot_dir,f"Histogramme_{alias}_Categorie.webp")
    axes=df.hist(column=caracteristique,legend=True,by="Type",
            figsize=(16, 8),      # Plus large et plus haut
            density=True,
            bins="auto", #densité de proba en histogramme avec un découpage intelligent
            layout=(2, 4),        # 2 lignes, 4 colonnes = 8 subplots
            sharex=True
            )
    nom=f"{alias} histograms by packet type"
    for ax in axes.flatten():
        ax.set_xlabel(alias)       # axe X
        ax.set_ylabel("Proportion")# axe Y
    plt.suptitle(nom)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}


def packetMain(columnList,year,month):
    aliases={"Bandwidth":"Bandwidth","Coding_rate":"Coding Rate","GW_EUI": "Id Gateway","SF":"Spreading Factor","freq":"Frequency",
             "modu":"Modulation","adr":"Adaptive Data Rate",
             "BitRate":"BitRate","Airtime":"Airtime","lsnr":"SNR","rssi":"Received Signal Strength","size":"Packet size",
             "rfch":"RF Chain",
             "Operator":"Operator"
             }
    files={}
    histogrammes=set(["BitRate","Airtime","lsnr","rssi","size"])#métriques qui doivent être analysées par histogramme
    df=Choose_Open(year,month)
    for column in columnList:
            dictionnaireCat={}
            alias=aliases[column] #pas de gestion pour voir s'il envoit un truc dedans ou pas, pas le temps, personne va modifier le javascript pour un projet comme ça
            if column=="adr": #fonction spéciale
                dictionnaireCat.update(Proportion_ADR_Cat(df,year,month))
                dictionnaireCat.update(RepartitionAdrGlobale(df,year,month))
            elif column in histogrammes:
                dictionnaireCat.update(plotHistogrammeParType(df,column,alias,year,month))
                dictionnaireCat.update(plotHistogramGlobal(df,column,alias,year,month))
            else:
                dictionnaireCat.update(RepartitionCaracteristiqueGlobale(df,column,alias,year,month))
                dictionnaireCat.update(RepartitionCaracteristiqueParCategorie(df,column,alias,year,month))
            files[column]=dictionnaireCat
    return files
if __name__=="__main__":
    execution={"GW_EUI":"gateway","Bandwidth":"BW","SF":"Spreading Factor","codr":"coding rate","freq":"Sous Bande"}
    plotHistogramGlobal("lsnr","SNR")
    plotHistogrammeParType("lsnr","SNR")
    for caracteristique,alias in execution.items():

        RepartitionCaracteristiqueParCategorie(caracteristique,alias)
        RepartitionCaracteristiqueGlobale(caracteristique,alias)
