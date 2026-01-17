# Copyright 2025 Charles Bouquet, David Magoudaya
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

def align_to_week_start(date, weekday=0):
    """
    Aligne une date au début de la semaine spécifiée
    
    :param date: Date à aligner
    :param weekday: Jour de la semaine (0=lundi, 6=dimanche)
    :return: Date alignée
    """
    days_since_target = (date.weekday() - weekday) % 7
    retour= date - timedelta(days=days_since_target)
    return retour.replace(hour=0, minute=0, second=0, microsecond=0) #pour pas avoir un plongeon à la fin du graphique

def align_to_month_start(date):
    """Aligne une date au début du mois"""
    return date.replace(day=1,hour=0, minute=0, second=0, microsecond=0) #pour pas avoir un plongeon à la fin du graphique
def align_to_day_start(date):
    """Aligne une date au début du jour"""
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

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
    date_format = date_formats.get(hop_interval, "%d-%m-%Y")
    start=df.index.min()
    if hop_interval=="days":
        start=align_to_day_start(start)
    elif hop_interval=="weeks" and hop_value==4: #1 mois
        start=align_to_month_start(start)
    elif hop_interval=="days" and (hop_value==31 or hop_value==30): #toujours 1 mois
        start=align_to_month_start(start)
    elif hop_interval=="weeks":
        start=align_to_week_start(start)
    

    
    end=start + timedelta(**{hop_interval:hop_value})
    files={}
    #map les arguments de timedelta pour faire par exemple timedelta(week=1)
    if start is not None and start > df.index.max():
        raise ValueError("start est après la dernière date disponible")

    while end < df.index.max():
        Copie=df[(df.index >= start) & (df.index < end)].copy()
        
        if len(Copie)>0: 
            timeSerie=Copie.resample(freq).size().dropna() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu
            plt.figure()
            timeSerie.plot(kind="line")
            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.xlim(left=start,right=Copie.index.max())
            nom=f"Nombre de paquets par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} a {end.strftime(date_format)}"
            plt.title(nom)
            plot_file=os.path.join(plot_dir,f"{nom.replace(" ","-")}.webp")
            plt.savefig(plot_file)
            plt.close()
            files[nom]=plot_file #j'enregistre le chemin du fichier dans un dictionnaire
            end = end + timedelta(**{hop_interval:hop_value}) #ex week=1, ça fonctionne
            start = start + timedelta(**{hop_interval:hop_value}) #on n'a pas de données, on décale d'une semaine pour avoir la suite du mois
    if start < df.index.max():
        end = df.index.max()
        Copie = df[(df.index >= start) & (df.index < end)].copy()
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).size().dropna()
            
            plt.figure()
            if len(timeSerie) == 1:
                timeSerie.plot(kind="bar", width=0.5)
                plt.xticks(rotation=45)
            else:
                timeSerie.plot(kind="line", linewidth=2)
            plt.xlim(left=start,right=Copie.index.max())

            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.grid(True, alpha=0.3)
            
            nom = f"Nombre de paquets par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} a {end.strftime('%d-%m-%Y')}"
            plt.title(nom)
            
            plot_file = os.path.join(plot_dir, f"{nom.replace(' ', '-')}.webp")
            plt.savefig(plot_file, dpi=100, bbox_inches='tight')
            plt.close()
            files[nom]=plot_file
    return files
def plotMultipleTimeSeries(df:pd.DataFrame,freq:str="D",hop_interval:str="weeks",hop_value:int=1):
    #Inspired by a code sample of David (but heavily modified since he didn't have the same data)
    #I have to pivot the table first to imitate his code after
    #Of course I have merged my code with his to permit input from the user.
    pivoted=pd.pivot_table(df,
                           index="@timestamp",
                           columns="Type",
                           aggfunc="size",
                           fill_value=0)
    date_format = date_formats.get(hop_interval, "%d-%m-%Y")
    start=df.index.min()
    if hop_interval=="days":
        start=align_to_day_start(start)
    elif hop_interval=="weeks" and hop_value==4: #1 mois
        start=align_to_month_start(start)
    elif hop_interval=="days" and (hop_value==31 or hop_value==30): #toujours 1 mois
        start=align_to_month_start(start)
    elif hop_interval=="weeks":
        start=align_to_week_start(start)

    #map les arguments de timedelta pour faire par exemple timedelta(week=1)
    if start is not None and start > df.index.max():
        raise ValueError("start est après la dernière date disponible")

    end=start + timedelta(**{hop_interval:hop_value})
    files={}

    while end < pivoted.index.max():
        Copie=pivoted[(pivoted.index >= start) & (pivoted.index < end)].copy()
        
        if len(Copie)>0: 
            timeSerie=Copie.resample(freq).sum().dropna() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu
            plt.figure()
            
            timeSerie.plot(kind="line")
            plt.xlim(left=start,right=Copie.index.max())
            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.legend(title='Type de paquet', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            nom=f"Nombre de paquets par Type et par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} a {end.strftime(date_format)}"
            plt.title(nom)
            plot_file=os.path.join(plot_dir,f"{nom.replace(" ","-")}.webp")
            plt.savefig(plot_file,dpi=100, bbox_inches='tight')
            plt.close()
            files[nom]=plot_file #j'enregistre le chemin du fichier dans un dictionnaire
            end = end + timedelta(**{hop_interval:hop_value}) #ex week=1, ça fonctionne
            start = start + timedelta(**{hop_interval:hop_value}) #on n'a pas de données, on décale d'une semaine pour avoir la suite du mois
    if start < pivoted.index.max():
        end = pivoted.index.max()
        Copie = pivoted[(pivoted.index >= start) & (pivoted.index < end)].copy()
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).sum().dropna()
            
            plt.figure()
            if len(timeSerie) == 1:
                timeSerie.plot(kind="bar", width=0.5)
                plt.xticks(rotation=45)
            else:
                timeSerie.plot(kind="line", linewidth=2)
            plt.xlim(left=start,right=Copie.index.max())
            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.grid(True, alpha=0.3)
            plt.legend(title='Type de paquet', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            nom = f"Nombre de paquets par Type et par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} a {end.strftime('%d-%m-%Y')}"
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
    #dftot=Choose_Open(year,month)
    #subdf=dftot[dftot["Type"].isin(categories)]
    files={}
    print(files)
    df=Choose_Open(year,month,categories)
    files["Saisonnalite globale"]=plotTimeSerie(df,freq,hop_interval,hop_value)#plot UNIQUEMENT les catégories sélectionnées
    files["Saisonnalite detaillée par type"]=plotMultipleTimeSeries(df,freq,hop_interval,hop_value)


    return files

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