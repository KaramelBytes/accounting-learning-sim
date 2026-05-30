from __future__ import annotations

from typing import Dict, List, Tuple

import streamlit as st

from engine import (
    AccountingScenarioEngine,
    JournalEntryLine,
    ScenarioResult,
    LENS_DEFINITIONS,
)

st.set_page_config(page_title="The Dual-Perspective Simulator", page_icon="📊", layout="wide")

WARM_LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --bg-page: #faf7f2;
    --bg-card: #ffffff;
    --bg-elevated: #f5f0ea;
    --text-primary: #2d2a24;
    --text-muted: #8a8580;
    --text-dim: #b5afa8;
    --accent-teal: #1a8a7a;
    --accent-teal-soft: rgba(26, 138, 122, 0.1);
    --accent-teal-hover: #157a6c;
    --accent-amber: #d4943a;
    --accent-amber-soft: rgba(212, 148, 58, 0.12);
    --accent-coral: #e06050;
    --accent-coral-soft: rgba(224, 96, 80, 0.1);
    --accent-green: #3a9a5a;
    --accent-green-soft: rgba(58, 154, 90, 0.12);
    --border: #e8e2da;
    --border-light: #f0ece6;
    --shadow-sm: 0 1px 3px rgba(45, 42, 36, 0.06);
    --shadow-md: 0 4px 12px rgba(45, 42, 36, 0.08);
    --shadow-lg: 0 8px 24px rgba(45, 42, 36, 0.1);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}

html, body, .stApp {
    background: var(--bg-page);
    color: var(--text-primary);
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, rgba(26, 138, 122, 0.04), transparent 60%),
        radial-gradient(ellipse at 100% 100%, rgba(212, 148, 58, 0.04), transparent 60%),
        var(--bg-page);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text-primary);
}

p, li, label, span, .stMarkdown, .stText {
    color: var(--text-primary);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
}

[data-testid="stSidebar"] {
    background: var(--bg-card);
    border-right: 1px solid var(--border-light);
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: var(--text-primary);
}

[data-testid="stSidebar"] hr {
    border-color: var(--border-light);
}

.sidebar-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent-teal);
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-light);
}

.stats-card {
    background: var(--bg-elevated);
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
}

.stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
    border-bottom: 1px solid var(--border-light);
}

.stat-row:last-child {
    border-bottom: none;
}

.stat-label {
    font-size: 0.78rem;
    color: var(--text-muted);
}

.stat-value {
    font-size: 1rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--text-primary);
}

.stat-value.good {
    color: var(--accent-green);
}

.stat-value.teal {
    color: var(--accent-teal);
}

.streak-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: var(--accent-amber-soft);
    color: var(--accent-amber);
    padding: 0.15rem 0.55rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}

.step-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    margin: 0 0 1.5rem 0;
    padding: 0.75rem 0;
}

.step-group {
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.step-circle {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    transition: all 0.3s ease;
    flex-shrink: 0;
}

.step-circle.completed {
    background: var(--accent-teal);
    color: white;
}

.step-circle.active {
    background: var(--bg-card);
    color: var(--accent-teal);
    border: 2px solid var(--accent-teal);
    box-shadow: 0 0 0 4px var(--accent-teal-soft);
}

.step-circle.pending {
    background: var(--bg-elevated);
    color: var(--text-dim);
    border: 2px solid var(--border);
}

.step-label {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-muted);
    white-space: nowrap;
}

.step-label.active {
    color: var(--accent-teal);
    font-weight: 600;
}

.step-label.completed {
    color: var(--accent-teal);
}

.step-connector {
    width: 44px;
    height: 2px;
    background: var(--border);
    border-radius: 2px;
    transition: background 0.3s ease;
    flex-shrink: 0;
}

.step-connector.completed {
    background: var(--accent-teal);
}

.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow-sm);
}

.card-scenario {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem 1.5rem 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-md);
    position: relative;
}

.card-scenario::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--accent-teal);
    border-radius: 4px 0 0 4px;
}

.card-analysis {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    height: 100%;
}

.lens-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.75rem;
}

.lens-badge.teal { background: var(--accent-teal-soft); color: var(--accent-teal); }
.lens-badge.amber { background: var(--accent-amber-soft); color: var(--accent-amber); }
.lens-badge.coral { background: var(--accent-coral-soft); color: var(--accent-coral); }
.lens-badge.green { background: var(--accent-green-soft); color: var(--accent-green); }

