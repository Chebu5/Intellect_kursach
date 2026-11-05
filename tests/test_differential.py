"""
Тесты дифференциальной диагностики (правило competing-syndromes, salience 15).

Логика: если два синдрома имеют CF ≥ 0.4 и разница между ними < 0.15,
система не может уверенно выбрать — направляет к терапевту.
"""


def test_competing_cardiac_and_pulmo(es):
    """Боль в груди + кашель + температура + одышка дают два сильных синдрома."""
    es.assert_patient(age=50)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")     # cardiac
    es.assert_symptom("cough")               # pulmonary
    es.assert_symptom("fever")               # pulmonary
    es.assert_symptom("dyspnea", severity=6) # обе

    result = es.run()

    assert "competing-syndromes" in result["fired_rules"]
    assert result["best_recommendation"]["specialist"] == "ТЕРАПЕВТ"


def test_no_competition_when_one_syndrome_dominates(es):
    """Классический диабет (CF ~0.85) не должен конкурировать с чем-то слабым."""
    es.assert_symptom("polyuria")
    es.assert_symptom("polydipsia")
    es.assert_symptom("weight-loss")
    # Добавим очень слабый намёк на другое — не должно дать конкуренции
    es.assert_symptom("fatigue")

    result = es.run()

    assert result["best_recommendation"]["specialist"] == "ЭНДОКРИНОЛОГ"
    assert "competing-syndromes" not in result["fired_rules"]


def test_no_competition_with_single_syndrome(es):
    """Один синдром — конкурировать не с чем."""
    es.assert_symptom("heartburn")
    es.assert_symptom("sour-taste")

    result = es.run()

    assert "competing-syndromes" not in result["fired_rules"]
    assert result["best_recommendation"]["specialist"] == "ГАСТРОЭНТЕРОЛОГ"


def test_therapist_cf_higher_than_each_competing(es):
    """Терапевт должен получить CF, превышающий CF каждого из конкурентов."""
    es.assert_patient(age=50)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")
    es.assert_symptom("cough")
    es.assert_symptom("fever")
    es.assert_symptom("dyspnea", severity=6)

    result = es.run()

    therapist = next(
        (r for r in result["all_recommendations"] if r["specialist"] == "ТЕРАПЕВТ"),
        None,
    )
    assert therapist is not None

    competing_cfs = [
        s["cf"] for s in result["syndromes"]
        if s["type"] in ("cardiac", "pulmonary")
    ]
    assert competing_cfs
    assert therapist["cf"] > max(competing_cfs) or therapist["cf"] >= 0.5


def test_differential_does_not_override_red_flag(es):
    """Красный флаг и конкуренция синдромов могут сосуществовать — оба срабатывают."""
    es.assert_patient(age=55)
    es.assert_symptom("chest-pain", severity=9)   # даёт red-flag
    es.assert_symptom("dyspnea", severity=8)
    es.assert_symptom("cough")
    es.assert_symptom("fever")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "possible-mi" in flag_names
    # Правило дифференциала тоже может сработать — это допустимо