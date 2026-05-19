from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

SourceKind = Literal['politician_trades', 'whale_flow', 'email_alerts', 'manual_alerts', 'wheel_strategy']
RiskMode = Literal['observe', 'paper', 'approval_required', 'auto_paper']

@dataclass
class Connection:
    name: str
    kind: str
    status: Literal['connected','mock','missing','error']
    detail: str

@dataclass
class Guardrails:
    max_position_pct: float = 5.0
    max_daily_loss_pct: float = 2.0
    require_human_approval: bool = True
    allowed_strategies: List[str] = field(default_factory=lambda: ['copy_trade', 'cash_secured_put', 'covered_call', 'wheel'])
    blocked_symbols: List[str] = field(default_factory=list)
    min_backtest_sharpe: float = 0.6

@dataclass
class SignalSource:
    id: str
    name: str
    kind: SourceKind
    connected: bool
    description: str
    last_signal: str

@dataclass
class AutomationRule:
    id: str
    name: str
    source_id: str
    cadence: str
    risk_mode: RiskMode
    enabled: bool
    instructions: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat()+'Z')

@dataclass
class BacktestResult:
    strategy: str
    symbol: str
    start_equity: float
    end_equity: float
    total_return_pct: float
    benchmark_return_pct: float
    sharpe: float
    max_drawdown_pct: float
    win_rate_pct: float
    trades: int
    equity_curve: List[Dict[str, Any]]
    notes: List[str]

@dataclass
class DraftOrder:
    id: str
    symbol: str
    side: Literal['buy','sell']
    qty: float
    order_type: str
    time_in_force: str
    status: Literal['draft','approved','rejected','submitted']
    rationale: str
    guardrail_checks: List[str]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat()+'Z')

def to_dict(obj):
    return asdict(obj)
