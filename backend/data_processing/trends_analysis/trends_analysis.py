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
import numpy as np
import os
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Trends")
os.makedirs(plot_dir,exist_ok=True)
os.makedirs(os.path.join(plot_dir,"Seasonality"),exist_ok=True)
os.makedirs(os.path.join(plot_dir,"Global"),exist_ok=True)
os.makedirs(os.path.join(plot_dir,"Stats"),exist_ok=True)

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
        Copie=df[(df.index >= start) & (df.index < end)]
        
        if len(Copie)>0: 
            timeSerie=Copie.resample(freq).size().dropna() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu
            timeSerie.plot(kind="line")
            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.xlim(left=start,right=Copie.index.max())
            titre=f"Nombre de paquets par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} à {end.strftime(date_format)}"
            plt.title(titre)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file=os.path.join(plot_dir,"Seasonality",f"{nom}.webp")
            plt.savefig(plot_file)
            plt.close()
            files[nom]=plot_file #j'enregistre le chemin du fichier dans un dictionnaire
            end = end + timedelta(**{hop_interval:hop_value}) #ex week=1, ça fonctionne
            start = start + timedelta(**{hop_interval:hop_value}) #on n'a pas de données, on décale d'une semaine pour avoir la suite du mois
    if start < df.index.max():
        end = df.index.max()
        Copie = df[(df.index >= start) & (df.index < end)]
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).size().dropna()
            
            if len(timeSerie) == 1:
                timeSerie.plot(kind="bar", width=0.5)
                plt.xticks(rotation=45)
            else:
                timeSerie.plot(kind="line", linewidth=2)
            plt.xlim(left=start,right=Copie.index.max())

            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.grid(True, alpha=0.3)
            
            nom = f"Nombre de paquets par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} à {end.strftime('%d-%m-%Y')}"
            plt.title(nom)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file = os.path.join(plot_dir,"Seasonality",f"{nom}.webp")
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
        Copie=pivoted[(pivoted.index >= start) & (pivoted.index < end)]
        
        if len(Copie)>0: 
            timeSerie=Copie.resample(freq).sum().dropna() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu          
            timeSerie.plot(kind="line")
            plt.xlim(left=start,right=Copie.index.max())
            plt.ylabel("Nombre de paquets")
            plt.xlabel("Date")
            plt.legend(title='Type de paquet', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            nom=f"Nombre de paquets par Type et par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} à {end.strftime(date_format)}"
            plt.title(nom)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file=os.path.join(plot_dir,"Global",f"{nom}.webp")
            plt.savefig(plot_file,dpi=100, bbox_inches='tight')
            plt.close()
            files[nom]=plot_file #j'enregistre le chemin du fichier dans un dictionnaire
            end = end + timedelta(**{hop_interval:hop_value}) #ex week=1, ça fonctionne
            start = start + timedelta(**{hop_interval:hop_value}) #on n'a pas de données, on décale d'une semaine pour avoir la suite du mois
    if start < pivoted.index.max():
        end = pivoted.index.max()
        Copie = pivoted[(pivoted.index >= start) & (pivoted.index < end)]
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).sum().dropna()
            
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
            nom = f"Nombre de paquets par Type et par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} à {end.strftime('%d-%m-%Y')}"
            plt.title(nom)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file = os.path.join(plot_dir,"Global", f"{nom}.webp")
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
    df=Choose_Open(year,month,categories)
    files["Saisonnalite globale"]=plotTimeSerie(df,freq,hop_interval,hop_value)#plot UNIQUEMENT les catégories sélectionnées
    files["Saisonnalite detaillée par type"]=plotMultipleTimeSeries(df,freq,hop_interval,hop_value)
    files["Saisonnalité avec statistiques"]=plotTimeSerieStats(df,freq,hop_interval,hop_value)

    return files

