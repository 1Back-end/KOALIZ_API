from datetime import datetime
import math
from typing import Any, Dict, Optional
import uuid
from fastapi.encoders import jsonable_encoder

from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased

from app.main import crud, models
from app.main import schemas
from app.main.crud.base import CRUDBase
from app.main.models import Contract,AbsenceStatusEnum
from app.main.schemas import ContractCreate, ContractUpdate, ContractMini, ContractList
from app.main.utils.helper import convert_dates_to_strings


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):

    @classmethod
    def create(self, db: Session, obj_in: ContractCreate, performed_by_uuid: str = None) -> Contract:
        db_obj = Contract(
            uuid=str(uuid.uuid4()),
            begin_date=obj_in.begin_date,
            end_date=obj_in.end_date,
            type=obj_in.type,
            annual_income=obj_in.annual_income,
            owner_uuid=performed_by_uuid,
            nursery_uuid=obj_in.nursery_uuid,
            has_company_contract=obj_in.has_company_contract,
            typical_weeks=obj_in.typical_weeks
        )
        db.add(db_obj)
        db.commit()

        after_changes = schemas.Contract.model_validate(db_obj).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="Contract",
            entity_id=db_obj.uuid,
            action="CREATE",
            before_changes={},
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        db.refresh(db_obj)
        return db_obj
    
    @classmethod
    def get_contract_by_uuid(cls, db: Session, uuid: str) -> Optional[Contract]:
        return db.query(Contract).\
            filter(Contract.uuid == uuid, or_(Contract.status != "DELETED", Contract.status.is_(None))).\
                first()
    
    @classmethod
    def get_client_account_by_uuid(cls, db: Session, uuid: str) -> Optional[models.ClientAccount]:
        return db.query(models.ClientAccount).\
            filter(models.ClientAccount.uuid == uuid).\
                first()
    
    @classmethod
    def update(cls, db: Session,obj_in: ContractUpdate, performed_by_uuid: str) -> ContractMini:
        contract = cls.get_contract_by_uuid(db, obj_in.uuid)

        # Create the log tracking
        before_changes = schemas.Contract.model_validate(contract).model_dump()

        # contract.begin_date = obj_in.begin_date if obj_in.begin_date else contract.begin_date
        # contract.end_date = obj_in.end_date if obj_in.end_date else contract.end_date
        # contract.type = obj_in.type if obj_in.type else contract.type
        # contract.annual_income = obj_in.annual_income if obj_in.annual_income else contract.annual_income
        # contract.caution = obj_in.caution if obj_in.caution else contract.caution
        # contract.reference = obj_in.reference if obj_in.reference else contract.reference
        # contract.note = obj_in.note if obj_in.note else contract.note
        contract.typical_weeks = obj_in.typical_weeks if obj_in.typical_weeks else contract.typical_weeks
        
        # if obj_in.has_company_contract == False:
        #     contract.has_company_contract = False
        # if obj_in.has_company_contract == True:
        #     contract.has_company_contract = True

        if obj_in.status in ['RUPTURED']:
            contract.date_of_rupture = datetime.now()
            contract.status = obj_in.status if obj_in.status else contract.status

        if obj_in.status in ['TERMINATED']:
            contract.date_of_termination = datetime.now()
            contract.status = obj_in.status if obj_in.status else contract.status

        if obj_in.status in ['ACCEPTED']:
            contract.date_of_acceptation = datetime.now()
            contract.status = obj_in.status if obj_in.status else contract.status

        db.commit()
        db.refresh(contract)

        after_changes = schemas.Contract.model_validate(contract).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="Contract",
            entity_id=contract.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return contract
    @classmethod
    def update_client_account(cls, db: Session,obj_in: schemas.ClientAccountContractUpdate, performed_by_uuid: str) -> ContractMini:
        client_account = cls.get_client_account_by_uuid(db, obj_in.uuid)

        # Create the log tracking
        before_changes = schemas.ClientAccountContractSchema.model_validate(client_account).model_dump()

        client_account.name = obj_in.name if obj_in.name else client_account.name
        client_account.bic = obj_in.bic if obj_in.bic else client_account.bic
        client_account.rum = obj_in.rum if obj_in.rum else client_account.rum
        client_account.iban = obj_in.iban if obj_in.iban else client_account.iban

        db.commit()
        db.refresh(client_account)

        after_changes = schemas.Contract.model_validate(client_account).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="ClientAccount",
            entity_id=client_account.uuid,
            action="UPDATED",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return client_account
    @classmethod
    def extend_the_contract(cls, db: Session,obj_in: schemas.ProlongeContract, performed_by_uuid: str) -> ContractMini:
        contract = cls.get_contract_by_uuid(db, obj_in.uuid)

        child = db.query(models.Child).filter(models.Child.uuid == obj_in.child_uuid).first()

        # Create the log tracking
        before_changes = schemas.Contract.model_validate(contract).model_dump()

        contract.end_date = obj_in.end_date

        db.commit()
        db.refresh(contract)

        crud.child_planning.insert_planning(db=db, child=child, nursery=contract.nursery)

        after_changes = schemas.Contract.model_validate(contract).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="Contract",
            entity_id=contract.uuid,
            action="UPDATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return contract
    
    @classmethod
    def publish_the_contract(cls, db: Session,contract_uuid: str, performed_by_uuid: str) -> ContractMini:
        exist_contract = cls.get_contract_by_uuid(db, contract_uuid)

        # Create the log tracking
        before_changes = schemas.Contract.model_validate(exist_contract).model_dump()

        contract = models.Contract(
            uuid=str(uuid.uuid4()),
            begin_date=exist_contract.begin_date,
            end_date=exist_contract.end_date,
            typical_weeks=exist_contract.typical_weeks,
            type=exist_contract.type,
            nursery_uuid=exist_contract.nursery_uuid,
            status=exist_contract.status,
            owner_uuid=exist_contract.owner_uuid
        )
        db.add(contract)
        db.flush()

        after_changes = schemas.Contract.model_validate(contract).model_dump()

        crud.audit_log.create(
            db=db,
            entity_type="Contract",
            entity_id=contract.uuid,
            action="DUPLICATE",
            before_changes=convert_dates_to_strings(before_changes),
            performed_by_uuid=performed_by_uuid,
            after_changes=convert_dates_to_strings(after_changes)
        )

        return contract
    
    @classmethod
    def delete(cls,db:Session, uuids:list[str]) -> ContractMini:
        db.query(Contract).filter(Contract.uuid.in_(uuids)).delete()
        db.commit()
    
    @classmethod
    def soft_delete(cls,db:Session, uuids:list[str], performed_by_uuid: str):
        contract_tab = db.query(Contract).\
            filter(Contract.uuid.in_(uuids),Contract.status!=AbsenceStatusEnum.DELETED)\
                .all()
        for contract in contract_tab:
            contract.status = AbsenceStatusEnum.DELETED
            db.commit()

            # Create the log tracking
            before_changes = schemas.Contract.model_validate(contract).model_dump()
            crud.audit_log.create(
                db=db,
                entity_type="Contract",
                entity_id=contract.uuid,
                action="DELETED",
                before_changes=convert_dates_to_strings(before_changes),
                performed_by_uuid=performed_by_uuid,
                after_changes={}
            )

    

    @classmethod
    def get_multi(
        cls,
        db:Session,
        page:int = 1,
        per_page:int = 30,
        order:Optional[str] = "desc",
        tag_uuid:Optional[str] = None,
        nursery_uuid:Optional[str] = None,
        child_uuid:Optional[str] = None,
        order_field:Optional[str] = 'date_added',
        keyword:Optional[str]= None,
        status:Optional[str]= None,
        owner_uuid: Optional[str] = None,
    ):
        record_query = db.query(Contract).filter(or_(Contract.status != "DELETED", Contract.status.is_(None))).\
            filter(Contract.nursery_uuid == nursery_uuid)
            # filter(Contract.nursery.has(models.Nursery.owner_uuid == owner_uuid))


        if keyword:
            record_query = record_query.filter(
                or_(
                    Contract.note.ilike('%' + str(keyword) + '%'),
                    Contract.reference.ilike('%' + str(keyword) + '%'),
                    Contract.child.has(
                        or_(
                            models.Child.firstname.ilike('%' + str(keyword) + '%'),
                            models.Child.lastname.ilike('%' + str(keyword) + '%'),
                        )
                    ),
                    Contract.parents.any(
                        or_(
                            models.Parent.firstname.ilike('%' + str(keyword) + '%'),
                            models.Parent.lastname.ilike('%' + str(keyword) + '%'),
                        )
                    )
                )
            )

        if status:
            record_query = record_query.filter(Contract.status == status)
        
        if child_uuid:
            record_query = record_query.filter(Contract.child.has(models.Child.uuid==child_uuid))
        
        if nursery_uuid:
            record_query = record_query.filter(Contract.nursery_uuid == nursery_uuid)

        if tag_uuid:
            TagAlias = aliased(models.Tags)
            TagElementAlias = aliased(models.TagElement)
            record_query = record_query.join(
                TagElementAlias, Contract.uuid == TagElementAlias.element_uuid
            ).join(
                TagAlias, TagElementAlias.tag_uuid == TagAlias.uuid
            ).filter(
                TagAlias.type == models.TagTypeEnum.CONTRACT,
                TagAlias.uuid == tag_uuid,
            )

        if order == "asc":
            record_query = record_query.order_by(getattr(Contract, order_field).asc())
        else:
            record_query = record_query.order_by(getattr(Contract, order_field).desc())


        total = record_query.count()
        record_query = record_query.offset((page - 1) * per_page).limit(per_page)

        return ContractList(
            total = total,
            pages = math.ceil(total/per_page),
            per_page = per_page,
            current_page =page,
            data =record_query
        )

contract = CRUDContract(Contract)
