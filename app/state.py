from __future__ import annotations
from typing import Dict, List
from .models import Guardrails, SignalSource, AutomationRule, DraftOrder

guardrails=Guardrails()

sources=[
    SignalSource('politicians','Politician copy-trading','politician_trades',False,'Track public congressional disclosures, delayed by reporting rules.','John Fetterman mock basket beat SPY in sample video.'),
    SignalSource('whales','Whale / unusual flow','whale_flow',False,'Track large option/stock flow and summarize into candidate signals.','No live feed connected; mock whale flow active.'),
    SignalSource('email_alerts','Creator / email alerts','email_alerts',False,'Ingest Gmail/Discord/Telegram alerts from traders you follow.','Paste alerts manually for now.'),
    SignalSource('manual','Manual alert inbox','manual_alerts',True,'Paste any trading idea and turn it into a guarded draft order/backtest.','Ready.'),
    SignalSource('wheel','Wheel strategy assistant','wheel_strategy',True,'Simulate cash-secured puts and covered calls on a chosen ticker.','TSLA wheel simulator ready.'),
]

automations=[
    AutomationRule('daily-politician-scan','Daily politician disclosure scan','politicians','daily 09:30 ET','approval_required',False,'Find new disclosures, score delayed copy-trade candidates, draft orders only.'),
    AutomationRule('weekly-wheel','Weekly wheel management','wheel','Fridays 15:30 ET','paper',True,'Review assignments, select next CSP/covered-call candidate, require approval before submit.'),
]

draft_orders: List[DraftOrder]=[]
learning_log=[
    {'time':'now','event':'Framework initialized: Source → Ingest → Guardrails → Backtest → Automate → Learn.'},
    {'time':'now','event':'Default mode is sandbox / approval-required to avoid uncontrolled trading.'},
]
manual_alerts: List[Dict]=[]
