"""
Unit tests for the enums module.
"""

import unittest
from strategy_analyzer.enums import TradingPeriodsPerYear, CalendarPeriodsPerYear

class TradingPeriodsPerYearTest(unittest.TestCase):
    def test_day(self):
        self.assertEqual(TradingPeriodsPerYear.DAY.value, 252)

    def test_week(self):
        self.assertEqual(TradingPeriodsPerYear.WEEK.value, 52)

    def test_month(self):
        self.assertEqual(TradingPeriodsPerYear.MONTH.value, 12)

    def test_year(self):
        self.assertEqual(TradingPeriodsPerYear.YEAR.value, 1)

class CalendarPeriodsPerYearTest(unittest.TestCase):
    def test_day(self):
        self.assertEqual(CalendarPeriodsPerYear.DAY.value, 365)

    def test_week(self):
        self.assertEqual(CalendarPeriodsPerYear.WEEK.value, 52)

    def test_month(self):
        self.assertEqual(CalendarPeriodsPerYear.MONTH.value, 12)

    def test_year(self):
        self.assertEqual(CalendarPeriodsPerYear.YEAR.value, 1)

if __name__ == '__main__':
    unittest.main()