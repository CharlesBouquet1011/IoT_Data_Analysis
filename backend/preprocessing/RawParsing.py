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
Docstring for backend.preprocessing.RawParsing

Fonctions qui servent globalement à parser les données raw
Fonctions: 
ADR(data:str)->bool: récupère l'ADR depuis une payload
addColAdr(df:pd.DataFrame)->pd.Dataframe: ajoute le champ ADR au Dataframe

By Charles Bouquet
"""

import base64
import pandas as pd
def ADR(data:str)->bool:
    """
    Docstring for ADR
    
    :param data: payload du paquet LoRaWan
    :type data: str
    :return: Adr du payload vrai ou faux
    :rtype: bool

    Renvoie True si l'ADR est set, False sinon
    """
    #on récupère la data dans la partie data de rxpk
    payload=base64.b64decode(data)
    fctrl=payload[5] #selon la doc, le fctrl est le 5e octet de la payload cf page 17 de lorawan 1.0.3
    #toujours selon la doc: dernier bit= ADDR donc on doit supprimer tous les autres
    filtre=0b10000000
    adr=(fctrl & filtre)!=0 #si le 7e bit (1er bit de poids fort donc) est 1, ça fait true, sinon false
    #rq fctrl>>7 fonctionne aussi normalement
    return adr

def addColAdr(df:pd.DataFrame)->pd.DataFrame:
    """
    Docstring for addColAdr
    
    :param df: Dataframe auquel on veut ajouter la colonne ADR
    :type df: pd.DataFrame
    :return: Dataframe avec la colonne ADR
    :rtype: DataFrame

    affecte la valeur de l'ADR à chaque paquet dans le dataframe
    """
    df["adr"]=df["data"].apply(ADR)
    
    return df

if __name__=="__main__":
    ADR("QEvzZQ+AdRkFXLf+jKfECijeO5k=")
    pass