.section-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border-light);
}

.section-number {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--accent-teal);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    flex-shrink: 0;
}

.section-number.completed {
    background: var(--accent-green);
}

.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
}

.scenario-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
}

.scenario-text {
    font-size: 0.95rem;
    line-height: 1.7;
    color: var(--text-primary);
}

.decision-notice {
    background: var(--accent-amber-soft);
    border: 1px solid rgba(212, 148, 58, 0.2);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.88rem;
}

.decision-notice strong {
    color: var(--accent-amber);
}

.focal-block {
    background: var(--bg-elevated);
    border-radius: var(--radius-sm);
    padding: 0.85rem 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.85rem;
}

.focal-icon {
    width: 38px;
    height: 38px;
    border-radius: var(--radius-sm);
    background: var(--accent-teal-soft);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}

.focal-info { flex: 1; }

.focal-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.05rem;
}

.focal-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--accent-teal);
}

.focal-type {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.1rem;
}

.journal-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.88rem;
    margin-bottom: 0.75rem;
}

.journal-table th {
    text-align: left;
    padding: 0.45rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-muted);
    border-bottom: 2px solid var(--border);
}

.journal-table td {
    padding: 0.5rem 0.65rem;
    border-bottom: 1px solid var(--border-light);
    vertical-align: top;
}

.journal-table tr:last-child td {
    border-bottom: none;
}

.journal-table .account-name {
    font-weight: 600;
    color: var(--text-primary);
}

.journal-table .account-type {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.1rem;
}

.journal-table .movement-label {
    font-size: 0.72rem;
    margin-top: 0.05rem;
}

.journal-table .movement-inc { color: var(--accent-green); }
.journal-table .movement-dec { color: var(--accent-coral); }
.journal-table .movement-na { color: var(--text-dim); }

.journal-table .amount-debit {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    color: var(--accent-teal);
}

.journal-table .amount-credit {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    color: var(--accent-coral);
}

.journal-table .amount-na {
    color: var(--text-dim);
    font-style: italic;
}

.feedback-card {
    border-radius: var(--radius-md);
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
}

.feedback-icon {
    font-size: 1.15rem;
    flex-shrink: 0;
    margin-top: 0.05rem;
}

.feedback-content { flex: 1; }
.feedback-content strong { font-weight: 600; }

.feedback-good {
    background: var(--accent-green-soft);
    border: 1px solid rgba(58, 154, 90, 0.2);
}

.feedback-learn {
    background: var(--accent-amber-soft);
    border: 1px solid rgba(212, 148, 58, 0.2);
}

.feedback-perfect {
    background: linear-gradient(135deg, var(--accent-teal-soft), var(--accent-green-soft));
    border: 1px solid rgba(26, 138, 122, 0.2);
}

.lens-def-block {
    background: var(--bg-elevated);
    border-radius: var(--radius-sm);
    padding: 0.7rem 0.9rem;
    font-size: 0.84rem;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    line-height: 1.5;
}

.teaching-note {
    background: var(--accent-amber-soft);
    border: 1px solid rgba(212, 148, 58, 0.15);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-top: 1rem;
    font-size: 0.88rem;
    line-height: 1.5;
}

.teaching-note strong {
    color: var(--accent-amber);
}

.analysis-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
    margin-top: 1rem;
}

.metric-highlight {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--accent-teal);
    padding: 0.4rem 0;
}

.stButton > button {
    border-radius: var(--radius-sm);
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-primary);
    transition: all 0.2s ease;
    min-height: 44px;
    box-shadow: var(--shadow-sm);
}

.stButton > button:hover {
    border-color: var(--accent-teal);
    color: var(--accent-teal);
    box-shadow: var(--shadow-md);
}

.stButton > button[kind="primary"] {
    background: var(--accent-teal);
    color: white;
    border-color: var(--accent-teal);
    box-shadow: 0 2px 8px rgba(26, 138, 122, 0.25);
}

.stButton > button[kind="primary"]:hover {
    background: var(--accent-teal-hover);
    border-color: var(--accent-teal-hover);
    box-shadow: 0 4px 12px rgba(26, 138, 122, 0.3);
}

[data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
    background: var(--bg-card);
    border-color: var(--border);
    border-radius: var(--radius-sm);
    min-height: 44px;
}

