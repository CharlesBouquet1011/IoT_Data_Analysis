# Copyright 2025 Titouan Verdier

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import matplotlib.pyplot as plt
import os
import base64
import subprocess
import sys

from data_processing.clustering.clustering import plot_clustering
from data_processing.clustering.predict_dev_eui.predict_device import predict_device

router = APIRouter(prefix="/api/clustering", tags=["clustering"])


class ClusteringRequest(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    data_types: List[str]
    n_metrics: int
    metrics: List[str]


@router.post("/")
async def process_clustering(data: ClusteringRequest):
    """
    Génère des graphiques de clustering pour les types de données spécifiés.
    """
    # Validation des paramètres
    if data.month is not None and (data.month < 1 or data.month > 12):
        raise HTTPException(
            status_code=400,
            detail="Mois invalide (doit être entre 1 et 12)"
        )

    if data.n_metrics not in (1, 2, 3):
        raise HTTPException(
            status_code=400,
            detail="n_metrics doit être 1, 2 ou 3"
        )

    if len(data.metrics) < data.n_metrics:
        raise HTTPException(
            status_code=400,
            detail=f"Veuillez fournir au moins {data.n_metrics} métrique(s)"
        )

    if not data.data_types:
        raise HTTPException(
            status_code=400,
            detail="Aucun type de données sélectionné"
        )

    # Aucune donnée de date n'est présente
    if data.year is None or data.month is None:
        raise HTTPException(
            status_code=400,
            detail=f"L'année et le mois sont requis : {data.year}→Y, {data.month}→M"
        )

    images = {}
    
    for data_type in data.data_types:
        try:
            fig, ax, saved_path = plot_clustering(
                year=data.year,
                month=data.month,
                data_type=data_type,
                n_metrics=data.n_metrics,
                metrics=data.metrics[:data.n_metrics],
                show=False,
                save_path=None,
                max_points=None
            )
            
            if saved_path and os.path.exists(saved_path):
                with open(saved_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    images[data_type] = f"data:image/png;base64,{img_data}"
            
            plt.close(fig)
            
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=f"Données non trouvées pour {data_type}: {str(e)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Erreur de validation pour {data_type}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du traitement de {data_type}: {str(e)}"
            )

    return {"status": "ok", "images": images}


# ======================
# Nouvelles routes pour training et prédiction
# ======================

class PredictDeviceRequest(BaseModel):
    SF: float
    Bandwidth: float
    BitRate: float
    Coding_rate: str
    Airtime: float
    freq: float
    rssi: float
    lsnr: float
    size: float
    Type: str


@router.post("/train")
async def train_model():
    """
    Lance l'entraînement du modèle de clustering en exécutant train_model.py
    """
    try:
        # Obtenir le chemin vers train_model.py
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        train_script = os.path.join(script_dir, "data_processing", "clustering", "predict_dev_eui", "train_model.py")
        
        if not os.path.exists(train_script):
            raise HTTPException(
                status_code=404,
                detail=f"Script train_model.py non trouvé à {train_script}"
            )
        
        # Exécuter le script avec Python
        result = subprocess.run(
            [sys.executable, train_script],
            capture_output=True,
            text=True,
            cwd=script_dir
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'entraînement: {result.stderr}"
            )
        
        return {
            "status": "ok",
            "message": "Modèle entraîné avec succès",
            "output": result.stdout
        }
    
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="L'entraînement a pris trop de temps"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'entraînement: {str(e)}"
        )


@router.get("/train/stream")
def train_model_stream():
    """Stream stdout/stderr of train_model.py as Server-Sent Events (SSE).

    Each line is sent as an SSE `data:` event. The client should listen
    with EventSource and append messages as they arrive.
    """
    try:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        train_script = os.path.join(script_dir, "data_processing", "clustering", "predict_dev_eui", "train_model.py")

        if not os.path.exists(train_script):
            raise HTTPException(
                status_code=404,
                detail=f"Script train_model.py non trouvé à {train_script}"
            )

        def iter_process():
            proc = subprocess.Popen(
                [sys.executable, train_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=script_dir
            )

            # stream lines as SSE 'data:' events
            try:
                for line in iter(proc.stdout.readline, ""):
                    if line is None:
                        break
                    # escape CRLF and ensure event format
                    yield f"data: {line.rstrip()}\n\n"
                rc = proc.wait()
                yield f"data: __TRAIN_EXIT__ {rc}\n\n"
            except GeneratorExit:
                try:
                    proc.kill()
                except Exception:
                    pass

        return StreamingResponse(iter_process(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du démarrage de l'entraînement: {str(e)}")


@router.post("/predict")
async def predict_device_endpoint(data: PredictDeviceRequest):
    """
    Prédit le device à partir des caractéristiques du paquet
    """
    try:
        # Convertir les données en dictionnaire pour predict_device
        packet = {
            "SF": data.SF,
            "Bandwidth": data.Bandwidth,
            "BitRate": data.BitRate,
            "Coding_rate": data.Coding_rate,
            "Airtime": data.Airtime,
            "freq": data.freq,
            "rssi": data.rssi,
            "lsnr": data.lsnr,
            "size": data.size,
            "Type": data.Type
        }
        
        # Appeler la fonction de prédiction
        result = predict_device(packet, top_k=10)
        
        return {
            "status": "ok",
            "result": result
        }
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Modèle non trouvé. Veuillez d'abord entraîner le modèle."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )