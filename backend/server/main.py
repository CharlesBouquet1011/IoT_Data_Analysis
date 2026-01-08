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
Docstring for backend.server.main

Server HTTP FastAPI pour l'application 
"""
from fastapi import FastAPI,UploadFile,File,HTTPException
import os
from server.models.preprocessing import PreprocessRequest
from preprocessing import prepare_data
from server.routes import stats
#Initialisation
app = FastAPI()
app.include_router(stats.router)
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(script_dir)
image_dir=os.path.join(parent_dir,"Images")
data_dir=os.path.join(parent_dir,"preprocessing","Data")
raw_data_dir=os.path.join(parent_dir,"preprocessing","Raw")
os.makedirs(image_dir,exist_ok=True)
os.makedirs(data_dir,exist_ok=True)
os.makedirs(raw_data_dir,exist_ok=True)


async def root():
    return {"message": "Hello World"}

@app.post("/api/upload")
async def uploadFile(file:UploadFile = File(...)): #syntaxe pour récupérer un fichier avec Fastapi
    path=os.path.join(raw_data_dir,"raw.json")
    with open(path,"wb") as f:
        while True:
            partie=await file.read(1024*1024) #lecture de 1 Mio à la fois pour ne pas prendre toute la RAM pour écrire un JSON
            if not partie:
                break
            f.write(partie)

@app.post("/api/preprocessing")
async def preprocessing(data:PreprocessRequest):
    if data.month < 1 or data.month > 12:
        raise HTTPException(
            status_code=400,
            detail="Mois invalide"
        )

    if not data.attrList:
        raise HTTPException(
            status_code=400,
            detail="Aucune caractéristique sélectionnée"
        )

    if data.rollingIntervalType == "nb":
        if not isinstance(data.rollingInterval, int) or data.rollingInterval < 2:
            raise HTTPException(
                status_code=400,
                detail="rollingInterval invalide pour le mode nb"
            )

    if data.rollingIntervalType == "Duree":
        if not isinstance(data.rollingInterval, str):
            raise HTTPException(
                status_code=400,
                detail="rollingInterval invalide pour le mode durée"
            )
    
    file=os.path.join(raw_data_dir,"raw.json")
    prepare_data(data.year,data.month,data.rollingInterval,data.attrList,file)
    return {"status":"ok","message":"Prétraitement terminé"}
        