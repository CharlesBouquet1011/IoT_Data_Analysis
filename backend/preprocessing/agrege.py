import os
import json
import ijson
from decimal import Decimal

script_dir = os.path.dirname(os.path.abspath(__file__))
fileDirectory = os.path.join(script_dir, "2023-12")
output_path = os.path.join(script_dir, "tout.json")

def json_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)   # ou str(obj) si tu veux zéro perte
    raise TypeError

with open(output_path, "w") as out:
    out.write("{\n")
    first = True

    for file in os.listdir(fileDirectory):
        if not file.endswith(".json"):
            continue

        with open(os.path.join(fileDirectory, file), "rb") as f:
            for key, value in ijson.kvitems(f, ""):
                if not first:
                    out.write(",\n")
                first = False

                out.write(
                    f'"{key}": {json.dumps(value, default=json_default)}'
                )

    out.write("\n}")
