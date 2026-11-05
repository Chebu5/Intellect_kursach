"""
Тесты модификаторов контекста (правила mod-*, salience 40).

Модификаторы должны:
  - повышать CF уже распознанного синдрома;
  - срабатывать ОДИН РАЗ (флаг modifier-applied) — защита от циклов;
  - не создавать синдром с нуля (только усиливать существующий).
"""


def _syndrome_cf(result: dict, syndrome_type: str) -> float:
    for s in result["syndromes"]:
        if s["type"] == syndrome_type:
            return s["cf"]
    return 0.0


def test_elderly_cardiac_modifier(es):
    es.assert_patient(age=70)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    assert "mod-elderly-cardiac" in result["fired_rules"]
    assert _syndrome_cf(result, "cardiac") > 0.6  # база 0.6 + модификатор


def test_young_patient_no_elderly_modifier(es):
    es.assert_patient(age=25)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    assert "mod-elderly-cardiac" not in result["fired_rules"]


def test_male_over_45_modifier(es):
    es.assert_patient(age=50, sex="male")
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    assert "mod-male-cardiac" in result["fired_rules"]


def test_female_no_male_modifier(es):
    es.assert_patient(age=50, sex="female")
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    assert "mod-male-cardiac" not in result["fired_rules"]


def test_diabetes_boosts_cardiac(es):
    es.assert_chronic("diabetes")
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    assert "mod-diabetes-cardiac" in result["fired_rules"]


def test_stacked_modifiers_increase_cf(es):
    """Пожилой мужчина-диабетик должен иметь CF кардио выше, чем без модификаторов."""
    # Baseline
    es_baseline = es.__class__(kb_path="knowledge_base/medical.clp")
    es_baseline.reset()
    es_baseline.assert_symptom("chest-pain", severity=6)
    es_baseline.assert_symptom("chest-radiation")
    baseline = es_baseline.run()
    baseline_cf = _syndrome_cf(baseline, "cardiac")

    # С модификаторами
    es.assert_patient(age=70, sex="male")
    es.assert_chronic("diabetes")
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")
    boosted = es.run()
    boosted_cf = _syndrome_cf(boosted, "cardiac")

    assert boosted_cf > baseline_cf
    assert "mod-elderly-cardiac" in boosted["fired_rules"]
    assert "mod-male-cardiac" in boosted["fired_rules"]
    assert "mod-diabetes-cardiac" in boosted["fired_rules"]


def test_modifier_fires_only_once(es):
    """Флаг modifier-applied должен предотвращать повторное срабатывание."""
    es.assert_patient(age=70)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")

    result = es.run()

    # В fired_rules правило указано ровно один раз
    assert result["fired_rules"].get("mod-elderly-cardiac") == 1


def test_modifier_does_not_create_syndrome(es):
    """Если синдрома нет вообще, модификатор не должен его создать."""
    es.assert_patient(age=70)
    # Никаких симптомов, связанных с кардио
    es.assert_symptom("headache")

    result = es.run()

    assert "mod-elderly-cardiac" not in result["fired_rules"]


def test_pregnancy_gyn_modifier(es):
    es.assert_patient(sex="female", pregnant="yes")
    es.assert_symptom("abdomen-pain")
    es.assert_symptom("lower-abdomen-pain")
    es.assert_symptom("vaginal-discharge")

    result = es.run()

    assert "mod-pregnancy-gyn" in result["fired_rules"]
    assert _syndrome_cf(result, "gyn") > 0.65


def test_smoker_pulmo_modifier(es):
    es.assert_chronic("smoker")
    es.assert_symptom("cough")
    es.assert_symptom("fever")
    es.assert_symptom("dyspnea", severity=6)

    result = es.run()

    assert "mod-smoker-pulmo" in result["fired_rules"]


def test_anticoagulant_bleeding_modifier(es):
    es.assert_patient(sex="female")
    es.assert_chronic("anticoagulants")
    es.assert_symptom("vaginal-bleeding")
    es.assert_symptom("lower-abdomen-pain")
    es.assert_symptom("vaginal-discharge")

    result = es.run()

    assert "mod-anticoagulant-bleeding" in result["fired_rules"]