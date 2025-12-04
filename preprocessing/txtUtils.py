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