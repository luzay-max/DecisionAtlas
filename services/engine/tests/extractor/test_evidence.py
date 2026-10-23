from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

from app.extractor.evidence import evaluate_evidence

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / 'scripts/eval/offline_decision_evidence.py'
FIXTURE = ROOT / 'services/engine/tests/fixtures/decision_evidence/cases.json'
CASES = json.loads(FIXTURE.read_text(encoding='utf-8'))['cases']


def runner():
    spec = importlib.util.spec_from_file_location('offline_evidence_runner', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['candidate']['id'])
def test_evidence_boundaries(case):
    result = evaluate_evidence(case['candidate'])
    assert result['diagnostic_status'] == case['expected']['diagnostic_status']
    assert set(case['expected']['reasons']) <= {c['reason'] for c in result['checks']}
    assert result['automatic_acceptance'] is False
    assert result['review_required'] is True


def test_merged_and_matching_quote_cannot_grant_trust():
    candidate = copy.deepcopy(CASES[0]['candidate'])
    candidate.update(review_state='accepted', human_signed_off=True, confidence=1.0)
    candidate['citations'][0].update(kind='pull_request', merged=True)
    result = evaluate_evidence(candidate)
    assert result['diagnostic_status'] == 'review_required'
    assert result['automatic_acceptance'] is False
    assert {'field':'semantic_support','status':'not_evaluated','reason':'human_review_required'} in result['checks']


def test_historical_observations_remain_ungraded():
    module = runner()
    report = module.build_report(json.loads(FIXTURE.read_text(encoding='utf-8')))
    assert report['historical_observation_count'] == 8
    assert report['provider_counts'] == {'synthetic':13, 'fake':8}
    assert report['model_accuracy'] == 'not_evaluated'
    assert report['human_review'] == 'not_run'
    assert [row['historical_ai_classification'] for row in report['historical_observations']].count('uncertain') == 1
    for row in report['historical_observations']:
        assert row['diagnostic_status'] == 'fail'
        assert any(c['reason'] == 'missing_quote_or_snapshot' for c in row['checks'])
        assert 'regression_status' not in row


def test_cli_is_deterministic_and_reports_failure(tmp_path):
    output = tmp_path / 'output'
    command = [sys.executable, str(SCRIPT), '--output', str(output)]
    assert subprocess.run(command, capture_output=True).returncode == 0
    first = {path.name:path.read_bytes() for path in output.iterdir()}
    assert subprocess.run(command, capture_output=True).returncode == 0
    assert first == {path.name:path.read_bytes() for path in output.iterdir()}
    fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
    fixture['cases'][0]['expected']['diagnostic_status'] = 'fail'
    bad = tmp_path / 'wrong-expectation.json'
    bad.write_text(json.dumps(fixture), encoding='utf-8')
    assert subprocess.run(command + ['--fixtures', str(bad)], capture_output=True).returncode == 1
    report = json.loads((output / 'report.json').read_text(encoding='utf-8'))
    assert report['regression']['fail'] == 1


@pytest.mark.parametrize('payload', [None, [], {}, {'schema_version':1,'cases':[]}, {'schema_version':1,'cases':[{}]}])
def test_invalid_fixture_exits_two(tmp_path, payload):
    fixture = tmp_path / 'invalid.json'
    fixture.write_text(json.dumps(payload), encoding='utf-8')
    result = subprocess.run([sys.executable, str(SCRIPT), '--fixtures', str(fixture), '--output', str(tmp_path / 'out')], capture_output=True)
    assert result.returncode == 2
    assert not (tmp_path / 'out').exists()


@pytest.mark.parametrize('start,end', [(True,5), (-1,5), (0,999), (5,2), ('0',5)])
def test_invalid_spans_are_rejected(start, end):
    candidate = copy.deepcopy(CASES[0]['candidate'])
    candidate['citations'][0].update(start=start,end=end)
    assert evaluate_evidence(candidate)['diagnostic_status'] == 'fail'
