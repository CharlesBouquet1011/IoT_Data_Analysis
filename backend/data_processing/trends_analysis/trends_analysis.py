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

from preprocessing.useData import Choose_Open
import pandas as pd
from datetime import timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Trends")
os.makedirs(plot_dir,exist_ok=True)




def plotTimeSerie(df:pd.DataFrame,freq:str="D",hop_interval:str="weeks",hop_value:int=1)->dict:
    """
    Docstring for plotTimeSerie
    
    :param df: DataFrame des données que l'on veut traiter
    :type df: pd.DataFrame
    :param freq: Fréquence d'agrégation (on agrège les données en jour, semaines, mois, années,...) pour l'analyse de saisonnalité
    :type freq: str
    :param hop_interval: unité du saut entre 2 graphiques (hours,days,weeks,...)
    :type hop_interval: str
    :param hop_value: valeur du saut dans l'unité donnée avant
    :type hop_value: int
    :return: dictionnaire contenant tous les chemins des fichiers ainsi que leur nom
    :rtype: dict
    """
    

    nom_freq = {
    "s": "seconde",      # Pour du debugging très fin
    "10s": "10 secondes", # Monitoring temps réel
    "30s": "30 secondes", # Monitoring temps réel
    "min": "minute",      # Analyse fine du trafic
    "5min": "5 minutes",  # Standard pour métriques IoT
    "10min": "10 minutes",
    "15min": "15 minutes", # Très courant (quart d'heure)
    "30min": "30 minutes", # Demi-heure
    "h": "heure",
    "D": "jour",
    "W": "semaine",
    "ME": "mois",         # Month End (plus précis que "M")
    "YE": "année"         # Year End (plus précis que "Y")
}
    # Formats de date en fonction de hop_interval
    date_formats = {
        "seconds": "%d-%m-%Y %H:%M:%S",
        "minutes": "%d-%m-%Y %H:%M",
        "hours": "%d-%m-%Y %H:%M",
        "days": "%d-%m-%Y",
        "weeks": "%d-%m-%Y",
        "months": "%m-%Y",
        "years": "%Y"
    }
    
    date_format = date_formats.get(hop_interval, "%d-%m-%Y")
    start=df.index.min()
    end=start + timedelta(**{hop_interval:hop_value})
    files={}
    #map les arguments de timedelta pour faire par exemple timedelta(week=1)
    if start is not None and start > df.index.max():
        raise ValueError("start est après la dernière date disponible")

    while end < df.index.max():
        Copie=df.copy()
        
        Copie=Copie[(Copie.index>=start) & (Copie.index<=end)]
        if len(Copie)>0: 
            timeSerie=Copie.resample(freq).size() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu
            plt.figure()
            timeSerie.plot(kind="line")
            plt.ylabel("nombre de paquets")
            plt.xlabel("Date")
            nom=f"Nombre de paquets par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} a {end.strftime(date_format)}"
            plt.title(nom)
            plot_file=os.path.join(plot_dir,f"{nom.replace(' ','-')}.webp")
            plt.savefig(plot_file)
            plt.close()
            files[nom]=plot_file #j'enregistre le chemin du fichier dans un dictionnaire
            end = end + timedelta(**{hop_interval:hop_value}) #ex week=1, ça fonctionne
            start = start + timedelta(**{hop_interval:hop_value}) #on n'a pas de données, on décale d'une semaine pour avoir la suite du mois
    if start < df.index.max():
        end = df.index.max()
        Copie = df.copy()
        Copie = Copie[(Copie.index >= start) & (Copie.index <= end)]
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).size()
            
            plt.figure(figsize=(12, 6))
            if len(timeSerie) == 1:
                timeSerie.plot(kind="bar", width=0.5)
                plt.xticks(rotation=45)
            else:
                timeSerie.plot(kind="line", marker='o', linewidth=2, markersize=6)
            
            plt.ylabel("nombre de paquets")
            plt.xlabel("Date")
            plt.grid(True, alpha=0.3)
            
            nom = f"Nombre de paquets par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} a {end.strftime('%d-%m-%Y')}"
            plt.title(nom)
            
            plot_file = os.path.join(plot_dir, f"{nom.replace(' ', '-')}.webp")
            plt.savefig(plot_file, dpi=100, bbox_inches='tight')
            plt.close()
            files[nom]=plot_file
        return files
        
def trends(year:int=None,month:int=None,categories:tuple|None=None,hop_interval:str="weeks",hop_value:int=1,freq:str="D")->dict:
    """
    Docstring for wrapper
    lance plot_timeseries 

    :param year: année des données à traiter
    :type year: int
    :param month: mois des données à traiter
    :type month: int
    :param categories: catégories concernées, none=tout
    :type categories: tuple | None
    :param hop_interval: unité du saut temporel entre 2 graphiques
    :type hop_interval: str
    :param hop_value: valeur du saut temporel entre 2 graphiques
    :type hop_value: int
    :param freq: frequence temporelle d'agrégation des paquets
    :type freq: str
    :return: dictionnaire des fichiers créés
    :rtype: dict
    """
    #map freq et hop_interval ?
    df=Choose_Open(year,month,categories)
    
    return plotTimeSerie(df,freq,hop_interval,hop_value)

if __name__=="__main__":
    #tests
    #frequences=["10s", "30s", "min", "5min", "15min","30min","h","D","W","M","Y"]
    #hop_intervals = ["seconds", "minutes", "hours", "days", "weeks"]
    start=pd.Timestamp("2023-10-01")
    end = start + timedelta(weeks=1)
    start=start.tz_localize("UTC")
    end=end.tz_localize("UTC")
    # timedelta_kwargs_map = {
    #     "days": "days",
    #     "weeks": "weeks",
    #     "hours": "hours",
    #     "minutes": "minutes",
    #     "seconds": "seconds"
    # } exemple de hop intervals
    trends(2023,10,None,"days",1,"h")