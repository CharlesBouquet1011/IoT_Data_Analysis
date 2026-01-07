from ...preprocessing.useData import *
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


def _proportion_ADR(categorie,repartitions):
    """
    Docstring for _proportion_ADR
    
    Fonction privée, ne l'utilisez pas seule
    :param categorie: Description
    """
    
    df=Ouvre_Json_Categorie(categorie)
    taux=df["adr"].mean() #déjà entre 0 et 1 (true/false) donc ça fonctionnera
    repartitions.append({"categorie":categorie,"adr":taux})
    

    
def Repartition_ADR_Cat():
    plot_file=os.path.join(plot_dir,f"Repartition_ADR_Categories.webp")
    repartitions=[]

    [_proportion_ADR(cat,repartitions) for cat in categories] #plots
    df=pd.DataFrame(repartitions).set_index("categorie")
    df.plot(kind='bar',legend=False)
    plt.ylabel("Proportion ADR")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.clf()


if __name__=="__main__":

    Repartition_ADR_Cat()