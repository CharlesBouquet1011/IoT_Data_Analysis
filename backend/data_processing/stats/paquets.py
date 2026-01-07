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
"""
Docstring for backend.data_processing.stats.paquets
"""
from ...preprocessing.useData import Choose_Open
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
from numpy import ndarray
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]
script_dir=os.path.dirname(os.path.abspath(__file__))
backend_dir=os.path.dirname(os.path.dirname(script_dir))
plot_dir=os.path.join(backend_dir,"Images","Stats")

def GatewayList(annee:int=None,mois:int=None)->ndarray:
    df=Choose_Open(annee,mois, ["Join Request"])
    gateway=df["GW_EUI"].unique()
    return gateway

def _proportionGWCat(annee,mois,categorie,repartitions,GW):
    """
    Docstring for _proportion_ADR
    
    Fonction privée, ne l'utilisez pas seule
    :param categorie: Description
    """
    
    df=Choose_Open(annee,mois,[categorie])
    nombre=len(df[df["GW_EUI"]==GW])
    tot=len(df)

    taux=nombre/tot 
    repartitions.append({"categorie":categorie,"gw":taux})

def RepartitionGWCat(annee:int=None,mois:int=None):
    for gw in GatewayList():
        repartitions=[]
        plot_file=os.path.join(plot_dir,f"Repartition_GW_Categories_{gw}.webp")
        [_proportionGWCat(annee,mois,cat,repartitions,gw) for cat in categories] #plots
        df=pd.DataFrame(repartitions).set_index("categorie")
        df.plot(kind='bar',legend=False)
        plt.ylabel(f"Proportion GW: {gw}")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(plot_file)
        plt.clf()

def _proportionGW(annee,mois,repartitions,GW):
    """
    Docstring for _proportion_ADR
    
    Fonction privée, ne l'utilisez pas seule
    :param categorie: Description
    """
    
    df=Choose_Open(annee,mois)
    nombre=len(df[df["GW_EUI"]==GW])
    tot=len(df)

    taux=nombre/tot 
    repartitions.append({"gateway":GW,"taux":taux})

def RepartitionGWTot(annee:int=None,mois:int=None):
    repartitions=[]
    plot_file=os.path.join(plot_dir,f"Repartition_GW_Totale.webp")
    [_proportionGW(annee,mois,repartitions,gw) for gw in GatewayList(annee,mois)] #plots
    df=pd.DataFrame(repartitions).set_index("gateway")
    df.plot(kind='bar',legend=False)
    plt.ylabel(f"Proportion GW totale")
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.clf()
    

if __name__=="__main__":
    RepartitionGWCat()
    RepartitionGWTot()