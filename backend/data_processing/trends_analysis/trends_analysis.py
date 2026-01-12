from ...preprocessing.useData import Choose_Open
import pandas as pd
from datetime import timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")


def plotTimeSerie(df:pd.DataFrame,freq:str="D",start:pd.Timestamp|None=None,end:pd.Timestamp|None=None):
    """
    Docstring for plotTimeSerie
    
    :param df: Description
    :param freq: à Adapter à la durée totale, exemple pour une semaine, agréger par jour, pour un jour, par heure, etc
    :type freq: str
    :param start: Description
    :type start: pd.Timestamp | None
    :param end: Description
    :type end: pd.Timestamp | None
    """
    Copie=df.copy()
    if start is not None:
        Copie=Copie[Copie.index>=start]
    if end is not None:
        Copie=Copie[Copie.index<=end]
    timeSerie=Copie.resample(freq).size() #regroupe par intervalle de temps à partir de début et met en valeur le nombre de paquets qu'il y a eu
    plt.figure()
    timeSerie.plot(kind="line")
    plt.ylabel("nombre de paquets")
    plt.xlabel("Date")
    nom=f"Serie temporelle par {freq} à partir de {start} a {end}"
    plt.title(nom)
    plot_file=os.path.join(plot_dir,f"{nom.replace(" ","-")}.webp")
    plt.savefig(plot_file)

def wrapper(year:int=None,month:int=None,categories:tuple|None=None,start:pd.Timestamp|None=None,end:pd.Timestamp|None=None,freq:str="D"):
    
    df=Choose_Open(year,month,categories)
    plotTimeSerie(df,freq,start,end)

if __name__=="__main__":
    frequences=["H","D","W","M","Y"]
    start=pd.Timestamp("2023-12-01")
    end = start + timedelta(weeks=1)
    wrapper(2023,12,None,start,end,"D")