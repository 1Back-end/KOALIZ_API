"""
Début de contrat                                            21/08/2024
Fin de contrat                                              07/03/2025
Date début du premier mois                                  21/08/2024
Date fin du premier mois                                    31/08/2024
Nombre de jour réel pour la premiere facture                5
Nombre de jour réel déduit du premiers mois (adaptation)    (5)6
Date début premier mois complet                             01/09/2024
date fin de contrat                                         07/03/2025
Accompte 10% à la signature
Horaire d'ouverture: 8h00 - 18h00
# Vacances
Fermeture crêche: 11 Novembre - 30 Novembre (3 semaines)
# Jour férié
- Mercredi 25 Décembre 2024
- Mercredi 01 Janvier 2025
# Fermeture exceptionnel
- Jeudi 15 Aout 2024
# Semaine Type
#1
Lundi     8h00 - 13h00 = 5h
Jeudi    10h00 - 16h00 = 6h
Vendredi  8h00 - 15h00 = 7h
#2
Lundi    08h00 - 12h00 | 13h00 - 18h00  = 9h
Mercredi 10h00 - 13h00  = 3h
# Prix TH 10 €
# CALCUL
DDC = 21/08/2024
DFC = 07/03/2025
DDP = 21/08/2024
DFP = 31/08/2024
NBJR = 5
NBJD = 5   -----> 6 (1) ---> Mettre 1 dans une variable des soustrations (férié + vacances)
DDPC = 01/09/2024
```
>>> import datetime
>>> datetime.date(2024, 9, 1).isocalendar()[1]
24
```
Nombre de jour ouvré déduit de la suite du contrat (jrs fériés) = 1 #si tombe dans le 1er mois ou dernier mois de facturation on soustrait dans le premier/dernier mois de facturation
NBSF = 3
NBHS = 15 H ((18 + 12) / 2)
NBJS = 2.5 ((2+3)/2)
MHJ = 6 ((5+6+7+9+3)/5)
TH = 10 €
CJ = 60 € (6 * 10 €)
NBJOP = 0 (5 - 5)
FPM =  0 € (0 * 60 €)
NBJO = 55 (Nombre de jour de présence de l'enfant hors premier et dernier mois vu que fini le 7 février) -> paramètre pour dire a partir de combien de jours on considère le dernier mois comme spécial | boolean pour dire si on prend ça ou non
SJFD = 7
NDJF = 1 (Nombre de jour férier)
RDJA = 1 (Reste de jour d'adaptation)
NBJOR = 47 (55 - 7 - 1) (si on ne lisse pas le dernier mois on ajoute)
Montant restant du contrat   = 2 820 € (47 * 60 €) = NBJOR x CJ  (si on ne lisse pas le dernier mois on ajoute)
NFL = 5 (si on ne lisse pas le dernier mois on ajoute)
NBJFM = 9,4 (47/5) = NBJOR/NFL
MM = 564 € (9,4 * 60 €)
ACP = 56,4 € (10% de 564€) -> viens de la config montant fixe ou pourcentage
MFA = 80 € (forfait 6 J)
MFI = 90 €
Facture d'accompte  56,4 € = ACP
Facture 1er mois    170 € = 0 + 80 + 90 = FPM + MFA + MFI
Facture mois complet 1  447,6 € = 564 - 56,4 - 60 = MM - ACP - (RDJAxCJ)
Facture mois complet 2  564 € = MM
Facture mois complet 3  564 € = MM
Facture mois complet 4  564 € = MM
Facture mois complet 5  564 € = MM
Facture mois de fin 6   120 € = 2 x 60 = 2 x CJ
Total = 3 110 €
"""
from calendar import monthrange
from datetime import datetime, timedelta, date
from time import sleep

from dateutil import rrule

from app.main.utils.quote_engine.types import Response, Week, DaySlot, Day, QuoteTimetable, QuoteTimeTableItem
from app.main.models.quote import AdaptationType, DepositType, InvoiceTimeType, QuoteTimetableItemType


