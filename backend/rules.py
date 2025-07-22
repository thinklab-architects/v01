def evaluate_condition(condition: dict, facts: dict) -> bool:
    """遞迴解析並評估條件"""
    if "all" in condition:
        return all(evaluate_condition(cond, facts) for cond in condition["all"])
    if "any" in condition:
        return any(evaluate_condition(cond, facts) for cond in condition["any"])

    # 基本條件判斷
    fact_name = condition["fact"]
    operator = condition["operator"]
    value = condition["value"]
    fact_value = facts.get(fact_name)

    if fact_value is None:
        return False # or raise an error for missing fact

    op_map = {
        "equal": lambda a, b: a == b,
        "notEqual": lambda a, b: a != b,
        "lessThan": lambda a, b: a < b,
        "lessThanInclusive": lambda a, b: a <= b,
        "greaterThan": lambda a, b: a > b,
        "greaterThanInclusive": lambda a, b: a >= b,
        "in": lambda a, b: a in b,
        "notIn": lambda a, b: a not in b,
    }

    if operator in op_map:
        return op_map[operator](fact_value, value)
    else:
        raise ValueError(f"Unsupported operator: {operator}")

def run_engine(facts: dict, rules: list) -> dict:
    """
    執行規則引擎，回傳通過與未通過的項目
    """
    results = {"passed": [], "failed": []}
    for rule in rules:
        try:
            # 如果條件成立，代表違規
            is_violation = evaluate_condition(rule["condition"], facts)
            if is_violation:
                results["failed"].append({
                    "id": rule["id"],
                    "article": rule["article"],
                    "violationMsg": rule["violationMsg"],
                    "suggestion": rule["suggestion"],
                    "severity": rule["severity"],
                })
        except Exception as e:
            print(f"Error evaluating rule {rule['id']}: {e}")
    return results
