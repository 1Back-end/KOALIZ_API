import uuid
from fastapi import APIRouter, Body, Depends, HTTPException
from typing import List, Any
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.main.core.i18n import __
from app.main.core import dependencies
from app.main import models, schemas
from app.main.models.message import MessageType
from app.main.utils.helper import convert_dates_to_strings
from app.main.utils.notification_client import notificationPublisher


router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/unread/count")
def unread_message_count(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: any = Depends(dependencies.TokenRequired(roles=None))
) -> Any:

    """ Unread messages count """

    notification_count = db.query(models.Message)\
        .filter(and_(models.Message.is_read != True, 
                     models.Message.sender_uuid == current_user.uuid,            
                     models.Message.status != models.MessageStatusEnum.DELETED
                    )
                )\
                .count()

    return notification_count

@router.get("/conversations", response_model=List[schemas.Conversation])
def fetch_all_conversations(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
):

    ''' Recupérer la liste des messages de l'utilisateur connecté '''

    conds = [
        models.Conversation.sender_uuid == current_user.uuid,
        models.Conversation.receiver_uuid == current_user.uuid,
        models.Conversation.status != models.MessageStatusEnum.DELETED
    ]

    conversations = db.query(models.Conversation)\
        .filter(or_(*conds[:1]), conds[2])\
        .order_by(models.Conversation.last_sending_date.desc())\
        .all()

    for conv in conversations:
        if current_user.uuid != conv.last_sender_uuid:
            conv.is_read = True
            db.commit()
        else:
            conv.is_read = conv.is_read
            db.commit()

    return conversations

