import aiohttp
import aioredis
import logging
import asyncio
import json

from channels.consumer import AsyncConsumer
from asgiref.sync import async_to_sync
from django.db import close_old_connections
from django.urls import reverse
from channels.exceptions import StopConsumer
from channels.generic.http import AsyncHttpConsumer
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from . import models
from Me2U import settings

logger = logging.getLogger(__name__)


# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         self.accept()
#         print('connected', event)
#
#     async def websocket_disconnect(self, event):
#         pass
#
#     async def websocket_receive(self, event):
#        print('receive', event)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    # print('we check this functions first')
    EMPLOYEE = 2
    CLIENT = 1

    def get_user_type(self, user, order_id):
        print('user:', user)
        order = get_object_or_404(models.Order, pk=order_id)
        print('order:', order)

        if user.is_employee:
            print('employee:', user.is_employee)
            order.last_spoken_to = user
            order.save()
            return ChatConsumer.EMPLOYEE

        elif order.user == user:
            print('user:', user)
            return ChatConsumer.CLIENT
        else:
            return None

    async def connect(self):
        print('we got here first to connect')

        self.order_id = self.scope['url_route']['kwargs']['order_id']
        print('Order id:', self.order_id)

        self.room_group_name = (
                "customer-service_%s" % self.order_id
        )
        print('we in connect:Group name', self.room_group_name)

        authorized = False
        if self.scope['user'].is_anonymous:
            print('anonymous user')
            await self.close()

        user_type = await database_sync_to_async(self.get_user_type)(self.scope['user'], self.order_id)
        print('user type:', user_type)

        if user_type == ChatConsumer.EMPLOYEE:
            print('logging... employee')
            logger.info("Opening chat stream for employee %s", self.scope['user'], )
            authorized = True
        elif user_type == ChatConsumer.CLIENT:
            print('logging... client')
            logger.info(
                'Opening chat stream for client %s', self.scope['user'], )
            authorized = True
        else:
            print('unauthorized')

            logger.info("Unauthorized connection from %s", self.scope["user"], )
            await self.close()

        if authorized:
            print('we came to create connection for channel_name:', self.channel_name)
            # print('redis url:', settings.REDIS_URL)
            self.r_conn = await aioredis.create_redis('redis://localhost')
            print('r_conn:', self.r_conn)

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            print('channel layer created:', self.channel_name)

            await self.accept()
            print('connection created')

            await self.channel_layer.group_send(self.room_group_name, {
                    'type': 'chat_join',
                    'username': self.scope['user'].get_username(),
                },
            )

    async def disconnect(self, close_code):
        print('we came to disconnect')

        if not self.scope['user'].is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name, {
                    'type': 'chat_leave',
                    'username': self.scope['user'].get_username(),
                }
            )
            logger.info("Closing chat stream for user %s", self.scope["user"],
                        )
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content):
        print('we came to receive', content)
        print('username', self.scope["user"].get_username())

        typ = content.get("type")

        if typ == "message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message",
                 "username": self.scope["user"].get_username(),
                 "message": content["message"],
                 },
            )

        elif typ == "heartbeat":
            print('we came to heartbeat')

            await self.r_conn.setex(
                "%s_%s"
                % (self.room_group_name, self.scope["user"].email,
                   ), 10,  # expiration (in 10 seconds)
                "1",  # dummy value
            )
            print("user is:", self.scope["user"].email)

    async def chat_message(self, event):
        await self.send_json(event)

    async def chat_join(self, event):
        await self.send_json(event)

    async def chat_leave(self, event):
        await self.send_json(event)


class ChatNotifyConsumer(AsyncHttpConsumer):
    # print("we came to notify customer service")

    def is_employee_func(self, user):
        # print('acertain employee status')
        return not user.is_anonymous and user.is_employee

    async def handle(self, body):
        print('we handling the requests')
        close_old_connections()
        is_employee = await database_sync_to_async(self.is_employee_func)(self.scope["user"])
        if is_employee:
            print('is_employee:', is_employee)
            logger.info(
                'Opening notify stream for user %s and params %s',
                self.scope.get('user'),
                self.scope.get('query_string'),
            )
            print('available user:', self.scope.get('user'))
            print('available chats:', self.scope.get('query_string'))
            await self.send_headers(
                headers=[
                    ("Cache-Control", "no-cache"),
                    ('Content-Type', 'text/event-stream'),
                    ('Transfer-Encoding', 'chunked'),
                ]
            )
            # print('headers:', self.send_headers())
            self.is_streaming = True
            # print('headers:', self.is_streaming)

            self.no_poll = (self.scope.get('query_string') == "nopoll")
            asyncio.get_event_loop().create_task(self.stream())
        else:
            logger.info(
                "Unauthorized notify stream for user %s and  params %s",
                self.scope.get("user"),
                self.scope.get("query_string"),
            )
            raise StopConsumer('Unauthorized')

    async def stream(self):
        print('We came to stream')
        print('We came to stream:', self.is_streaming)
        r_conn = await aioredis.create_redis('redis://localhost')
        print('r_conn:', r_conn)
        print('r_conn:', self.is_streaming)
        while self.is_streaming:
            print('streaming true:', self.is_streaming)
            active_chats = await r_conn.keys(
                'customer-service_*'
            )
            print("active chats:", active_chats)
            presences = {}
            for i in active_chats:
                _, order_id, user_email = i.decode('utf8').split('_')

                if order_id in presences:
                    presences[order_id].append(user_email)
                else:
                    presences[order_id] = [user_email]

            print('presense items:', presences)
            data = []
            for order_id, emails in presences.items():
                data.append(
                    {
                        'link': reverse('me2ushop:cs_chat', kwargs={'order_id': order_id}),

                        'text': "%s (%s)" % (order_id, ", ".join(emails)),
                    }
                )
                payload = "data: %s\n\n" % json.dumps(data)
                logger.info(
                    'Broadcasting presence info to user %s', self.scope['user'],
                )
                if self.no_poll:
                    await self.send_body(payload.encode('utf-8'))
                    self.is_streaming = False
                else:
                    await self.send_body(
                        payload.encode('utf-8'),
                        more_body=self.is_streaming,
                    )
                    await asyncio.sleep(5)

    async def disconnect(self):
        logger.info(
            "Closing notify stream for user %s", self.scope.get("user"),
        )
        self.is_streaming = False


class OrderTrackerConsumer(AsyncHttpConsumer):
    # print('we came here to check')
    def verify_user(self, user, order_id):
        # print('we also came to verify')
        order = get_object_or_404(models.Order, pk=order_id)
        # print('order:', order)
        # print('order:', order.user)
        # print('order:', user)

        return order.user == user

    async def query_remote_server(self, order_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    'https://pastebin.com/raw/YVrKuC7h'
            ) as resp:
                return await resp.read()

    async def handle(self, body):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        is_authorized = await database_sync_to_async(
            self.verify_user)(self.scope['user'], self.order_id)

        if is_authorized:
            # print('true')
            logger.info(
                'Order tracking request for user %s and order %s',
                self.scope.get('user'),
                self.order_id
            )
            payload = await self.query_remote_server(self.order_id)
            logger.info(
                'Order tracking request for user %s and order %s',
                payload,
                self.scope.get('user'),
                self.order_id
            )
            await self.send_response(200, payload)
        else:
            # print('unauthorized')
            raise StopConsumer('unauthorized')
