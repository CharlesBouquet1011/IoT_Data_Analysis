import json

def flatten_datas(file):
    with open(file, "r") as f:
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
    with open("flattened_datas.json", "w") as f:
        json.dump(output, f, indent=2)

flatten_datas("res_114781.json")