# Trading Signal Lab

A runnable MVP inspired by the YouTube workflow: **Source → Ingest → Guardrails → Backtest → Automate → Learn**.

It works immediately in sandbox mode with mock market/broker data, and it has optional hooks for Alpaca paper trading.

## Run

```bash
cd /home/ad/trading-signal-lab
python3 -m uvicorn app.main:app --reload --port 8787
```

Open: http://127.0.0.1:8787

## Optional Alpaca paper connection

Set these env vars before running if you want the broker adapter to connect instead of mock mode:

```bash
export ALPACA_API_KEY_ID=...
export ALPACA_API_SECRET_KEY=...
export ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

The MVP defaults to **human approval / paper-only behavior**. It generates draft orders and stores automation rules, but does not place live orders unless explicitly extended.

## What is included

- Trading dashboard with connections/status, strategy builder, guardrails, backtest, automations, learning log.
- Signal sources: politicians, whale/news, email/creator alerts, manual alerts, wheel strategy.
- Backtests: deterministic mock history for copy-trading and wheel strategy simulations.
- Broker abstraction: mock broker now, Alpaca paper status/orders hook if keys are present.
- API: `/api/state`, `/api/backtest`, `/api/automation`, `/api/order/draft`, `/api/ingest/manual`.

## Safety note

This is for testing/product validation. Nothing here is financial advice.
