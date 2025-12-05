# Copyright 2025 Titouan Verdier
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
