from datetime import datetime, date
import math
from typing import  Optional, List

from fastapi import HTTPException, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_

from app.main.core.i18n import __
from app.main.crud.base import CRUDBase
from sqlalchemy.orm import Session, aliased,joinedload
from app.main import crud, schemas, models
from app.main.utils.quote_engine import QuoteEngine
import uuid
from app.main.core.security import generate_code, generate_slug
from app.main.utils.helper import convert_dates_to_strings


class CRUDPreRegistration(CRUDBase[schemas.PreregistrationDetails, schemas.PreregistrationCreate, schemas.PreregistrationUpdate]):

    @classmethod
    def get_by_uuid(cls, db: Session, uuid: str) -> Optional[schemas.PreregistrationDetails]:
        return db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()

    @classmethod
    def delete_a_special_folder(cls, db: Session, folder_uuid: str, performed_by_uuid: str):
        folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == folder_uuid).first()
        if not folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        # Create the log tracking
        before_changes = schemas.PreregistrationDetails.model_validate(folder).model_dump()
        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=folder.uuid,
            action="DELETE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes={}
        )

        db.delete(folder)
        db.commit()

    @classmethod
    def change_status_of_a_special_folder(cls, db: Session, folder_uuid: str, status: str, performed_by_uuid: str,
                                          background_task=None) -> Optional[schemas.PreregistrationDetails]:

        exist_folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == folder_uuid).first()
        if not exist_folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        if not exist_folder.quote:
            background_task.add_task(cls.generate_quote, cls, db, exist_folder.uuid)

        # Create the log tracking
        before_changes = schemas.PreregistrationDetails.model_validate(exist_folder).model_dump()

        exist_folder.status = status
        if exist_folder.quote:
            exist_folder.quote.status = status if status in [st.value for st in models.QuoteStatusType] else exist_folder.quote.status
        
        if status in ['REFUSED']:
            exist_folder.refused_date = datetime.now()

        if status in ['ACCEPTED']:
            exist_folder.accepted_date = datetime.now()
            exist_folder.child.is_accepted = True

            if not exist_folder.contract_uuid:
                contract = models.Contract(
                    uuid=str(uuid.uuid4()),
                    begin_date=exist_folder.pre_contract.begin_date,
                    end_date=exist_folder.pre_contract.end_date,
                    typical_weeks=exist_folder.pre_contract.typical_weeks,
                    type=models.ContractType.REGULAR
                )
                db.add(contract)
                exist_folder.contract_uuid = contract.uuid
                exist_folder.child.contract_uuid = contract.uuid
            else:
                exist_folder.contract.begin_date = exist_folder.pre_contract.begin_date
                exist_folder.contract.end_date = exist_folder.pre_contract.end_date
                exist_folder.contract.typical_weeks = exist_folder.pre_contract.typical_weeks
                exist_folder.contract.type = models.ContractType.REGULAR

            if exist_folder.quote and exist_folder.quote.status != models.QuoteStatusType.ACCEPTED:
                exist_folder.quote.status = models.QuoteStatusType.ACCEPTED
                crud.quote.update_status(db, exist_folder.quote, models.QuoteStatusType.ACCEPTED)
                crud.invoice.generate_invoice(db, exist_folder.quote.uuid, exist_folder.contract_uuid)

            db.flush()

            # Insert planning for child
            # background_task.add_task(crud.child_planning.insert_planning, exist_folder.nursery, exist_folder.child, db)
            crud.child_planning.insert_planning(db=db, child=exist_folder.child, nursery=exist_folder.nursery)

        db.commit()

        after_changes = schemas.PreregistrationDetails.model_validate(exist_folder).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=exist_folder.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        # Update others folders with refused status
        if status in ['ACCEPTED']:
            others_folders = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid!=folder_uuid).\
                filter(models.PreRegistration.child_uuid==exist_folder.child_uuid).\
                all()
            for folder in others_folders:
                folder.status = models.PreRegistrationStatusType.REFUSED
                folder.refused_date = datetime.now()
                db.commit()

        return exist_folder

    @classmethod
    def add_tracking_case(cls, db: Session, obj_in: schemas.TrackingCase, interaction_type: str, performed_by_uuid: str) -> Optional[schemas.PreregistrationDetails]:
        exist_folder = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == obj_in.preregistration_uuid).first()
        if not exist_folder:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        interaction = models.TrackingCase(
            uuid=str(uuid.uuid4()),
            preregistration_uuid=exist_folder.uuid,
            interaction_type=interaction_type,
            details=obj_in.details.root
        )
        db.add(interaction)
        db.commit()

        after_changes = schemas.TrackingCaseMini.model_validate(interaction).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="TrackingCase",
            entity_id=interaction.uuid,
            action="CREATE",
            before_changes={},
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return exist_folder

    @classmethod
    def update(cls, db: Session, obj_in: schemas.PreregistrationUpdate, performed_by_uuid: str) -> models.Child:

        preregistration = db.query(models.PreRegistration).\
            filter(models.PreRegistration.uuid==obj_in.uuid).\
            first()

        # Before update the data
        before_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        obj_in.nurseries = set(obj_in.nurseries)
        nurseries = crud.nursery.get_by_uuids(db, obj_in.nurseries)
        if len(obj_in.nurseries) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        # Child information update
        child = db.query(models.Child).filter(models.Child.uuid==obj_in.child.uuid).first()
        if not child:
            raise HTTPException(status_code=404, detail=__("child-not-found"))

        child.firstname=obj_in.child.firstname
        child.lastname=obj_in.child.lastname
        child.gender=obj_in.child.gender
        child.birthdate=obj_in.child.birthdate
        child.birthplace=obj_in.child.birthplace

        # Contract information update
        contract = db.query(models.PreContract).filter(models.PreContract.uuid == obj_in.pre_contract.uuid).first()
        if not contract:
            raise HTTPException(status_code=404, detail=__("contract-not-found"))

        contract.begin_date=obj_in.pre_contract.begin_date,
        contract.end_date=obj_in.pre_contract.end_date,
        contract.typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)

        # Delete the old parents data
        db.query(models.ParentGuest).\
            filter(models.ParentGuest.child_uuid==child.uuid).\
            delete()

        db.commit()

        for pg in obj_in.parents:

            parent_guest = models.ParentGuest(
                uuid=str(uuid.uuid4()),
                link=pg.link,
                firstname=pg.firstname,
                lastname=pg.lastname,
                birthplace=pg.birthplace,
                fix_phone=pg.fix_phone,
                phone=pg.phone,
                email=pg.email,
                recipient_number=pg.recipient_number,
                zip_code=pg.zip_code,
                city=pg.city,
                country=pg.country,
                profession=pg.profession,
                annual_income=pg.annual_income,
                company_name=pg.company_name,
                has_company_contract=pg.has_company_contract,
                dependent_children=pg.dependent_children,
                disabled_children=pg.disabled_children,
                child_uuid=child.uuid
            )
            db.add(parent_guest)

        code = cls.code_unicity(code=generate_slug(f"{child.firstname} {child.lastname}"), db=db)
        for nursery_uuid in obj_in.nurseries:
            preregistration = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid==obj_in.uuid).\
                filter(models.PreRegistration.nursery_uuid==nursery_uuid).\
                first()
            if preregistration:
                preregistration.code = code
                preregistration.note = obj_in.note if obj_in.note else preregistration.note
                db.commit()

        db.commit()
        db.refresh(child)

        # After update the data
        after_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=preregistration.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return child
    @classmethod
    def update_pre_registration(cls, db: Session, obj_in: schemas.PreregistrationUpdate) -> models.Child:

        preregistration = db.query(models.PreRegistration).\
            filter(models.PreRegistration.uuid==obj_in.uuid).\
            first()

        # Before update the data
        before_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        obj_in.nurseries = set(obj_in.nurseries)
        nurseries = crud.nursery.get_by_uuids(db, obj_in.nurseries)
        if len(obj_in.nurseries) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        # Child information update
        child = db.query(models.Child).filter(models.Child.uuid==obj_in.child.uuid).first()
        if not child:
            raise HTTPException(status_code=404, detail=__("child-not-found"))

        child.firstname=obj_in.child.firstname
        child.lastname=obj_in.child.lastname
        child.gender=obj_in.child.gender
        child.birthdate=obj_in.child.birthdate
        child.birthplace=obj_in.child.birthplace

        # Contract information update
        contract = db.query(models.PreContract).filter(models.PreContract.uuid == obj_in.pre_contract.uuid).first()
        if not contract:
            raise HTTPException(status_code=404, detail=__("contract-not-found"))

        contract.begin_date=obj_in.pre_contract.begin_date,
        contract.end_date=obj_in.pre_contract.end_date,
        contract.typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)

        # Delete the old parents data
        db.query(models.ParentGuest).\
            filter(models.ParentGuest.child_uuid==child.uuid).\
            delete()

        db.commit()

        for pg in obj_in.parents:

            parent_guest = models.ParentGuest(
                uuid=str(uuid.uuid4()),
                link=pg.link,
                firstname=pg.firstname,
                lastname=pg.lastname,
                birthplace=pg.birthplace,
                fix_phone=pg.fix_phone,
                phone=pg.phone,
                email=pg.email,
                recipient_number=pg.recipient_number,
                zip_code=pg.zip_code,
                city=pg.city,
                country=pg.country,
                profession=pg.profession,
                annual_income=pg.annual_income,
                company_name=pg.company_name,
                has_company_contract=pg.has_company_contract,
                dependent_children=pg.dependent_children,
                disabled_children=pg.disabled_children,
                child_uuid=child.uuid
            )
            db.add(parent_guest)

        code = cls.code_unicity(code=generate_slug(f"{child.firstname} {child.lastname}"), db=db)
        for nursery_uuid in obj_in.nurseries:
            preregistration = db.query(models.PreRegistration).\
                filter(models.PreRegistration.uuid==obj_in.uuid).\
                filter(models.PreRegistration.nursery_uuid==nursery_uuid).\
                first()
            if preregistration:
                preregistration.code = code
                preregistration.note = obj_in.note if obj_in.note else preregistration.note
                db.commit()

        db.commit()
        db.refresh(child)

        # After update the data
        after_changes = schemas.PreregistrationDetails.model_validate(preregistration).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="PreRegistration",
            entity_id=preregistration.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            after_changes=convert_dates_to_strings(after_changes)
        )

        return child

    @classmethod
    def get_child_by_uuid(cls, db: Session, uuid: str) -> Optional[schemas.ChildDetails]:
        return db.query(models.Child).filter(models.Child.uuid == uuid).first()
    
    @classmethod
    def get_child_by_uuids(cls, db: Session, uuid_tab: list[str]) -> Optional[list[schemas.ChildDetails]]:
        return db.query(models.Child).filter(models.Child.uuid.in_(uuid_tab)).all()

    @staticmethod
    def determine_cmg(db: Session, dependent_children: int, family_type: models.FamilyType,
                      annual_income: float, birthdate: date, quote_uuid: str) -> Optional[models.QuoteCMG]:

        cmg_dependent_children = dependent_children
        if dependent_children < 1:
            cmg_dependent_children = 1
        if dependent_children > 4:
            cmg_dependent_children = 4

        cmg_amount_range: models.CMGAmountRange = db.query(models.CMGAmountRange).filter(
            models.CMGAmountRange.number_children == cmg_dependent_children).filter(
            models.CMGAmountRange.family_type == family_type).first()
        if not cmg_amount_range:
            return None

        today = date.today()
        child_age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

        print(f"child_age {child_age}")
        if child_age < 0:
            child_age = 0

        cmg_amount_obj = db.query(models.CMGAmount).filter(models.CMGAmount.child_age_lower <= child_age).filter(
            models.CMGAmount.child_age_upper > child_age).first()
        if not cmg_amount_obj:
            return None

        cmg_amount = 0
        band_number = 0
        if annual_income <= cmg_amount_range.lower:
            band_number = 1
            cmg_amount = cmg_amount_obj.tranche_1_amount
        elif annual_income > cmg_amount_range.lower and annual_income <= cmg_amount_range.upper:
            band_number = 2
            cmg_amount = cmg_amount_obj.tranche_2_amount
        elif annual_income > cmg_amount_range.upper:
            band_number = 3
            cmg_amount = cmg_amount_obj.tranche_3_amount

        q_cmg: models.QuoteCMG = db.query(models.QuoteCMG).filter(models.QuoteCMG.quote_uuid == quote_uuid).first()
        if q_cmg:
            q_cmg.amount = cmg_amount
            q_cmg.family_type = family_type
            q_cmg.number_children = dependent_children
            q_cmg.annual_income = annual_income
            q_cmg.band_number = band_number
        else:
            q_cmg = models.QuoteCMG(
                uuid=str(uuid.uuid4()),
                amount=cmg_amount,
                family_type=family_type,
                number_children=dependent_children,
                annual_income=annual_income,
                band_number=band_number,
                quote_uuid=quote_uuid
            )
            db.add(q_cmg)
        return q_cmg

    def generate_quote(self, db: Session, preregistration_uuid):
        exist_preregistration = self.get_by_uuid(db, preregistration_uuid)
        if not exist_preregistration:
            return

        nursery_holiday_days: list[models.NuseryHoliday] = db.query(models.NuseryHoliday).filter(models.NuseryHoliday.nursery_uuid == exist_preregistration.nursery_uuid).all()
        nursery_closing_periods: list[models.NurseryCloseHour] = db.query(models.NurseryCloseHour).filter(models.NurseryCloseHour.nursery_uuid == exist_preregistration.nursery_uuid).all()
        holiday_days = [
            date(year, holiday_day.month, holiday_day.day) for holiday_day in nursery_holiday_days for year in
            range(exist_preregistration.pre_contract.begin_date.year,
                  exist_preregistration.pre_contract.end_date.year + 1)
        ]
        closing_periods = [
            (date(year, nursery_closing_period.start_month, nursery_closing_period.start_day),
             date(year if nursery_closing_period.end_month >= nursery_closing_period.start_month else year + 1,
                  nursery_closing_period.end_month, nursery_closing_period.end_day)) for nursery_closing_period in
            nursery_closing_periods
            for year in range(exist_preregistration.pre_contract.begin_date.year,
                              exist_preregistration.pre_contract.end_date.year + 1)
        ]

        quote: models.Quote = db.query(models.Quote).filter(
            models.Quote.preregistration_uuid == exist_preregistration.uuid).filter(
            models.Quote.nursery_uuid == exist_preregistration.nursery_uuid).first()

        quote_setting: models.QuoteSetting = db.query(models.QuoteSetting).filter(
            models.QuoteSetting.is_default == True).first()

        if quote:
            # paying_parent: Optional[models.ParentGuest] = quote.parent_guest

            quote_engine_res = QuoteEngine(
                contract_start_date=exist_preregistration.pre_contract.begin_date,
                contract_end_date=exist_preregistration.pre_contract.end_date,
                rate_per_hour=quote.hourly_rate,
                planning_weeks=exist_preregistration.pre_contract.typical_weeks,
                holiday_days=holiday_days,
                closing_periods=closing_periods,
                adaptation_type=quote.adaptation_type,
                adaptation_package_costs=quote.adaptation_package_costs,
                adaptation_package_days=quote.adaptation_package_days,
                adaptation_hourly_rate=quote.adaptation_hourly_rate,
                adaptation_hours_number=quote.adaptation_hours_number,
                has_deposit=quote.has_deposit,
                deposit_type=quote.deposit_type,
                deposit_percentage=quote.deposit_percentage,
                deposit_value=quote.deposit_value,
                has_registration_fee=quote.has_registration_fee,
                registration_fee=quote.registration_fee,
                last_special_month=quote_setting.last_special_month,
                min_days_for_last_special_month=quote_setting.min_days_for_last_special_month,
                invoice_timing=quote_setting.invoicing_time
            )
            db.query(models.QuoteTimetable).filter(models.QuoteTimetable.quote_uuid==quote.uuid).delete()
        else:
            paying_parent: Optional[
                models.ParentGuest] = exist_preregistration.child.paying_parent if exist_preregistration.child.paying_parent else None

            if not paying_parent:
                return
            parent_guest_uuid = paying_parent.uuid

            dependent_children = paying_parent.dependent_children
            dependent_children_req = dependent_children if dependent_children else dependent_children + 1
            annual_income = paying_parent.annual_income

            average_days_per_week = sum(
                [
                    1 if day else 0 for typical_week in exist_preregistration.pre_contract.typical_weeks for day in
                    typical_week
                ]
            ) / len(exist_preregistration.pre_contract.typical_weeks)

            hours_per_week = sum([(int(time_slot["to_time"].split(":")[0]) - int(time_slot["from_time"].split(":")[0])) + (
                    int(time_slot["to_time"].split(":")[1]) - int(time_slot["from_time"].split(":")[1])) / 60 for
                                  typical_week in
                                  exist_preregistration.pre_contract.typical_weeks for day in typical_week for time_slot in
                                  day]) / len(
                exist_preregistration.pre_contract.typical_weeks) / average_days_per_week

            hourly_rate = 0
            for hourly_rate_range in quote_setting.hourly_rate_ranges:
                if hours_per_week < hourly_rate_range.number_of_hours:
                    hourly_rate = hourly_rate_range.hourly_rate

            quote_engine_res = QuoteEngine(
                contract_start_date=exist_preregistration.pre_contract.begin_date,
                contract_end_date=exist_preregistration.pre_contract.end_date,
                rate_per_hour=hourly_rate,
                planning_weeks=exist_preregistration.pre_contract.typical_weeks,
                holiday_days=holiday_days,
                closing_periods=closing_periods,
                adaptation_type=models.AdaptationType.PACKAGE,
                adaptation_package_costs=quote_setting.adaptation_package_costs,
                adaptation_package_days=quote_setting.adaptation_package_days,
                adaptation_hourly_rate=quote_setting.adaptation_hourly_rate,
                adaptation_hours_number=quote_setting.adaptation_hours_number,
                has_deposit=quote_setting.has_deposit,
                deposit_type=quote_setting.deposit_type,
                deposit_percentage=quote_setting.deposit_percentage,
                deposit_value=quote_setting.deposit_value,
                has_registration_fee=quote_setting.has_registration_fee,
                registration_fee=quote_setting.registration_fee,
                last_special_month=quote_setting.last_special_month,
                min_days_for_last_special_month=quote_setting.min_days_for_last_special_month,
                invoice_timing=quote_setting.invoicing_time
            )

            quote = models.Quote(
                uuid=str(uuid.uuid4()),
                title="",
                nursery_uuid=exist_preregistration.nursery_uuid,
                preregistration_uuid=exist_preregistration.uuid,
                parent_guest_uuid=parent_guest_uuid,
                child_uuid=exist_preregistration.child_uuid,
                pre_contract_uuid=exist_preregistration.pre_contract_uuid,
                hourly_rate=hourly_rate,
                has_registration_fee=quote_setting.has_registration_fee,
                registration_fee=quote_setting.registration_fee,
                has_deposit=quote_setting.has_deposit,
                deposit_type=quote_setting.deposit_type,
                deposit_percentage=quote_setting.deposit_percentage,
                deposit_value=quote_setting.deposit_value,
                adaptation_type=models.AdaptationType.PACKAGE,
                adaptation_package_costs=quote_setting.adaptation_package_costs,
                adaptation_package_days=quote_setting.adaptation_package_days,
                adaptation_hourly_rate=quote_setting.adaptation_hourly_rate,
                adaptation_hours_number=quote_setting.adaptation_hours_number,
                quote_setting_uuid=quote_setting.uuid
            )
            db.add(quote)

            determine_cmgs = self.determine_cmg(db, dependent_children_req, models.FamilyType.SINGLE_PARENT,
                                                annual_income, exist_preregistration.child.birthdate, quote.uuid)
            print(f"determine_cmgs {determine_cmgs}")

        res_generation = quote_engine_res.generate_quote()
        quote.first_month_cost = res_generation.fpm_first_month_cost
        quote.monthly_cost = res_generation.mm_monthly_cost
        quote.total_cost = res_generation.total

        quote.monthly_billed_hours = res_generation.monthly_billed_hours
        quote.smoothing_months = res_generation.nfl_smoothing_month_count
        quote.weeks_in_smoothing = res_generation.weeks_in_smoothing
        quote.deductible_weeks = res_generation.deductible_weeks
        quote.monthly_cost = res_generation.mm_monthly_cost
        quote.total_closing_days = res_generation.sjfd_closing_days

        for quote_timetable_res in res_generation.quote_timetables:
            quote_timetable = models.QuoteTimetable(
                uuid=str(uuid.uuid4()),
                date_to=quote_timetable_res.billing_date,
                invoicing_period_start=quote_timetable_res.billing_period_start,
                invoicing_period_end=quote_timetable_res.billing_period_end,
                amount=quote_timetable_res.amount,
                quote_uuid=quote.uuid
            )
            db.add(quote_timetable)
            for item in quote_timetable_res.items:
                if item.quote_type == models.QuoteTimetableItemType.ADAPTATION:
                    title = "item-adaptation"
                elif item.quote_type == models.QuoteTimetableItemType.DEPOSIT:
                    title = "item-deposit"
                elif item.quote_type == models.QuoteTimetableItemType.INVOICE:
                    title = "item-invoice"
                elif item.quote_type == models.QuoteTimetableItemType.REGISTRATION:
                    title = "item-registration"
                else:
                    title = item.quote_type.title()

                quote_timetable_item = models.QuoteTimetableItem(
                    uuid=str(uuid.uuid4()),
                    title_fr=__(title, "fr"),
                    title_en=__(title, "en"),
                    type=item.quote_type,
                    amount=item.amount,
                    quote_timetable_uuid=quote_timetable.uuid,
                    total_hours=item.total_hours,
                    unit_price=item.unit_price
                )
                db.add(quote_timetable_item)
        db.commit()

    @classmethod
    def create(cls, db: Session, obj_in: schemas.PreregistrationCreate, background_task: BackgroundTasks, current_user_uuid: str = None) -> models.Child:

        obj_in.nurseries = set(obj_in.nurseries)
        nurseries = crud.nursery.get_by_uuids(db, obj_in.nurseries, current_user_uuid)
        if len(obj_in.nurseries) != len(nurseries):
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        child = models.Child(
            uuid=str(uuid.uuid4()),
            firstname=obj_in.child.firstname,
            lastname=obj_in.child.lastname,
            gender=obj_in.child.gender,
            birthdate=obj_in.child.birthdate,
            birthplace=obj_in.child.birthplace,
            added_by_uuid=current_user_uuid
        )
        db.add(child)
        db.flush()
        contract = models.PreContract(
            uuid=str(uuid.uuid4()),
            begin_date=obj_in.pre_contract.begin_date,
            end_date=obj_in.pre_contract.end_date,
            typical_weeks=jsonable_encoder(obj_in.pre_contract.typical_weeks)
        )
        db.add(contract)
        db.flush()

        child.pre_contract_uuid = contract.uuid

        for pg in obj_in.parents:
            parent_guest = models.ParentGuest(
                uuid=str(uuid.uuid4()),
                link=pg.link,
                firstname=pg.firstname,
                lastname=pg.lastname,
                birthplace=pg.birthplace,
                fix_phone=pg.fix_phone,
                phone=pg.phone,
                email=pg.email,
                recipient_number=pg.recipient_number,
                zip_code=pg.zip_code,
                city=pg.city,
                country=pg.country,
                profession=pg.profession,
                annual_income=pg.annual_income,
                company_name=pg.company_name,
                has_company_contract=pg.has_company_contract,
                dependent_children=pg.dependent_children,
                disabled_children=pg.disabled_children,
                child_uuid=child.uuid
            )
            db.add(parent_guest)
            db.flush()

        preregistration_uuids: list[str] = []
        code = cls.code_unicity(code=generate_slug(f"{child.firstname} {child.lastname}"), db=db)
        for nursery_uuid in obj_in.nurseries:
            new_preregistration = models.PreRegistration(
                uuid=str(uuid.uuid4()),
                code=code,
                child_uuid=child.uuid,
                nursery_uuid=nursery_uuid,
                pre_contract_uuid=contract.uuid,
                note=obj_in.note,
                status=models.PreRegistrationStatusType.PENDING
            )
            db.add(new_preregistration)
            db.flush()

            preregistration_uuids.append(new_preregistration.uuid)

        db.commit()
        db.refresh(child)

        for preregistration_uuid in preregistration_uuids:
            background_task.add_task(cls.generate_quote, cls, db, preregistration_uuid)

        return child

    @classmethod
    def get_by_code(cls, db: Session, code: str) -> Optional[schemas.PreregistrationDetails]:
        return db.query(models.PreRegistration).filter(models.PreRegistration.code == code).first()


    def get_many(self,
        db,
        nursery_uuid,
        status,
        begin_date,
        end_date,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = None,
        order_field: Optional[str] = None,
        keyword: Optional[str] = None,
        tag_uuid=None,
    ):
        record_query = db.query(models.PreRegistration).filter(models.PreRegistration.nursery_uuid==nursery_uuid)
        if status:
            record_query = record_query.filter(models.PreRegistration.status==status)

        if begin_date and end_date:
            record_query = record_query.filter(models.PreRegistration.date_added.between(begin_date, end_date))

        if keyword:
            record_query = record_query.filter(models.PreRegistration.child.has(
                or_(
                    models.Child.firstname.ilike('%' + str(keyword) + '%'),
                    models.Child.lastname.ilike('%' + str(keyword) + '%'),
                ))
            )
        if tag_uuid:
            TagAlias = aliased(models.Tags)
            TagElementAlias = aliased(models.TagElement)
            record_query = record_query.join(
                TagElementAlias, models.PreRegistration.uuid == TagElementAlias.element_uuid
            ).join(
                TagAlias, TagElementAlias.tag_uuid == TagAlias.uuid
            ).filter(
                TagAlias.type == models.TagTypeEnum.PRE_ENROLLMENT,
                TagAlias.uuid == tag_uuid,
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(models.PreRegistration, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(models.PreRegistration, order_field).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.PreRegistrationList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )
    
    def get_transmission(
        self,
        child_uuid: str,
        db:Session,
        nursery_uuid:str,
        date:date = None
    ):
        child = db.query(models.Child).filter(models.Child.uuid == child_uuid).first()

        if date:
            # Step 2: Load filtered relations and assign to the child object
            child.meals = db.query(models.Meal).\
                filter(models.Meal.child_uuid == child.uuid, models.Meal.date_added == date).\
                filter(models.Meal.nursery_uuid == nursery_uuid).\
                all()
            child.activities = db.query(models.ChildActivity).\
                filter(models.ChildActivity.child_uuid == child.uuid, models.ChildActivity.date_added == date).\
                filter(models.ChildActivity.nursery_uuid == nursery_uuid).\
                all()
            child.naps = db.query(models.Nap).\
                filter(models.Nap.child_uuid == child.uuid, models.Nap.date_added == date).\
                filter(models.Nap.nursery_uuid == nursery_uuid).\
                all()
            child.health_records = db.query(models.HealthRecord).\
                filter(models.HealthRecord.child_uuid == child.uuid, models.HealthRecord.date_added == date).\
                filter(models.HealthRecord.nursery_uuid == nursery_uuid).\
                all()
            child.hygiene_changes = db.query(models.HygieneChange).\
                filter(models.HygieneChange.child_uuid == child.uuid, models.HygieneChange.date_added == date).\
                filter(models.HygieneChange.nursery_uuid == nursery_uuid).\
                all()
            child.observations = db.query(models.Observation).\
                filter(models.Observation.child_uuid == child.uuid, models.Observation.date_added == date).\
                filter(models.Observation.nursery_uuid == nursery_uuid).\
                all()
            media_uuids = [i.media_uuid for i in db.query(models.children_media).filter(models.children_media.c.child_uuid==child_uuid).all()]
            child.media = db.query(models.Media).\
                filter(models.Media.uuid.in_(media_uuids), models.Media.date_added == date).\
                all()

        return child

    def get_tracking_cases(self,
        db,
        preregistration_uuid,
        interaction_type,
        page: int = 1,
        per_page: int = 30,
        order: Optional[str] = 'desc',
        order_field: Optional[str] = 'date_added',
        # keyword: Optional[str] = None,
    ):
        record_query = db.query(models.TrackingCase).filter(models.TrackingCase.preregistration_uuid==preregistration_uuid)
        if interaction_type:
            record_query = record_query.filter(models.TrackingCase.interaction_type==interaction_type)

        # if keyword:
        #     record_query = record_query.filter(
        #         or_(
        #             models.Child.firstname.ilike('%' + str(keyword) + '%'),
        #             models.Child.lastname.ilike('%' + str(keyword) + '%'),
        #         )
        #     )


        if order == "asc":
            record_query = record_query.order_by(getattr(models.TrackingCase, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(models.TrackingCase, order_field).desc())

        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return schemas.TrackingCaseList(
            total=total,
            pages=math.ceil(total / per_page),
            per_page=per_page,
            current_page=page,
            data=record_query
        )


    def transfer(self, db, uuid, obj_in: schemas.TransferPreRegistration, current_user_uuid: str):
        preregistration = db.query(models.PreRegistration).filter(models.PreRegistration.uuid == uuid).first()
        if not preregistration:
            raise HTTPException(status_code=404, detail=__("folder-not-found"))

        nursery = crud.nursery.get_by_uuid(db, obj_in.nursery_uuid)
        if not nursery or nursery.owner_uuid != current_user_uuid:
            raise HTTPException(status_code=404, detail=__("nursery-not-found"))

        if preregistration.nursery_uuid == obj_in.nursery_uuid:
            raise HTTPException(status_code=400, detail=__("folder-already-in-nursery"))

        preregistration.nursery_uuid = nursery.uuid
        db.commit()
        return preregistration

    @classmethod
    def code_unicity(cls, code: str, db: Session):
        while cls.get_by_code(db, code):
            slug = f"{code}-{generate_code(length=4)}"
            return cls.code_unicity(slug, db)
        return code

    def is_active(self, user: models.Administrator) -> bool:
        return user.status == models.UserStatusType.ACTIVED


preregistration = CRUDPreRegistration(models.PreRegistration)


