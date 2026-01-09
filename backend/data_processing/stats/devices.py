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
Docstring for backend.data_processing.stats.devices

Fichier contenant des fonctions utiles pour dénombrer/track les devices intéragissant avec les gateway

Fonctions:

"""

from preprocessing.useData import Choose_Open #pour executer ce fichier or du serveur, rajouter ... devant le module
from numpy import ndarray
categories=["Confirmed Data Up","Confirmed Data Down","Join Accept","Join Request","Proprietary","RFU","Unconfirmed Data Up","Unconfirmed Data Down"]

def nombreDevices(annee:int=None,mois:int=None)->int:
    df=Choose_Open(annee,mois, ("Join Request",))
    nombre=df["Dev_EUI"].nunique(dropna=True)
    return nombre
def Devices(annee:int=None,mois:int=None)->ndarray:
    df=Choose_Open(annee,mois, ("Join Request",))
    devices=df["Dev_EUI"].unique()
    return devices

def trackDevices(annee:int=None,mois:int=None,categories:list=None):
    df=Choose_Open(annee,mois,tuple(categories))
    #Problèmes: 
    # - certains Dev_EUI sont== "" (pas renseignés) (problème pour dénombrer les devices également)
    # - Je n'ai aucun paquet où j'ai à la fois le Dev_EUI et le Dev_Addr pour faire le mapping des deux, ensemble

if __name__=="__main__":
    print(nombreDevices())
    print(Devices())