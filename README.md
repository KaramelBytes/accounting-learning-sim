# Accounting Simulator - Dual-Perspective Learning Tool

**Try it live:** [Streamlit Community Cloud App](https://accounting-learning-sim-karamelbytes.streamlit.app)  
**View the code:** [GitHub Repository](https://github.com/KaramelBytes/accounting-learning-sim)

---

## About

This project is an interactive Streamlit simulator that teaches one business event from two angles:

- **The Auditor's View** (financial accounting / GAAP reporting)
- **The CFO's View** (managerial accounting / decision support)

Learners make a first-pass guess, then reveal guided feedback and side-by-side analysis.

Built by an MBA student with a background in IT, this tool was created to bridge the gap between classroom accounting theory and the decision-making reality faced by executives. Every scenario forces you to reconcile what the books say with what a manager actually needs to know.

## Current feature set

- Engine-driven random scenario generation via `AccountingScenarioEngine` in `engine.py`
- 14 built-in scenarios across financial accounting and managerial decision contexts
- A focal account prompt for debit/credit and increase/decrease reasoning
- Decision-mode scenarios that intentionally produce no journal entry until execution
- Explicit "Today" vs "Future Period" effects for accounting and cash flow timing
- Four managerial lens categories with definitions shown in the UI
- Teaching feedback for common misconceptions after reveal
- Modern warm light-themed Streamlit UI in `app.py`

## Managerial lenses used in the app

- Cash vs. Accrual Timing
- Cost Behavior
- Incremental Analysis
- Working Capital & Liquidity

## Scenario catalog

### Cash vs. Accrual Timing

- Prepaid Insurance
- Machine Purchase and Depreciation
- Credit Sale
- Cash Received Before Service
- Accrued Wages
- Multi-Period Subscription

### Working Capital & Liquidity

- Inventory Purchase on Credit
- Early Payment Discount

### Incremental Analysis

- Bad Debt Estimate
- Special Order Decision
- Make vs. Buy Decision

### Cost Behavior

- R&D Spend - Sunk Cost
- Automation - Fixed vs. Variable Cost Tradeoff
- Production Volume Increase - Fixed Cost Dilution

## How the learner flow works

1. Generate a scenario.
2. Make an accounting guess:
   - Transaction scenarios: choose debit/credit direction and whether the focal account increases or decreases.
   - Decision scenarios: decide whether a journal entry exists today.
3. Choose the most relevant managerial lens.
4. Reveal analysis to see:
   - Guess feedback and teaching notes
   - The Auditor's View: journal lines and net income timing
   - The CFO's View: lens rationale, metric output, and cash timing

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Launch the app:

```bash
streamlit run app.py
```

## Requirements

Current runtime dependency:

- streamlit (see `requirements.txt`)

## Project files

- `app.py`: Streamlit UI, state management, guessing workflow, and rendering
- `engine.py`: data models, lens taxonomy, and scenario generation logic
- `requirements.txt`: Python dependencies

## Suggested future enhancements

- Persist learner progress and streaks in session or local storage
- Add scenario filtering by lens or topic
- Add instructor mode with deterministic seeds
- Add difficulty settings and adaptive feedback depth
