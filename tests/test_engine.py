import math
import re
import unittest

from engine import AccountingScenarioEngine, grade_answers


class EngineTests(unittest.TestCase):
    def test_catalog_balance_questions_and_answer_variety(self):
        engine = AccountingScenarioEngine(42)
        movements = set()
        for key in engine.SCENARIO_CATALOG:
            for _ in range(60):
                scenario = engine.generate_scenario(key)
                self.assertEqual(scenario.scenario_key, key)
                self.assertTrue(scenario.practice.prompt)
                self.assertTrue(math.isfinite(scenario.practice.answer))
                self.assertTrue(scenario.financial.future_period)
                self.assertTrue(scenario.managerial.future_cash_label)
                for lines in (scenario.financial.today_journal_entry, scenario.financial.future_journal_preview):
                    balance = sum(line.amount * (1 if line.direction == 'Debit' else -1 if line.direction == 'Credit' else 0) for line in lines)
                    self.assertAlmostEqual(balance, 0)
                if not scenario.is_decision_scenario:
                    focal = scenario.focal_account
                    movements.add((focal.correct_direction, focal.increases))
                    self.assertTrue(any(line.account == focal.account for line in scenario.financial.today_journal_entry))
                answers = dict(direction=scenario.focal_account.correct_direction,
                               movement='Increases' if scenario.focal_account.increases else 'Decreases',
                               entry='No — this is a decision, not yet a transaction',
                               lens=scenario.managerial.primary_metric, practice=round(scenario.practice.answer, 2))
                self.assertTrue(all(grade_answers(scenario, answers).values()))
                for lens in scenario.secondary_lenses:
                    self.assertTrue(grade_answers(scenario, dict(answers, lens=lens))['lens'])
                self.assertFalse(grade_answers(scenario, dict(answers, practice=None))['practice'])
                self.assertFalse(grade_answers(scenario, dict(answers, practice=scenario.practice.answer + 1))['practice'])
        self.assertEqual(movements, {('Debit', True), ('Debit', False), ('Credit', True), ('Credit', False)})

    def test_volume_dilution_does_not_invent_profit(self):
        scenario = AccountingScenarioEngine(5).generate_scenario('volume_increase')
        units = int(re.search(r'adding ([\d,]+) more', scenario.scenario_text)[1].replace(',', ''))
        unit_cost = int(re.search(r'Variable cost is \$(\d+)', scenario.scenario_text)[1])
        self.assertIsNone(scenario.financial.future_net_income_impact)
        self.assertEqual(scenario.practice.answer, units * unit_cost)
        self.assertEqual(scenario.financial.future_journal_preview[0].amount, units * unit_cost)
        self.assertEqual(scenario.managerial.cash_flow_future, -units * unit_cost)

    def test_bad_debt_write_off_is_non_cash(self):
        scenario = AccountingScenarioEngine(5).generate_scenario('allowance_doubtful')
        self.assertEqual(scenario.managerial.cash_flow_future, 0)
        self.assertEqual(scenario.practice.answer, 0)
        self.assertIn('collection shortfall', scenario.managerial.metric_value)

    def test_discount_reduces_unsold_inventory(self):
        scenario = AccountingScenarioEngine(5).generate_scenario('early_payment_discount')
        lines = scenario.financial.today_journal_entry
        self.assertEqual(lines[-1].account, 'Inventory')
        self.assertEqual(lines[-1].direction, 'Credit')
        self.assertEqual(scenario.financial.today_net_income_impact, 0)
        self.assertEqual(scenario.financial.future_net_income_impact, lines[-1].amount)
        self.assertIn('perpetual inventory', scenario.scenario_text)

    def test_special_order_changes_recommendation_and_uses_net_cash(self):
        engine = AccountingScenarioEngine(42)
        signs = set()
        for _ in range(150):
            scenario = engine.generate_scenario('special_order')
            text = scenario.scenario_text
            units = int(re.search(r'([\d,]+) cabinet units', text)[1].replace(',', ''))
            price = int(re.search(r'at \$(\d+) each', text)[1])
            cost = int(re.search(r'Variable cost per unit is \$(\d+)', text)[1])
            expected = units * (price - cost)
            self.assertEqual(scenario.financial.future_net_income_impact, expected)
            self.assertEqual(scenario.managerial.cash_flow_future, expected)
            signs.add((expected > 0) - (expected < 0))
        self.assertEqual(signs, {-1, 0, 1})

    def test_automation_negative_results_are_named_as_decreases(self):
        engine = AccountingScenarioEngine(42)
        found = False
        for _ in range(100):
            scenario = engine.generate_scenario('automation_tradeoff')
            if scenario.financial.future_net_income_impact < 0:
                found = True
                self.assertIn('decrease', scenario.financial.future_summary)
                self.assertNotIn('improvement', scenario.financial.future_summary)
        self.assertTrue(found)

    def test_reproducibility_and_unknown_topic(self):
        first, second = AccountingScenarioEngine(7), AccountingScenarioEngine(7)
        self.assertEqual([first.generate_scenario() for _ in range(30)], [second.generate_scenario() for _ in range(30)])
        with self.assertRaises(ValueError):
            first.generate_scenario('missing')


if __name__ == '__main__':
    unittest.main()
