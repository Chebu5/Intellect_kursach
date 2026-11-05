from typing import Dict, List


STAGES = [
    ("rf-",         "Красные флаги (экстренная помощь)"),
    ("syn-",        "Распознавание синдромов"),
    ("mod-",        "Модификаторы контекста (возраст, пол, беременность, болезни)"),
    ("promote",     "Формирование рекомендации"),
    ("competing",   "Дифференциальная диагностика"),
    ("report",      "Итоговый вывод"),
]


def group_explanation(fired: Dict[str, int]) -> Dict[str, List[str]]:
    groups = {label: [] for _, label in STAGES}
    for rule, count in fired.items():
        entry = f"{rule} (×{count})" if count > 1 else rule
        for prefix, label in STAGES:
            if rule.startswith(prefix):
                groups[label].append(entry)
                break
    return {k: v for k, v in groups.items() if v}