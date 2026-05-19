from __future__ import annotations
import math, random
from datetime import date, timedelta
from typing import Dict, List
from .models import BacktestResult

SEED_BY_SYMBOL = {'TSLA': 42, 'NVDA': 7, 'AAPL': 11, 'SPY': 1, 'MSFT': 13}

def _mock_prices(symbol: str, days: int = 252) -> List[float]:
    rnd = random.Random(SEED_BY_SYMBOL.get(symbol.upper(), 99))
    price = {'TSLA': 190, 'NVDA': 118, 'AAPL': 205, 'SPY': 525, 'MSFT': 430}.get(symbol.upper(), 100)
    out=[]
    drift = 0.00045 if symbol.upper() != 'TSLA' else 0.00065
    vol = 0.018 if symbol.upper() in ('TSLA','NVDA') else 0.010
    for _ in range(days):
        shock = rnd.gauss(drift, vol)
        price = max(5, price * (1 + shock))
        out.append(round(price, 2))
    return out

def _metrics(curve: List[float], trades: int, wins: int, benchmark: List[float], strategy: str, symbol: str, notes: List[str]) -> BacktestResult:
    returns = [(curve[i]/curve[i-1]-1) for i in range(1, len(curve))]
    avg = sum(returns)/len(returns) if returns else 0
    std = (sum((r-avg)**2 for r in returns)/max(1,len(returns)-1))**0.5 if returns else 0
    sharpe = (avg/std*math.sqrt(252)) if std else 0
    peak=curve[0]; max_dd=0
    for v in curve:
        peak=max(peak,v)
        max_dd=min(max_dd, v/peak - 1)
    end=curve[-1]
    bench_return=(benchmark[-1]/benchmark[0]-1)*100
    start_date=date.today()-timedelta(days=len(curve))
    points=[]
    for i,v in enumerate(curve):
        if i % max(1, len(curve)//80)==0 or i==len(curve)-1:
            points.append({'date': (start_date+timedelta(days=i)).isoformat(), 'equity': round(v,2)})
    return BacktestResult(strategy=strategy, symbol=symbol.upper(), start_equity=10000, end_equity=round(end,2), total_return_pct=round((end/10000-1)*100,2), benchmark_return_pct=round(bench_return,2), sharpe=round(sharpe,2), max_drawdown_pct=round(max_dd*100,2), win_rate_pct=round((wins/max(1,trades))*100,1), trades=trades, equity_curve=points, notes=notes)

def backtest_copy_trade(symbol: str='SPY', delay_days: int=2, conviction: float=0.55) -> BacktestResult:
    prices=_mock_prices(symbol, 252)
    spy=_mock_prices('SPY', 252)
    cash=10000.0; shares=0.0; curve=[]; trades=0; wins=0; entry=0.0
    for i,p in enumerate(prices):
        # mock external signal every 17 days; conviction controls buy/sell bias
        if i > delay_days and i % 17 == delay_days:
            signal_buy = random.Random(i + SEED_BY_SYMBOL.get(symbol.upper(), 99)).random() < conviction
            if signal_buy and shares == 0:
                qty=(cash*0.90)/p; shares=qty; cash-=qty*p; entry=p; trades+=1
            elif (not signal_buy) and shares > 0:
                cash += shares*p; wins += 1 if p > entry else 0; shares=0; trades+=1
        curve.append(cash + shares*p)
    if shares:
        cash += shares*prices[-1]; wins += 1 if prices[-1] > entry else 0; curve[-1]=cash
    return _metrics(curve, trades, wins, spy, 'copy_trade', symbol, [
        'Mock copy-trading simulation: external source signals are delayed before execution.',
        'Use this to validate UX and guardrail behavior; connect real source data later.'
    ])

def backtest_wheel(symbol: str='TSLA', put_delta: float=0.30, call_delta: float=0.30) -> BacktestResult:
    prices=_mock_prices(symbol, 252)
    spy=_mock_prices('SPY', 252)
    cash=10000.0; shares=0; curve=[]; trades=0; wins=0; cost_basis=0.0
    rnd=random.Random(1000 + SEED_BY_SYMBOL.get(symbol.upper(), 99))
    for i,p in enumerate(prices):
        if i % 7 == 0: # weekly option cycle
            if shares == 0:
                strike=p*(1-0.04-put_delta*0.03); premium=max(20, p*100*0.006*(0.8+rnd.random()*0.6))
                cash += premium; trades += 1; wins += 1
                # assignment if weekly move down enough
                future=prices[min(len(prices)-1, i+6)]
                if future < strike and cash >= strike*100:
                    shares=100; cash-=strike*100; cost_basis=strike-premium/100
            else:
                strike=max(cost_basis*1.03, p*(1+0.04+call_delta*0.02)); premium=max(15, p*100*0.004*(0.8+rnd.random()*0.6))
                cash += premium; trades += 1; wins += 1
                future=prices[min(len(prices)-1, i+6)]
                if future > strike:
                    cash += strike*100; wins += 1 if strike > cost_basis else 0; shares=0; cost_basis=0
        curve.append(cash + shares*p)
    return _metrics(curve, trades, wins, spy, 'wheel_strategy', symbol, [
        'Wheel simulation sells weekly cash-secured puts until assigned, then covered calls until called away.',
        'Premiums are modeled, not live option quotes. Use Alpaca/OPRA data before any real trading.'
    ])

def run_backtest(strategy: str, symbol: str) -> BacktestResult:
    if strategy == 'wheel_strategy':
        return backtest_wheel(symbol)
    return backtest_copy_trade(symbol)
