from data_processing import RepartitionCaracteristiqueGlobale,RepartitionCaracteristiqueParCategorie,Repartition_ADR_Cat,nombreDevices
from fastapi import APIRouter
import os

router = APIRouter(prefix="/api/stats", tags=["stats"])
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir=os.path.dirname(script_dir)
image_dir=os.path.join(parent_dir,"Images")
data_dir=os.path.join(parent_dir,"preprocessing","Data")
raw_data_dir=os.path.join(parent_dir,"preprocessing","Raw")