"""
Fichier regroupant toutes les fonctions utiles au preprocessing des donnes
"""

import pandas as pd
import os
import datetime
import matplotlib
matplotlib.use('Agg') #backend non interactif
import matplotlib.pyplot as plt
#en forme de procédure pour la lisibilité

def produce_dataset(df:pd.DataFrame,verbose:bool,undefined_toggle:bool,outlier_toggle:bool,duree,selected_attrs:list,fichier_sortie:str):
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
        initial_count = len(df)
        df.dropna(inplace=True,axis=0,subset=selected_attrs,how="any") #on veut trier uniquement sur les attributs renseignés
        if verbose: print(f"Removed {initial_count - len(df)} packets with undefined values.") # VERBOSE affichage du nombre de paquets supprimés car attribut non défini

    #on marque les entrées aberrantes puis on les supprimera dans un 2nd temps
    #sinon on pourrait supprimer des valeurs qui n'étaient pas si aberrantes que ça
    df["outlier"]=False
    
    if outlier_toggle:
        for attr in selected_attrs:
            if pd.api.types.is_numeric_dtype(df[attr]):
                #duree peut être soit une durée en temps "7d" soit un nombre de points
                q1=df[attr].rolling(duree).quantile(0.25) #premier quartile  (fenêtre glissante)
                q3=df[attr].rolling(duree).quantile(0.75)#dernier quartile (fenêtre glissante)
                IQRange=q3-q1   #écart interquartile
                df["outlier"]=(df["outlier"]) | (df[attr]<=(q1-1.5*IQRange)) | (df[attr]>=(q3+1.5*IQRange)) 
        df=df[~ df["outlier"]]
        
    if verbose: print(f"Remaining packets after processing: {len(df)}") # VERBOSE sauvegarde du dataset
    df.to_json("./"+fichier_sortie, orient="index", indent=2) #il faudra readJson avec orient="index"
    print("custom_dataset.json generated successfully.") # VERBOSE terminé !
    return df #au cas où

def open_df(fichier:str)->pd.DataFrame:
    df= pd.read_json(fichier)
    df["@timestamp"]=pd.to_datetime(df["@timestamp"])
    df.set_index("@timestamp",inplace=True) #Pandas autorise d'avoir des index non uniques donc ça ne posera pas problème quoi qu'il arrive
    return df

def plot_timeSeries(df:pd.DataFrame,attrs:list,begin=None,end=None):
    t=datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    
    CurrentDir = os.path.dirname(os.path.abspath(__file__))
    plotDir=os.path.join(CurrentDir,t)
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
    


if __name__=="__main__":
    #tests
    df=open_df("preprocessing/flattened_datas.json")
    print(df)
    df=produce_dataset(df,True,True,True,30,["Airtime","BitRate","rssi","lsnr"],"preprocessing/nettoye.json")
    print(df)
    plot_timeSeries(df,["Airtime","BitRate","rssi","lsnr"],pd.to_datetime("2023-10-12T19:42:00.723Z"))