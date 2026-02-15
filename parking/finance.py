    from dataclasses import dataclass
    from datetime import datetime


    @dataclass
    class LedgerEntry:
        kind: str   # "REVENUE" or "EXPENSE"
        amount: float
        source: str
        date: datetime

    
    @dataclass
    class Party:
        name: str
        role: str   # "DEBTOR" OR "CREDITOR"
        amount: float
        created_at: datetime
        due_date: datetime
        note: str = ""


class FinanceManager:
    def __init__(self):
        self ._ledger = []    #list of LedgerEntry
        self._parties = []    #list of Party

    def add_revenue(self, amount, source, date=None):
        self._add_ledger("REVENUE", amount, source, date)

    def add_expense(self, amount, source, date=None):
        self._add_ledger("EXPENSE", amount, source, date)

    def _add_ledger(self, kind, amount, source, date):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        if date is None:
            date = datetime.now()

    self._ledger.append(LedgerEntry(kind=kind, amount=float(amount), source=source, date=date))


    def total_revenue(self):
        total = 0.0
        for e in self._ledger:
            if e.kind == "REVENUE":
                total += e.amount
            return total

    def total_expenses(self):
        total = 0.0
        for e in self._ledger:
            if e.kind == "EXPENSE":
                total += e.amount
            return total

    def profit(self):
        return self.total_revenue() - self.total_expenses()

    def add_party(self, party):
        role = party.role.upper()
        if role != "DEBITOR" and role != "CREDITOR":
            raise ValueError("Role must be DEBITOR or CREDITOR.")
            if party.amount < 0:
                raise ValueError("Amount cannot be negative.")
                self._parties.append(party)
 
 def list_creditors(self):
    result = []
    for p in self._parties:
        if p.role.upper() == "CREDITOR":
            result.append(p)
            return result

def list debtors(self):
    result = []
    for p in self._parties:
        if p.role.upper() == "DEBTOR":
            result.append(p)
            return result


def debtors_over_30_days(self, days=30, as_of=None):
    if as_of is None:
        as_of = datetime.now()

    overdue_list = []
    for d in self.list_debtors():
        overdue_days = (as_of.date() - d.due_date.date()).days
        if overdue_days > days:
            overdue_list.append(d)
            return overdue_list
     
