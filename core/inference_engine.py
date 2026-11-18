import io
import pathlib
from collections import Counter
from typing import Dict, Any
import clips


class CaptureRouter(clips.Router):
    """
    Роутер, перехватывающий вывод CLIPS в буфер.
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

    def __init__(self, kb_dir: str = None):
        # Если путь не передан, ищем папку knowledge_base в корне проекта
        if kb_dir is None:
            base_dir = pathlib.Path(__file__).parent.parent
            kb_dir = base_dir / "knowledge_base"
        else:
            kb_dir = pathlib.Path(kb_dir)

        self.env = clips.Environment()
        
        # Загружаем все .clp файлы в алфавитном порядке.
        # Это гарантирует, что 00_base.clp (с шаблонами и функциями) 
        # загрузится самым первым, а остальные файлы смогут его использовать.
        for clp_file in sorted(kb_dir.glob("*.clp")):
            self.env.load(str(clp_file))

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

    def assert_symptom(self, name: str, duration: str = "unknown"):
        """
        Добавляет факт симптома. 
        Параметр severity удален, так как в UI нет ползунков, 
        а в шаблоне CLIPS нет этого слота.
        """
        self.env.find_template("symptom").assert_fact(
            name=clips.Symbol(name),
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