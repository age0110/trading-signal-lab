from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from . import state
from .backtester import run_backtest
from .broker import get_broker
from .models import to_dict, AutomationRule

app=FastAPI(title='Trading Signal Lab', version='0.1.0')
app.mount('/static', StaticFiles(directory='/home/ad/trading-signal-lab/app/static'), name='static')

class BacktestRequest(BaseModel):
    strategy: str='wheel_strategy'
    symbol: str='TSLA'
class AutomationRequest(BaseModel):
    name: str
    source_id: str
    cadence: str='daily 09:30 ET'
    risk_mode: str='approval_required'
    enabled: bool=True
    instructions: str='Draft orders only; require approval.'
class ManualAlert(BaseModel):
    text: str
    symbol: str='TSLA'
    side: str='buy'
    qty: float=1
class OrderDraftRequest(BaseModel):
    symbol: str='TSLA'
    side: str='buy'
    qty: float=1
    rationale: str='User requested sandbox draft order.'

@app.get('/')
def index(): return FileResponse('/home/ad/trading-signal-lab/app/static/index.html')

@app.get('/api/health')
def health(): return {'ok': True}

@app.get('/api/state')
def get_state():
    broker=get_broker()
    connections=[broker.connection(),
        {'name':'Market Data','kind':'data','status':'mock','detail':'Synthetic price history active; plug in yfinance/Alpaca data later.'},
        {'name':'Chat / Phone Control','kind':'chat','status':'mock','detail':'Use this Discord thread for commands; API endpoints are local.'},
    ]
    return {
        'connections':[to_dict(c) if hasattr(c,'__dataclass_fields__') else c for c in connections],
        'account': broker.account(),
        'sources':[to_dict(s) for s in state.sources],
        'guardrails': to_dict(state.guardrails),
        'automations':[to_dict(a) for a in state.automations],
        'draft_orders':[to_dict(o) for o in state.draft_orders],
        'learning_log': state.learning_log,
        'manual_alerts': state.manual_alerts[-10:],
    }

@app.post('/api/backtest')
def backtest(req: BacktestRequest): return to_dict(run_backtest(req.strategy, req.symbol))

@app.post('/api/automation')
def automation(req: AutomationRequest):
    rule=AutomationRule(str(len(state.automations)+1), req.name, req.source_id, req.cadence, req.risk_mode, req.enabled, req.instructions)
    state.automations.append(rule)
    state.learning_log.append({'time':'now','event':f'Automation created: {rule.name}'})
    return to_dict(rule)

@app.post('/api/ingest/manual')
def ingest(alert: ManualAlert):
    item=alert.model_dump(); state.manual_alerts.append(item)
    draft=get_broker().draft_order(alert.symbol, alert.side, alert.qty, 'Generated from manual alert: '+alert.text[:160], state.guardrails)
    state.draft_orders.append(draft)
    state.learning_log.append({'time':'now','event':f'Manual alert ingested for {alert.symbol.upper()}; draft order created.'})
    return {'alert': item, 'draft_order': to_dict(draft)}

@app.post('/api/order/draft')
def draft(req: OrderDraftRequest):
    order=get_broker().draft_order(req.symbol, req.side, req.qty, req.rationale, state.guardrails)
    state.draft_orders.append(order)
    return to_dict(order)
