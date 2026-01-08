from preprocessing.useData import Choose_Open #pour executer ce fichier or du serveur, rajouter ... devant le module
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")
os.makedirs(plot_dir,exist_ok=True )


def _proportion_ADR(repartitions:list,annee:int|None=None,mois:int|None=None,categorie:str|None=None):
    """
    Docstring for _proportion_ADR
    
    Fonction privée, ne l'utilisez pas seule
    :param categorie: Description
    """
    if categorie is not None:
        df=Choose_Open(annee,mois,[categorie])
    else:
        df=Choose_Open(annee,mois)
    taux=df["adr"].mean() #déjà entre 0 et 1 (true/false) donc ça fonctionnera
    if categorie is None:
        categorie="Global"
    repartitions.append({"categorie":categorie,"adr":taux})
    

    
def Repartition_ADR_Cat(annee:int|None=None,mois:int|None=None)->dict:
    plot_file=os.path.join(plot_dir,f"Repartition_ADR_Categories.webp")
    repartitions=[]

    [_proportion_ADR(repartitions,annee,mois,cat) for cat in categories] #plots
    df=pd.DataFrame(repartitions).set_index("categorie")
    df.plot(kind='bar',legend=False)
    nom="Proportion ADR Par Categorie"
    if annee is not None:
        nom+= " "+ str(annee)
    if mois is not None:
        nom+=" "+ str(mois)
    plt.ylabel(nom)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    
    return {nom:plot_file}

def RepartitionAdrGlobale(annee:int|None=None,mois:int|None=None)->dict:
    plot_file=os.path.join(plot_dir,f"Repartition_ADR_Globale.webp")
    repartitions=[]
    nom="Proportion ADR Globale"
    if annee is not None:
        nom+= " "+ str(annee)
    if mois is not None:
        nom+=" "+ str(mois)
    [_proportion_ADR(repartitions,annee,mois)]
    df=pd.DataFrame(repartitions).set_index("categorie")
    df.plot(kind='bar',legend=False)
    plt.ylabel(nom)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close()
    return {nom:plot_file}
if __name__=="__main__":

    Repartition_ADR_Cat()