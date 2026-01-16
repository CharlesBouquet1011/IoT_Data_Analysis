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
import dask_cudf
import pandas as pd
import os
import cudf
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

def addNwkOperator(df: dask_cudf.DataFrame) -> dask_cudf.DataFrame:
    file = os.path.join(script_dir, "operateursLoraWan.csv")

    # Lecture opérateurs (CPU → GPU)
    ops = pd.read_csv(file, sep=";", encoding="utf-8")

    def splitPrefixLen(x):
        prefix, length = x.strip().split("/")
        return int(prefix, 16), int(length)

    tmp = ops["DevAddr Prefix"].apply(splitPrefixLen)
    ops["Prefix"] = tmp.apply(lambda x: x[0])
    ops["Length"] = tmp.apply(lambda x: x[1])
    ops["comparaison"] = ops["Prefix"] >> (32 - ops["Length"])

    ops_gpu = cudf.from_pandas(ops[["comparaison", "Operator"]])

    # ============================
    # 🔥 CORRECTION MAJEURE ICI 🔥
    # ============================

    # Dev_Add est HEX -> conversion propre
    devaddr_int = (
        df["Dev_Add"]
        .astype("str")
        .str.zfill(8)
        .str.slice(0, 8)
        .str.hex_to_int()
    )

    # Network ID = 7 MSB (>> 25)
    df["NwkId"] = (devaddr_int // (2**25)).astype("Int64")

    # Merge opérateur
    df = df.merge(
        ops_gpu,
        how="left",
        left_on="NwkId",
        right_on="comparaison"
    )

    # Nettoyage
    df = df.drop(columns=["comparaison", "NwkId"])
    df = df.reset_index(drop=True)

    return df