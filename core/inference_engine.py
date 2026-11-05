import io
from collections import Counter
from typing import Dict, Any
import clips


class CaptureRouter(clips.Router):
    """
    Роутер, перехватывающий вывод CLIPS в буфер.

    Наследуется от clips.Router (абстрактный класс), поэтому обязан
    передать в super().__init__ имя и приоритет.
    """

    def __init__(self, name: str = "capture-router", priority: int = 10):
        super().__init__(name, priority)
        self.buffer = io.StringIO()

    def query(self, name: str) -> bool:
        # Перехватываем стандартный вывод и трассировку watch
        return name in ("stdout", "trace")

    def write(self, name: str, message: str):
        self.buffer.write(message)

    def getvalue(self) -> str:
        return self.buffer.getvalue()

    def clear(self):
        self.buffer = io.StringIO()


class MedicalExpertSystem:
    """Обёртка над CLIPS с многоуровневым выводом и сбором объяснений."""

    def __init__(self, kb_path: str = "knowledge_base/medical.clp"):
        self.env = clips.Environment()
        self.env.load(kb_path)

        # Подключаем собственный роутер
        self.router = CaptureRouter()
        self.env.add_router(self.router)

        # Включаем трассировку срабатывания правил
        self.env.eval("(watch rules)")

    def reset(self):
        self.env.reset()
        self.router.clear()
        self.env.eval("(watch rules)")

    # ---------- ввод ----------
    def assert_patient(self, age: int = 0, sex: str = "unknown", pregnant: str = "no"):
        t = self.env.find_template("patient")
        t.assert_fact(age=age, sex=clips.Symbol(sex), pregnant=clips.Symbol(pregnant))

    def assert_chronic(self, name: str):
        self.env.find_template("chronic-condition").assert_fact(name=clips.Symbol(name))

    def assert_symptom(self, name: str, severity: int = 5, duration: str = "unknown"):
        self.env.find_template("symptom").assert_fact(
            name=clips.Symbol(name),
            severity=severity,
            duration=clips.Symbol(duration),
        )

    # ---------- вывод ----------
    def run(self) -> Dict[str, Any]:
        self.env.run()

        recommendations, red_flags, syndromes = [], [], []
        for fact in self.env.facts():
            tn = fact.template.name
            if tn == "recommendation":
                recommendations.append({
                    "specialist": str(fact["specialist"]),
                    "cf": float(fact["cf"]),
                    "urgency": str(fact["urgency"]),
                })
            elif tn == "red-flag":
                red_flags.append({
                    "name": str(fact["name"]),
                    "action": str(fact["action"]),
                })
            elif tn == "syndrome":
                syndromes.append({
                    "type": str(fact["type"]),
                    "cf": float(fact["cf"]),
                })

        best = max(recommendations, key=lambda r: r["cf"]) if recommendations else None

        # Парсим трассировку: строки вида "FIRE 1 syn-cardiac-radiation: ..."
        fired = Counter()
        for line in self.router.getvalue().splitlines():
            if line.startswith("FIRE"):
                parts = line.split()
                if len(parts) >= 3:
                    fired[parts[2].rstrip(":")] += 1

        return {
            "best_recommendation": best,
            "all_recommendations": recommendations,
            "red_flags": red_flags,
            "syndromes": sorted(syndromes, key=lambda s: -s["cf"]),
            "fired_rules": dict(fired),
            "trace": self.router.getvalue(),
        }