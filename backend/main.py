import json
from typing import List, Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .rules import run_engine

app = FastAPI()

# 允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 在生產環境中應指定前端的網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入規則
with open("i:/vscoding/datamining/v01/backend/rules.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

class BuildingParameters(BaseModel):
    floorCount: int = Field(..., gt=0, description="樓層數")
    elevatorCount: int = Field(..., ge=0, description="電梯數量")
    buildingHeight: float = Field(..., gt=0, description="建築物高度 (m)")
    usage: str = Field(..., description="使用類組 (例: A-1)")
    hasRoofPlatform: bool = Field(False, description="是否設置屋頂避難平台")

@app.post("/check-compliance")
async def check_compliance(params: BuildingParameters):
    results = run_engine(params.model_dump(), rules)
    return results
