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
Docstring for preprocessing.txtUtils
"""
import os
def write_log_removed(content:str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    chemin=os.path.join(script_dir,"logs")
    os.makedirs(chemin,exist_ok=True)
    file=os.path.join(chemin,"Removed.txt")
    with open(file,"a",encoding="utf-8") as f:
        f.write(content)