[data-testid="stSelectbox"] div[data-baseweb="select"] * {
    color: var(--text-primary) !important;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
    font-size: 0.82rem;
}

.stAlert {
    background: var(--accent-teal-soft);
    color: var(--text-primary);
    border: 1px solid rgba(26, 138, 122, 0.2);
    border-radius: var(--radius-sm);
}

.streamlit-expanderHeader {
    background: var(--bg-elevated);
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    color: var(--text-primary);
}

.stDivider {
    border-color: var(--border-light);
}

@media (max-width: 768px) {
    .step-indicator {
        gap: 0.25rem;
        padding: 0.5rem 0;
        overflow-x: auto;
        justify-content: flex-start;
    }

    .step-circle {
        width: 28px;
        height: 28px;
        font-size: 0.72rem;
    }

    .step-label {
        font-size: 0.68rem;
    }

    .step-connector {
        width: 20px;
    }

    .analysis-grid {
        grid-template-columns: 1fr;
    }

    .card-scenario {
        padding: 1rem 1rem 1rem 1.25rem;
    }

    .scenario-title {
        font-size: 1.1rem;
    }

    .focal-block {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.4rem;
    }

    .journal-table {
        font-size: 0.78rem;
    }

    .journal-table th,
    .journal-table td {
        padding: 0.35rem 0.4rem;
    }

    .header-title {
        font-size: 0.95rem;
    }
}

@media (max-width: 480px) {
    .step-connector {
        width: 12px;
    }

    .step-circle {
        width: 24px;
        height: 24px;
        font-size: 0.68rem;
    }

    .card-scenario {
        padding: 0.85rem;
    }

    .scenario-text {
        font-size: 0.88rem;
    }
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeInUp 0.35s ease-out;
}

