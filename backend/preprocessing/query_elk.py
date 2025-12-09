from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
#from elasticsearch_dsl import Search, Q, Date, Range, A 
import json
import os

def download_data(gte="2023-10-12T00:00:00",lt="2023-10-13T00:00:00",year="2023",month="octobre"):
    es = Elasticsearch("http://abita.alias.inria.fr:9200")
    script_dir = os.path.dirname(os.path.abspath(__file__))

    query = {"query": {
            "match_all": {}
            }
    }

    query = {"query":{
            "range":{
                "@timestamp":{
                    "gte": gte ,
                    "lt": lt
                    }
                }
            }
    }

    index = "loraproject1"


    #resp = es.search(index=index, query=query, from_=1, size=10000)


    res = dict()

    nb=0
    nb_reboot = 0
    resp = scan(client=es, query=query, index=index, scroll="5m", size=10000)

    for h in resp:
        if nb == 0:
            print(h)

        d= h["_source"]
        if "RebootGW" in d:
            nb_reboot += 1
        else:
            nb += 1
            gw = d["GW_EUI"]
            ts = d["@timestamp"]
            res[ts] = res.get(ts, [])
            res[ts].append(d)

            if nb%10000 == 0:
                print(nb//10000, "* 10 000 éléments")
            if nb%1000000 == 0:
                print(nb,"éléments => création fichier")
                with open(f"res_{nb//1000000}.json", "w") as f:
                    json.dump(res, f, sort_keys=True, indent=4)
                res=dict()

    print(nb,"-",len(res),"éléments au total (nb_reboot =",nb_reboot,")")

    path=os.path.join(script_dir,f"./Download/{year}")
    os.makedirs(path,exist_ok=True)
    filepath=os.path.join(path,month)
    with open(filepath, "w") as f:
        json.dump(res, f, sort_keys=True, indent=4)
    
    return filepath

"""
tranche = 1000
res = []



for i in range(nb//tranche):
    start = i*tranche
    end = min((i+1)*tranche, nb)
      
    print(f"From {start} to {end}")


    slice = s[start:end]


    for hit in slice.scan():    
        res.append(hit.to_dict())
    
    print(len(res))
"""

if __name__=="__main__":
    #tests

    download_data()
    pass