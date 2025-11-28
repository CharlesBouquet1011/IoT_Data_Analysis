"""
Fichier regroupant toutes les fonctions utiles au preprocessing des donnes
"""

import pandas as pd
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

    custom_df = df[selected_attrs].copy()

    if undefined_toggle:
        initial_count = len(custom_df)
        custom_df.dropna(inplace=True)
        if verbose: print(f"Removed {initial_count - len(custom_df)} packets with undefined values.") # VERBOSE affichage du nombre de paquets supprimés car attribut non défini

    #on marque les entrées aberrantes puis on les supprimera dans un 2nd temps
    #sinon on pourrait supprimer des valeurs qui n'étaient pas si aberrantes que ça
    custom_df["outlier"]=False
    
    if outlier_toggle:
        for attr in selected_attrs:
            if pd.api.types.is_numeric_dtype(custom_df[attr]):
                #duree peut être soit une durée en temps "7d" soit un nombre de points
                q1=custom_df[attr].rolling(duree).quantile(0.25) #premier quartile  (fenêtre glissante)
                q3=custom_df[attr].rolling(duree).quantile(0.75)#dernier quartile (fenêtre glissante)
                IQRange=q3-q1   #écart interquartile
                custom_df["outlier"]=custom_df["outlier"] | custom_df[attr]<=(q1-1.5*IQRange) | custom_df[attr]>=(q3+1.5*IQRange) 
        custom_df=custom_df[~ custom_df["outlier"]]
        
    if verbose: print(f"Remaining packets after processing: {len(custom_df)}") # VERBOSE sauvegarde du dataset
    custom_df.to_json(fichier_sortie, orient="records", indent=2)
    print("custom_dataset.json generated successfully.") # VERBOSE terminé !
