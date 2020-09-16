import asyncio
import json
from django.contrib.auth.models import Group
from django.test import TestCase
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator, HttpCommunicator
from unittest.mock import patch, MagicMock
from main import factories
from me2ushop import consumers
from channels.testing import HttpCommunicator
from django.test import tag


@tag('e2e')
class TestConsumers(TestCase):
    def test_chat_between_two_users_works(self):
        def init_db():
            user = factories.UserFactory(email='dddd@gmail.com',
                                         username='dogechi')
            order = factories.OrderFactory(user=user)
            cs_user = factories.UserFactory(email='customerservice@me2u.domain',
                                            username='Lawi',
                                            is_staff=True)
            employees, _ = Group.objects.get_or_create(
                name='Employees'
            )
            cs_user.groups.add(employees)
            return user, order, cs_user

        async def test_body():
            user, order, cs_user = await database_sync_to_async(init_db)()
            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/me2ushop/customer-service/%d/" % order.id,
            )
            communicator.scope['user'] = user
            communicator.scope['url_route'] = {'kwargs': {'order_id': order.id}}
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            cs_communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/me2ushop/customer-service/%d/" % order.id,
            )

            cs_communicator.scope['user'] = cs_user
            cs_communicator.scope['url_route'] = {'kwargs': {'order_id': order.id}}
            connected, _ = await cs_communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to(
                {
                    'type': 'message',
                    'message': 'hello customer service'
                }
            )

            await asyncio.sleep(1)

            await cs_communicator.send_json_to(
                {"type": "message", "message": "hello user"}
            )
            self.assertEquals(await communicator.receive_json_from(),
                              {"type": "chat_join", "username": "dddd@gmail.com"}, )
            self.assertEquals(await communicator.receive_json_from(),
                              {"type": "chat_join", "username": "customerservice@me2u.domain"}, )
            self.assertEquals(await communicator.receive_json_from(),
                              {"type": "chat_message",
                               "username": "dddd@gmail.com",
                               "message": "hello customer service",
                               }, )
            self.assertEquals(await communicator.receive_json_from(),
                              {"type": "chat_message",
                               "username": "customerservice@me2u.domain",
                               "message": "hello user",
                               }, )
            await communicator.disconnect()
            await cs_communicator.disconnect()

            order.refresh_from_db()
            self.assertEquals(order.last_spoken_to, cs_user)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_chat_blocks_unauthorized_users(self):
        def init_db():
            user = factories.UserFactory(
                email='oprah@gmail.com',
                username='oprah'
            )
            order = factories.OrderFactory()
            return user, order

        async def test_body():
            user, order = await database_sync_to_async(init_db)()
            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/me2ushop/customer-service/%d/" % order.id,
            )
            communicator.scope['user'] = user
            communicator.scope['url_route'] = {'kwargs': {'order_id': order.id}}
            connected, _ = await communicator.connect()
            self.assertFalse(connected)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_chat_presence_works(self):
        def init_db():
            user = factories.UserFactory(
                username='john',
                email='user@gmail.com'
            )
            order = factories.OrderFactory(user=user)
            cs_user = factories.UserFactory(email='customerservice@me2u.domain',
                                            username='Lawi',
                                            is_staff=True)
            employees, _ = Group.objects.get_or_create(
                name='Employees'
            )
            cs_user.groups.add(employees)
            return user, order, cs_user

        async def test_body():
            user, order, cs_user = await database_sync_to_async(init_db)()
            communicator = WebsocketCommunicator(
                consumers.ChatConsumer,
                "/ws/me2ushop/customer-service/%d/" % order.id,
            )
            communicator.scope['user'] = user
            communicator.scope['url_route'] = {'kwargs': {'order_id': order.id}}
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({'type': 'heartbeat'})
            await communicator.disconnect()

            communicator = HttpCommunicator(
                consumers.ChatNotifyConsumer,
                'GET',
                'me2ushop/customer-service/notify/'
            )
            communicator.scope['user'] = cs_user
            communicator.scope['query_string'] = 'nopoll'

            response = await communicator.get_response()
            self.assertTrue(
                response["body"].startswith(b"data: ")
            )
            payload = response['body'][6:]
            data = json.loads(payload.decode('utf8'))
            self.assertEquals(
                data,
                [
                    {"link": "/me2ushop/customer-service/%d/" % order.id,
                     "text": "%d (user@gmail.com)" % order.id, }
                ],
                'expecting someone in the room but on one found'
            )
            await asyncio.sleep(10)
            communicator = HttpCommunicator(
                consumers.ChatNotifyConsumer,
                'GET',
                'me2ushop/customer-service/notify/'
            )
            communicator.scope['user'] = cs_user
            communicator.scope['query_string'] = 'nopoll'

            response = await communicator.get_response()
            self.assertTrue(
                response["body"].startswith(b"data: ")
            )
            payload = response['body'][6:]
            data = json.loads(payload.decode('utf8'))
            self.assertEquals(
                data,
                [],
                'expecting on one in the room but someone found'
            )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())

    def test_order_tracker_works(self):
        def init_db():
            user = factories.UserFactory(
                username='makori28',
                email='mobiletracker@site.com'
            )
            order = factories.OrderFactory(user=user)
            return user, order

        async def test_body():
            user, order = await database_sync_to_async(
                init_db
            )()
            awaitable_reqestor = asyncio.coroutine(
                MagicMock(return_value=b"SHIPPED")
            )
            with patch.object(
                    consumers.OrderTrackerConsumer, 'query_remote_server'
            ) as mock_requestor:
                mock_requestor.side_effect = awaitable_reqestor
                communicator = HttpCommunicator(
                    consumers.OrderTrackerConsumer,
                    'GET',
                    '/mobile-api/my-orders/%d/tracker/' % order.id,
                )
                communicator.scope['user'] = user
                communicator.scope['url_route'] = {
                    'kwargs': {'order_id': order.id}
                }
                response = await communicator.get_response()
                data = response['body'].decode('utf8')

                mock_requestor.assert_called_once()
                self.assertEquals(
                    data,
                    'SHIPPED'
                )

        loop = asyncio.get_event_loop()
        loop.run_until_complete(test_body())
