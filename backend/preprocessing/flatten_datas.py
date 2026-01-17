
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


import os
import ijson
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from decimal import Decimal
def flatten_datas(file: str, output_dir: str, chunk_size=100_000):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file)

    def convert_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    buffer = []
    all_columns = set()  # Collecter TOUTES les colonnes de TOUS les chunks
    parquet_writer = None

    with open(file_path, "r", encoding="utf-8") as f:
        objects = ijson.kvitems(f, "")

        for _, packet in objects:
            if not isinstance(packet, dict):
                continue

            flat = {}
            
            # Vérifier si rxpk existe et n'est pas vide
            has_rxpk = "rxpk" in packet and isinstance(packet["rxpk"], list) and len(packet["rxpk"]) > 0
            
            for k, v in packet.items():
                if k == "rxpk" and has_rxpk:
                    for rk, rv in packet["rxpk"][0].items():
                        flat[rk] = convert_decimal(rv)
                elif k == "stat" and isinstance(v, dict):
                    for sk, sv in v.items():
                        flat[sk] = convert_decimal(sv)
                elif k not in ("rxpk", "stat"):
                    flat[k] = convert_decimal(v)
            
            if has_rxpk:
                all_columns.update(flat.keys())  # ← Ajouter TOUTES les colonnes rencontrées
                buffer.append(flat)

            if len(buffer) >= chunk_size:
                df = pd.DataFrame(buffer)
                
                # S'assurer que TOUTES les colonnes sont présentes
                for col in all_columns:
                    if col not in df.columns:
                        df[col] = None
                
                # Trier pour cohérence
                df = df[sorted(all_columns)]
                
                table = pa.Table.from_pandas(df, preserve_index=False)

                if parquet_writer is None:
                    parquet_writer = pq.ParquetWriter(
                        output_dir,
                        table.schema,
                        compression="zstd"
                    )

                parquet_writer.write_table(table)
                buffer.clear()

        # flush final
        if buffer:
            df = pd.DataFrame(buffer)
            
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            
            df = df[sorted(all_columns)]

            table = pa.Table.from_pandas(df, preserve_index=False)
            
            if parquet_writer is None:
                parquet_writer = pq.ParquetWriter(
                    output_dir,
                    table.schema,
                    compression="zstd"
                )
            
            parquet_writer.write_table(table)

        if parquet_writer:
            parquet_writer.close()