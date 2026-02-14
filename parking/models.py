from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta


# -----------------------------
# Vehicle Classes (OOP: Inheritance + Polymorphism)
# -----------------------------
class Vehicle(ABC):
    def __init__(self, plate):
        # Encapsulation (we keep plate in protected variable)
        self._plate = plate.strip().upper()

    def get_plate(self):
        return self._plate

    @abstractmethod
    def get_vehicle_type(self):
        pass


class Car(Vehicle):
    def get_vehicle_type(self):
        return "CAR"


class Bike(Vehicle):
    def get_vehicle_type(self):
        return "BIKE"


class Truck(Vehicle):
    def get_vehicle_type(self):
        return "TRUCK"


# -----------------------------
# Pass Classes (OOP: Inheritance + Polymorphism)
# -----------------------------
class Pass(ABC):
    def __init__(self, pass_id, issued_at=None):
        self._pass_id = pass_id.strip().upper()
        if issued_at is None:
            issued_at = datetime.now()
        self._issued_at = issued_at

    def get_pass_id(self):
        return self._pass_id

    def get_issued_at(self):
        return self._issued_at

    @abstractmethod
    def pass_type(self):
        pass

    @abstractmethod
    def is_valid(self, at_time=None):
        pass


class SingleEntryPass(Pass):
    def __init__(self, pass_id, issued_at=None):
        super().__init__(pass_id, issued_at)
        self._used = False

    def mark_used(self):
        self._used = True

    def pass_type(self):
        return "SINGLE"

    def is_valid(self, at_time=None):
        return not self._used


class WeeklyPass(Pass):
    def __init__(self, pass_id, issued_at=None):
        super().__init__(pass_id, issued_at)
        self._expires_at = self.get_issued_at() + timedelta(days=7)

    def pass_type(self):
        return "WEEKLY"

    def is_valid(self, at_time=None):
        if at_time is None:
            at_time = datetime.now()
        return at_time <= self._expires_at


class MonthlyPass(Pass):
    def __init__(self, pass_id, issued_at=None):
        super().__init__(pass_id, issued_at)
        self._expires_at = self.get_issued_at() + timedelta(days=30)

    def pass_type(self):
        return "MONTHLY"

    def is_valid(self, at_time=None):
        if at_time is None:
            at_time = datetime.now()
        return at_time <= self._expires_at


# -----------------------------
# Fee Calculator (Encapsulation)
# -----------------------------
class FeeCalculator:
    def __init__(self):
        # rate per hour
        self._hourly_rate = {
            "CAR": 5.0,
            "BIKE": 3.0,
            "TRUCK": 8.0
        }

        # pass price (this is revenue when pass is sold)
        self._pass_price = {
            "SINGLE": 0.0,
            "WEEKLY": 60.0,
            "MONTHLY": 180.0
        }

        self._minimum_fee = 5.0

    def get_pass_price(self, pass_type):
        pass_type = pass_type.upper()
        return float(self._pass_price.get(pass_type, 0.0))

    def calculate_fee(self, vehicle_type, duration_minutes, pass_type):
        vehicle_type = vehicle_type.upper()
        pass_type = pass_type.upper()

        # if weekly/monthly pass, parking fee is 0
        if pass_type == "WEEKLY" or pass_type == "MONTHLY":
            return 0.0

        # SINGLE entry: time based fee
        hours = (duration_minutes + 59) // 60  # ceiling hours
        if hours < 1:
            hours = 1

        rate = self._hourly_rate.get(vehicle_type, 5.0)
        fee = hours * rate

        if fee < self._minimum_fee:
            fee = self._minimum_fee

        return fee


# -----------------------------
# Parking Ticket + Parking Lot
# -----------------------------
@dataclass(frozen=True)
class ParkingTicket:
    ticket_id: str
    plate: str
    vehicle_type: str
    entry_time: datetime
    pass_type: str
    pass_id: str

    def duration_minutes(self, exit_time):
        mins = int((exit_time - self.entry_time).total_seconds() // 60)
        if mins < 0:
            mins = 0
        return mins


class ParkingLot:
    def __init__(self, capacity=300):
        self._capacity = capacity
        self._active = {}  # plate -> ParkingTicket

    def available_spaces(self):
        return self._capacity - len(self._active)

    def check_in(self, ticket):
        if self.available_spaces() <= 0:
            raise ValueError("Parking lot is full.")
        if ticket.plate in self._active:
            raise ValueError("Vehicle already parked.")
        self._active[ticket.plate] = ticket

    def check_out(self, plate):
        plate = plate.strip().upper()
        if plate not in self._active:
            raise ValueError("No active ticket for this plate.")
        return self._active.pop(plate)