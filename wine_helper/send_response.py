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
        criteria = data["criteria"]
        criteria_list = []
        for criterion in criteria:
            crit = Criteria(criterion["name"], criterion["value"])
            criteria_list.append(crit)
        wine_list = api.get_wines_by_criteria(criteria_list)
        text = ""

        for wine in wine_list:
            text += wine.get_name().decode('utf-8')
            text += "," + wine.get_appellation().decode('utf-8')
            text += "," + str(wine.get_vintage())
            text += "\n"

        pprint(wine_list)

        if not text:
            text = 'Aucun vin de correspond à votre recherche'

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
