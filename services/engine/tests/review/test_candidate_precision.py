from types import SimpleNamespace

from app.review.candidate_precision import build_profile, rank_profiles


def _decision(
    decision_id: int,
    *,
    title: str,
    chosen_option: str,
    confidence: float = 0.8,
    metadata: dict | None = None,
):
    return SimpleNamespace(
        id=decision_id,
        title=title,
        problem="We need a durable engineering choice for the service.",
        chosen_option=chosen_option,
        tradeoffs="This reduces operational risk while keeping the migration reversible.",
        confidence=confidence,
        candidate_metadata_json=metadata,
        created_at=None,
    )


def _evidence(count: int = 2):
    refs = [SimpleNamespace(quote=f"grounded decision evidence {index}", url="https://example.test/source") for index in range(count)]
    artifact = SimpleNamespace(url="https://example.test/artifact")
    return refs, artifact


def test_grounded_candidate_outscores_confidence_only_candidate() -> None:
    grounded = _decision(1, title="Choose Redis cache", chosen_option="Use Redis", confidence=0.75)
    thin = _decision(2, title="Choose queue", chosen_option="Use queue", confidence=0.99)

    profiles = rank_profiles([grounded, thin], {1: _evidence(2), 2: ([], None)})

    assert profiles[1].score > profiles[2].score
    assert profiles[1].tier in {"strong", "partial"}
    assert profiles[2].tier == "weak"


def test_salvaged_and_legacy_origin_are_explicit() -> None:
    salvaged = _decision(
        1,
        title="Choose migration strategy",
        chosen_option="Use staged migration",
        metadata={"artifact_family": "migration", "parser_salvaged": True},
    )
    legacy = _decision(2, title="Choose storage", chosen_option="Use Postgres")

    salvaged_profile = build_profile(salvaged, *_evidence())
    legacy_profile = build_profile(legacy, *_evidence())

    assert salvaged_profile.parser_salvaged is True
    assert "parser_salvaged" in salvaged_profile.reasons
    assert legacy_profile.artifact_family == "unknown"
    assert legacy_profile.parser_salvaged is None
    assert "unknown_extraction_origin" in legacy_profile.reasons


def test_near_duplicates_have_stable_representative_without_deleting_rows() -> None:
    first = _decision(10, title="Choose Redis cache", chosen_option="Use Redis", confidence=0.7)
    duplicate = _decision(11, title="Choose Redis caching", chosen_option="Use Redis", confidence=0.9)
    unrelated = _decision(12, title="Choose database migration", chosen_option="Use Postgres", confidence=0.9)
    evidence = {10: _evidence(2), 11: _evidence(1), 12: _evidence(2)}

    profiles = rank_profiles([first, duplicate, unrelated], evidence)

    assert profiles[10].cluster_id == profiles[11].cluster_id
    assert profiles[profiles[10].duplicate_of or 10].is_representative
    assert profiles[12].cluster_id is None
    assert {10, 11, 12} == set(profiles)

    repeated = rank_profiles([first, duplicate, unrelated], evidence)
    assert [(item.cluster_id, item.duplicate_of, item.score) for item in repeated.values()] == [
        (item.cluster_id, item.duplicate_of, item.score) for item in profiles.values()
    ]
