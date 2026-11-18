from typing import Any, Dict, List

URGENCY_RANK = {"routine": 0, "urgent": 1, "emergency": 2}


def specialist_distribution(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Сводит recommendation-факты по специалистам.

    confidence — коэффициент уверенности CF в процентах.
    """
    best: Dict[str, Dict[str, Any]] = {}
    for r in recommendations:
        sp = r["specialist"]
        cur = best.get(sp)
        if cur is None:
            best[sp] = {"specialist": sp, "cf": r["cf"], "urgency": r["urgency"]}
        else:
            cur["cf"] = max(cur["cf"], r["cf"])
            if URGENCY_RANK.get(r["urgency"], 0) > URGENCY_RANK.get(cur["urgency"], 0):
                cur["urgency"] = r["urgency"]

    for item in best.values():
        item["confidence"] = round(100 * max(item["cf"], 0.0))

    return sorted(best.values(), key=lambda i: -i["cf"])
