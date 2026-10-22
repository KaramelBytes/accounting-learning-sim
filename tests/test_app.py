import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from engine import AccountingScenarioEngine

APP = str(Path(__file__).resolve().parents[1] / 'app.py')


def click(app, label):
    next(button for button in app.button if button.label == label).click().run()


class LearnerFlowTests(unittest.TestCase):
    def test_all_topics_reveal_future_results_and_lock_one_attempt(self):
        app = AppTest.from_file(APP).run()
        for count, key in enumerate(AccountingScenarioEngine.SCENARIO_CATALOG, 1):
            app.selectbox(key='topic_filter').set_value(key).run()
            click(app, '✦ Generate New Scenario')
            self.assertFalse(app.exception)
            scenario = app.session_state['scenario']
            self.assertIsNone(app.selectbox(key='lens_guess').value)
            self.assertIsNone(app.number_input(key='practice_guess').value)
            self.assertFalse(any('<span class="lens-badge' in item.value for item in app.markdown))
            if scenario.is_decision_scenario:
                app.selectbox(key='entry_exists_guess').set_value('No — this is a decision, not yet a transaction')
            else:
                app.selectbox(key='direction_guess').set_value(scenario.focal_account.correct_direction)
                app.selectbox(key='increases_guess').set_value('Increases' if scenario.focal_account.increases else 'Decreases')
            app.selectbox(key='lens_guess').set_value(scenario.managerial.primary_metric)
            app.number_input(key='practice_guess').set_value(round(scenario.practice.answer, 2))
            click(app, 'Reveal Analysis')
            self.assertFalse(app.exception)
            self.assertTrue(app.selectbox(key='lens_guess_submitted').disabled)
            self.assertEqual(app.selectbox(key='lens_guess_submitted').value, scenario.managerial.primary_metric)
            self.assertEqual(app.number_input(key='practice_guess_submitted').value, round(scenario.practice.answer, 2))
            self.assertTrue(app.number_input(key='practice_guess_submitted').disabled)
            self.assertEqual(app.session_state['stats']['attempted'], count)
            self.assertEqual(app.session_state['stats']['perfect'], count)
            self.assertEqual(len(app.session_state['stats']['covered']), count)
            rendered = '\n'.join(item.value for item in app.markdown)
            self.assertIn(scenario.financial.future_summary, rendered)
            self.assertIn(f'<span class="stat-value">{count}</span>', rendered)
            app.run()
            self.assertEqual(app.session_state['stats']['attempted'], count)

    def test_incomplete_attempt_and_wrong_answers(self):
        app = AppTest.from_file(APP).run()
        app.selectbox(key='topic_filter').set_value('special_order').run()
        click(app, '✦ Generate New Scenario')
        click(app, 'Reveal Analysis')
        self.assertTrue(app.warning)
        self.assertEqual(app.session_state['stats']['attempted'], 0)
        app.selectbox(key='entry_exists_guess').set_value('Yes — a transaction has occurred')
        app.selectbox(key='lens_guess').set_value('Cost Behavior')
        app.number_input(key='practice_guess').set_value(123456789.0)
        click(app, 'Reveal Analysis')
        self.assertFalse(app.exception)
        stats = app.session_state['stats']
        self.assertEqual(stats['perfect'], 0)
        self.assertEqual(stats['lens_results']['Incremental Analysis'], {'correct': 0, 'total': 1})
        self.assertEqual(stats['lens_results']['Cost Behavior']['total'], 0)
        self.assertTrue(app.info)


if __name__ == '__main__':
    unittest.main()
