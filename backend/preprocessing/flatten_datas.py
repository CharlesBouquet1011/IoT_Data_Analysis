# Copyright 2025 Titouan Verdier, Charles Bouquet
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
Functions:
flatten_datas:
applatit le json en entrée et en crée un en sortie
"""


import json
import ijson
import os
from decimal import Decimal
#comment ça la fonction ne traitait que le premier paquet de chaque timestamp ??
def flatten_datas(file: str, output_path: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file)
    def convert_decimal(obj):
        """Convertit récursivement les Decimal en float"""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_decimal(item) for item in obj]
        return obj
    with open(file_path, "r", encoding="utf-8") as f, open(output_path, "w", encoding="utf-8") as out_f:
        first = True

        # On itère sur chaque élément du dictionnaire (clé = timestamp)
        objects = ijson.kvitems(f, '')  # renvoie (clé, valeur)
        for timestamp, packets in objects:
            if not packets:
                continue
            # on prend le premier paquet pour simplifier (comme ton code actuel)
            for p in packets:

                flat = {}
                for k, v in p.items():
                    if k != "rxpk" and k != "stat":
                        flat[k] = v
                    elif k == "rxpk" and v:
                        rx = v[0]
                        for rk, rv in rx.items():
                            flat[rk] = rv
                    elif k == "stat" and v:
                        for sk, sv in v.items():
                            flat[sk] = sv
                    else:
                        flat[k] = None
                flat = convert_decimal(flat)

                json.dump(flat, out_f)
                out_f.write("\n")