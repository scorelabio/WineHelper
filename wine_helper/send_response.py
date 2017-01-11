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
import db_tools as db
from Criteria import Criteria

# "Constants" (variables that should not change)
RESULTS_LIMIT = 3

# Initializing client
messenger = MessengerClient(access_token=os.getenv('FB_PAGE_TOKEN'))


def send_facebook_message(fbid, data):
    """
    TODO: write description
    """
    pprint("[DEBUG] send_facebook_message")
    pprint("[DEBUG] data ---------------v")
    pprint(data)
    pprint("[DEBUG] data ---------------^")

    if 'criteria' in data and data["criteria"]:
        store_criteria(fbid, data["criteria"])
    if 'action' in data:
        if data["action"] == 'api_call':
            handle_api_call(fbid)
        elif data["action"] == 'reset':
            reset_search(fbid)
    if 'response' in data and data["response"]:
        for item in data["response"]:
            handle_response(fbid, item)


def store_criteria(fbid, criteria):
    """
    TODO: write description
    """
    pprint("[DEBUG][send_response.py][store_criteria]")
    user = db.get_user_by_id(fbid)
    if user is None:
        pprint("[DEBUG][send_response.py][store_criteria] user is None")
        db.create_user(fbid)
    for criterion in criteria:
        db.create_criterion(fbid, criterion)


def reset_search(fbid):
    """
    TODO: write description
    """
    db.close_search(fbid)


def handle_response(fbid, data):
    """
    TODO: write description
    """
    pprint("[DEBUG] handle_response")
    pprint("[DEBUG] data ---------------v")
    pprint(data)
    pprint("[DEBUG] data ---------------^")
    if 'type' in data:
        pprint("type in data ok")
        if data["type"] == "text":
            pprint("[DEBUG] type text ok")
            handle_text(fbid, data)
        elif data["type"] == "button":
            pprint("[DEBUG] type button ok")
            handle_button(fbid, data)
        else:
            pprint("[DEBUG] type else ok")
            handle_error(fbid)


def handle_text(fbid, data):
    """
    Handles the sending to messenger of a text message
    """
    pprint("[DEBUG] handle_text")
    recipient = messages.Recipient(recipient_id=fbid)
    message = messages.Message(text=data["text"])
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


def handle_api_call(fbid):
    """
    TODO: write description
    """
    recipient = messages.Recipient(recipient_id=fbid)
    message = messages.Message(text='API call')
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)

            # wine_list = api.build_wine_list(data, RESULTS_LIMIT)
            # text = "Voici les meilleurs vins présentants les critères recherchés :\n".decode('utf-8')
            # res = ""
            #
            # for wine in wine_list:
            #     res += "- "
            #     res += wine.get_name().decode('utf-8')
            #     res += ", " + wine.get_appellation().decode('utf-8')
            #     res += " (" + str(wine.get_vintage()) + ")"
            #     res += ", " + wine.get_color()['fr'].decode('utf-8')
            #     res += ", " + wine.get_taste()['fr'].decode('utf-8')
            #     res += ", " + str(wine.get_price()) + " euros"
            #     res += "\n"

            # pprint(wine_list)

            # if not res:
            #     res = "Aucun vin ne correspond à votre recherche".decode('utf-8')

            # text += res

            # message = messages.Message(text=text)
            # request = messages.MessageRequest(recipient, message)
            # messenger.send(request)
