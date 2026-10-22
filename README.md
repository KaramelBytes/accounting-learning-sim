# Accounting Simulator - Dual-Perspective Learning Tool

**Try it live:** [Streamlit Community Cloud App](https://accounting-learning-sim-karamelbytes.streamlit.app)  
**View the code:** [GitHub Repository](https://github.com/KaramelBytes/accounting-learning-sim)

---

## About

This project is an interactive Streamlit simulator that teaches one business event from two angles:

- **The Auditor's View** (financial accounting / GAAP reporting)
- **The CFO's View** (managerial accounting / decision support)

Learners make a first-pass guess, then reveal guided feedback and side-by-side analysis.

Built by an MBA student with a background in IT, this tool was created to bridge the gap between classroom accounting theory and the decision-making reality faced by executives. Each scenario pairs an accounting prediction with a numerical practice question, then explains how the reporting and managerial perspectives connect.

## Current feature set

- Engine-driven random scenario generation via `AccountingScenarioEngine` in `engine.py`
- 14 built-in scenarios across financial accounting and managerial decision contexts
- Topic selection or random practice, with a session topic-coverage checklist
- Varied focal accounts for debit/credit and increase/decrease reasoning
- One numerical practice question per scenario, including contribution and make-or-buy calculations
- Special orders that can favor acceptance, rejection, or financial indifference
- Decision-mode scenarios that intentionally produce no journal entry until execution
- Explicit "Today" vs "Future Period" effects for accounting and cash flow timing
- Four managerial lens categories with definitions and accepted secondary lenses where applicable
- Locked first-attempt submissions with financial, lens, and calculation scores
- Session accuracy, streaks, and topic coverage (reset on page reload)
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

1. Click **Start practicing**, or select a topic in the sidebar and generate a scenario.
2. Make an accounting guess:
   - Transaction scenarios: choose debit/credit direction and whether the focal account increases or decreases.
   - Decision scenarios: decide whether a journal entry exists today.
3. Choose a managerial lens and answer the numerical practice question. Enter cash outflows and adverse income changes as negative numbers when prompted; round calculations to cents.
4. Reveal analysis. All questions must be answered; submissions lock and are scored once. The lens badge appears after reveal. You will see:
   - A compact profit-versus-cash comparison with explicit future periods
   - Guess feedback, a calculation formula and worked result, and teaching notes
   - Your saved answers in a collapsed, read-only review section
   - The Auditor's View: journal lines and before-tax income effects, including conditional future results even when no journal preview is available
   - The CFO's View: lens rationale, metric output, and event-specific cash timing
5. Click **Next scenario** after the analysis to begin a fresh attempt using the selected topic; topic coverage counts submitted topics, not mastery.

## Accounting scope and assumptions

These are introductory, simplified U.S. GAAP teaching examples, not a complete reporting or investment model. Income effects are before tax. Revenue-only previews omit delivery costs unless supplied; inventory-sale previews may show only the cost component. Manufacturing wages and depreciation are treated as period expenses for the timing exercises rather than modeling a full overhead-allocation system.

- Each future income section identifies its event or period; each future cash label identifies its scope and comparison basis. Annual savings versus an alternative are distinct from absolute receipts or payments.
- Early-payment discounts assume gross recording, perpetual inventory, and unsold goods. The discount credits Inventory; its later income benefit is relative to paying the full invoice. The annualized discount return is a simple annualization, not a compounded yield.
- Bad-debt estimates reduce expected collections. The estimate and eventual write-off do not themselves cause cash payments.
- Special orders assume spare capacity, no displacement of regular sales, and cash variable costs. Make-or-buy assumes equivalent supplier quality and capacity, no alternative use of released capacity, and relevant cash costs.
- Automation assumes straight-line depreciation, zero salvage value, and the stated output and labor savings. Accounting income improvement does not establish investment value; discounting and other operating costs are excluded.
- Higher production spreads unchanged fixed overhead across more units. It does not by itself create a profit saving; the volume scenario leaves future income undetermined without a selling price.
- Lens choices overlap. Accepted secondary lenses receive credit; the worked analysis retains the catalog's primary lens. Lens accuracy is recognition practice, not proof of managerial judgment.

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

## Validation

With dependencies installed, run:

```bash
python -m unittest discover -s tests -v
```

The suite checks scenario calculations and balanced entries, answer variety, positive/negative/zero special orders, and Streamlit learner flows across all 14 topics. UI checks cover answer concealment, future-result visibility, input validation, locked submissions, and session scoring. These component tests do not assess browser layout; use the separate Chromium checks below.

For browser regression checks, install the optional tooling:

```bash
pip install playwright
python -m playwright install chromium
```

With the app running locally in another terminal, run:

```bash
python tests/browser_review.py --url http://127.0.0.1:8501 --output /tmp/accounting-layout-review
```

This checks desktop (1440px), tablet (768px), and phone (390px and 320px) layouts. It checks all 14 pre-reveal narratives and exercises decision and transaction flows, currency rendering, label and caption contrast, grouped panels, narrow journal tables, saved submissions, and next-scenario navigation. Screenshots and a JSON result summary are saved in the output directory. Browser emulation does not replace testing on physical devices or other browser engines.

The engine also accepts a deterministic seed for reproducible exercises in code: `AccountingScenarioEngine(seed=42)`. There is no instructor seed control in the UI.

## Project files

- `app.py`: Streamlit UI, state management, guessing workflow, and rendering
- `engine.py`: data models, lens taxonomy, and scenario generation logic
- `requirements.txt`: Python dependencies
- `tests/`: engine regression checks and Streamlit interaction tests

## Suggested future enhancements

- Persist progress across sessions
- Add filtering by managerial lens and practice focused on missed questions
- Expose deterministic seeds in an instructor UI
- Add difficulty settings and adaptive feedback depth
