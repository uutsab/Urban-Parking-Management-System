from datetime import datetime, timedelta

from parking.models import (
    ParkingLot, ParkingTicket, FeeCalculator,
    Car, Bike, Truck,
    SingleEntryPass, WeeklyPass, MonthlyPass
)
from parking.finance import FinanceManager, Party
from parking.reporting import ReportingManager


class ParkingApp:
    def __init__(self):
        self.lot = ParkingLot(300)
        self.fees = FeeCalculator()
        self.finance = FinanceManager()
        self.reporting = ReportingManager()

        self._ticket_no = 1000
        self._pass_no = 5000

    # -------------------
    # basic input helpers (friendly)
    # -------------------
    def read_text(self, msg):
        while True:
            value = input(msg).strip()
            if value != "":
                return value
            print("Please enter a value (cannot be empty).")

    def read_float(self, msg):
        while True:
            value = input(msg).strip()
            try:
                num = float(value)
                if num < 0:
                    print("Number cannot be negative.")
                else:
                    return num
            except ValueError:
                print("Invalid number, try again (example: 12.50).")

    def read_int(self, msg):
        while True:
            value = input(msg).strip()
            try:
                return int(value)
            except ValueError:
                print("Invalid integer, try again (example: 30).")

    def next_ticket_id(self):
        self._ticket_no += 1
        return "T" + str(self._ticket_no)

    def next_pass_id(self):
        self._pass_no += 1
        return "P" + str(self._pass_no)

    # -------------------
    # create vehicle/pass (simple factory)
    # -------------------
    def create_vehicle(self, vehicle_type, plate):
        vehicle_type = vehicle_type.upper()
        if vehicle_type == "CAR":
            return Car(plate)
        if vehicle_type == "BIKE":
            return Bike(plate)
        if vehicle_type == "TRUCK":
            return Truck(plate)
        raise ValueError("Vehicle type must be CAR/BIKE/TRUCK.")

    def create_pass(self, pass_type):
        pass_type = pass_type.upper()
        pid = self.next_pass_id()

        if pass_type == "SINGLE":
            return SingleEntryPass(pid)
        if pass_type == "WEEKLY":
            return WeeklyPass(pid)
        if pass_type == "MONTHLY":
            return MonthlyPass(pid)
        raise ValueError("Pass type must be SINGLE/WEEKLY/MONTHLY.")

    # -------------------
    # system features
    # -------------------
    def vehicle_entry(self):
        try:
            vt = self.read_text("Vehicle type (CAR/BIKE/TRUCK): ")
            plate = self.read_text("Plate number: ")
            pt = self.read_text("Pass type (SINGLE/WEEKLY/MONTHLY): ")

            vehicle = self.create_vehicle(vt, plate)
            p = self.create_pass(pt)

            # pass sale revenue
            price = self.fees.get_pass_price(p.pass_type())
            if price > 0:
                self.finance.add_revenue(price, p.pass_type() + " Pass Sale", datetime.now())
                self.reporting.record_sale(datetime.now(), p.pass_type(), price)

            ticket = ParkingTicket(
                ticket_id=self.next_ticket_id(),
                plate=vehicle.get_plate(),
                vehicle_type=vehicle.get_vehicle_type(),
                entry_time=datetime.now(),
                pass_type=p.pass_type(),
                pass_id=p.get_pass_id()
            )

            self.lot.check_in(ticket)
            self.reporting.record_vehicle(datetime.now(), vehicle.get_vehicle_type())

            print("\n✅ Vehicle Entered Successfully!")
            print("Ticket:", ticket.ticket_id)
            print("Plate:", ticket.plate)
            print("Pass :", ticket.pass_type, ticket.pass_id)
            print("Available spaces:", self.lot.available_spaces(), "\n")

        except ValueError as e:
            print("❌ Entry failed:", e, "\n")

    def vehicle_exit(self):
        try:
            plate = self.read_text("Plate number to exit: ").upper()
            ticket = self.lot.check_out(plate)

            exit_time = datetime.now()
            mins = ticket.duration_minutes(exit_time)
            fee = self.fees.calculate_fee(ticket.vehicle_type, mins, ticket.pass_type)

            if fee > 0:
                self.finance.add_revenue(fee, "Parking Fee", exit_time)
                self.reporting.record_sale(exit_time, "SINGLE", fee)

            print("\n✅ Vehicle Exited Successfully!")
            print("Ticket:", ticket.ticket_id)
            print("Duration:", mins, "minutes")
            print("Fee: $%.2f" % fee)
            print("Available spaces:", self.lot.available_spaces(), "\n")

        except ValueError as e:
            print("❌ Exit failed:", e, "\n")

    def add_expense(self):
        src = self.read_text("Expense source (e.g., Electricity): ")
        amt = self.read_float("Expense amount: ")
        try:
            self.finance.add_expense(amt, src, datetime.now())
            print("✅ Expense saved.\n")
        except ValueError as e:
            print("❌ Error:", e, "\n")

    def add_debtor_creditor(self):
        role = self.read_text("Role (DEBTOR/CREDITOR): ").upper()
        name = self.read_text("Name: ")
        amt = self.read_float("Amount: ")
        due_days = self.read_int("Due in how many days? (0 = today): ")
        note = input("Note (optional): ").strip()

        created = datetime.now()
        due_date = created + timedelta(days=due_days)

        try:
            party = Party(name=name, role=role, amount=amt,
                          created_at=created, due_date=due_date, note=note)
            self.finance.add_party(party)
            print("✅ Saved.\n")
        except ValueError as e:
            print("❌ Error:", e, "\n")

    def finance_summary(self):
        print("\n--- FINANCE SUMMARY ---")
        print("Revenue : $%.2f" % self.finance.total_revenue())
        print("Expenses: $%.2f" % self.finance.total_expenses())
        print("Profit  : $%.2f" % self.finance.profit())
        print()

    def show_debtors_over_30(self):
        debtors = self.finance.debtors_over_30_days(30)
        print("\n--- DEBTORS OVER 30 DAYS ---")
        if len(debtors) == 0:
            print("No overdue debtors.\n")
            return

        for d in debtors:
            overdue_days = (datetime.now().date() - d.due_date.date()).days
            print("-", d.name, "| $%.2f" % d.amount, "| overdue", overdue_days, "days | due", d.due_date.date())
        print()

    def show_creditors(self):
        creditors = self.finance.list_creditors()
        print("\n--- CREDITORS ---")
        if len(creditors) == 0:
            print("No creditors.\n")
            return

        for c in creditors:
            print("-", c.name, "| $%.2f" % c.amount, "| due", c.due_date.date(), "| note:", c.note)
        print()

    def monthly_sales_report(self):
        report = self.reporting.monthly_sales_report()
        print("\n--- MONTHLY SALES REPORT ---")
        if len(report) == 0:
            print("No sales data yet.\n")
            return

        for month in report:
            data = report[month]
            print(month,
                  ": SINGLE=$%.2f" % data["SINGLE"],
                  "| WEEKLY=$%.2f" % data["WEEKLY"],
                  "| MONTHLY=$%.2f" % data["MONTHLY"],
                  "| TOTAL=$%.2f" % data["TOTAL"])
        print()

    def monthly_vehicle_report(self):
        report = self.reporting.monthly_vehicle_count_report()
        print("\n--- MONTHLY VEHICLE COUNT REPORT ---")
        if len(report) == 0:
            print("No vehicle data yet.\n")
            return

        for month in report:
            data = report[month]
            print(month,
                  ": CAR=", data["CAR"],
                  "| BIKE=", data["BIKE"],
                  "| TRUCK=", data["TRUCK"],
                  "| TOTAL=", data["TOTAL"])
        print()

    # -------------------
    # main menu
    # -------------------
    def run(self):
        while True:
            print("==== Urban City Parking System ====")
            print("1. Vehicle Entry")
            print("2. Vehicle Exit")
            print("3. Add Expense")
            print("4. Add Debtor/Creditor")
            print("5. Finance Summary")
            print("6. Debtors Over 30 Days")
            print("7. List Creditors")
            print("8. Monthly Sales Report")
            print("9. Monthly Vehicle Count Report")
            print("0. Exit")

            choice = input("Choose option: ").strip()

            if choice == "1":
                self.vehicle_entry()
            elif choice == "2":
                self.vehicle_exit()
            elif choice == "3":
                self.add_expense()
            elif choice == "4":
                self.add_debtor_creditor()
            elif choice == "5":
                self.finance_summary()
            elif choice == "6":
                self.show_debtors_over_30()
            elif choice == "7":
                self.show_creditors()
            elif choice == "8":
                self.monthly_sales_report()
            elif choice == "9":
                self.monthly_vehicle_report()
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Try again.\n")


if __name__ == "__main__":
    ParkingApp().run()