# coding: utf-8

import json

from django.test import TestCase, Client
from django.urls import reverse

import mock

client = Client()


class FacebookCallbackTest(TestCase):

    def test_callback_url(self):
        """
        Is the callback configured on Facebook indeed routed as it should ?
        """
        self.assertEqual(
            reverse('facebook_callback'),
            '/wine_helper/9850eea4020c130fb92af877a626248479ef038f67a8638090',
            )

    @mock.patch('messengerbot.MessengerClient.send')
    def test_handle_welcome(self, mock_messenger_client):
        # https://docs.python.org/3.5/library/unittest.mock-examples.html
        message_data = {
            'entry': [
                {
                    'messaging': [
                        {
                            'sender': {
                                'id': 1234
                            },
                            'message': {
                                # Actual message here
                                'text': 'Bonjour'
                            }
                        }
                    ]
                },
            ]
        }
        response = client.post(
            path=reverse('facebook_callback'),
            data=json.dumps(message_data),
            content_type='application/json'
            )
        mock_messenger_client.assert_called_once()
