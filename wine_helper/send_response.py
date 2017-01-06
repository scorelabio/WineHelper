#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sytem dependencies
import os
import json
from pprint import pprint

# Vendors
# https://github.com/geeknam/messengerbot
from messengerbot import MessengerClient, messages, attachments, templates, elements

import api_tools as api
from Criteria import Criteria

# "Constants" (variables that should not change)
RESULTS_LIMIT = 3

# Initializing client
messenger = MessengerClient(access_token=os.getenv('FB_PAGE_TOKEN'))


def send_facebook_message(fbid, data):
    """
    Calls the right function according to the data type
    """
    recipient = messages.Recipient(recipient_id=fbid)

    if 'type' in data:
        if (data["type"] == "text"):
            handle_text(fbid, data)
        elif (data["type"] == "button"):
            handle_button(fbid, data)
        else:
            handle_error(fbid)


def handle_text(fbid, data):
    """
    Handles the sending to messenger of a text message
    """
    recipient = messages.Recipient(recipient_id=fbid)
    if (data["api_call"] == False):
        message = messages.Message(text=data["text"])
        request = messages.MessageRequest(recipient, message)
        messenger.send(request)
    else:
        wine_list = api.build_wine_list(data, RESULTS_LIMIT)
        text = "Voici les meilleurs vins présentants les critères recherchés :\n".decode('utf-8')
        res = ""

        for wine in wine_list:
            res += "- "
            res += wine.get_name().decode('utf-8')
            res += ", " + wine.get_appellation().decode('utf-8')
            res += " (" + str(wine.get_vintage()) + ")"
            res += ", " + wine.get_color()['fr'].decode('utf-8')
            res += ", " + wine.get_taste()['fr'].decode('utf-8')
            res += ", " + str(wine.get_price()) + " euros"
            res += "\n"

        pprint(wine_list)

        if not res:
            res = "Aucun vin ne correspond à votre recherche".decode('utf-8')

        text += res

        message = messages.Message(text=text)
        request = messages.MessageRequest(recipient, message)
        messenger.send(request)


def handle_button(fbid, data):
    """
    Handles the sending to messenger of a button template of postback buttons
    """
    recipient = messages.Recipient(recipient_id=fbid)
    text = data["text"]
    button_list = []
    for option in data["options"]:
        button_text = option["text"]
        button_payload = option["payload"]
        button_list.append(elements.PostbackButton(
            title=button_text,
            payload=button_payload
            )
        )
    template = templates.ButtonTemplate(
        text=text,
        buttons=button_list
    )
    attachment = attachments.TemplateAttachment(template=template)
    message = messages.Message(attachment=attachment)
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)


def handle_error(fbid):
    """
    Sends an error message to messenger
    """
    recipient = messages.Recipient(recipient_id=fbid)
    message = messages.Message(text='Oups, une erreur est survenue.')
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)
