"""
Общие фикстуры pytest.

Ключевая идея: каждый тест получает СВЕЖИЙ экземпляр MedicalExpertSystem
с уже очищенной рабочей памятью. Это изолирует тесты друг от друга —
CLIPS хранит состояние глобально для Environment, поэтому без reset()
правила из предыдущего теста могли бы повлиять на следующий.
"""

import sys
from pathlib import Path

import pytest

# Добавляем корень проекта в sys.path, чтобы `from core...` работал
# независимо от того, откуда запущен pytest.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.inference_engine import MedicalExpertSystem  # noqa: E402


@pytest.fixture
def es():
    """Свежая экспертная система перед каждым тестом."""
    system = MedicalExpertSystem(kb_path=str(ROOT / "knowledge_base" / "medical.clp"))
    system.reset()
    return system