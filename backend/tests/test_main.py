import os
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models import ComplianceRule

# Mark all tests in this file as asyncio tests
pytestmark = pytest.mark.asyncio

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "test-key")
HEADERS = {"X-API-KEY": ADMIN_API_KEY}

ELEVATOR_RULE = {
    "id": "ELEVATOR_BASIC_REQUIREMENT",
    "article": "建築技術規則 設計施工編 第55條",
    "condition": {
      "all": [
        { "fact": "floorCount", "operator": "greaterThanInclusive", "value": 6 },
        { "fact": "elevatorCount", "operator": "lessThan", "value": 1 }
      ]
    },
    "violationMsg": "電梯數量不足",
    "suggestion": "建議增設電梯",
    "severity": "必要"
}

def test_check_compliance_no_rules(client, db_session):
    """Test checking compliance when no rules are in the database."""
    # 清空資料庫規則
    db_session.execute("DELETE FROM compliance_rules")
    db_session.commit()
    client.post("/admin/reload-rules", headers=HEADERS)
    response = client.post("/check-compliance", json={
        "floorCount": 10, "elevatorCount": 0, "buildingHeight": 40,
        "usage": "H-2", "hasRoofPlatform": False
    })
    assert response.status_code == 200
    data = response.json()
    assert data["failed"] == []

import pytest

@pytest.mark.asyncio
async def test_check_compliance_with_db_rule(client, db_session):
    """Test that a rule from the DB is correctly applied."""
    # 1. Add a rule to the test database
    rule = ComplianceRule(rule_id=ELEVATOR_RULE["id"], rule_data=ELEVATOR_RULE, is_active=True)
    db_session.add(rule)
    await db_session.commit()

    # 2. Manually trigger a reload to load the rule into the app's memory
    # In a real app, this would happen on startup, but here we trigger it manually.
    client.post("/admin/reload-rules", headers=HEADERS)

    # 3. Test a failing case
    response_fail = client.post("/check-compliance", json={
        "floorCount": 7, "elevatorCount": 0, "buildingHeight": 30,
        "usage": "H-2", "hasRoofPlatform": False
    })
    assert response_fail.status_code == 200
    data_fail = response_fail.json()
    assert len(data_fail["failed"]) == 1
    assert data_fail["failed"][0]["id"] == "ELEVATOR_BASIC_REQUIREMENT"

    # 4. Test a passing case
    response_pass = client.post("/check-compliance", json={
        "floorCount": 5, "elevatorCount": 0, "buildingHeight": 20,
        "usage": "H-2", "hasRoofPlatform": False
    })
    assert response_pass.status_code == 200
    assert response_pass.json()["failed"] == []

@pytest.mark.asyncio
async def test_reload_rules(client, db_session):
    """Test the reload-rules endpoint."""
    # 清空資料庫規則
    db_session.execute("DELETE FROM compliance_rules")
    await db_session.commit()
    reload_response1 = client.post("/admin/reload-rules", headers=HEADERS)
    assert reload_response1.status_code == 200
    assert reload_response1.json().get("rule_count", 0) == 0

    # Add a rule to the DB
    rule = ComplianceRule(rule_id=ELEVATOR_RULE["id"], rule_data=ELEVATOR_RULE, is_active=True)
    db_session.add(rule)
    await db_session.commit()

    # Reload again and check if the count is updated
    reload_response2 = client.post("/admin/reload-rules", headers=HEADERS)
    assert reload_response2.status_code == 200
    assert reload_response2.json().get("rule_count", 0) == 1