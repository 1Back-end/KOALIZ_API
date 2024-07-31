import calendar
from datetime import datetime, timedelta
from math import ceil

from app.main import models
from app.main.models.db.session import SessionLocal


class Quotation:
    def __init__(self, start_date, end_date, rate_per_hour, adaptation_days, adaptation_cost, registration_fee, closure_weeks, preregistration: models.PreRegistration = None, quote: models.Quote = None):
        self.quote = quote
        self.preregistration = preregistration
        self.start_date = datetime.strptime(start_date, '%d/%m/%Y')
        self.end_date = datetime.strptime(end_date, '%d/%m/%Y')
        self.rate_per_hour = rate_per_hour
        self.adaptation_days = adaptation_days
        self.adaptation_cost = adaptation_cost
        self.registration_fee = registration_fee
        self.closure_weeks = closure_weeks
        self.weekly_schedules = []

    def calculate_weekly_hours(self):
        weekly_hours = []
        for schedule in self.weekly_schedules:
            total_hours = sum(schedule.values())
            weekly_hours.append(total_hours)
        return weekly_hours

    def calculate_costs(self):
        first_day_of_first_month = self.start_date
        last_day_of_first_month = first_day_of_first_month.replace(day=calendar.monthrange(self.start_date.year, self.start_date.month)[1])
        real_days_for_first_invoice: int = 0
        adaptation_days: int = 0
        if self.quote.adaptation_type == models.AdaptationType.PACKAGE:
            adaptation_days = self.quote.adaptation_package_days
        if self.quote.adaptation_type == models.AdaptationType.HOURLY:
            adaptation_days = round(self.quote.adaptation_hours_number / 24, 3)
        real_days_deducted_from_first_month: int = adaptation_days if adaptation_days >= real_days_for_first_invoice else adaptation_days-real_days_for_first_invoice
        remaining_adaptation_days: int = adaptation_days - real_days_deducted_from_first_month

        start_first_complete_month = last_day_of_first_month + timedelta(days=1)
        end_first_complete_month = start_first_complete_month.replace(day=calendar.monthrange(start_first_complete_month.year, start_first_complete_month.month)[1])

        db = SessionLocal()
        nursery_closed_days = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.nursery_uuid==self.preregistration.nursery_uuid).all()
        for nursery_closed_day in nursery_closed_days:
            pass

        deposit_amount: float = 0
        if self.quote.has_deposit:
            if self.quote.deposit_type == models.DepositType.VALUE:
                deposit_amount = self.quote.deposit_value
            else:
                deposit_amount = 0

        weekdays_count = []
        current_date = first_day_of_first_month
        while current_date <= last_day_of_first_month:
            week_start = current_date - timedelta(days=current_date.weekday())
            week_end = week_start + timedelta(days=6)

            week_data = []
            for weekday in range(5):
                if week_start + timedelta(days=weekday) <= last_day_of_first_month:
                    week_data.append(weekday)

            weekdays_count.append(week_data)
            current_date = week_end + timedelta(days=1)


        typical_weeks = [
          [
            [
              {
                "to_time": "12:00",
                "from_time": "09:00"
              },
              {
                "to_time": "16:00",
                "from_time": "13:00"
              }
            ],
            [
              {
                "to_time": "17:00",
                "from_time": "09:00"
              }
            ],
            [
              {
                "to_time": "12:00",
                "from_time": "09:00"
              },
              {
                "to_time": "16:00",
                "from_time": "13:00"
              }
            ],
            [
              {
                "to_time": "12:00",
                "from_time": "09:00"
              },
              {
                "to_time": "16:00",
                "from_time": "13:00"
              }
            ],
            [
              {
                "to_time": "17:30",
                "from_time": "08:00"
              }
            ]
          ],
            [
                [
                ],
                [
                    {
                        "to_time": "17:00",
                        "from_time": "09:00"
                    }
                ],
                [],
                [
                    {
                        "to_time": "12:00",
                        "from_time": "09:00"
                    },
                    {
                        "to_time": "16:00",
                        "from_time": "13:00"
                    }
                ],
                [
                    {
                        "to_time": "17:30",
                        "from_time": "08:00"
                    }
                ]
            ]
        ]
        print(f"weekdays_count: {weekdays_count}")
        for week_index, days in enumerate(weekdays_count):
            print(f"days: {days}")
            # for dow_i, dow in enumerate(self.preregistration.pre_contract.typical_weeks[len(week_index)%len(self.preregistration.pre_contract.typical_weeks)]):
            for dow_i, dow in enumerate(typical_weeks[week_index%len(typical_weeks)]):
                print(f"dow: {dow}, dow_i: {dow_i}")
                if dow and dow_i in days:
                    real_days_for_first_invoice += 1
        return real_days_for_first_invoice
        weekly_hours = self.calculate_weekly_hours()
        average_weekly_hours = sum(weekly_hours) / len(weekly_hours)
        daily_hours = average_weekly_hours / 5  # Assuming a 5-day week
        cost_per_day = daily_hours * self.rate_per_hour
        initial_billable_days = 9 - self.adaptation_days  # Adjust based on the document's specifics
        first_month_cost = initial_billable_days * cost_per_day + self.adaptation_cost + self.registration_fee
        total_days_in_contract = (self.end_date - self.start_date).days - self.closure_weeks * 7
        total_billable_days = total_days_in_contract - initial_billable_days
        remaining_contract_cost = total_billable_days * cost_per_day
        monthly_cost = remaining_contract_cost / 11  # Assuming 11 full months
        return {
            'first_month_cost': first_month_cost,
            'monthly_cost': monthly_cost,
            'total_contract_cost': first_month_cost + remaining_contract_cost
        }


quotation = Quotation(
    start_date='22/07/2024',
    end_date='31/07/2025',
    rate_per_hour=9.2,
    adaptation_days=5,
    adaptation_cost=150,
    registration_fee=90,
    closure_weeks=5
)

# contract.add_weekly_schedule(week1)
# contract.add_weekly_schedule(week2)
# costs = contract.calculate_costs()
# print(f"First month cost: {costs['first_month_cost']:.2f} €")
print(f"First month cost: {quotation.calculate_costs()} €")
# print(f"Monthly cost: {costs['monthly_cost']:.2f} €")
# print(f"Total contract cost: {costs['total_contract_cost']:.2f} €")
