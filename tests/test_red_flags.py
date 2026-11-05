"""
Тесты красных флагов (правила rf-*, salience 100).

Красные флаги — критическая часть системы: они должны срабатывать
независимо от остального вывода и не зависеть от модификаторов.
"""


def test_possible_myocardial_infarction(es):
    es.assert_symptom("chest-pain", severity=9)
    es.assert_symptom("dyspnea", severity=7)

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "possible-mi" in flag_names
    assert "rf-chest-cardiac" in result["fired_rules"]

    # В action должно быть упоминание скорой
    action = next(rf["action"] for rf in result["red_flags"] if rf["name"] == "possible-mi")
    assert "СКОРУЮ" in action.upper()


def test_mild_chest_pain_does_not_trigger_mi(es):
    """Боль слабой интенсивности (< 7) не должна давать красный флаг."""
    es.assert_symptom("chest-pain", severity=3)
    es.assert_symptom("dyspnea", severity=4)

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "possible-mi" not in flag_names


def test_thunderclap_headache(es):
    es.assert_symptom("headache", severity=10)
    es.assert_symptom("sudden-onset")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "possible-sah" in flag_names
    assert "rf-thunderclap" in result["fired_rules"]


def test_acute_abdomen(es):
    es.assert_symptom("abdomen-pain", severity=8)
    es.assert_symptom("abdomen-rigid")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "acute-abdomen" in flag_names
    assert "rf-abdomen-rigid" in result["fired_rules"]


def test_anaphylaxis(es):
    es.assert_symptom("skin-rash")
    es.assert_symptom("dyspnea", severity=8)
    es.assert_symptom("throat-swelling")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "anaphylaxis" in flag_names
    assert "rf-anaphylaxis" in result["fired_rules"]


def test_stroke_fast(es):
    es.assert_symptom("facial-droop")
    es.assert_symptom("arm-weakness")
    es.assert_symptom("speech-difficulty")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "stroke" in flag_names
    assert "rf-stroke-fast" in result["fired_rules"]


def test_obstetric_bleeding_requires_pregnancy(es):
    """Акушерское кровотечение срабатывает только при беременности=yes."""
    es.assert_patient(sex="female", pregnant="yes")
    es.assert_symptom("vaginal-bleeding")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "obstetric-emergency" in flag_names


def test_obstetric_bleeding_not_triggered_without_pregnancy(es):
    es.assert_patient(sex="female", pregnant="no")
    es.assert_symptom("vaginal-bleeding")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "obstetric-emergency" not in flag_names


def test_suicidal_thoughts(es):
    es.assert_symptom("suicidal-thoughts")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "psychiatric-emergency" in flag_names
    assert "rf-suicidal" in result["fired_rules"]


def test_hyperglycemia_crisis(es):
    es.assert_symptom("polyuria", severity=9)
    es.assert_symptom("polydipsia")
    es.assert_symptom("confusion")

    result = es.run()

    flag_names = {rf["name"] for rf in result["red_flags"]}
    assert "hhs-dka" in flag_names


def test_red_flag_reported_in_output(es):
    """Правило report-emergency должно вывести текстовое предупреждение."""
    es.assert_symptom("facial-droop")
    es.assert_symptom("arm-weakness")
    es.assert_symptom("speech-difficulty")

    result = es.run()

    assert "ВНИМАНИЕ" in result["trace"] or "КРАСНЫЕ ФЛАГИ" in result["trace"]
    assert "report-emergency" in result["fired_rules"]