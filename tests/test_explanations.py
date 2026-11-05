"""
Тесты механизма объяснений.

Проверяем:
  - группировка сработавших правил по этапам работает;
  - ни одно правило из fired_rules не теряется при группировке;
  - трассировка CLIPS содержит сообщения о срабатывании правил.
"""

from core.explanation import STAGES, group_explanation


def _fire_all_stages(es):
    """Сценарий, в котором срабатывают правила всех этапов."""
    es.assert_patient(age=70, sex="male")
    es.assert_chronic("diabetes")
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")
    es.assert_symptom("cough")
    es.assert_symptom("fever")
    es.assert_symptom("dyspnea", severity=6)
    return es.run()


def test_group_explanation_returns_dict(es):
    result = _fire_all_stages(es)
    grouped = group_explanation(result["fired_rules"])

    assert isinstance(grouped, dict)
    assert all(isinstance(v, list) for v in grouped.values())


def test_no_rule_lost_in_grouping(es):
    """Каждое сработавшее правило должно попасть ровно в одну группу."""
    result = _fire_all_stages(es)
    grouped = group_explanation(result["fired_rules"])

    grouped_flat = [rule for rules in grouped.values() for rule in rules]

    # Каждое имя правила (без префикса "×N") присутствует в группах
    for rule_name in result["fired_rules"]:
        assert any(rule_name in entry for entry in grouped_flat), \
            f"Правило {rule_name} потерялось при группировке"


def test_stages_present_for_multi_stage_scenario(es):
    """В комплексном сценарии должны присутствовать минимум 3 этапа."""
    result = _fire_all_stages(es)
    grouped = group_explanation(result["fired_rules"])

    assert len(grouped) >= 3


def test_red_flag_group_present(es):
    es.assert_symptom("facial-droop")
    es.assert_symptom("arm-weakness")
    es.assert_symptom("speech-difficulty")
    result = es.run()

    grouped = group_explanation(result["fired_rules"])
    rf_stage = next(
        (label for prefix, label in STAGES if prefix == "rf-"),
        None,
    )
    assert rf_stage in grouped
    assert any("rf-stroke-fast" in r for r in grouped[rf_stage])


def test_syndrome_group_present(es):
    es.assert_symptom("polyuria")
    es.assert_symptom("polydipsia")
    es.assert_symptom("weight-loss")
    result = es.run()

    grouped = group_explanation(result["fired_rules"])
    syn_stage = next(
        (label for prefix, label in STAGES if prefix == "syn-"),
        None,
    )
    assert syn_stage in grouped
    assert any("syn-diabetes" in r for r in grouped[syn_stage])


def test_modifier_group_present(es):
    es.assert_patient(age=70)
    es.assert_symptom("chest-pain", severity=6)
    es.assert_symptom("chest-radiation")
    result = es.run()

    grouped = group_explanation(result["fired_rules"])
    mod_stage = next(
        (label for prefix, label in STAGES if prefix == "mod-"),
        None,
    )
    assert mod_stage in grouped
    assert any("mod-elderly-cardiac" in r for r in grouped[mod_stage])


def test_report_group_present(es):
    """Правило report-diagnosis должно попасть в группу отчётов."""
    es.assert_symptom("heartburn")
    es.assert_symptom("sour-taste")
    result = es.run()

    grouped = group_explanation(result["fired_rules"])
    report_stage = next(
        (label for prefix, label in STAGES if prefix == "report"),
        None,
    )
    assert report_stage in grouped


def test_trace_contains_fire_messages(es):
    """Трассировка CLIPS должна содержать строки 'FIRE N <rule>:'."""
    es.assert_symptom("heartburn")
    es.assert_symptom("sour-taste")
    result = es.run()

    assert "FIRE" in result["trace"]
    assert "syn-gerd-classic" in result["trace"] or "syn-gerd" in result["trace"]


def test_empty_fired_rules_gives_empty_groups():
    """Без сработавших правил группировка возвращает пустой словарь."""
    grouped = group_explanation({})
    assert grouped == {}


def test_single_rule_grouped_correctly():
    """Единичное правило попадает в правильную группу."""
    grouped = group_explanation({"rf-chest-cardiac": 1})
    rf_stage = next(label for prefix, label in STAGES if prefix == "rf-")
    assert rf_stage in grouped
    assert "rf-chest-cardiac" in grouped[rf_stage]


def test_duplicate_rule_count_rendered():
    """Правило, сработавшее N раз, отображается как 'rule (×N)'."""
    grouped = group_explanation({"syn-cardiac-radiation": 3})
    syn_stage = next(label for prefix, label in STAGES if prefix == "syn-")
    assert any("×3" in entry for entry in grouped[syn_stage])