@router.post("", response_model=schemas.Message)
def send_message(
    *,
    db: Session = Depends(dependencies.get_db),
    receiver_uuid: str = Body(...),
    content: str = Body(...),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Send message '''


    exist_conversation: models.Conversation = db.query(models.Conversation)\
            .filter(
                or_(
                    and_(models.Conversation.sender_uuid == current_user.uuid, models.Conversation.receiver_uuid == receiver_uuid),
                    and_(models.Conversation.sender_uuid == receiver_uuid, models.Conversation.receiver_uuid == current_user.uuid),
                ),
                models.Conversation.status != models.MessageStatusEnum.DELETED
            )\
            .first()
    
    exist_receiver = db.query(models.Parent).\
                        filter(models.Parent.uuid == receiver_uuid).\
                first() \
            or\
                    db.query(models.Administrator).\
                            filter(models.Administrator.uuid == receiver_uuid).\
                                first()
    
    if not exist_receiver:
        raise HTTPException(status_code=404, detail=__("receiver-not-found"))

    if not exist_conversation:
        exist_conversation = models.Conversation(
            uuid=str(uuid.uuid4()),
            sender_uuid=current_user.uuid,
            receiver_uuid=receiver_uuid,
            last_message=content,
            is_read=False,
            last_sender_uuid=current_user.uuid
        )
        db.add(exist_conversation)
        db.commit()

        # Notification
        notification = schemas.Conversation.model_validate(exist_conversation).model_dump()
        conversation_schema = convert_dates_to_strings(notification)
        # notificationPublisher.publish(channel=receiver_uuid, type="EVENT_NEW_CONVERSATION", data= conversation_schema)

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=content,
            message_type=MessageType.MESSAGE,
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    else:
        exist_conversation.last_message = content
        exist_conversation.last_sender_uuid = current_user.uuid


        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=content,
            message_type=MessageType.MESSAGE,
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    db.add(new_message)
    db.commit()

    # Get the messsage schema
    message = schemas.Message.model_validate(new_message).model_dump()
    message_schema = convert_dates_to_strings(message)
    print(message_schema)

    # Notification
    # notificationPublisher.publish(channel="{}-{}".format(exist_conversation.sender_uuid, exist_conversation.receiver_uuid), type="EVENT_NEW_MESSAGE_IN_CONVERSATION", data = message_schema)

    return new_message


@router.post("/file", response_model=schemas.Message)
def send_message_file(
    *,
    db: Session = Depends(dependencies.get_db),
    obj_in: schemas.MessageFileSend = Body(...),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Send image message '''

    # Get file to database
    file_name = ""
    storage = db.query(models.Storage).filter(models.Storage.uuid==obj_in.file_uuid).first()

    if not storage:
        raise HTTPException(status_code=404, detail=__("file-not-found"))
    
    exist_conversation = db.query(models.Conversation)\
            .filter(
                or_(
                    and_(models.Conversation.sender_uuid == current_user.uuid, models.Conversation.receiver_uuid == obj_in.receiver_uuid),
                    and_(models.Conversation.sender_uuid == obj_in.receiver_uuid, models.Conversation.receiver_uuid == current_user.uuid),
                ),
                models.Conversation.status != models.MessageStatusEnum.DELETED
            )\
            .first()
    
    exist_receiver = db.query(models.Parent).\
                        filter(models.Parent.uuid == obj_in.receiver_uuid).\
                first() \
            or\
                    db.query(models.Administrator).\
                            filter(models.Administrator.uuid == obj_in.receiver_uuid).\
                                first()
    
    if not exist_receiver:
        raise HTTPException(status_code=404, detail=__("receiver-not-found"))

    if not exist_conversation:
        exist_conversation = models.Conversation(
            uuid=str(uuid.uuid4()),
            sender_uuid=current_user.uuid,
            receiver_uuid=obj_in.receiver_uuid,
            last_message=file_name if file_name else storage.url,
            is_read=False,
            last_sender_uuid=current_user.uuid
        )
        db.add(exist_conversation)
        db.commit()

        # Notification
        notification = schemas.Conversation.model_validate(exist_conversation).model_dump()
        conversation_schema = convert_dates_to_strings(notification)
        # notificationPublisher.publish(channel=obj_in.receiver_uuid, type="EVENT_NEW_CONVERSATION", data= conversation_schema)

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=file_name if file_name else storage.url,
            sender_uuid=current_user.uuid,
            message_type=MessageType.MESSAGE,
            is_file=False if storage and storage.mimetype.split("/")[0] in ["image"] else True,
            is_image=True if storage and storage.mimetype.split("/")[0] in ["image"] else False,
            file_uuid=storage.uuid if storage else None,
            uuid=str(uuid.uuid4())
        )
    else:
        exist_conversation.last_message = file_name if file_name else storage.url
        exist_conversation.last_sender_uuid = current_user.uuid

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=file_name if file_name else storage.url,
            sender_uuid=current_user.uuid,
            message_type=MessageType.MESSAGE,
            is_file=False if storage and storage.mimetype.split("/")[0] in ["image"] else True,
            is_image=True if storage and storage.mimetype.split("/")[0] in ["image"] else False,
            file_uuid=storage.uuid if storage else None,
            uuid=str(uuid.uuid4())
        )
    db.add(new_message)
    db.commit()


    # Get the messsage schema
    message = schemas.Message.model_validate(new_message).model_dump()
    message_schema = convert_dates_to_strings(message)

    # Notification
    # notificationPublisher.publish(channel="{}-{}".format(exist_conversation.sender_uuid, exist_conversation.receiver_uuid), type="EVENT_NEW_MESSAGE_IN_CONVERSATION", data = message_schema)

    return new_message

