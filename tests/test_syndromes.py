"""
Тесты распознавания синдромов (правила syn-*, salience 50).

Проверяем, что CF накапливается корректно: одиночные симптомы дают
слабую гипотезу, а классические триады — сильную (≥ 0.7).
"""


def _syndrome_cf(result: dict, syndrome_type: str) -> float:
    for s in result["syndromes"]:
        if s["type"] == syndrome_type:
            return s["cf"]
    return 0.0


def test_diabetes_classic_triad(es):
    es.assert_symptom("polyuria")
    es.assert_symptom("polydipsia")
    es.assert_symptom("weight-loss")

    result = es.run()

    assert _syndrome_cf(result, "diabetes") >= 0.8
    assert result["best_recommendation"]["specialist"] == "ЭНДОКРИНОЛОГ"
    assert "syn-diabetes-classic" in result["fired_rules"]


def test_diabetes_partial_weaker_than_classic(es):
    """Без похудания CF должен быть заметно ниже."""
    es.assert_symptom("polyuria")
    es.assert_symptom("polydipsia")
    # weight-loss отсутствует

    result = es.run()

    cf = _syndrome_cf(result, "diabetes")
    assert 0.4 <= cf <= 0.7
    assert "syn-diabetes-partial" in result["fired_rules"]
    assert "syn-diabetes-classic" not in result["fired_rules"]


def test_migraine(es):
    es.assert_symptom("headache")
    es.assert_symptom("photophobia")
    es.assert_symptom("nausea")

    result = es.run()

    assert _syndrome_cf(result, "migraine") >= 0.7
    assert result["best_recommendation"]["specialist"] == "НЕВРОЛОГ"


def test_migraine_with_aura(es):
    es.assert_symptom("headache")
    es.assert_symptom("visual-aura")

    result = es.run()

    assert _syndrome_cf(result, "migraine") >= 0.6
    assert "syn-migraine-aura" in result["fired_rules"]


def test_tension_headache(es):
    es.assert_symptom("headache")
    es.assert_symptom("stress")

    result = es.run()

    assert _syndrome_cf(result, "tension-headache") > 0.0
    assert "syn-tension" in result["fired_rules"]
    # Нет светобоязни → мигрень не должна доминировать
    assert _syndrome_cf(result, "migraine") < _syndrome_cf(result, "tension-headache")


def test_cluster_headache(es):
    es.assert_symptom("headache")
    es.assert_symptom("eye-pain")
    es.assert_symptom("nasal-congestion")

    result = es.run()

    assert _syndrome_cf(result, "cluster-headache") >= 0.6


def test_gerd_classic(es):
    es.assert_symptom("heartburn")
    es.assert_symptom("sour-taste")

    result = es.run()

    assert _syndrome_cf(result, "gerd") >= 0.6
    assert result["best_recommendation"]["specialist"] == "ГАСТРОЭНТЕРОЛОГ"


def test_radiculopathy_with_weakness(es):
    """Слабость в ноге — более сильный признак, чем просто онемение."""
    es.assert_symptom("back-pain")
    es.assert_symptom("leg-radiation")
    es.assert_symptom("muscle-weakness")

    result = es.run()

    assert _syndrome_cf(result, "radiculopathy") >= 0.7
    assert "syn-radic-weakness" in result["fired_rules"]


def test_hypothyroid(es):
    es.assert_symptom("cold-intolerance")
    es.assert_symptom("weight-gain")
    es.assert_symptom("fatigue")

    result = es.run()

    assert _syndrome_cf(result, "hypothyroid") >= 0.5
    assert result["best_recommendation"]["specialist"] == "ЭНДОКРИНОЛОГ"


def test_allergy(es):
    es.assert_symptom("skin-rash")
    es.assert_symptom("itching")
    es.assert_symptom("after-contact")

    result = es.run()

    assert _syndrome_cf(result, "allergy") >= 0.7
    assert result["best_recommendation"]["specialist"] == "АЛЛЕРГОЛОГ-ИММУНОЛОГ"


def test_panic_disorder(es):
    es.assert_symptom("panic-attack")
    es.assert_symptom("palpitations")

    result = es.run()

    assert _syndrome_cf(result, "panic-disorder") >= 0.6
    assert result["best_recommendation"]["specialist"] == "ПСИХОТЕРАПЕВТ"


def test_depression(es):
    es.assert_symptom("low-mood")
    es.assert_symptom("anhedonia")
    es.assert_symptom("insomnia")

    result = es.run()

    assert _syndrome_cf(result, "depression") >= 0.7
    assert result["best_recommendation"]["specialist"] == "ПСИХИАТР"


def test_uti(es):
    es.assert_symptom("dysuria")
    es.assert_symptom("polyuria")
    es.assert_symptom("fever")

    result = es.run()

    assert _syndrome_cf(result, "uti") >= 0.5
    assert result["best_recommendation"]["specialist"] == "УРОЛОГ"


def test_renal_colic(es):
    es.assert_symptom("flank-pain", severity=8)
    es.assert_symptom("hematuria")

    result = es.run()

    assert _syndrome_cf(result, "renal-colic") >= 0.7
    assert result["best_recommendation"]["specialist"] == "УРОЛОГ"


def test_no_syndrome_below_threshold(es):
    """Один слабый симптом не должен давать рекомендацию."""
    es.assert_symptom("headache")  # без stress, без photophobia, без aura

    result = es.run()

    # Нет синдрома ≥ 0.4 → нет рекомендации
    assert result["best_recommendation"] is None