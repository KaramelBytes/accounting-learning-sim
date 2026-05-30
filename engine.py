from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Lens taxonomy
# ---------------------------------------------------------------------------

LENS_DEFINITIONS: Dict[str, str] = {
    "Cash vs. Accrual Timing": (
        "When does cash actually move vs. when does accounting recognize income or expense? "
        "These two often differ, and that gap is the story."
    ),
    "Cost Behavior": (
        "Which costs are fixed (unchanged with volume) and which are variable (scale with output)? "
        "Understanding this changes how you interpret unit economics and pricing."
    ),
    "Incremental Analysis": (
        "Which costs and revenues actually change because of this specific decision? "
        "Sunk costs and allocated fixed costs are irrelevant — only the deltas matter."
    ),
    "Working Capital & Liquidity": (
        "How does this affect the company's short-term cash position and ability to meet near-term obligations? "
        "Profitable firms can still fail if liquidity dries up."
    ),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JournalEntryLine:
    account: str
    account_type: str
    direction: str   # "Debit", "Credit", or "N/A"
    amount: float


@dataclass(frozen=True)
class FocalAccount:
    """The single account the learner is asked to reason about."""
    account: str
    account_type: str
    correct_direction: str   # "Debit" or "Credit"
    increases: bool          # True if the direction increases the account balance
    teaching_note: str       # One sentence explaining why


@dataclass(frozen=True)
class FinancialImpact:
    today_journal_entry: List[JournalEntryLine]
    today_net_income_impact: float
    today_summary: str
    future_journal_preview: List[JournalEntryLine]
    future_net_income_impact: float
    future_summary: str


@dataclass(frozen=True)
class ManagerialImpact:
    primary_metric: str       # One of the four lens labels
    lens_definition: str      # Full definition string for UI display
    metric_value: str
    cash_flow_today: float
    cash_flow_future: float
    decision_note: str


@dataclass(frozen=True)
class ScenarioResult:
    scenario_key: str
    title: str
    scenario_text: str
    is_decision_scenario: bool   # True = no journal entry until action is taken
    focal_account: FocalAccount
    financial: FinancialImpact
    managerial: ManagerialImpact
    misconception_note: str


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class AccountingScenarioEngine:
    """Generates accounting learning scenarios with financial vs managerial views."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._scenario_builders: List[Callable[[], ScenarioResult]] = [
            # Cash vs. Accrual Timing (5)
            self._prepaid_insurance,
            self._depreciation,
            self._credit_sale,
            self._unearned_revenue,
            self._accrued_wages,
            # Working Capital & Liquidity (2)
            self._inventory_purchase,
            self._early_payment_discount,
            # Incremental Analysis (3)
            self._allowance_for_doubtful_accounts,
            self._special_order_decision,
            self._make_vs_buy,
            # Cost Behavior (3)
            self._r_and_d_spend,
            self._automation_tradeoff,
            self._volume_increase,
            # Deferred subscription kept as Cash vs. Accrual Timing
            self._deferred_revenue_subscription,
        ]

    def generate_scenario(self) -> ScenarioResult:
        builder = self._rng.choice(self._scenario_builders)
        return builder()

    def _money(self, value: float) -> str:
        return f"${value:,.0f}"

    # ------------------------------------------------------------------
    # Cash vs. Accrual Timing
    # ------------------------------------------------------------------

    def _prepaid_insurance(self) -> ScenarioResult:
        annual_premium = self._rng.choice([12000, 18000, 24000, 30000])
        months_covered = self._rng.choice([6, 12])
        monthly_expense = annual_premium / months_covered

        return ScenarioResult(
            scenario_key="prepaid_insurance",
            title="Prepaid Insurance",
            scenario_text=(
                f"Dana Marsh, Halcyon Woodworks' Controller, just cut a check for "
                f"{self._money(annual_premium)} to renew the plant's property and liability "
                f"coverage — a {months_covered}-month policy effective today. "
                f"Ray Okonkwo is asking Dana why this doesn't show up as an expense on this month's P&L."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Prepaid Insurance",
                account_type="Asset",
                correct_direction="Debit",
                increases=True,
                teaching_note=(
                    "Cash is paid now but the benefit is consumed over time, so it enters the books "
                    "as an asset — a debit that increases Prepaid Insurance."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Prepaid Insurance", "Asset", "Debit", annual_premium),
                    JournalEntryLine("Cash", "Asset", "Credit", annual_premium),
                ],
                today_net_income_impact=0.0,
                today_summary="Under GAAP matching, no insurance expense is recognized today — the payment creates an asset.",
                future_journal_preview=[
                    JournalEntryLine("Insurance Expense", "Expense", "Debit", monthly_expense),
                    JournalEntryLine("Prepaid Insurance", "Asset", "Credit", monthly_expense),
                ],
                future_net_income_impact=-monthly_expense,
                future_summary=(
                    f"Each future month, {self._money(monthly_expense)} is expensed as coverage is consumed."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Operating cash outflow today: {self._money(annual_premium)}",
                cash_flow_today=-annual_premium,
                cash_flow_future=0.0,
                decision_note=(
                    "Cash is fully committed now. Future months show zero cash impact but carry "
                    "monthly expense — don't double-count this in future period cost planning."
                ),
            ),
            misconception_note="Common mistake: treating the entire upfront payment as an immediate period expense.",
        )

    def _depreciation(self) -> ScenarioResult:
        machine_cost = self._rng.choice([50000, 80000, 120000])
        useful_life = self._rng.choice([5, 8, 10])
        annual_dep = machine_cost / useful_life

        return ScenarioResult(
            scenario_key="depreciation",
            title="Machine Purchase and Depreciation",
            scenario_text=(
                f"Priya Solis just took delivery of a new CNC router for the cabinet shop — "
                f"{self._money(machine_cost)} wired out of the operating account this morning. "
                f"Useful life is estimated at {useful_life} years with no salvage value. "
                f"Ray wants to know why net income didn't move today despite the cash leaving."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Equipment",
                account_type="Asset",
                correct_direction="Debit",
                increases=True,
                teaching_note=(
                    "The machine is capitalized as an asset on purchase — a debit that increases Equipment. "
                    "Expense recognition is spread over its useful life, not taken today."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Equipment", "Asset", "Debit", machine_cost),
                    JournalEntryLine("Cash", "Asset", "Credit", machine_cost),
                ],
                today_net_income_impact=0.0,
                today_summary="The purchase is capitalized today; expense is recognized over useful life under matching.",
                future_journal_preview=[
                    JournalEntryLine("Depreciation Expense", "Expense", "Debit", annual_dep),
                    JournalEntryLine("Accumulated Depreciation", "Contra-Asset", "Credit", annual_dep),
                ],
                future_net_income_impact=-annual_dep,
                future_summary=(
                    f"Straight-line annual depreciation will reduce future net income by {self._money(annual_dep)} per year."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Full cash out today: {self._money(machine_cost)} | Annual non-cash charge: {self._money(annual_dep)}",
                cash_flow_today=-machine_cost,
                cash_flow_future=0.0,
                decision_note=(
                    "Depreciation is non-cash — cash already left on day one. "
                    "For capacity pricing and long-run decisions, depreciation signals the cost of using this asset each period."
                ),
            ),
            misconception_note="Common mistake: expensing the full machine purchase in the income statement on the day of purchase.",
        )

    def _credit_sale(self) -> ScenarioResult:
        sale_value = self._rng.choice([40000, 50000, 70000])
        variable_cost_ratio = self._rng.choice([0.45, 0.55, 0.6])
        cogs = round(sale_value * variable_cost_ratio, 2)
        contribution_margin = sale_value - cogs

        return ScenarioResult(
            scenario_key="credit_sale",
            title="Credit Sale",
            scenario_text=(
                f"Cal Nguyen just closed a {self._money(sale_value)} order with a regional "
                f"furniture chain — cabinets shipped and delivered today, but payment terms are "
                f"net 60. Product cost on the order came to {self._money(cogs)}. "
                f"Dana is booking the sale now; Cal is confused why revenue hits before the check arrives."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Accounts Receivable",
                account_type="Asset",
                correct_direction="Debit",
                increases=True,
                teaching_note=(
                    "Delivery triggers revenue recognition even without cash — the right to collect "
                    "is an asset, so Accounts Receivable is debited to increase it."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Accounts Receivable", "Asset", "Debit", sale_value),
                    JournalEntryLine("Sales Revenue", "Revenue", "Credit", sale_value),
                    JournalEntryLine("Cost of Goods Sold", "Expense", "Debit", cogs),
                    JournalEntryLine("Inventory", "Asset", "Credit", cogs),
                ],
                today_net_income_impact=contribution_margin,
                today_summary="Revenue is recognized when earned (delivery), not when cash is collected.",
                future_journal_preview=[
                    JournalEntryLine("Cash", "Asset", "Debit", sale_value),
                    JournalEntryLine("Accounts Receivable", "Asset", "Credit", sale_value),
                ],
                future_net_income_impact=0.0,
                future_summary="Collection later changes only asset mix (A/R to Cash), with no new profit.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Profit recognized today: {self._money(contribution_margin)} | Cash arrives in ~60 days",
                cash_flow_today=0.0,
                cash_flow_future=sale_value,
                decision_note=(
                    "Income is booked now but cash comes later — watch the receivables aging. "
                    "A growing A/R balance can mask a cash flow problem even when profits look healthy."
                ),
            ),
            misconception_note="Common mistake: thinking no income is recognized until cash is received.",
        )

    def _unearned_revenue(self) -> ScenarioResult:
        prepayment = self._rng.choice([10000, 20000, 36000])
        months = self._rng.choice([6, 12])
        monthly_revenue = prepayment / months

        return ScenarioResult(
            scenario_key="unearned_revenue",
            title="Cash Received Before Service",
            scenario_text=(
                f"A regional home builder just wired Halcyon {self._money(prepayment)} upfront "
                f"to lock in a {months}-month custom millwork supply agreement starting next month. "
                f"The cash is in the bank, but Dana tells Ray she can't book it as revenue yet — "
                f"Ray wants to understand why."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Unearned Revenue",
                account_type="Liability",
                correct_direction="Credit",
                increases=True,
                teaching_note=(
                    "Cash is received but the obligation to deliver service hasn't been fulfilled yet, "
                    "so it's a liability — credited to increase Unearned Revenue."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Cash", "Asset", "Debit", prepayment),
                    JournalEntryLine("Unearned Revenue", "Liability", "Credit", prepayment),
                ],
                today_net_income_impact=0.0,
                today_summary="Cash receipt creates a liability until service is performed.",
                future_journal_preview=[
                    JournalEntryLine("Unearned Revenue", "Liability", "Debit", monthly_revenue),
                    JournalEntryLine("Service Revenue", "Revenue", "Credit", monthly_revenue),
                ],
                future_net_income_impact=monthly_revenue,
                future_summary=(
                    f"Each service month, {self._money(monthly_revenue)} becomes earned revenue and increases net income."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Cash received now: {self._money(prepayment)} | Revenue earned monthly: {self._money(monthly_revenue)}",
                cash_flow_today=prepayment,
                cash_flow_future=0.0,
                decision_note=(
                    "Strong upfront cash is great for liquidity, but the income statement won't reflect "
                    "it yet. Budget capacity and delivery costs across the full service window."
                ),
            ),
            misconception_note="Common mistake: recording all cash receipts as immediate revenue.",
        )

    def _accrued_wages(self) -> ScenarioResult:
        wages = self._rng.choice([8000, 12000, 18000])

        return ScenarioResult(
            scenario_key="accrued_wages",
            title="Accrued Wages",
            scenario_text=(
                f"It's the last day of the month at Halcyon Woodworks. The shop floor crew has "
                f"earned {self._money(wages)} in wages since the last payroll run, but payday "
                f"isn't until next Friday. Dana is recording the liability now. "
                f"Ray asks why this hits the income statement before anyone gets paid."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Wages Payable",
                account_type="Liability",
                correct_direction="Credit",
                increases=True,
                teaching_note=(
                    "The obligation to pay exists before cash leaves — Wages Payable is credited "
                    "to record the growing liability."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Wage Expense", "Expense", "Debit", wages),
                    JournalEntryLine("Wages Payable", "Liability", "Credit", wages),
                ],
                today_net_income_impact=-wages,
                today_summary="Expense is recognized when incurred, even before cash payment.",
                future_journal_preview=[
                    JournalEntryLine("Wages Payable", "Liability", "Debit", wages),
                    JournalEntryLine("Cash", "Asset", "Credit", wages),
                ],
                future_net_income_impact=0.0,
                future_summary="Future payment settles the liability with no additional expense recognition.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Expense hits income now: {self._money(wages)} | Cash leaves next period",
                cash_flow_today=0.0,
                cash_flow_future=-wages,
                decision_note=(
                    "This period's income already absorbs the wage cost. "
                    "Next period's cash flow takes the hit — important for short-term liquidity planning."
                ),
            ),
            misconception_note="Common mistake: waiting until the payment date to recognize wage expense.",
        )

    def _deferred_revenue_subscription(self) -> ScenarioResult:
        cash = self._rng.choice([24000, 36000, 48000])
        months = self._rng.choice([12, 24])
        monthly = cash / months

        return ScenarioResult(
            scenario_key="deferred_subscription",
            title="Multi-Period Subscription",
            scenario_text=(
                f"A national retail chain just paid Halcyon {self._money(cash)} upfront for a "
                f"{months}-month preferred supply and design consultation arrangement. "
                f"Ray is thrilled about the cash; Dana reminds him the P&L won't reflect it "
                f"all at once — and explains what the books actually show today."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Deferred Revenue",
                account_type="Liability",
                correct_direction="Credit",
                increases=True,
                teaching_note=(
                    "Like unearned revenue, the cash receipt creates an obligation to deliver — "
                    "Deferred Revenue is a liability, credited to increase it until service is earned."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Cash", "Asset", "Debit", cash),
                    JournalEntryLine("Deferred Revenue", "Liability", "Credit", cash),
                ],
                today_net_income_impact=0.0,
                today_summary="Revenue is deferred until service is delivered over time.",
                future_journal_preview=[
                    JournalEntryLine("Deferred Revenue", "Liability", "Debit", monthly),
                    JournalEntryLine("Subscription Revenue", "Revenue", "Credit", monthly),
                ],
                future_net_income_impact=monthly,
                future_summary=f"Each month, recognize {self._money(monthly)} of revenue as performance obligations are met.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Cash vs. Accrual Timing",
                lens_definition=LENS_DEFINITIONS["Cash vs. Accrual Timing"],
                metric_value=f"Cash runway boost today: {self._money(cash)} | Monthly revenue recognition: {self._money(monthly)}",
                cash_flow_today=cash,
                cash_flow_future=0.0,
                decision_note=(
                    "Cash arrives upfront but profitability builds slowly on the income statement. "
                    "Management must budget support and delivery costs across the entire subscription horizon."
                ),
            ),
            misconception_note="Common mistake: mistaking strong upfront cash collections for immediate profitability.",
        )

    # ------------------------------------------------------------------
    # Working Capital & Liquidity
    # ------------------------------------------------------------------

    def _inventory_purchase(self) -> ScenarioResult:
        purchase = self._rng.choice([25000, 40000, 55000])

        return ScenarioResult(
            scenario_key="inventory_purchase",
            title="Inventory Purchase on Credit",
            scenario_text=(
                f"Beth Calder placed a lumber and hardware order for {self._money(purchase)} "
                f"with Halcyon's primary supplier — stock received today, invoice due in 30 days. "
                f"Ray notices the cash balance didn't move but wants to understand what actually "
                f"changed on the books and when this will hit the income statement."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Accounts Payable",
                account_type="Liability",
                correct_direction="Credit",
                increases=True,
                teaching_note=(
                    "Receiving inventory on credit creates an obligation to pay — Accounts Payable "
                    "is a liability, credited to record that the balance is growing."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Inventory", "Asset", "Debit", purchase),
                    JournalEntryLine("Accounts Payable", "Liability", "Credit", purchase),
                ],
                today_net_income_impact=0.0,
                today_summary="Purchasing inventory does not hit net income until inventory is sold.",
                future_journal_preview=[
                    JournalEntryLine("Cost of Goods Sold", "Expense", "Debit", purchase),
                    JournalEntryLine("Inventory", "Asset", "Credit", purchase),
                ],
                future_net_income_impact=-purchase,
                future_summary="Expense recognition occurs when inventory is matched to related revenue at sale.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Working Capital & Liquidity",
                lens_definition=LENS_DEFINITIONS["Working Capital & Liquidity"],
                metric_value=f"Near-term cash commitment: {self._money(purchase)} due in 30 days",
                cash_flow_today=0.0,
                cash_flow_future=-purchase,
                decision_note=(
                    "No cash moves today, but this is a locked-in 30-day obligation. "
                    "Buying too much inventory too fast ties up working capital and can pinch cash before the goods even sell."
                ),
            ),
            misconception_note="Common mistake: treating inventory purchase as an immediate expense.",
        )

    def _early_payment_discount(self) -> ScenarioResult:
        invoice = self._rng.choice([20000, 30000, 50000])
        discount_rate = self._rng.choice([0.01, 0.02])
        discount = round(invoice * discount_rate, 2)
        net_payment = invoice - discount

        return ScenarioResult(
            scenario_key="early_payment_discount",
            title="Early Payment Discount",
            scenario_text=(
                f"Beth Calder flags a supplier invoice for {self._money(invoice)} sitting in "
                f"accounts payable with terms {int(discount_rate * 100)}/10 net 30 — pay within "
                f"10 days and Halcyon saves {self._money(discount)}, or wait the full 30 days and "
                f"pay in full. Ray asks Beth to run the numbers; they decide to pay early today. "
                f"Dana needs to record the settlement."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Accounts Payable",
                account_type="Liability",
                correct_direction="Debit",
                increases=False,
                teaching_note=(
                    "Paying off a liability reduces it — Accounts Payable is debited to decrease "
                    "the balance. Liabilities normally carry a credit balance, so a debit shrinks them."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Accounts Payable", "Liability", "Debit", invoice),
                    JournalEntryLine("Cash", "Asset", "Credit", net_payment),
                    JournalEntryLine("Purchase Discounts", "Contra-Expense", "Credit", discount),
                ],
                today_net_income_impact=0.0,
                today_summary=(
                    "Settling the payable early removes the liability. The discount reduces inventory "
                    "cost basis rather than creating immediate income."
                ),
                future_journal_preview=[],
                future_net_income_impact=0.0,
                future_summary="No future entries — the obligation is fully settled today.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Working Capital & Liquidity",
                lens_definition=LENS_DEFINITIONS["Working Capital & Liquidity"],
                metric_value=(
                    f"Cash out today: {self._money(net_payment)} | "
                    f"Discount captured: {self._money(discount)} | "
                    f"Annualized return: ~{int(discount_rate * (365 / 20) * 100)}%"
                ),
                cash_flow_today=-net_payment,
                cash_flow_future=0.0,
                decision_note=(
                    f"Capturing a {int(discount_rate * 100)}% discount for paying 20 days early "
                    f"is equivalent to an annualized return of ~{int(discount_rate * (365 / 20) * 100)}%. "
                    "Almost always worth taking unless liquidity is critically tight."
                ),
            ),
            misconception_note=(
                "Common mistake: treating early payment as purely a cash management choice "
                "without calculating the annualized cost of forgoing the discount."
            ),
        )

    # ------------------------------------------------------------------
    # Incremental Analysis
    # ------------------------------------------------------------------

    def _allowance_for_doubtful_accounts(self) -> ScenarioResult:
        credit_sales = self._rng.choice([120000, 180000, 250000])
        bad_debt_rate = self._rng.choice([0.01, 0.02, 0.03])
        estimate = round(credit_sales * bad_debt_rate, 2)

        return ScenarioResult(
            scenario_key="allowance_doubtful",
            title="Bad Debt Estimate",
            scenario_text=(
                f"It's period-end at Halcyon. Cal's team closed {self._money(credit_sales)} in "
                f"credit sales this quarter — mostly to mid-size retailers on net 45 terms. "
                f"Based on Halcyon's collections history, Dana estimates {bad_debt_rate:.0%} "
                f"will likely go uncollected. Ray wants to know why Dana is booking a loss before "
                f"anyone has actually defaulted."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Allowance for Doubtful Accounts",
                account_type="Contra-Asset",
                correct_direction="Credit",
                increases=True,
                teaching_note=(
                    "A contra-asset carries the opposite normal balance to its paired asset. "
                    "Crediting Allowance for Doubtful Accounts increases it, which reduces the net "
                    "carrying value of Accounts Receivable on the balance sheet."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Bad Debt Expense", "Expense", "Debit", estimate),
                    JournalEntryLine("Allowance for Doubtful Accounts", "Contra-Asset", "Credit", estimate),
                ],
                today_net_income_impact=-estimate,
                today_summary="GAAP matching requires estimating expected credit losses in the same period as related sales.",
                future_journal_preview=[
                    JournalEntryLine("Allowance for Doubtful Accounts", "Contra-Asset", "Debit", estimate),
                    JournalEntryLine("Accounts Receivable", "Asset", "Credit", estimate),
                ],
                future_net_income_impact=0.0,
                future_summary="Write-offs draw down the allowance and do not create new expense at that time.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Incremental Analysis",
                lens_definition=LENS_DEFINITIONS["Incremental Analysis"],
                metric_value=f"Expected incremental loss from credit sales: {self._money(estimate)}",
                cash_flow_today=0.0,
                cash_flow_future=-estimate,
                decision_note=(
                    "This estimate is the incremental cost of extending credit. "
                    "It informs whether credit terms should be tightened, which customers need "
                    "closer scrutiny, and how to price for default risk in future contracts."
                ),
            ),
            misconception_note="Common mistake: recording bad debt expense only when specific invoices actually default.",
        )

    def _special_order_decision(self) -> ScenarioResult:
        units = self._rng.choice([800, 1000, 1400])
        offer_price = self._rng.choice([22, 24, 26])
        variable_cost = self._rng.choice([14, 16, 18])
        contribution_per_unit = offer_price - variable_cost
        total_contribution = units * contribution_per_unit

        return ScenarioResult(
            scenario_key="special_order",
            title="Special Order Decision",
            scenario_text=(
                f"A contract furniture broker has approached Cal Nguyen with a one-time order: "
                f"{units:,} cabinet units at ${offer_price} each for a hotel fit-out project — "
                f"a buyer that doesn't compete with any of Halcyon's existing retail accounts. "
                f"Variable cost per unit is ${variable_cost}. Priya confirms the floor has idle "
                f"capacity and fixed overhead is fully absorbed by the current production run. "
                f"Ray and Cal are deciding whether to accept. No contract has been signed yet."
            ),
            is_decision_scenario=True,
            focal_account=FocalAccount(
                account="No Entry — Decision Not Yet Executed",
                account_type="N/A",
                correct_direction="N/A",
                increases=False,
                teaching_note=(
                    "No journal entry exists because management is still deciding. "
                    "Decisions have no accounting until they become executed transactions."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("No Entry", "N/A", "N/A", 0.0),
                ],
                today_net_income_impact=0.0,
                today_summary="No journal entry exists until management accepts and the transaction is executed.",
                future_journal_preview=[],
                future_net_income_impact=total_contribution,
                future_summary=(
                    f"If accepted and fulfilled, expected incremental operating income is {self._money(total_contribution)}."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Incremental Analysis",
                lens_definition=LENS_DEFINITIONS["Incremental Analysis"],
                metric_value=f"Incremental contribution if accepted: {self._money(total_contribution)}",
                cash_flow_today=0.0,
                cash_flow_future=units * offer_price,
                decision_note=(
                    "Fixed costs are irrelevant here — they don't change with this order. "
                    "Positive incremental contribution means accepting adds to profit, "
                    "provided spare capacity exists and regular customers aren't undercut."
                ),
            ),
            misconception_note=(
                "Common mistake: allocating fixed overhead to the order and rejecting it because the "
                "fully-absorbed cost exceeds the offer price."
            ),
        )

    def _make_vs_buy(self) -> ScenarioResult:
        annual_units = self._rng.choice([5000, 8000, 12000])
        internal_variable = self._rng.choice([18, 22, 26])
        internal_fixed_total = self._rng.choice([40000, 60000, 80000])
        buy_price = self._rng.choice([20, 24, 28])
        avoidable_fixed = round(internal_fixed_total * 0.4, 2)
        unavoidable_fixed = internal_fixed_total - avoidable_fixed

        internal_total = (internal_variable * annual_units) + internal_fixed_total
        buy_total = (buy_price * annual_units) + unavoidable_fixed
        incremental_saving = internal_total - buy_total

        return ScenarioResult(
            scenario_key="make_vs_buy",
            title="Make vs. Buy Decision",
            scenario_text=(
                f"Halcyon currently machines its own drawer slide assemblies in-house — "
                f"{annual_units:,} units per year at ${internal_variable}/unit variable cost, "
                f"plus {self._money(internal_fixed_total)} in fixed overhead, of which "
                f"{self._money(avoidable_fixed)} could be eliminated if the line shuts down. "
                f"An offshore supplier quoted Beth ${buy_price}/unit delivered. "
                f"Priya and Ray are running the numbers before bringing a recommendation to ownership. "
                f"No decision has been made and no contract is in place."
            ),
            is_decision_scenario=True,
            focal_account=FocalAccount(
                account="No Entry — Decision Not Yet Executed",
                account_type="N/A",
                correct_direction="N/A",
                increases=False,
                teaching_note=(
                    "Management is analyzing costs before a decision is made. "
                    "No transaction has occurred, so no journal entry exists yet."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("No Entry", "N/A", "N/A", 0.0),
                ],
                today_net_income_impact=0.0,
                today_summary="No accounting entry until a decision is made and a contract is executed.",
                future_journal_preview=[],
                future_net_income_impact=incremental_saving if incremental_saving > 0 else -abs(incremental_saving),
                future_summary=(
                    f"If outsourcing is chosen, net annual {'saving' if incremental_saving > 0 else 'additional cost'} "
                    f"is {self._money(abs(incremental_saving))} after accounting for unavoidable fixed costs."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Incremental Analysis",
                lens_definition=LENS_DEFINITIONS["Incremental Analysis"],
                metric_value=(
                    f"Avoidable cost if outsourced: {self._money((internal_variable * annual_units) + avoidable_fixed)} | "
                    f"Buy cost: {self._money(buy_price * annual_units)}"
                ),
                cash_flow_today=0.0,
                cash_flow_future=incremental_saving,
                decision_note=(
                    f"The {self._money(unavoidable_fixed)} in unavoidable fixed costs doesn't change "
                    "either way — exclude it from the decision. Only avoidable costs and the buy price are relevant."
                ),
            ),
            misconception_note=(
                "Common mistake: comparing the full internal cost (including unavoidable fixed overhead) "
                "to the buy price, which makes outsourcing look cheaper than it actually is."
            ),
        )

    # ------------------------------------------------------------------
    # Cost Behavior
    # ------------------------------------------------------------------

    def _r_and_d_spend(self) -> ScenarioResult:
        spend = self._rng.choice([15000, 30000, 45000, 60000])

        return ScenarioResult(
            scenario_key="r_and_d",
            title="R&D Spend — Sunk Cost",
            scenario_text=(
                f"Halcyon cut a {self._money(spend)} check today to a product design consultancy "
                f"exploring whether flat-pack modular cabinetry is viable at Halcyon's production "
                f"scale — early feasibility work only. Ray will decide next quarter whether to "
                f"greenlight full development. Dana is expensing it now; Ray asks why it can't "
                f"sit on the balance sheet as an asset given it might lead to something valuable."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="R&D Expense",
                account_type="Expense",
                correct_direction="Debit",
                increases=True,
                teaching_note=(
                    "Under GAAP, most internal research is expensed immediately — debiting R&D Expense "
                    "increases it, which directly reduces net income in the current period."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("R&D Expense", "Expense", "Debit", spend),
                    JournalEntryLine("Cash", "Asset", "Credit", spend),
                ],
                today_net_income_impact=-spend,
                today_summary="Under GAAP, most internal research spending is expensed as incurred — no capitalization.",
                future_journal_preview=[],
                future_net_income_impact=0.0,
                future_summary="No automatic future entry unless separate development milestones are reached.",
            ),
            managerial=ManagerialImpact(
                primary_metric="Cost Behavior",
                lens_definition=LENS_DEFINITIONS["Cost Behavior"],
                metric_value=f"Sunk cost after payment: {self._money(spend)}",
                cash_flow_today=-spend,
                cash_flow_future=0.0,
                decision_note=(
                    "Once paid, this R&D spend is a sunk cost — it does not change regardless of "
                    "the go/no-go decision next quarter. Only future incremental development costs "
                    "and expected returns should drive that decision."
                ),
            ),
            misconception_note="Common mistake: capitalizing all R&D as an asset because it may create future value.",
        )

    def _automation_tradeoff(self) -> ScenarioResult:
        equipment_cost = self._rng.choice([60000, 90000, 120000])
        useful_life = self._rng.choice([5, 6, 8])
        annual_labor_saved = self._rng.choice([15000, 20000, 25000])
        annual_dep = equipment_cost / useful_life
        net_annual_impact = annual_labor_saved - annual_dep

        return ScenarioResult(
            scenario_key="automation_tradeoff",
            title="Automation — Fixed vs. Variable Cost Tradeoff",
            scenario_text=(
                f"Priya has been pushing for an automated edge-banding machine to replace a "
                f"manual finishing station — {self._money(equipment_cost)} capital cost, "
                f"{useful_life}-year life, and Priya estimates it eliminates "
                f"{self._money(annual_labor_saved)} in annual variable labour. "
                f"Ray approved it; the wire went out today. Dana is recording the purchase. "
                f"Ray wants to understand how the cost structure of the finishing operation "
                f"just changed."
            ),
            is_decision_scenario=False,
            focal_account=FocalAccount(
                account="Equipment",
                account_type="Asset",
                correct_direction="Debit",
                increases=True,
                teaching_note=(
                    "Purchasing equipment is a capital expenditure — it's an asset acquisition, "
                    "not an immediate expense. Debit Equipment to increase the asset balance."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("Equipment", "Asset", "Debit", equipment_cost),
                    JournalEntryLine("Cash", "Asset", "Credit", equipment_cost),
                ],
                today_net_income_impact=0.0,
                today_summary="Capital purchase is recorded as an asset today; expense recognized via depreciation over useful life.",
                future_journal_preview=[
                    JournalEntryLine("Depreciation Expense", "Expense", "Debit", annual_dep),
                    JournalEntryLine("Accumulated Depreciation", "Contra-Asset", "Credit", annual_dep),
                ],
                future_net_income_impact=annual_labor_saved - annual_dep,
                future_summary=(
                    f"Annual depreciation of {self._money(annual_dep)} replaces {self._money(annual_labor_saved)} "
                    f"in variable labor cost, for a net income improvement of {self._money(net_annual_impact)} per year."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Cost Behavior",
                lens_definition=LENS_DEFINITIONS["Cost Behavior"],
                metric_value=(
                    f"Variable labor eliminated: {self._money(annual_labor_saved)}/yr | "
                    f"New fixed depreciation charge: {self._money(annual_dep)}/yr"
                ),
                cash_flow_today=-equipment_cost,
                cash_flow_future=annual_labor_saved,
                decision_note=(
                    "This trade converts variable labor cost (scales with output) into fixed depreciation "
                    "(unchanged regardless of volume). At high volumes, fixed cost per unit falls — "
                    "automation wins. At low volumes, the fixed charge is harder to absorb."
                ),
            ),
            misconception_note=(
                "Common mistake: comparing only the upfront equipment cost to labor savings without "
                "accounting for how the cost structure change affects profitability at different volumes."
            ),
        )

    def _volume_increase(self) -> ScenarioResult:
        fixed_costs = self._rng.choice([80000, 100000, 120000])
        current_units = self._rng.choice([2000, 4000, 5000])
        additional_units = self._rng.choice([1000, 2000])
        variable_cost_per_unit = self._rng.choice([12, 15, 18])
        new_units = current_units + additional_units

        current_fixed_per_unit = round(fixed_costs / current_units, 2)
        new_fixed_per_unit = round(fixed_costs / new_units, 2)
        fixed_saving_per_unit = round(current_fixed_per_unit - new_fixed_per_unit, 2)

        return ScenarioResult(
            scenario_key="volume_increase",
            title="Production Volume Increase — Fixed Cost Dilution",
            scenario_text=(
                f"Cal just landed a short-notice restock request from a regional chain — "
                f"Priya says the floor can handle it without adding a shift. Current month's "
                f"run is {current_units:,} units; adding {additional_units:,} more is on the table. "
                f"Fixed overhead is {self._money(fixed_costs)} per month and won't move either way. "
                f"Variable cost is ${variable_cost_per_unit}/unit. Ray asks Priya what this "
                f"actually does to the unit cost before they agree to a price. No order is confirmed yet."
            ),
            is_decision_scenario=True,
            focal_account=FocalAccount(
                account="No Entry — Decision Not Yet Executed",
                account_type="N/A",
                correct_direction="N/A",
                increases=False,
                teaching_note=(
                    "This is a planning decision, not a transaction. No accounting entry is recorded "
                    "until production actually occurs and costs are incurred."
                ),
            ),
            financial=FinancialImpact(
                today_journal_entry=[
                    JournalEntryLine("No Entry", "N/A", "N/A", 0.0),
                ],
                today_net_income_impact=0.0,
                today_summary="No journal entry until production runs and costs are incurred.",
                future_journal_preview=[
                    JournalEntryLine("Work in Process Inventory", "Asset", "Debit", variable_cost_per_unit * new_units),
                    JournalEntryLine("Accounts Payable / Cash", "Liability", "Credit", variable_cost_per_unit * new_units),
                ],
                future_net_income_impact=round(fixed_saving_per_unit * new_units, 2),
                future_summary=(
                    f"When goods sell, the fixed cost dilution saves "
                    f"{self._money(round(fixed_saving_per_unit * new_units, 2))} vs. the previous "
                    f"volume level — variable costs of {self._money(variable_cost_per_unit * new_units)} "
                    f"flow through COGS."
                ),
            ),
            managerial=ManagerialImpact(
                primary_metric="Cost Behavior",
                lens_definition=LENS_DEFINITIONS["Cost Behavior"],
                metric_value=(
                    f"Fixed cost/unit now: {self._money(current_fixed_per_unit)} | "
                    f"Fixed cost/unit at new volume: {self._money(new_fixed_per_unit)} | "
                    f"Saving: {self._money(fixed_saving_per_unit)}/unit"
                ),
                cash_flow_today=0.0,
                cash_flow_future=-(variable_cost_per_unit * additional_units),
                decision_note=(
                    f"Fixed costs don't change — adding {additional_units:,} units dilutes the fixed "
                    f"overhead per unit by {self._money(fixed_saving_per_unit)}. "
                    "Only the incremental variable cost of the extra units matters for the go/no-go."
                ),
            ),
            misconception_note=(
                "Common mistake: applying the current fully-absorbed unit cost (fixed + variable) "
                "to the additional units, which overstates the true incremental cost."
            ),
        )


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def journal_line_to_dict(line: JournalEntryLine) -> Dict[str, str | float]:
    return {
        "Account": line.account,
        "Type": line.account_type,
        "Direction": line.direction,
        "Amount": line.amount,
    }