def plotTimeSerieStats(df: pd.DataFrame, freq: str = "D", hop_interval: str = "weeks", hop_value: int = 1) -> dict:
    #fait par IA, optimisé par mes soins (parce que vraiment c'était pas ça, y avait des fuites de mémoire partout et des compréhensions
    #de liste alors que c'est pandas...)
    """
    Docstring for plotTimeSerieStats
    Trace les données sur les intervalles de temps demandé ainsi avec la fréquence demandée ainsi que les données typiques sur cette période (moyenne et écart type)

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
    start = df.index.min()
    
    if hop_interval == "days":
        start = align_to_day_start(start)
    elif hop_interval == "weeks" and hop_value == 4:  # 1 mois
        start = align_to_month_start(start)
    elif hop_interval == "days" and (hop_value == 31 or hop_value == 30):  # toujours 1 mois
        start = align_to_month_start(start)
    elif hop_interval == "weeks":
        start = align_to_week_start(start)

    end = start + timedelta(**{hop_interval: hop_value})
    files = {}
    
    if start is not None and start > df.index.max():
        raise ValueError("start est après la dernière date disponible")

    # Préparer un DataFrame avec toutes les périodes pour stats
    # On fait ça UNE SEULE FOIS avant la boucle
    df_stats = df.copy()
    df_stats['weekday'] = df_stats.index.weekday
    df_stats['date'] = df_stats.index.date
    
    # Resample et créer un DataFrame avec offset
    all_periods_data = []
    for date in df_stats['date'].unique():
        date_start = pd.Timestamp(date).replace(hour=0, minute=0, second=0, microsecond=0)
        if date_start.tzinfo is None and df.index[0].tzinfo is not None:
            date_start = date_start.tz_localize(df.index[0].tzinfo)
        
        # Déterminer la durée de la période
        date_end = date_start + timedelta(**{hop_interval: hop_value})
        
        period_data = df[(df.index >= date_start) & (df.index < date_end)]
        if len(period_data) > 0:
            resampled = period_data.resample(freq).size()
            for ts, count in resampled.items():
                offset = (ts - date_start).total_seconds()
                all_periods_data.append({
                    'period_start': date_start,
                    'weekday': date_start.weekday(),
                    'offset': offset,
                    'count': count,
                    'timestamp': ts
                })
    
    stats_df = pd.DataFrame(all_periods_data)

    while end < df.index.max():
        Copie = df[(df.index >= start) & (df.index < end)]
        
        if len(Copie) > 0:
            # Données de la période actuelle
            timeSerie = Copie.resample(freq).size().dropna()
            
            weekday = start.weekday()
            weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            weekday_name = weekday_names[weekday]
            
            # Exclure la période actuelle des stats
            stats_filtered = stats_df[stats_df['period_start'] != start]
            
            # Stats sur le même weekday
            same_weekday_stats = stats_filtered[stats_filtered['weekday'] == weekday].groupby('offset')['count'].agg(['mean', 'std'])
            
            # Stats sur tous les jours (uniquement pour plots journaliers)
            all_days_stats = None
            if hop_interval == "days" and hop_value == 1:
                all_days_stats = stats_filtered.groupby('offset')['count'].agg(['mean', 'std'])
            
            # Plot
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Courbe de la période actuelle
            ax.plot(timeSerie.index, timeSerie.values,
                   label=f'Période du {start.strftime(date_format)}',
                   linewidth=2.5, marker='o', markersize=5, color='#2E86AB', zorder=3)
            
            # Moyenne du même weekday
            if len(same_weekday_stats) > 0:
                mean_times =start + pd.to_timedelta(same_weekday_stats.index, unit="s")
                
                ax.plot(mean_times, same_weekday_stats['mean'].values,
                       label=f'Moyenne des {weekday_name}s ({len(stats_filtered[stats_filtered["weekday"]==weekday]["period_start"].unique())} périodes)',
                       linewidth=2, linestyle='--', color='#A23B72', zorder=2)
                
                ax.fill_between(mean_times,
                               same_weekday_stats['mean'] - same_weekday_stats['std'],
                               same_weekday_stats['mean'] + same_weekday_stats['std'],
                               alpha=0.2, color='#A23B72',
                               label=f'± 1 σ ({weekday_name}s)', zorder=1)
            
            # Moyenne de tous les jours (si plot journalier)
            if all_days_stats is not None and len(all_days_stats) > 0:
                mean_times_all=start + pd.to_timedelta(all_days_stats.index, unit="s")
                
                ax.plot(mean_times_all, all_days_stats['mean'].values,
                       label=f'Moyenne de tous les jours ({len(stats_filtered["period_start"].unique())} jours)',
                       linewidth=2, linestyle=':', color='#F18F01', zorder=2)
                
                ax.fill_between(mean_times_all,
                               all_days_stats['mean'] - all_days_stats['std'],
                               all_days_stats['mean'] + all_days_stats['std'],
                               alpha=0.15, color='#F18F01',
                               label='± 1 σ (tous les jours)', zorder=1)
            
            ax.set_ylabel("Nombre de paquets")
            ax.set_xlabel("Date")
            ax.set_xlim(left=start, right=Copie.index.max())
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            nom = f"Statistiques Nombre de paquets par {nom_freq.get(freq)} a partir de {start.strftime(date_format)} à {end.strftime(date_format)}"
            ax.set_title(nom)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file = os.path.join(plot_dir,"Stats", f"{nom}.webp")
            plt.savefig(plot_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            files[nom] = plot_file
            
        end = end + timedelta(**{hop_interval: hop_value})
        start = start + timedelta(**{hop_interval: hop_value})
    
    # Traiter la dernière période incomplète
    if start < df.index.max():
        end = df.index.max()
        Copie = df[(df.index >= start) & (df.index < end)]
        
        if len(Copie) > 0:
            timeSerie = Copie.resample(freq).size().dropna()
            
            weekday = start.weekday()
            weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            weekday_name = weekday_names[weekday]
            
            stats_filtered = stats_df[stats_df['period_start'] != start]
            same_weekday_stats = stats_filtered[stats_filtered['weekday'] == weekday].groupby('offset')['count'].agg(['mean', 'std'])
            
            all_days_stats = None
            if hop_interval == "days" and hop_value == 1:
                all_days_stats = stats_filtered.groupby('offset')['count'].agg(['mean', 'std'])
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            if len(timeSerie) == 1:
                ax.bar(timeSerie.index, timeSerie.values, width=0.5, color='#2E86AB', label='Période actuelle')
            else:
                ax.plot(timeSerie.index, timeSerie.values,
                       linewidth=2.5, marker='o', markersize=5, color='#2E86AB', 
                       label=f'Période du {start.strftime(date_format)}', zorder=3)
            
            if len(same_weekday_stats) > 0:
                mean_times =start + pd.to_timedelta(same_weekday_stats.index, unit="s")
                mean_times_filtered = mean_times[mean_times<end]
                mean_vals = same_weekday_stats['mean'].values[:len(mean_times_filtered)]
                std_vals = same_weekday_stats['std'].values[:len(mean_times_filtered)]
                
                if len(mean_times_filtered) > 0:
                    ax.plot(mean_times_filtered, mean_vals,
                           linewidth=2, linestyle='--', color='#A23B72',
                           label=f'Moyenne {weekday_name}s', zorder=2)
                    
                    ax.fill_between(mean_times_filtered,
                                   mean_vals - std_vals,
                                   mean_vals + std_vals,
                                   alpha=0.2, color='#A23B72',
                                   label=f'± 1 σ ({weekday_name}s)', zorder=1)
            
            if all_days_stats is not None and len(all_days_stats) > 0:
                mean_times_all=start + pd.to_timedelta(all_days_stats.index, unit="s")
                mean_times_all_filtered = mean_times_all[mean_times_all<end]
                mean_vals_all = all_days_stats['mean'].values[:len(mean_times_all_filtered)]
                std_vals_all = all_days_stats['std'].values[:len(mean_times_all_filtered)]
                
                if len(mean_times_all_filtered) > 0:
                    ax.plot(mean_times_all_filtered, mean_vals_all,
                           linewidth=2, linestyle=':', color='#F18F01',
                           label='Moyenne tous jours', zorder=2)
                    
                    ax.fill_between(mean_times_all_filtered,
                                   mean_vals_all - std_vals_all,
                                   mean_vals_all + std_vals_all,
                                   alpha=0.15, color='#F18F01',
                                   label='± 1 σ (tous)', zorder=1)
            
            ax.set_xlim(left=start, right=Copie.index.max())
            ax.set_ylabel("Nombre de paquets")
            ax.set_xlabel("Date")
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            nom = f"Statistiques Nombre de paquets par {nom_freq.get(freq, freq)} a partir de {start.strftime('%d-%m-%Y')} a {end.strftime('%d-%m-%Y')}"
            ax.set_title(nom)
            nom=f"{start.strftime(date_format)}-{end.strftime(date_format)}"
            plot_file = os.path.join(plot_dir,"Stats", f"{nom}.webp")
            plt.savefig(plot_file, dpi=100, bbox_inches='tight')
            plt.close()
            
            files[nom] = plot_file
    
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