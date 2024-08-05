from decimal import Decimal

from app.main.models.quote import QuoteTimetableItemType
from datetime import date


class QuoteTimeTableItem:
    amount: Decimal
    qty: Decimal
    quote_type: QuoteTimetableItemType

    def __init__(self, amount: float, qty: float, quote_type: QuoteTimetableItemType):
        self.amount = Decimal("%.2f" % amount)
        self.quote_type = quote_type
        self.qty = Decimal("%.2f" % qty)


class QuoteTimetable:
    billing_date: date
    amount: Decimal
    items: list[QuoteTimeTableItem]

    def __init__(self, billing_date: date, amount: float, items: list[QuoteTimeTableItem]):
        self.billing_date = billing_date
        self.amount = Decimal("%.2f" % amount)
        self.items = items


class Response:
    total: Decimal
    quote_timetables: list[QuoteTimetable]
    acp_deposit_amount: Decimal
    fpm_first_month_cost: Decimal
    mm_monthly_cost: Decimal
    mfa_adaptation_package_cost: Decimal
    mfi_registration_fee: Decimal
    mrc_remaining_contract_cost_after_first_month: Decimal
    last_month_amount: Decimal

    def __init__(self, total: float, quote_timetables: list[QuoteTimetable], acp_deposit_amount: float,
                 fpm_first_month_cost: float, mm_monthly_cost: float, mfa_adaptation_package_cost: float, mfi_registration_fee: float,
                 mrc_remaining_contract_cost_after_first_month: float, last_month_amount: float):
        self.total = Decimal("%.2f" % total)
        self.quote_timetables = quote_timetables
        self.acp_deposit_amount = Decimal("%.2f" % acp_deposit_amount)
        self.fpm_first_month_cost = Decimal("%.2f" % fpm_first_month_cost)
        self.mm_monthly_cost = Decimal("%.2f" % mm_monthly_cost)
        self.mfa_adaptation_package_cost = Decimal("%.2f" % mfa_adaptation_package_cost)
        self.mfi_registration_fee = Decimal("%.2f" % mfi_registration_fee)
        self.mrc_remaining_contract_cost_after_first_month = Decimal("%.2f" % mrc_remaining_contract_cost_after_first_month)
        self.last_month_amount = Decimal("%.2f" % last_month_amount)

    def __str__(self):
        str_response = f"Total: {self.total}\n"
        index = 1
        for quote_timetable in self.quote_timetables:
            str_response += f"===={index}=====\n"
            str_response += f"{quote_timetable.billing_date} - {quote_timetable.amount}\n"
            for item in quote_timetable.items:
                str_response += f"{item.qty} - {item.amount} - {item.quote_type.title()}\n"
            index += 1
        return str_response
class DaySlot:
    from_time: str
    to_time: str
    duration: float

    def __init__(self, from_time: str, to_time: str):
        self.from_time = from_time
        self.to_time = to_time
        # calculate duration by subtracting to_time from from_time
        self.duration = (
                (int(to_time.split(":")[0]) - int(from_time.split(":")[0])) +
                (int(to_time.split(":")[1]) - int(from_time.split(":")[1])) / 60
        )

    def __str__(self):
        return f"DaySlot: {self.from_time} - {self.to_time} ({self.duration} hours)"


class Day:
    duration: float
    slots: list[DaySlot]

    def __init__(self, slots: list[DaySlot]):
        self.slots = slots
        # calculate hour_duration by summing up the duration of all slots
        self.duration = sum(
            [
                slot.duration for slot in slots
            ]
        )

    def __str__(self):
        return f"Day: {self.slots} ({self.duration} hours)"


class Week:
    days: list[Day]
    days_count: int
    duration_per_week: float

    def __init__(self, days: list[Day]):
        self.days = days
        # calculate duration_per_week by summing up the duration of all days
        self.duration_per_week = sum(
            [
                day.duration for day in days
            ]
        )
        self.days_count = sum(
            [
                1 if day.slots else 0 for day in days
            ]
        )

    def __str__(self):
        return f"Week: {len(self.days)} ({self.duration_per_week} hours)"
