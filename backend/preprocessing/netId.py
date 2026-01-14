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
Docstring for backend.preprocessing.netId
a pour but d'identifier de quel opérateur provient un paquet
"""
import pandas as pd
import os
script_dir=os.path.dirname(os.path.abspath(__file__))
def nwkId(DevAdd)->int:
    """
    Docstring for netId
    
    :param DevAdd: devAdd du paquet LoRaWan 
    :type DevAdd: str
    :return: NetId 
    :rtype: int

    Renvoie True si l'ADR est set, False sinon
    """
    if not pd.isna(DevAdd):
        DevAdd_str = str(DevAdd).zfill(8)  # s’assure qu’il y a 8 caractères pour un hex
        DevAdd=int(DevAdd_str,16) #Hexadécimal: base 16
        Id=DevAdd>>25 #on supprime les 25 zéros inutiles à la fin (Network Id: 7 premiers bits)
        return Id
    else:
        return pd.NA

def splitPrefixLen(DevAddrPrefix:str):
    prefix,longueur=DevAddrPrefix.strip().split("/")
    return int(prefix,16),int(longueur) #toujours base 16 pour le prefixe

def shiftPrefix(Prefix,Longueur):
    return Prefix>>(32-Longueur)

def addNwkOperator(df:pd.DataFrame)->pd.DataFrame:
    df["NwkId"]=df["Dev_Add"].apply(nwkId)
    file=os.path.join(script_dir,"operateursLoraWan.csv")
    TableauOperateurs = pd.read_csv(file, sep=";", encoding="utf-8")
    # Utilise zip pour séparer les tuples correctement
    result = TableauOperateurs["DevAddr Prefix"].apply(splitPrefixLen)#je dois faire une série de tuples
    TableauOperateurs["Prefix"] = result.apply(lambda x: x[0])
    TableauOperateurs["longueurPrefix"] = result.apply(lambda x: x[1]) 
    TableauOperateurs["comparaison"]=TableauOperateurs.apply(lambda ligne: ligne["Prefix"]>>(32-ligne["longueurPrefix"]),axis=1)
    df["NwkId"] = pd.to_numeric(df["NwkId"], errors='coerce').astype('Int64') #conversion de la colonne problématique (quelques Dev_Addr sont vides)
    #merge des tables pour associer mes clés (NwkId) aux Opérateurs
    df=df.merge(TableauOperateurs[["comparaison","Operator"]],"left",
                left_on="NwkId",
                right_on="comparaison")
    df.drop("comparaison",inplace=True,errors="ignore")
    df.drop("NwkId",inplace=True,errors="ignore")
    return df