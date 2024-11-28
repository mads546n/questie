import unittest
import main


class TestCalculatePerformance(unittest.TestCase):
    def setUp(self):
        main.reset_planner()

    # Test to ensure all metrics are zero when there are no quests
    def test_no_quests(self):
        performance = main.calculate_performance()
        self.assertEqual(performance['total_quests'], 0)
        self.assertEqual(performance['completed_quests'], 0)
        self.assertEqual(performance['average_completed_per_day'], 0)
        for day_data in performance['quests_per_day'].values():
            self.assertEqual(day_data['total'], 0)
            self.assertEqual(day_data['completed'], 0)

    # Test adding quests where none are completed
    def test_quests_no_completion(self):
        main.weekly_planner['Monday'].append({'completed': False})
        main.weekly_planner['Tuesday'].append({'completed': False})
        performance = main.calculate_performance()
        self.assertEqual(performance['total_quests'], 2)
        self.assertEqual(performance['completed_quests'], 0)
        self.assertEqual(performance['average_completed_per_day'], 0)
        self.assertEqual(performance['quests_per_day']['Monday']['total'], 1)
        self.assertEqual(performance['quests_per_day']['Monday']['completed'], 0)
        self.assertEqual(performance['quests_per_day']['Tuesday']['total'], 1)
        self.assertEqual(performance['quests_per_day']['Tuesday']['completed'], 0)

    # Test to add quests and mark some of them as completed
    def test_quests_with_completion(self):
        main.weekly_planner['Monday'].append({'completed': True})
        main.weekly_planner['Tuesday'].append({'completed': False})
        main.weekly_planner['Wednesday'].append({'completed': True})
        main.weekly_planner['Wednesday'].append({'completed': True})
        performance = main.calculate_performance()
        self.assertEqual(performance['total_quests'], 4)
        self.assertEqual(performance['completed_quests'], 3)
        self.assertAlmostEqual(performance['average_completed_per_day'], 3 / 7)
        self.assertEqual(performance['quests_per_day']['Monday']['total'], 1)
        self.assertEqual(performance['quests_per_day']['Monday']['completed'], 1)
        self.assertEqual(performance['quests_per_day']['Tuesday']['total'], 1)
        self.assertEqual(performance['quests_per_day']['Tuesday']['completed'], 0)
        self.assertEqual(performance['quests_per_day']['Wednesday']['total'], 2)
        self.assertEqual(performance['quests_per_day']['Wednesday']['completed'], 2)


if __name__ == '__main__':
    unittest.main()
