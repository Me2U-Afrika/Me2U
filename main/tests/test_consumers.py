import asyncio
from django.contrib.auth.models import Group
from django.test import TestCase
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

# class TestConsumers(TestCase):
#     def test_chat_between_two_users_works(self):
#         def init_db():
#             user = factories.UserFactory(
#
#             )