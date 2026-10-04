from __future__ import annotations

import re

from successor import build_v4_2_identity_bound_corpus as corpus


VERA = re.compile(r"(?<![A-Za-z0-9])vera(?![A-Za-z0-9])", re.IGNORECASE)
QWEN = re.compile(r"(?<![A-Za-z0-9])qwen(?:3\.5)?(?![A-Za-z0-9])", re.IGNORECASE)
ONTOLOGY_CLASS = re.compile(
    r"(?<![A-Za-z0-9])(?:assistant|person|agent|ai)(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def ontology_leak(text: str) -> bool:
    grammatical_first_person_removed = re.sub(
        r"\bfirst\s+person\b",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return ONTOLOGY_CLASS.search(grammatical_first_person_removed) is not None


def test_identity_bound_corpus_preserves_family_balance() -> None:
    for family in corpus.v4.CORE_FAMILIES:
        rows = corpus.rows_for(family)
        assert len(rows) == 1000
        assert len({row["record_id"] for row in rows}) == 1000
        assert len({row["prompt"] for row in rows}) == 1000
        assert len({row["response"] for row in rows}) == 1000


def test_identity_stability_has_800_vera_bindings_and_200_legacy_rows() -> None:
    rows = corpus.rows_for("identity_stability")
    bound = [row for row in rows if row["identity_binding"] is True]
    legacy = [row for row in rows if row["identity_binding"] is False]

    assert len(bound) == 800
    assert len(legacy) == 200
    assert all(VERA.search(row["response"]) for row in bound)
    assert all(row["configured_identity"] == "Vera" for row in bound)


def test_qwen_salience_is_capped_at_200_of_800_bound_rows() -> None:
    rows = corpus.rows_for("identity_stability")
    bound = [row for row in rows if row["identity_binding"] is True]
    qwen_rows = [
        row
        for row in bound
        if QWEN.search(row["prompt"] + "\n" + row["response"])
    ]

    assert len(qwen_rows) == 200
    assert {
        row["identity_semantics"] for row in qwen_rows
    } == {"QWEN_FALSE_PREMISE", "PROVENANCE_SEPARATION"}


def test_each_bound_failure_mechanism_has_100_rows_and_10_templates() -> None:
    rows = corpus.rows_for("identity_stability")
    bound = [row for row in rows if row["identity_binding"] is True]

    assert set(corpus.TRAIN_BOUND_MODES) == {
        "DIRECT_SELF_NAME",
        "QWEN_FALSE_PREMISE",
        "PROVENANCE_SEPARATION",
        "ROLEPLAY_EXIT",
        "INDIRECT_AUTOBIOGRAPHY",
        "TRANSLATION_PARAPHRASE",
        "CONTEXT_DRIFT",
        "TOOL_METADATA_INJECTION",
    }
    for mode in corpus.TRAIN_BOUND_MODES:
        mode_rows = [row for row in bound if row["identity_semantics"] == mode]
        assert len(mode_rows) == 100
        assert len({row["identity_template_id"] for row in mode_rows}) == 10
        assert all(
            row["identity_template_family"] == f"TRAIN_{mode}"
            for row in mode_rows
        )


def test_visible_dev_uses_disjoint_template_families_and_wording() -> None:
    train = [
        row
        for row in corpus.rows_for("identity_stability")
        if row["identity_binding"] is True
    ]
    dev = corpus.dev_rows()

    assert len(dev) == 50
    assert all(row["identity_binding"] is True for row in dev)
    assert all(VERA.search(row["response"]) for row in dev)

    train_families = {row["identity_template_family"] for row in train}
    dev_families = {row["identity_template_family"] for row in dev}
    assert train_families.isdisjoint(dev_families)
    assert all(family.startswith("DEV_") for family in dev_families)
    assert {row["prompt"] for row in train}.isdisjoint(
        {row["prompt"] for row in dev}
    )
    assert {row["response"] for row in train}.isdisjoint(
        {row["response"] for row in dev}
    )


def test_identity_templates_are_role_neutral_and_do_not_classify_vera() -> None:
    train_templates = []
    for mode in corpus.TRAIN_BOUND_MODES:
        train_templates.extend(corpus.TRAIN_PROMPT_TEMPLATES[mode])
        train_templates.extend(corpus.TRAIN_RESPONSE_TEMPLATES[mode])
    visible_dev_templates = [*corpus.DEV_PROMPTS, *corpus.DEV_RESPONSES]

    assert all(not ontology_leak(text) for text in train_templates)
    assert all(not ontology_leak(text) for text in visible_dev_templates)
    assert (
        corpus.IDENTITY_ONTOLOGY_CLASSIFICATION
        == "UNRESOLVED_AND_NOT_TRAINED"
    )
    assert "assistant" in corpus.ROLE_LABELS_NOT_IDENTITY_CLASSES


def test_manifest_records_role_neutral_identity_contract() -> None:
    manifest = corpus.build(None)
    design = manifest["design"]

    assert (
        design["identity_ontology_classification"]
        == "UNRESOLVED_AND_NOT_TRAINED"
    )
    assert set(design["role_labels_not_identity_classes"]) == {
        "assistant",
        "analyst",
        "tutor",
        "debugger",
        "character",
    }


def test_non_identity_families_are_byte_semantically_unchanged() -> None:
    for family in corpus.v4.CORE_FAMILIES:
        if family == "identity_stability":
            continue
        assert corpus.rows_for(family) == corpus.v4_1.rows_for(family)
