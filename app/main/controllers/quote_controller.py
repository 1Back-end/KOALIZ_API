import datetime


class Contract:
    def __init__(self, start_date, end_date, rate_per_hour, adaptation_days, adaptation_cost, registration_fee, closure_weeks):
        self.start_date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
        self.end_date = datetime.datetime.strptime(end_date, '%d/%m/%Y')
        self.rate_per_hour = rate_per_hour
        self.adaptation_days = adaptation_days
        self.adaptation_cost = adaptation_cost
        self.registration_fee = registration_fee
        self.closure_weeks = closure_weeks
        self.weekly_schedules = []

    def add_weekly_schedule(self, weekly_schedule):
        self.weekly_schedules.append(weekly_schedule)

    def calculate_weekly_hours(self):
        weekly_hours = []
        for schedule in self.weekly_schedules:
            total_hours = sum(schedule.values())
            weekly_hours.append(total_hours)
        return weekly_hours

    def calculate_costs(self):
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


def main():
    contract = Contract(
        start_date='18/06/2024',
        end_date='31/05/2025',
        rate_per_hour=9.2,
        adaptation_days=5,
        adaptation_cost=150,
        registration_fee=90,
        closure_weeks=5
    )
    week1 = {
        'Monday': 10,
        'Tuesday': 10,
        'Wednesday': 4,
        'Thursday': 10,
        'Friday': 8
    }
    week2 = {
        'Monday': 8,
        'Tuesday': 8,
        'Wednesday': 4,
        'Thursday': 8,
        'Friday': 8
    }
    contract.add_weekly_schedule(week1)
    contract.add_weekly_schedule(week2)
    costs = contract.calculate_costs()
    print(f"First month cost: {costs['first_month_cost']:.2f} €")
    print(f"Monthly cost: {costs['monthly_cost']:.2f} €")
    print(f"Total contract cost: {costs['total_contract_cost']:.2f} €")

if __name__ == "__main__":
    main()