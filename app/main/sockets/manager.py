import json
from typing import List
from fastapi import WebSocket, status, WebSocketDisconnect
from starlette.websockets import WebSocketState
from requests import Session
from app.main.core import dependencies

from .redis  import  redis_manager
import asyncio
from aioredis.client import PubSub, Redis
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SocketConnectionManager:
    
    def __init__(self):
        self.calling_prospects: List[str] = []
        
    
    async def connector(self, websocket: WebSocket, channel: str):
        
        async def consumer_handler(conn: Redis, ws: WebSocket):
            try:
                while True:
                    if ws.client_state == WebSocketState.CONNECTED:
                        message = await ws.receive_text()
                        print(type(message))
                        print(message)
                        if message:
                            await conn.publish(channel, message)
            except WebSocketDisconnect as exc:
                logger.info(f"Socket receive_text failed {exc}")

        async def producer_handler(pubsub: PubSub, ws: WebSocket):
            await pubsub.subscribe(channel)
            try:
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        await ws.send_json(json.loads(message.get('data')))
            except WebSocketDisconnect as exc:
                logger.info(f"Socket websocket send jsonn failed {exc}")

        pubsub = redis_manager.aioredis.pubsub()

        #consumer_task = consumer_handler(conn=redis_manager.aioredis, ws=websocket)
        producer_task = producer_handler(pubsub=pubsub, ws=websocket)
        done, pending = await asyncio.wait(
            [producer_task], return_when=asyncio.FIRST_COMPLETED, #consumer_task
        )
        logger.debug(f"Done task: {done}")
        for task in pending:
            logger.debug(f"Canceling task: {task}")
            task.cancel()

    async def join_service(self, websocket: WebSocket, db: Session, token: str, user_uuid: str):
        current_user  = await dependencies.SocketTokenRequired(token=token, roles=None)(db=db)
        if current_user ==  False:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        else:
            await websocket.accept()
            try:
                while True:
                    await self.connector(websocket, f"user-{user_uuid}")
            except Exception as e:
                logger.info(f"Client #{current_user.uuid} left the socket")

    async def join(self, websocket: WebSocket, db: Session, token: str):

        current_user  = await dependencies.SocketTokenRequired(token=token, roles=None)(db=db)
        print(f"Current user {current_user}")
        if current_user ==  False:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        else:
            await websocket.accept()
            try:
                logger.info(current_user.email)
                while True:
                    await self.connector(websocket, f"user-{current_user.public_id}")
            except Exception as e:
                logger.info(f"Client #{current_user.public_id} left the socket")


socket_manager = SocketConnectionManager()
