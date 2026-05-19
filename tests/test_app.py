from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get('/api/health')
    assert r.status_code == 200
    assert r.json()['ok'] is True

def test_state_contains_framework_parts():
    r = client.get('/api/state')
    assert r.status_code == 200
    data = r.json()
    assert data['sources']
    assert data['guardrails']['require_human_approval'] is True
    assert any(c['kind'] == 'broker' for c in data['connections'])

def test_backtest_wheel_returns_metrics():
    r = client.post('/api/backtest', json={'strategy':'wheel_strategy','symbol':'TSLA'})
    assert r.status_code == 200
    data = r.json()
    assert data['strategy'] == 'wheel_strategy'
    assert data['equity_curve']
    assert 'sharpe' in data
    assert data['trades'] > 0

def test_manual_alert_creates_draft_order():
    r = client.post('/api/ingest/manual', json={'text':'buy 3 tsla if guardrails pass','symbol':'TSLA','side':'buy','qty':3})
    assert r.status_code == 200
    data = r.json()
    assert data['draft_order']['symbol'] == 'TSLA'
    assert data['draft_order']['status'] == 'draft'
    assert data['draft_order']['guardrail_checks']
