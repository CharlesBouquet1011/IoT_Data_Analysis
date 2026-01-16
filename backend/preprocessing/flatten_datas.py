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
import base64
def flatten_datas(file: str, output_dir: str, chunk_size=100_000):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file)
    os.makedirs(output_dir, exist_ok=True)

    def convert_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    buffer = []
    part = 0
    parquet_writer = None
    columns_order = None  # pour forcer l'ordre des colonnes

    with open(file_path, "r", encoding="utf-8") as f:
        objects = ijson.kvitems(f, "")

        for _, packet in objects:
            if not isinstance(packet, dict):
                continue

            flat = {}
            for k, v in packet.items():
                if k == "rxpk" and isinstance(v, list) and v:
                    for rk, rv in v[0].items():
                        flat[rk] = convert_decimal(rv)
                elif k == "stat" and isinstance(v, dict):
                    for sk, sv in v.items():
                        flat[sk] = convert_decimal(sv)
                elif k not in ("rxpk", "stat"):
                    flat[k] = convert_decimal(v)
                if k == "data" and isinstance(v, str):
                    flat[k] = base64.b64decode(v)
            

            buffer.append(flat)

            if len(buffer) >= chunk_size:
                df = pd.DataFrame(buffer)

                # initialiser l'ordre des colonnes
                if columns_order is None:
                    columns_order = df.columns.tolist()

                # réordonner et ajouter les colonnes manquantes
                for col in columns_order:
                    if col not in df.columns:
                        df[col] = None
                df = df[columns_order]

                table = pa.Table.from_pandas(df, preserve_index=False)

                if parquet_writer is None:
                    parquet_writer = pq.ParquetWriter(
                        os.path.join(output_dir, "flat.parquet"),
                        table.schema,
                        compression="zstd"
                    )

                parquet_writer.write_table(table)
                buffer.clear()

        # flush final
        if buffer:
            df = pd.DataFrame(buffer)
            for col in columns_order:
                if col not in df.columns:
                    df[col] = None
            df = df[columns_order]

            table = pa.Table.from_pandas(df, preserve_index=False)
            parquet_writer.write_table(table)

        if parquet_writer:
            parquet_writer.close()
