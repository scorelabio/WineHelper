#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sytem dependencies
import json
from pprint import pprint

# Vendors
import requests

# Django
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import send_response as sr
import wit_handler as wit

#  ------------------------ Tokens -------------------------------
PAGE_ACCESS_TOKEN = "EAAYU6e7AspIBAHvYtRp44RebfWQGlVRUNTTIpqmd27i6nSHCW61noR7yDOrpGlzaRaRO2NreAXful5OlodZAy7xB9Y6SftRW9YfYl4aQ0MPD2HLa3Ey2k6hvfVfEVxuHIMmAkgJ9gnrbdFuVbXr6wMFQzPUteYmk0x5heegZDZD"
VERIFY_TOKEN = "b2ac128f9d0c4ba8fdfad7b37eb66b8f2e86d09a75c6720a43"




class FacebookCallbackView(generic.View):
    """
    This endpoint serves as the Facebook Messenger callback
    The bot can be messaged at this url: http://m.me/scorelab.winehelper

    Cf. docs: https://developers.facebook.com/docs/graph-api/webhooks
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles server verification performed by Facebook
        """
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        if token == VERIFY_TOKEN:
            if challenge:
                return HttpResponse(challenge)
            else:
                HttpResponse('Error, invalid challenge')
        else:
            return HttpResponse('Error, invalid token')

    def post(self, request, *args, **kwargs):
        """
        Handles Facebook messages
        """
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                sender_id = None
                received_message = None

                if 'sender' in message:
                    sender_id = message['sender']['id']
                if 'message' in message:
                    received_message = message['message']['text']
                if 'postback' in message:
                    received_message = message['postback']['payload']

                if sender_id is not None and received_message is not None:
                    json_answer = wit.treatment(received_message.encode('utf-8'))
                    sr.send_facebook_message(sender_id, json_answer)
        return HttpResponse()
