import unittest
from datetime import datetime, timedelta

from parking.finance import FinanceManager, Party
from parking.reporting import ReportingManager


class TestUrbanParking(unittest.TestCase):
    def test_profit_calculation(self):
        fm = FinanceManager()
        fm.add_revenue(200, "Parking Fee", datetime(2026, 2, 1))
        fm.add_expense(50, "Electricity", datetime(2026, 2, 1))
        self.assertEqual(fm.profit(), 150)

    def test_debtors_over_30_days(self):
        fm = FinanceManager()
        now = datetime(2026, 2, 15)

        fm.add_party(Party(
            name="Old Debtor",
            role="DEBTOR",
            amount=100,
            created_at=now - timedelta(days=60),
            due_date=now - timedelta(days=40),
            note="should appear"
        ))

        fm.add_party(Party(
            name="New Debtor",
            role="DEBTOR",
            amount=100,
            created_at=now - timedelta(days=10),
            due_date=now - timedelta(days=5),
            note="should not appear"
        ))

        overdue = fm.debtors_over_30_days(30, as_of=now)
        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].name, "Old Debtor")

    def test_monthly_sales_report_total(self):
        rm = ReportingManager()
        rm.record_sale(datetime(2026, 2, 1), "WEEKLY", 60)
        rm.record_sale(datetime(2026, 2, 2), "MONTHLY", 180)
        rm.record_sale(datetime(2026, 2, 3), "SINGLE", 15)

        report = rm.monthly_sales_report()
        self.assertEqual(report["2026-02"]["TOTAL"], 255)

    def test_monthly_vehicle_count(self):
        rm = ReportingManager()
        rm.record_vehicle(datetime(2026, 1, 1), "CAR")
        rm.record_vehicle(datetime(2026, 1, 2), "CAR")
        rm.record_vehicle(datetime(2026, 1, 3), "BIKE")

        report = rm.monthly_vehicle_count_report()
        self.assertEqual(report["2026-01"]["CAR"], 2)
        self.assertEqual(report["2026-01"]["TOTAL"], 3)


if __name__ == "__main__":
    unittest.main()