@router.post("/reservation", response_model=schemas.Message)
def create_a_reservation(
    *,
    db: Session = Depends(dependencies.get_db),
    obj_in: schemas.ReservationMessageCreate = Body(...),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Create a reservation '''

    exist_receiver = db.query(models.Parent).\
                        filter(models.Parent.uuid == obj_in.receiver_uuid).\
                first() \
            or\
                    db.query(models.Administrator).\
                            filter(models.Administrator.uuid == obj_in.receiver_uuid).\
                                first()
    
    if not exist_receiver:
        raise HTTPException(status_code=404, detail=__("receiver-not-found"))

    exist_conversation: models.Conversation = db.query(models.Conversation)\
            .filter(
                or_(
                    and_(models.Conversation.sender_uuid == current_user.uuid, models.Conversation.receiver_uuid == obj_in.receiver_uuid),
                    and_(models.Conversation.sender_uuid == obj_in.receiver_uuid, models.Conversation.receiver_uuid == current_user.uuid),
                ),
                models.Conversation.status != models.MessageStatusEnum.DELETED
            )\
            .first()

    if not exist_conversation:
        exist_conversation = models.Conversation(
            uuid=str(uuid.uuid4()),
            sender_uuid=current_user.uuid,
            receiver_uuid=obj_in.receiver_uuid,
            last_message=MessageType.RESERVATION,
            is_read=False,
            last_sender_uuid=current_user.uuid
        )
        db.add(exist_conversation)
        db.commit()

        # Notification
        notification = schemas.Conversation.model_validate(exist_conversation).model_dump()
        conversation_schema = convert_dates_to_strings(notification)
        # notificationPublisher.publish(channel=receiver_uuid, type="EVENT_NEW_CONVERSATION", data= conversation_schema)

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.RESERVATION,
            message_type=MessageType.RESERVATION,
            payload_json={
                "begin": jsonable_encoder(obj_in.begin),
                "end": jsonable_encoder(obj_in.end)
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    else:
        exist_conversation.last_message = MessageType.RESERVATION
        exist_conversation.last_sender_id = current_user.uuid


        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.RESERVATION,
            message_type=MessageType.RESERVATION,
            payload_json={
                "begin": jsonable_encoder(obj_in.begin),
                "end": jsonable_encoder(obj_in.end)
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    db.add(new_message)
    db.commit()

    # Get the messsage schema
    message = schemas.Message.model_validate(new_message).model_dump()
    message_schema = convert_dates_to_strings(message)
    print(message_schema)

    # Notification
    # notificationPublisher.publish(channel="{}-{}".format(exist_conversation.sender_uuid, exist_conversation.receiver_uuid), type="EVENT_NEW_MESSAGE_IN_CONVERSATION", data = message_schema)

    return new_message

@router.post("/absence", response_model=schemas.Message)
def create_a_absence(
    *,
    db: Session = Depends(dependencies.get_db),
    obj_in: schemas.AbsenceMessageCreate = Body(...),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Create a absence '''

    exist_receiver = db.query(models.Parent).\
                        filter(models.Parent.uuid == obj_in.receiver_uuid).\
                first() \
            or\
                    db.query(models.Administrator).\
                            filter(models.Administrator.uuid == obj_in.receiver_uuid).\
                                first()

    print("exist-receiver134",exist_receiver)

    if not exist_receiver:
        raise HTTPException(status_code=404, detail=__("receiver-not-found"))

    exist_conversation: models.Conversation = db.query(models.Conversation)\
            .filter(
                or_(
                    and_(models.Conversation.sender_uuid == current_user.uuid, models.Conversation.receiver_uuid == obj_in.receiver_uuid),
                    and_(models.Conversation.sender_uuid == obj_in.receiver_uuid, models.Conversation.receiver_uuid == current_user.uuid),
                ),
                    models.Conversation.status!= models.MessageStatusEnum.DELETED  # Remplacez 'active' par le statut souhaité

            )\
            .first()

    if not exist_conversation:
        exist_conversation = models.Conversation(
            uuid=str(uuid.uuid4()),
            sender_uuid=current_user.uuid,
            receiver_uuid=obj_in.receiver_uuid,
            last_message=MessageType.ABSENCE,
            is_read=False,
            last_sender_uuid=current_user.uuid
        )
        db.add(exist_conversation)
        db.commit()

        # Notification
        notification = schemas.Conversation.model_validate(exist_conversation).model_dump()
        conversation_schema = convert_dates_to_strings(notification)
        # notificationPublisher.publish(channel=receiver_uuid, type="EVENT_NEW_CONVERSATION", data= conversation_schema)

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.ABSENCE,
            message_type=MessageType.ABSENCE,
            status= models.MessageStatusEnum.DELIVERED,
            payload_json={
                "begin": jsonable_encoder(obj_in.begin),
                "end": jsonable_encoder(obj_in.end)
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    else:
        exist_conversation.last_message = MessageType.ABSENCE
        exist_conversation.last_sender_id = current_user.uuid


        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.ABSENCE,
            message_type=MessageType.ABSENCE,
            status= models.MessageStatusEnum.DELIVERED,
            payload_json={
                "begin": jsonable_encoder(obj_in.begin),
                "end": jsonable_encoder(obj_in.end),
                "note": obj_in.note
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    db.add(new_message)
    db.commit()

    # Get the messsage schema
    message = schemas.Message.model_validate(new_message).model_dump()
    message_schema = convert_dates_to_strings(message)
    print(message_schema)

    # Notification
    # notificationPublisher.publish(channel="{}-{}".format(exist_conversation.sender_uuid, exist_conversation.receiver_uuid), type="EVENT_NEW_MESSAGE_IN_CONVERSATION", data = message_schema)

    return new_message

@router.post("/late", response_model=schemas.Message)
def create_a_late(
    *,
    db: Session = Depends(dependencies.get_db),
    obj_in: schemas.AbsenceCreate = Body(...),
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Create a late '''


    exist_conversation: models.Conversation = db.query(models.Conversation)\
            .filter(
                or_(
                    and_(models.Conversation.sender_uuid == current_user.uuid, models.Conversation.receiver_uuid == obj_in.receiver_uuid),
                    and_(models.Conversation.sender_uuid == obj_in.receiver_uuid, models.Conversation.receiver_uuid == current_user.uuid),
                ),
                    models.Conversation.status!= models.MessageStatusEnum.DELETED  # Remplacez 'active' par le statut souhaité

            )\
            .first()
    
    exist_receiver = db.query(models.Parent).\
        filter(models.Parent.uuid == obj_in.receiver_uuid).\
            first() \
                \
            or \
                db.query(models.Administrator).\
                    filter(models.Administrator.uuid == obj_in.receiver_uuid).\
                        first()

    if not exist_receiver:
        raise HTTPException(status_code=404, detail=__("receiver-not-found"))
    
    if not exist_conversation:
        exist_conversation = models.Conversation(
            uuid=str(uuid.uuid4()),
            sender_uuid=current_user.uuid,
            receiver_uuid=obj_in.receiver_uuid,
            last_message=MessageType.LATE,
            is_read=False,
            last_sender_uuid=current_user.uuid
        )
        db.add(exist_conversation)
        db.commit()

        # Notification
        notification = schemas.Conversation.model_validate(exist_conversation).model_dump()
        conversation_schema = convert_dates_to_strings(notification)
        # notificationPublisher.publish(channel=receiver_uuid, type="EVENT_NEW_CONVERSATION", data= conversation_schema)

        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.LATE,
            message_type=MessageType.LATE,
            status= models.MessageStatusEnum.DELIVERED,
            payload_json={
                "duration": obj_in.duration
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    else:
        exist_conversation.last_message = MessageType.LATE
        exist_conversation.last_sender_id = current_user.uuid


        new_message = models.Message(
            conversation_uuid=exist_conversation.uuid,
            content=MessageType.LATE,
            status= models.MessageStatusEnum.DELIVERED,
            message_type=MessageType.LATE,
            payload_json={
                "duration": obj_in.duration
            },
            sender_uuid=current_user.uuid,
            uuid=str(uuid.uuid4())
        )
    db.add(new_message)
    db.commit()

    # Get the messsage schema
    message = schemas.Message.model_validate(new_message).model_dump()
    message_schema = convert_dates_to_strings(message)
    print(message_schema)

    # Notification
    # notificationPublisher.publish(channel="{}-{}".format(exist_conversation.sender_uuid, exist_conversation.receiver_uuid), type="EVENT_NEW_MESSAGE_IN_CONVERSATION", data = message_schema)

    return new_message

@router.get("/{conversation_uuid}", response_model=List[schemas.Message], status_code=200)
def fetch_conversation_messages(
    *,
    db: Session = Depends(dependencies.get_db),
    conversation_uuid: str,
    current_user: any = Depends(dependencies.TokenRequired(roles=None)),
) -> Any:

    ''' Recupérer la liste des messages d'une conversation '''

    messages = []

    exist_conversation = db.query(models.Conversation)\
    .filter(
        models.Conversation.uuid == conversation_uuid,
        or_(
            models.Conversation.sender_uuid == current_user.uuid,
            models.Conversation.receiver_uuid == current_user.uuid
        ),
        models.Conversation.status!= models.MessageStatusEnum.DELETED  # Remplacez 'active' par le statut souhaité
    )\
    .first()
    # print("exist_conversation11",exist_conversation)

    if not exist_conversation:
        raise HTTPException(
            status_code=404,
            detail=__("conversation-not-found")
        )
    

    if current_user.uuid != exist_conversation.last_sender_uuid:
        exist_conversation.is_read = True
        for message in db.query(models.Message).filter(
            models.Message.conversation_uuid == exist_conversation.uuid,
            models.Conversation.status!= models.MessageStatusEnum.DELETED).all():

            message.is_read = True
            db.add(message)
            db.commit()
        db.add(exist_conversation)
        db.commit()

    messages = db.query(models.Message)\
        .filter(
            models.Message.conversation_uuid == exist_conversation.uuid,
            models.Conversation.status!= models.MessageStatusEnum.DELETED)\
        .order_by(models.Message.sending_date.desc())\
        .all()
    return messages
