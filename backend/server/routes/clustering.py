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
from pydantic import BaseModel
from typing import List, Optional
import matplotlib.pyplot as plt
import os
import base64

from data_processing.clustering.clustering import plot_clustering

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

    if data.n_metrics not in (1, 2):
        raise HTTPException(
            status_code=400,
            detail="n_metrics doit être 1 ou 2"
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
