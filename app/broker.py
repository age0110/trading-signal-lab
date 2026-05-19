from __future__ import annotations
import os, uuid, requests
from typing import Dict, List
from .models import Connection, DraftOrder, Guardrails

class Broker:
    def connection(self) -> Connection: raise NotImplementedError
    def account(self) -> Dict: raise NotImplementedError
    def draft_order(self, symbol: str, side: str, qty: float, rationale: str, guardrails: Guardrails) -> DraftOrder: raise NotImplementedError

class MockBroker(Broker):
    def connection(self):
        return Connection('Mock Broker', 'broker', 'mock', 'Paper sandbox; no real orders will be sent.')
    def account(self):
        return {'mode':'mock', 'equity': 100000, 'buying_power': 100000, 'currency':'USD'}
    def draft_order(self, symbol, side, qty, rationale, guardrails):
        checks=[
            f'Max position size <= {guardrails.max_position_pct}% account equity',
            f'Max daily loss <= {guardrails.max_daily_loss_pct}% account equity',
            'Human approval required' if guardrails.require_human_approval else 'Auto-paper allowed',
        ]
        if symbol.upper() in [s.upper() for s in guardrails.blocked_symbols]: checks.append('BLOCKED: symbol is on blocklist')
        return DraftOrder(str(uuid.uuid4())[:8], symbol.upper(), side, qty, 'market', 'day', 'draft', rationale, checks)

class AlpacaPaperBroker(MockBroker):
    def __init__(self):
        self.key=os.getenv('ALPACA_API_KEY_ID')
        self.secret=os.getenv('ALPACA_API_SECRET_KEY')
        self.base=os.getenv('ALPACA_BASE_URL','https://paper-api.alpaca.markets').rstrip('/')
    def _headers(self): return {'APCA-API-KEY-ID': self.key or '', 'APCA-API-SECRET-KEY': self.secret or ''}
    def connection(self):
        if not self.key or not self.secret:
            return Connection('Alpaca Paper', 'broker', 'missing', 'Set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY to connect.')
        try:
            r=requests.get(self.base+'/v2/account', headers=self._headers(), timeout=5)
            if r.ok: return Connection('Alpaca Paper', 'broker', 'connected', 'Account API reachable; order execution remains approval-gated.')
            return Connection('Alpaca Paper', 'broker', 'error', f'HTTP {r.status_code}: {r.text[:120]}')
        except Exception as e:
            return Connection('Alpaca Paper', 'broker', 'error', str(e))
    def account(self):
        if not self.key or not self.secret: return super().account()
        try:
            r=requests.get(self.base+'/v2/account', headers=self._headers(), timeout=5)
            if r.ok:
                data=r.json(); return {'mode':'alpaca_paper','equity': data.get('equity'), 'buying_power': data.get('buying_power'), 'currency': data.get('currency','USD')}
        except Exception: pass
        return super().account()

def get_broker() -> Broker:
    return AlpacaPaperBroker()