@keyframes pulse-green {
    0% { box-shadow: 0 0 0 0 rgba(58, 154, 90, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(58, 154, 90, 0); }
    100% { box-shadow: 0 0 0 0 rgba(58, 154, 90, 0); }
}

.pulse-correct {
    animation: pulse-green 0.6s ease-out;
}

.app-footer {
    text-align: center;
    padding: 2rem 1rem 1rem;
    font-size: 0.78rem;
    color: var(--text-dim);
    line-height: 1.6;
}

.app-footer a {
    color: var(--accent-teal);
    text-decoration: none;
    font-weight: 500;
}

.app-footer a:hover {
    text-decoration: underline;
}

.app-footer .footer-divider {
    display: inline-block;
    width: 4px;
    height: 4px;
    background: var(--text-dim);
    border-radius: 50%;
    margin: 0 0.5rem;
    vertical-align: middle;
    opacity: 0.5;
}
</style>
"""

LENS_OPTIONS = list(LENS_DEFINITIONS.keys())

LENS_COLORS: Dict[str, str] = {
    "Cash vs. Accrual Timing": "teal",
    "Cost Behavior": "amber",
    "Incremental Analysis": "coral",
    "Working Capital & Liquidity": "green",
}

LENS_EMOJIS: Dict[str, str] = {
    "Cash vs. Accrual Timing": "⏱",
    "Cost Behavior": "📊",
    "Incremental Analysis": "🎯",
    "Working Capital & Liquidity": "💧",
}


def init_state() -> None:
    if "engine" not in st.session_state:
        st.session_state.engine = AccountingScenarioEngine()
    if "scenario" not in st.session_state:
        st.session_state.scenario = None
    if "reveal" not in st.session_state:
        st.session_state.reveal = False
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "attempted": 0,
            "correct_financial": 0,
            "correct_lens": 0,
            "perfect": 0,
            "streak": 0,
            "best_streak": 0,
            "lens_results": {l: {"correct": 0, "total": 0} for l in LENS_OPTIONS},
        }
    if "stats_recorded_for" not in st.session_state:
        st.session_state.stats_recorded_for = None


def format_money(value: float) -> str:
    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):,.0f}"


def net_income_direction(value: float) -> str:
    if value > 0:
        return "Increase"
    if value < 0:
        return "Decrease"
    return "No immediate effect"


def account_movement(line: JournalEntryLine) -> Tuple[str, str]:
    if line.direction not in {"Debit", "Credit"}:
        return ("neutral", "No account movement yet")
    normal_debit_types = {"Asset", "Expense", "Contra-Liability"}
    normal_credit_types = {"Liability", "Equity", "Revenue", "Contra-Asset", "Contra-Expense"}
    if line.account_type in normal_debit_types:
        increases = line.direction == "Debit"
    elif line.account_type in normal_credit_types:
        increases = line.direction == "Credit"
    else:
        return ("neutral", "Classification depends on policy context")
    if increases:
        return ("inc", "Increases")
    return ("dec", "Decreases")


def render_journal_table(lines: list[JournalEntryLine]) -> None:
    if not lines:
        st.markdown('<div class="card" style="text-align:center;color:var(--text-dim);">No journal entry for this period.</div>', unsafe_allow_html=True)
        return

    if len(lines) == 1 and lines[0].direction == "N/A":
        st.markdown(
            f'<div style="text-align:center;padding:0.75rem;color:var(--text-dim);font-style:italic;">{lines[0].account}</div>',
            unsafe_allow_html=True,
        )
        return

    table_rows = ""
    for line in lines:
        css_class, movement_label = account_movement(line)
        movement_class = {
            "inc": "movement-inc",
            "dec": "movement-dec",
            "neutral": "movement-na",
        }.get(css_class, "movement-na")

        debit_cell = ""
        credit_cell = ""
        if line.direction == "Debit":
            debit_cell = f'<span class="amount-debit">{format_money(line.amount)}</span>'
            credit_cell = '<span class="amount-na">—</span>'
        elif line.direction == "Credit":
            debit_cell = '<span class="amount-na">—</span>'
            credit_cell = f'<span class="amount-credit">{format_money(line.amount)}</span>'
        else:
            debit_cell = '<span class="amount-na">—</span>'
            credit_cell = '<span class="amount-na">—</span>'

        table_rows += f"""
        <tr>
            <td>
                <div class="account-name">{line.account}</div>
                <div class="account-type">{line.account_type}</div>
                <div class="movement-label {movement_class}">{movement_label}</div>
            </td>
            <td>{debit_cell}</td>
            <td>{credit_cell}</td>
        </tr>"""

    st.markdown(
        f"""<table class="journal-table">
            <thead><tr>
                <th>Account</th>
                <th>Debit</th>
                <th>Credit</th>
            </tr></thead>
            <tbody>{table_rows}</tbody>
        </table>""",
        unsafe_allow_html=True,
    )


def render_step_indicator(current_step: int) -> None:
    steps = [
        ("1", "Scenario"),
        ("2", "Your Guess"),
        ("3", "Analysis"),
    ]
    html = '<div class="step-indicator">'
    for i, (num, label) in enumerate(steps):
        step_num = i + 1
        if step_num < current_step:
            circle_class = "completed"
            label_class = "completed"
            content = "✓"
        elif step_num == current_step:
            circle_class = "active"
            label_class = "active"
            content = num
        else:
            circle_class = "pending"
            label_class = ""
            content = num

        if i > 0:
            connector_class = "completed" if step_num <= current_step else ""
            html += f'<div class="step-connector {connector_class}"></div>'

        html += f'<div class="step-group"><div class="step-circle {circle_class}">{content}</div><span class="step-label {label_class}">{label}</span></div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_guess_section(scenario: ScenarioResult) -> Tuple[str, str, str, str]:
    focal = scenario.focal_account

    st.markdown(
        """<div class="section-header"><div class="section-number">2</div><div class="section-title">Your Guess</div></div>""",
        unsafe_allow_html=True,
    )

    fin_col1, fin_col2 = st.columns([1, 1])

    with fin_col1:
        st.markdown("##### The Auditor's Question")
        st.caption("Financial Accounting / External Reporting")

        if scenario.is_decision_scenario:
            st.markdown(
                '<div class="decision-notice"><strong>⚠️ Heads up:</strong> This scenario describes a business situation, '
                "not necessarily a completed transaction.</div>",
                unsafe_allow_html=True,
            )
            entry_guess = st.selectbox(
                "Does this event generate a journal entry today?",
                ["Yes — a transaction has occurred", "No — this is a decision, not yet a transaction"],
                index=0,
                key="entry_exists_guess",
            )
            direction_guess = "N/A"
            increases_guess = "N/A"
        else:
            entry_guess = "Yes — a transaction has occurred"
            st.markdown(
                f"""<div class="focal-block">
                    <div class="focal-icon">📋</div>
                    <div class="focal-info">
                        <div class="focal-label">Focus Account</div>
                        <div class="focal-name">{focal.account}</div>
                        <div class="focal-type">{focal.account_type}</div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )
            gcols = st.columns(2)
            with gcols[0]:
                direction_guess = st.selectbox(
                    "Debited or Credited?", ["Debit", "Credit"], key="direction_guess"
                )
            with gcols[1]:
                increases_guess = st.selectbox(
                    "Increases or Decreases?", ["Increases", "Decreases"], key="increases_guess"
                )

    with fin_col2:
        st.markdown("##### The CFO's Question")
        st.caption("Managerial Accounting / Internal Decision Support")

        with st.expander("Show lens definitions"):
            for lens, definition in LENS_DEFINITIONS.items():
                color = LENS_COLORS.get(lens, "teal")
                st.markdown(
                    f'<div class="lens-def-block"><strong>{LENS_EMOJIS.get(lens, "")} {lens}:</strong> {definition}</div>',
                    unsafe_allow_html=True,
                )

        lens_guess = st.selectbox(
            "Which managerial lens applies?",
            LENS_OPTIONS,
            key="lens_guess",
        )

    return direction_guess, increases_guess, entry_guess, lens_guess


