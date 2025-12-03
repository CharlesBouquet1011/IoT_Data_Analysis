"""
Functions:
flatten_datas:
applatit le json en entrée et en crée un en sortie
"""


import json
import os

def flatten_datas(file:str,output_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file)

    with open(file_path, "r") as f:
        data = json.load(f)
    output = []
    for timestamp, packets in data.items():
        p = packets[0]
        flat = {}
        for k, v in p.items():
            if k != "rxpk" and k != "stat":
                flat[k] = v
            elif "rxpk" in p and len(p["rxpk"]) > 0:
                rx = p["rxpk"][0]
                for k, v in rx.items():
                    flat[k] = v
            elif "stat" in p and len(p["stat"]) > 0:
                stat = p["stat"]
                for k, v in stat.items():
                    flat[k] = v
            else:
                flat[k] = None
        output.append(flat)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
