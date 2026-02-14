from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SaleRecord:
    date: datetime
    pass_type: str   # SINGLE/WEEKLY/MONTHLY
    amount: float


@dataclass(frozen=True)
class VehicleRecord:
    date: datetime
    vehicle_type: str  # CAR/BIKE/TRUCK


class ReportingManager:
    def __init__(self):
        self._sales = []     # list of SaleRecord
        self._vehicles = []  # list of VehicleRecord

    def _month_key(self, dt):
        return dt.strftime("%Y-%m")

    def record_sale(self, date, pass_type, amount):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        self._sales.append(SaleRecord(date=date, pass_type=pass_type.upper(), amount=float(amount)))

    def record_vehicle(self, date, vehicle_type):
        self._vehicles.append(VehicleRecord(date=date, vehicle_type=vehicle_type.upper()))

    def monthly_sales_report(self):
        report = {}  # month -> dict

        for s in self._sales:
            m = self._month_key(s.date)
            if m not in report:
                report[m] = {"SINGLE": 0.0, "WEEKLY": 0.0, "MONTHLY": 0.0, "TOTAL": 0.0}

            report[m][s.pass_type] += s.amount

        # calculate TOTAL
        for m in report:
            total = report[m]["SINGLE"] + report[m]["WEEKLY"] + report[m]["MONTHLY"]
            report[m]["TOTAL"] = total

        return dict(sorted(report.items()))

    def monthly_vehicle_count_report(self):
        report = {}  # month -> dict

        for v in self._vehicles:
            m = self._month_key(v.date)
            if m not in report:
                report[m] = {"CAR": 0, "BIKE": 0, "TRUCK": 0, "TOTAL": 0}

            report[m][v.vehicle_type] += 1

        for m in report:
            report[m]["TOTAL"] = report[m]["CAR"] + report[m]["BIKE"] + report[m]["TRUCK"]

        return dict(sorted(report.items()))