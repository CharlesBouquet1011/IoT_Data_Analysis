# Copyright 2025 Paul-Henri Lucotte

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
from typing import Optional
import os
import base64

from data_processing.regression.regression import run_signal_models

router = APIRouter(prefix="/api/regression", tags=["regression"])


class RegressionRequest(BaseModel):
    year: int
    month: int
    data_type: str


@router.post("/")
async def process_regression(data: RegressionRequest):
    """
    Lance les modèles de régression et affiche les figures générées.
    """

    if data.month < 1 or data.month > 12:
        raise HTTPException(status_code=400, detail="Mois invalide (1–12)")

    try:
        # Run your existing regression code
        results = run_signal_models(
            year=data.year,
            month=data.month,
            data_type=data.data_type
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    images = {}
    image_paths = {
        "rssi": results["images"].get("rssi_plot"),
        "snr": results["images"].get("snr_plot"),
        "residuals": results["images"].get("residual_plots")
    }
    for key, path in image_paths.items():
        if not path or not os.path.exists(path):
            raise HTTPException(
                status_code=500,
                detail=f"Missing regression image: {key}"
            )
        with open(path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode("utf-8")
            images[key] = f"data:image/png;base64,{img_data}"

    if not images:
        raise HTTPException(status_code=500, detail="Aucune image générée")

    return {
        "status": "ok",
        "images": images,
        "stats": results.get("stats", {})
    }