def render_guess_feedback(
    scenario: ScenarioResult,
    direction_guess: str,
    increases_guess: str,
    entry_guess: str,
    lens_guess: str,
) -> None:
    focal = scenario.focal_account
    correct_lens = scenario.managerial.primary_metric
    stats = st.session_state.stats
    key = scenario.scenario_key

    st.markdown(
        """<div class="section-header"><div class="section-number completed">✓</div><div class="section-title">Feedback</div></div>""",
        unsafe_allow_html=True,
    )

    financial_correct = False
    lens_correct = False

    if scenario.is_decision_scenario:
        correct_entry = "No — this is a decision, not yet a transaction"
        if entry_guess == correct_entry:
            financial_correct = True
            st.markdown(
                '<div class="feedback-card feedback-good fade-in"><div class="feedback-icon">✓</div>'
                '<div class="feedback-content"><strong>Correct!</strong> No journal entry exists until the decision '
                "becomes an executed transaction.</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="feedback-card feedback-learn fade-in"><div class="feedback-icon">✗</div>'
                '<div class="feedback-content"><strong>Not quite.</strong> This scenario describes a decision under '
                "evaluation, not a completed transaction. Decisions have no entry until they are executed. "
                "The books only record what <em>has happened</em>, not what might happen.</div></div>",
                unsafe_allow_html=True,
            )
    else:
        correct_direction = focal.correct_direction
        correct_increases = "Increases" if focal.increases else "Decreases"
        direction_correct = direction_guess == correct_direction
        increases_correct = increases_guess == correct_increases
        financial_correct = direction_correct and increases_correct

        if financial_correct:
            st.markdown(
                f'<div class="feedback-card feedback-good fade-in pulse-correct"><div class="feedback-icon">✓</div>'
                f'<div class="feedback-content"><strong>Correct!</strong> {focal.account} is <strong>{correct_direction}ed</strong>, '
                f"which <strong>{correct_increases}</strong> the account balance.</div></div>",
                unsafe_allow_html=True,
            )
        else:
            parts = []
            if not direction_correct:
                parts.append(
                    f"You chose <strong>{direction_guess}</strong> but the correct side is "
                    f"<strong>{correct_direction}</strong>."
                )
            if not increases_correct:
                parts.append(
                    f"You said this <strong>{increases_guess.lower()}</strong> the account, "
                    f"but it actually <strong>{correct_increases.lower()}</strong> it."
                )
            body = " ".join(parts)
            st.markdown(
                f'<div class="feedback-card feedback-learn fade-in"><div class="feedback-icon">✗</div>'
                f'<div class="feedback-content"><strong>Not quite.</strong> {body}<br><br>'
                f'<em>{focal.teaching_note}</em></div></div>',
                unsafe_allow_html=True,
            )

    if lens_guess == correct_lens:
        lens_correct = True
        st.markdown(
            f'<div class="feedback-card feedback-good fade-in"><div class="feedback-icon">✓</div>'
            f'<div class="feedback-content"><strong>Correct lens</strong> — {correct_lens}.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="feedback-card feedback-learn fade-in"><div class="feedback-icon">✗</div>'
            f'<div class="feedback-content">The primary lens here is <strong>{correct_lens}</strong>, not {lens_guess}. '
            f"{LENS_DEFINITIONS[correct_lens]}</div></div>",
            unsafe_allow_html=True,
        )

    if financial_correct and lens_correct:
        st.markdown(
            '<div class="feedback-card feedback-perfect fade-in"><div class="feedback-icon">🎯</div>'
            '<div class="feedback-content"><strong>Perfect!</strong> You nailed both the financial and managerial '
            "perspectives.</div></div>",
            unsafe_allow_html=True,
        )

    if key != st.session_state.stats_recorded_for:
        stats["attempted"] += 1
        if financial_correct:
            stats["correct_financial"] += 1
        if lens_correct:
            stats["correct_lens"] += 1
        if financial_correct and lens_correct:
            stats["perfect"] += 1
            stats["streak"] += 1
            if stats["streak"] > stats["best_streak"]:
                stats["best_streak"] = stats["streak"]
        else:
            stats["streak"] = 0
        if lens_guess in stats["lens_results"]:
            stats["lens_results"][lens_guess]["total"] += 1
            if lens_guess == correct_lens:
                stats["lens_results"][lens_guess]["correct"] += 1
        st.session_state.stats_recorded_for = key


