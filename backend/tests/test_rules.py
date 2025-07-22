import json
from rules import run_engine

# 載入所有規則
with open("i:/vscoding/datamining/v01/backend/rules.json", "r", encoding="utf-8") as f:
    all_rules = json.load(f)

def test_elevator_basic_requirement_fail():
    """測試：樓層數 >= 6 且電梯數 < 1，應觸發違規"""
    facts = {
        "floorCount": 7,
        "elevatorCount": 0,
        "buildingHeight": 30,
        "usage": "H-2",
        "hasRoofPlatform": False
    }
    results = run_engine(facts, all_rules)
    failed_ids = [item['id'] for item in results['failed']]
    assert "ELEVATOR_BASIC_REQUIREMENT" in failed_ids

def test_elevator_basic_requirement_pass():
    """測試：樓層數 < 6，不應觸發違規"""
    facts = {
        "floorCount": 5,
        "elevatorCount": 0,
        "buildingHeight": 20,
        "usage": "H-2",
        "hasRoofPlatform": False
    }
    results = run_engine(facts, all_rules)
    failed_ids = [item['id'] for item in results['failed']]
    assert "ELEVATOR_BASIC_REQUIREMENT" not in failed_ids
