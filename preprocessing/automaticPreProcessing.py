"""
Docstring for preprocessing.automaticPreProcessing

"""


from preprocessing_utils import prepare_data

def main(rolling_interval=30,list_attr=["Airtime","BitRate","rssi","lsnr"]):
    months=[i for i in range(12,13)]
    years=[i for i in range(2025,2026)]
    for year in years:
        for month in months:
            prepare_data(year,month,rolling_interval,list_attr )

def configureMain():
    res=input("Voulez-vous une fenêtre glissante en entier ?")
    if res.lower()=="oui":
        while type(res)!=int:
            res=input("Veuillez choisir la taille de la fenêtre en nombre de points :")
            try:
                res=int(res)
            except:
                print("Veuillez choisir un entier positif")
        rolling_interval=res
    else:
        print("Vous avez choisi de définir la fenêtre glissante à l'aide d'un interval temporel")
        
        choices=["30min","12h","1d","7d","30d","365d"] 
        print(choices)  
        while type(res)!=int and res>6:
            res=input("Veuillez choisir parmi les choix proposés ci dessus (de 0 à 5)") 
            try:
                res=int(res)
            except:
                print("veuillez rentrer un nombre compris entre 0 et 5")
        rolling_interval=res
    return rolling_interval

if __name__=="__main__":
    main()