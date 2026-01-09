from ...preprocessing.useData import Choose_Open #pour executer ce fichier or du serveur, rajouter ... devant le module
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")

def analysePacketsDevEUIEmpty(mois:int|None=None,annee:int|None=None):
    df=Choose_Open(mois,annee)
    

    dfDevEuiEmpty=df[(df["Type"]=="Join Request") & (df["Dev_EUI"]=="")]
    for colonne in dfDevEuiEmpty.select_dtypes(include="number").columns:
        plot_file=os.path.join(plot_dir,f"manuel_{colonne}.webp")
        plt.figure()
        dfDevEuiEmpty[colonne].plot.box()
        plt.savefig(plot_file)
        plt.close()
    #résultat de l'analyse, tous ces paquets en version 1
    #Airtimes identiques
    #Bitrates à 5500 environ (identiques aussi)
    #freq majoritairement entre 868.2 et 868.4
    #size majoritairement à 10
    #rien d'autre d'intéressant

if __name__=="__main__":
    analysePacketsDevEUIEmpty()