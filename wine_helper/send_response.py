# -*- coding: utf-8 -*-

# System dependencies
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
    if 'last_step' in data:
        store_last_step(fbid, data["last_step"])
    if 'storyline' in data:
        store_storyline(fbid,data["storyline"])
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


def adapt_message_to_wit(fbid, message):
    """
    TODO: write description
    """
    user = db.get_user_by_id(fbid)
    last_step = None
    storyline = None

    if user is None:
        db.create_user(fbid)

    last_step = db.get_last_step_by_user_id(fbid)
    storyline = db.get_storyline_by_user_id(fbid)

    if last_step is not None:
        message = message + "_" + last_step
    if storyline is not None:
        message = message + "_" + storyline

    return message


def store_last_step(fbid, last_step):
    """
    TODO: write description
    """
    db.create_last_step(fbid, last_step)


def store_storyline(fbid, storyline):
    """
    Add to the user with fbid the storyline defined by the variable storyline.
    """
    db.create_storyline(fbid, storyline)


def store_criteria(fbid, criteria):
    """
    Add the criteria to the user with the id equal to fbid
    """
    user = db.get_user_by_id(fbid)
    if user is None:
        db.create_user(fbid)
    for criterion in criteria:
        db.create_criterion(fbid, criterion)


def reset_search(fbid):
    """
    Close the current_search of the user with id fbid
    """
    db.close_search(fbid)


def handle_response(fbid, data):
    """
    TODO: write description
    """
    if 'type' in data:
        if data["type"] == "text":
            handle_text(fbid, data)
        elif data["type"] == "button":
            handle_button(fbid, data)
        else:
            handle_error(fbid)


def handle_text(fbid, data):
    """
    Handles the sending to messenger of a text message
    """
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

    text = ""
    criteria_data = db.get_criteria_data_by_id(fbid)
    if criteria_data is not None:
        wine_list = api.build_wine_list(criteria_data, RESULTS_LIMIT)
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
    else:
        text = "Une erreur s'est produite"

    message = messages.Message(text=text)
    request = messages.MessageRequest(recipient, message)
    messenger.send(request)