class QuoteEngine:
    contract_start_date: date
    contract_end_date: date
    rate_per_hour: float
    planning_weeks: list[Week]
    holiday_days: list[date]
    closing_periods: list[tuple[date, date]]

    adaptation_type: AdaptationType
    adaptation_package_costs: float
    adaptation_package_days: float
    adaptation_hourly_rate: float
    adaptation_hours_number: int

    has_deposit: bool
    deposit_type: DepositType
    deposit_percentage: float
    deposit_value: float

    has_registration_fee: bool
    registration_fee: float

    last_special_month: bool
    min_days_for_last_special_month: int

    invoice_timing: InvoiceTimeType

    def __init__(
            self, contract_start_date: date, contract_end_date: date, rate_per_hour: float,
            planning_weeks: list[list[list[dict]]], holiday_days: list[date], closing_periods: list[tuple[date, date]],
            adaptation_type: AdaptationType, adaptation_package_costs: float, adaptation_package_days: float,
            adaptation_hourly_rate: float, adaptation_hours_number: int, has_deposit: bool, deposit_type: DepositType,
            deposit_percentage: float, deposit_value: float, has_registration_fee: bool, registration_fee: float,
            last_special_month: bool, min_days_for_last_special_month: int, invoice_timing: InvoiceTimeType
    ):
        self.contract_start_date = contract_start_date
        self.contract_end_date = contract_end_date
        self.rate_per_hour = rate_per_hour
        self.planning_weeks = [
            Week(days=[
                Day(slots=[
                    DaySlot(from_time=slot["from_time"], to_time=slot["to_time"]) for slot in day
                ]) for day in week
            ]) for week in planning_weeks
        ]
        self.holiday_days = holiday_days
        self.closing_periods = closing_periods
        self.adaptation_type = adaptation_type
        self.adaptation_package_costs = adaptation_package_costs
        self.adaptation_package_days = adaptation_package_days
        self.adaptation_hourly_rate = adaptation_hourly_rate
        self.adaptation_hours_number = adaptation_hours_number
        self.has_deposit = has_deposit
        self.deposit_type = deposit_type
        self.deposit_percentage = deposit_percentage
        self.deposit_value = deposit_value
        self.has_registration_fee = has_registration_fee
        self.registration_fee = registration_fee
        self.last_special_month = last_special_month
        self.min_days_for_last_special_month = min_days_for_last_special_month
        self.invoice_timing = invoice_timing

    def generate_quote(self) -> Response:
        # starting of the generation
        start_datetime = datetime.now()
        ddc_contract_start_date = self.contract_start_date
        dfc_contract_end_date = self.contract_end_date
        ddp_first_month_start_date = self.contract_start_date
        dfp_first_month_end_date = self.contract_start_date.replace(
            day=monthrange(self.contract_start_date.year, self.contract_start_date.month)[1])
        # get the real days for the first month based on the planning weeks and start and end date of the first
        # month, we will get the numbers of weeks inside the first month, then based on the planning weeks we will
        # get the number of days for each week, then we will get the number of days for each day of the week
        nbjr_real_days_for_first_invoice = 0
        first_week_index = ddp_first_month_start_date.isocalendar()[1]
        last_week_index = dfp_first_month_end_date.isocalendar()[1]
        first_day_of_first_week = ddp_first_month_start_date - timedelta(days=ddp_first_month_start_date.weekday())
        for week_index in range(last_week_index - first_week_index + 1):
            week = self.planning_weeks[week_index % len(self.planning_weeks)]
            for day_index, day in enumerate(week.days):
                if not day.slots:
                    continue
                # check if the current day is between the start and end date of the first month
                current_date = first_day_of_first_week + timedelta(days=week_index * 7 + day_index)
                if ddp_first_month_start_date <= current_date <= dfp_first_month_end_date:
                    nbjr_real_days_for_first_invoice += 1

        nbhs_total_hours_per_week = sum(
            [week.duration_per_week for week in self.planning_weeks]
        ) / len(self.planning_weeks)

        nbjs_total_days_per_week = sum(
            [week.days_count for week in self.planning_weeks]
        ) / len(self.planning_weeks)

        mhj_average_duration_per_day = nbhs_total_hours_per_week / nbjs_total_days_per_week

        adaption_days = self.adaptation_package_days \
            if self.adaptation_type == AdaptationType.PACKAGE \
            else self.adaptation_hours_number / mhj_average_duration_per_day

        nbjd_real_days_deducted_from_first_month = nbjr_real_days_for_first_invoice \
            if adaption_days > nbjr_real_days_for_first_invoice \
            else nbjr_real_days_for_first_invoice - adaption_days

        rdja_remain_adaption_days = adaption_days - nbjd_real_days_deducted_from_first_month \
            if adaption_days > nbjr_real_days_for_first_invoice else 0

        ddpc_first_complete_month_start_date = dfp_first_month_end_date + timedelta(days=1)

        th_hourly_rate = self.rate_per_hour
        cj_daily_cost = th_hourly_rate * mhj_average_duration_per_day

        nbjop_billable_first_month_days = nbjr_real_days_for_first_invoice - nbjd_real_days_deducted_from_first_month
        fpm_first_month_cost = nbjop_billable_first_month_days * cj_daily_cost

        nbjo_remaining_contract_days = 0
        sjfd_closing_days = 0
        last_special_month_days = 0
        is_last_special_month_matched = False
        last_end_date = dfc_contract_end_date
        if self.last_special_month:
            first_day_of_last_month = dfc_contract_end_date.replace(day=1)
            last_day_of_last_month = dfc_contract_end_date
            first_week_index_of_last_month = first_day_of_last_month.isocalendar()[1]
            last_week_index_of_last_month = last_day_of_last_month.isocalendar()[1]
            first_day_of_first_week_of_last_month = first_day_of_last_month - timedelta(
                days=first_day_of_last_month.weekday())
            days_count = 0
            closing_days_count = 0
            for week_index in range(last_week_index_of_last_month - first_week_index_of_last_month + 1):
                week = self.planning_weeks[
                    (first_week_index - first_week_index_of_last_month - week_index) % len(self.planning_weeks)]
                for day_index, day in enumerate(week.days):
                    if not day.slots:
                        continue
                    # check if the current day is between the start and end date of the first month
                    current_date = first_day_of_first_week_of_last_month + timedelta(days=week_index * 7 + day_index)
                    if first_day_of_last_month <= current_date <= last_day_of_last_month:
                        days_count += 1
                        if any([closing_period[0] <= current_date <= closing_period[1] for closing_period in
                                self.closing_periods]) and current_date not in self.holiday_days:
                            closing_days_count += 1
            if days_count <= self.min_days_for_last_special_month:
                last_special_month_days = days_count
                is_last_special_month_matched = True
                sjfd_closing_days = closing_days_count
                last_end_date = first_day_of_last_month - timedelta(days=1)

        # get number of weeks between the ddpc_first_complete_month_start_date and last_end_date
        remaing_contract_weeks_count = self.__weeks_between(ddpc_first_complete_month_start_date, last_end_date)
        # identify the numbers of weeks per each planning weeks
        first_week_index_of_last_month = ddpc_first_complete_month_start_date.isocalendar()[1]
        first_day_of_first_week_of_last_month = ddpc_first_complete_month_start_date - timedelta(
            days=ddpc_first_complete_month_start_date.weekday())

        for week_index in range(remaing_contract_weeks_count + 1):
            week = self.planning_weeks[
                (first_week_index - first_week_index_of_last_month - week_index) % len(self.planning_weeks)]
            for day_index, day in enumerate(week.days):
                if not day.slots:
                    continue
                # check if the current day is between the start and end date of the first month
                current_date = first_day_of_first_week_of_last_month + timedelta(days=week_index * 7 + day_index)
                if ddpc_first_complete_month_start_date <= current_date <= last_end_date:
                    nbjo_remaining_contract_days += 1
                    if any([closing_period[0] <= current_date <= closing_period[1] for closing_period in
                            self.closing_periods]) and current_date not in self.holiday_days:
                        sjfd_closing_days += 1

        ndjf_holiday_days = 0
        ndjf_holiday_first_month_days = 0
        for holiday_day in self.holiday_days:
            # get the week index of the holiday day and check if it's between the start and end date of the contract and
            # based on the week index get the week and the day index of the holiday day and check if the day is in the
            # planning weeks
            week_index = holiday_day.isocalendar()[1]
            if ddc_contract_start_date <= holiday_day <= dfc_contract_end_date:
                # if the first week index is odd or even we will get the week based on the week index modulo the length
                week = self.planning_weeks[(first_week_index - week_index) % len(self.planning_weeks)]
                day_index = holiday_day.weekday()
                if week.days[day_index].slots:
                    ndjf_holiday_days += 1
                    if ddp_first_month_start_date <= holiday_day <= dfp_first_month_end_date:
                        ndjf_holiday_first_month_days += 1

        nbjor_real_contract_days_after_first_month = nbjo_remaining_contract_days - sjfd_closing_days - ndjf_holiday_days

        mrc_remaining_contract_cost_after_first_month = nbjor_real_contract_days_after_first_month * cj_daily_cost
        nfl_smoothing_month_count = self.__months_between(ddpc_first_complete_month_start_date, last_end_date)
        nbjfm_numbers_of_days_per_month = nbjor_real_contract_days_after_first_month / nfl_smoothing_month_count
        mm_monthly_cost = nbjfm_numbers_of_days_per_month * cj_daily_cost
        print(mm_monthly_cost)
        if self.has_deposit:
            acp_deposit_amount = (mm_monthly_cost * self.deposit_percentage / 100) if self.deposit_type == DepositType.PERCENTAGE else self.deposit_value
        else:
            acp_deposit_amount = 0
        mfa_adaptation_package_cost = self.adaptation_package_costs if self.adaptation_type == AdaptationType.PACKAGE else self.adaptation_hours_number * self.adaptation_hourly_rate
        mfi_registration_fee = self.registration_fee

        last_month_amount = last_special_month_days * cj_daily_cost
        quote_timetables = []
        if self.has_deposit:
            quote_timetables.append(QuoteTimetable(
                billing_date=ddc_contract_start_date,
                amount=acp_deposit_amount,
                items=[
                    QuoteTimeTableItem(
                        amount=acp_deposit_amount,
                        quote_type=QuoteTimetableItemType.DEPOSIT,
                        qty=1
                    )
                ]
            ))
        quote_timetables.append(QuoteTimetable(
            billing_date=dfp_first_month_end_date if self.invoice_timing == InvoiceTimeType.END_OF_MONTH else dfp_first_month_end_date.replace(day=1),
            amount=fpm_first_month_cost + mfa_adaptation_package_cost + mfi_registration_fee,
            items=[
                QuoteTimeTableItem(
                    amount=fpm_first_month_cost,
                    quote_type=QuoteTimetableItemType.REGISTRATION,
                    qty=nbjop_billable_first_month_days/mhj_average_duration_per_day
                ),
                QuoteTimeTableItem(
                    amount=mfa_adaptation_package_cost,
                    quote_type=QuoteTimetableItemType.ADAPTATION,
                    qty=adaption_days
                ),
                QuoteTimeTableItem(
                    amount=mfi_registration_fee,
                    quote_type=QuoteTimetableItemType.REGISTRATION,
                    qty=1
                )
            ]
        ))
        current_month = (ddpc_first_complete_month_start_date + timedelta(days=35)).replace(day=1) - timedelta(days=1)
        remaing_acp_deposit_amount = acp_deposit_amount
        for month in range(1, nfl_smoothing_month_count + 1):
            amount = mm_monthly_cost - ((rdja_remain_adaption_days * cj_daily_cost) if month == 1 else 0)
            if amount < remaing_acp_deposit_amount:
                remaing_acp_deposit_amount -= amount
                amount = 0
            else:
                amount -= remaing_acp_deposit_amount
                remaing_acp_deposit_amount = 0
            quote_timetables.append(QuoteTimetable(
                billing_date=current_month if self.invoice_timing == InvoiceTimeType.END_OF_MONTH else current_month.replace(day=1),
                amount=amount,
                items=[
                    QuoteTimeTableItem(
                        amount=amount,
                        quote_type=QuoteTimetableItemType.REGISTRATION,
                        qty=nbjfm_numbers_of_days_per_month/mhj_average_duration_per_day
                    )
                ]
            ))
            current_month = (current_month + timedelta(days=35)).replace(day=1) - timedelta(days=1)
        if is_last_special_month_matched:
            quote_timetables.append(QuoteTimetable(
                billing_date=self.contract_end_date if self.invoice_timing == InvoiceTimeType.END_OF_MONTH else self.contract_end_date.replace(day=1),
                amount=last_month_amount,
                items=[
                    QuoteTimeTableItem(
                        amount=last_month_amount,
                        quote_type=QuoteTimetableItemType.REGISTRATION,
                        qty=last_special_month_days/mhj_average_duration_per_day
                    )
                ]
            ))
        response = Response(
            total=(
                    acp_deposit_amount + fpm_first_month_cost + mfa_adaptation_package_cost + mfi_registration_fee
                    - (rdja_remain_adaption_days * cj_daily_cost)
                    + mrc_remaining_contract_cost_after_first_month + last_month_amount
            ),
            acp_deposit_amount=acp_deposit_amount,
            fpm_first_month_cost=fpm_first_month_cost,
            mfa_adaptation_package_cost=mfa_adaptation_package_cost,
            mfi_registration_fee=mfi_registration_fee,
            mrc_remaining_contract_cost_after_first_month=mrc_remaining_contract_cost_after_first_month,
            last_month_amount=last_month_amount,
            quote_timetables=quote_timetables
        )
        end_datetime = datetime.now()
        print(f"Execution time in seconds: {(end_datetime - start_datetime).seconds}")
        return response

    def __weeks_between(self, start_date: date, end_date: date):
        start_date_monday = start_date - timedelta(days=start_date.weekday())
        end_date_sunday = end_date + timedelta(days=6 - end_date.weekday())
        weeks = rrule.rrule(rrule.WEEKLY, dtstart=start_date_monday, until=end_date_sunday)
        return weeks.count()

    def __months_between(self, start_date: date, end_date: date):
        start_date_of_month = start_date.replace(day=1)
        end_date_of_month = (end_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        months = rrule.rrule(rrule.MONTHLY, dtstart=start_date_of_month, until=end_date_of_month)
        return months.count()


quote = QuoteEngine(
    contract_start_date=date(2024, 8, 21),
    contract_end_date=date(2025, 3, 7),
    rate_per_hour=10,
    planning_weeks=[
        [
            [
                {
                    "from_time": "08:00",
                    "to_time": "13:30"
                }
            ],
            [],
            [],
            [
                {
                    "from_time": "10:00",
                    "to_time": "16:00"
                }
            ],
            [
                {
                    "from_time": "08:00",
                    "to_time": "15:00"
                }
            ],
        ],
        [
            [
                {
                    "from_time": "08:00",
                    "to_time": "12:00"
                },
                {
                    "from_time": "13:00",
                    "to_time": "18:00"
                }
            ],
            [],
            [
                {
                    "from_time": "10:00",
                    "to_time": "13:00"
                }
            ],
            [],
            []
        ]
    ],
    holiday_days=[
        date(2024, 12, 25),
        date(2025, 1, 1),
        date(2024, 8, 15)
    ],
    closing_periods=[
        (date(2024, 11, 11), date(2024, 11, 30))
    ],
    adaptation_type=AdaptationType.PACKAGE,
    adaptation_package_costs=80,
    adaptation_package_days=6,
    adaptation_hourly_rate=0,
    adaptation_hours_number=0,
    has_deposit=True,
    deposit_type=DepositType.PERCENTAGE,
    deposit_percentage=10,
    deposit_value=0,
    has_registration_fee=True,
    registration_fee=90,
    last_special_month=True,
    min_days_for_last_special_month=5,
    invoice_timing=InvoiceTimeType.END_OF_MONTH
)
print(quote.generate_quote())