def render_sidebar_stats() -> None:
    stats = st.session_state.stats

    st.markdown('<div class="sidebar-header">Your Progress</div>', unsafe_allow_html=True)

    if stats["streak"] >= 2:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:0.75rem;">'
            f'<span class="streak-badge">🔥 {stats["streak"]} streak</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    attempted = stats["attempted"]
    financial_acc = round(stats["correct_financial"] / attempted * 100) if attempted else 0
    lens_acc = round(stats["correct_lens"] / attempted * 100) if attempted else 0
    perfect_acc = round(stats["perfect"] / attempted * 100) if attempted else 0

    rows = [
        ("Attempted", str(attempted), ""),
        ("Financial Accuracy", f"{financial_acc}%", "good" if financial_acc >= 70 else ""),
        ("Lens Accuracy", f"{lens_acc}%", "good" if lens_acc >= 70 else ""),
        ("Perfect Answers", f"{perfect_acc}%", "teal" if perfect_acc >= 50 else ""),
        ("Best Streak", str(stats["best_streak"]), "teal" if stats["best_streak"] >= 3 else ""),
    ]
    for label, value, cls in rows:
        cls_attr = f' class="{cls}"' if cls else ""
        st.markdown(
            f'<div class="stat-row"><span class="stat-label">{label}</span>'
            f'<span class="stat-value{cls_attr}">{value}</span></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.5rem;">'
                "Session stats reset when you reload the page.</div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        '<div class="app-footer">'
        'Built by an MBA student'
        '<span class="footer-divider"></span>'
        '<a href="https://github.com/KaramelBytes/accounting-learning-sim" target="_blank">View source on GitHub</a>'
        '<span class="footer-divider"></span>'
        'MIT Licensed'
        '</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    st.markdown(WARM_LIGHT_CSS, unsafe_allow_html=True)
    init_state()

    with st.sidebar:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">'
            '<span style="font-size:1.3rem;">📊</span>'
            '<span style="font-family:Space Grotesk,sans-serif;font-weight:700;font-size:1rem;color:var(--accent-teal);">'
            "Dual-Perspective Simulator</span></div>",
            unsafe_allow_html=True,
        )

        if st.button("✦ Generate New Scenario", use_container_width=True):
            st.session_state.scenario = st.session_state.engine.generate_scenario()
            st.session_state.reveal = False
            st.session_state.stats_recorded_for = None

        st.divider()

        if st.session_state.scenario is not None:
            render_sidebar_stats()
        else:
            st.caption("Generate a scenario above to start tracking your progress.")

    scenario: ScenarioResult | None = st.session_state.scenario

    if scenario is None:
        st.markdown(
            '<div style="text-align:center;padding:4rem 2rem;">'
            '<div style="font-size:2.5rem;margin-bottom:1rem;">📊</div>'
            '<h2 style="color:var(--text-primary);margin-bottom:0.5rem;">Welcome to the Dual-Perspective Simulator</h2>'
            '<p style="color:var(--text-muted);max-width:500px;margin:0 auto;line-height:1.6;">'
            "Learn accounting from two angles at once. Each scenario challenges you to think like "
            "both an <strong>auditor</strong> (GAAP reporting) and a <strong>CFO</strong> "
            "(managerial decision-making).</p>"
            '<div style="margin-top:1.5rem;color:var(--text-dim);font-size:0.9rem;">'
            "Click <strong>Generate New Scenario</strong> in the sidebar to begin.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        render_footer()
        return

    is_revealed = st.session_state.reveal

    current_step = 3 if is_revealed else 2
    render_step_indicator(current_step)

    lens_color = LENS_COLORS.get(scenario.managerial.primary_metric, "teal")
    lens_emoji = LENS_EMOJIS.get(scenario.managerial.primary_metric, "")

    st.markdown(
        f"""<div class="card-scenario">
            <span class="lens-badge {lens_color}">{lens_emoji} {scenario.managerial.primary_metric}</span>
            <div class="scenario-title">{scenario.title}</div>
            <div class="scenario-text">{scenario.scenario_text}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    direction_guess, increases_guess, entry_guess, lens_guess = render_guess_section(scenario)

    st.divider()

    if not is_revealed:
        reveal_clicked = st.button("Reveal Analysis", type="primary", use_container_width=True)
        if reveal_clicked:
            st.session_state.reveal = True
            st.rerun()

    if st.session_state.reveal:
        render_guess_feedback(scenario, direction_guess, increases_guess, entry_guess, lens_guess)

        st.markdown(
            """<div class="section-header" style="margin-top:1.5rem;"><div class="section-number completed">✓</div>"""
            """<div class="section-title">Full Analysis</div></div>""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="analysis-grid">',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """<div class="card-analysis">
                <h4 style="margin-bottom:0.25rem;">The Auditor's View</h4>
                <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:1rem;">Financial Accounting / GAAP Reporting</div>""",
                unsafe_allow_html=True,
            )

            st.markdown("**Today**")
            render_journal_table(scenario.financial.today_journal_entry)
            ni_today = scenario.financial.today_net_income_impact
            direction_today = net_income_direction(ni_today)
            st.markdown(
                f'<div class="metric-highlight">Net Income: {format_money(ni_today)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:1rem;">{direction_today} &mdash; {scenario.financial.today_summary}</div>', unsafe_allow_html=True)

            if scenario.financial.future_journal_preview:
                st.markdown("**Future Period**")
                render_journal_table(scenario.financial.future_journal_preview)
                ni_future = scenario.financial.future_net_income_impact
                direction_future = net_income_direction(ni_future)
                st.markdown(
                    f'<div class="metric-highlight">Net Income: {format_money(ni_future)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f'<div style="font-size:0.85rem;color:var(--text-muted);">{direction_future} &mdash; {scenario.financial.future_summary}</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(
                """<div class="card-analysis">
                <h4 style="margin-bottom:0.25rem;">The CFO's View</h4>
                <div style="font-size:0.82rem;color:var(--text-muted);margin-bottom:1rem;">Managerial Accounting / Decision Support</div>""",
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<span class="lens-badge {lens_color}" style="margin-bottom:0.5rem;">{lens_emoji} {scenario.managerial.primary_metric}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="lens-def-block">{scenario.managerial.lens_definition}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="metric-highlight">{scenario.managerial.metric_value}</div>',
                unsafe_allow_html=True,
            )

            cf_today = scenario.managerial.cash_flow_today
            cf_future = scenario.managerial.cash_flow_future
            st.markdown(
                f'<div style="margin-top:0.5rem;"><strong>Cash Flow Today:</strong> <span style="font-family:Space Grotesk,sans-serif;font-weight:600;color:{"var(--accent-coral)" if cf_today < 0 else "var(--accent-green)"};">{format_money(cf_today)}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="margin-bottom:0.75rem;"><strong>Cash Flow Future:</strong> <span style="font-family:Space Grotesk,sans-serif;font-weight:600;color:{"var(--accent-coral)" if cf_future < 0 else "var(--accent-green)"};">{format_money(cf_future)}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-size:0.88rem;line-height:1.5;color:var(--text-muted);">{scenario.managerial.decision_note}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="teaching-note"><strong>💡 Common Misconception:</strong> {scenario.misconception_note}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


if __name__ == "__main__":
    main()
