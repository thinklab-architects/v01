import json
import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from rules import run_engine

# Load environment variables from .env file
load_dotenv()
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

app = FastAPI()

# --- State Management for Rules ---
rules: List[Dict[str, Any]] = []

# 允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 在生產環境中應指定前端的網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_rules_from_file():
    """Loads rules from the JSON file into the global 'rules' variable."""
    global rules
    try:
        # Build a path to rules.json relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        rules_path = os.path.join(current_dir, "rules.json")
        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)
        print(f"✅ Rules loaded successfully. {len(rules)} rules in memory.")
    except FileNotFoundError:
        print(f"❌ ERROR: rules.json not found at {rules_path}. The rule engine will not work.")
        rules = []
    except json.JSONDecodeError:
        print("❌ ERROR: Could not decode rules.json. Please check for syntax errors.")
        # In case of a syntax error, it's safer to keep the old rules loaded.
        # Here we reset, but you might want a different strategy in production.
        rules = []

async def verify_api_key(x_api_key: str = Header(..., description="Admin API Key for privileged operations")):
    """Dependency to verify the admin API key."""
    if not ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin API key is not configured on the server. Cannot perform this action."
        )
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Admin API Key."
        )

@app.on_event("startup")
async def startup_event():
    """Load rules when the application starts."""
    load_rules_from_file()

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

@app.post("/admin/reload-rules", tags=["Admin"], dependencies=[Depends(verify_api_key)])
async def reload_rules():
    """
    **[Admin]** Reloads the compliance rules from the `rules.json` file.

    This allows for updating the rules without restarting the server. Requires a valid `X-API-KEY` in the request header.
    """
    load_rules_from_file()
    return {"message": "Rules reloaded successfully.", "rule_count": len(rules)}
