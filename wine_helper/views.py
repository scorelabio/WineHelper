# -*- coding: utf-8 -*-

# System dependencies
import os
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
from wine_helper.models import Search

from django.shortcuts import render
from .models import Team
from django.conf import settings
import bot
import urllib


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
        if token == os.getenv('FB_VERIFY_TOKEN'):
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
                    pprint("[DEBUG] received message -------------------------------v")
                    pprint(received_message.encode('utf-8'))
                    pprint("[DEBUG] received message -------------------------------^")
                    adapted_message = sr.adapt_message_to_wit(sender_id, received_message.encode('utf-8'))
                    pprint("[DEBUG] adapted message ________________________________v")
                    pprint(adapted_message)
                    pprint("[DEBUG] adapted message ________________________________^")
                    json_answer = wit.treatment(adapted_message, sender_id)
                    pprint("[DEBUG] data from Wit ==================================v")
                    pprint(json_answer)
                    pprint("[DEBUG] data from Wit ==================================^")
                    sr.send_facebook_message(sender_id, json_answer)
        return HttpResponse()

pyBot = bot.Bot()


def slack_oauth(request):
    code = request.GET['code']

    params = {
        'code': code,
        'client_id': settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET
    }
    url = 'https://slack.com/api/oauth.access'
    json_response = requests.get(url, params)
    data = json.loads(json_response.text)
    Team.objects.get_or_create(
        name=data['team_name'],
        team_id=data['team_id'],
        bot_user_id=data['bot']['bot_user_id'],
        bot_access_token=data['bot']['bot_access_token']
    )
    return HttpResponse('Bot added to your Slack team!')

    
def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
    type of event recieved from Slack
    slack_event : dict
    JSON response from a Slack reaction event

    Returns
    ----------
    obj
    Response object with 200 - ok or 500 - No Event Handler error"""
    team_id = slack_event["team_id"]
    pyBot.find_team(team_id)



    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        return HttpResponse("Welcome Message Sent", 200,)

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" and slack_event["event"].get("attachments"):
        user_id = slack_event["event"].get("user")
        if slack_event["event"]["attachments"][0].get("is_share"):
            # Update the onboarding message and check off "Share this Message"
            pyBot.update_share(team_id, user_id)
            return HttpResponse("Welcome message updates with shared message",
                                 200,)

    # ============= Reaction Added Events ============= #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "reaction_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_emoji(team_id, user_id)
        return HttpResponse("Welcome message updates with reactji", 200,)

    # =============== Pin Added Events ================ #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "pin_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_pin(team_id, user_id)
        return HttpResponse("Welcome message updates with pin", 200,)

    elif event_type == "message":
        sender_id = None
        print "MESSAGE ICI \n \n"        
        message_id = slack_event["event"]["event_ts"]
        print message_id
        if "user" in slack_event["event"] and message_id != pyBot.last_message_id:
            sender_id = slack_event["event"]["user"]
            pyBot.last_message_id = message_id
            adapted_message = pyBot.adapt_message_to_wit(sender_id, slack_event["event"]["text"].encode('utf-8'))
            message = wit.treatment(adapted_message, sender_id)
            channel = slack_event["event"]["channel"]
            pyBot.send_message(sender_id, channel, message)
        return HttpResponse("TTTTTTT", 200)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    channel = slack_event["event"]["channel"]
    
    #if "user" in slack_event["event"]:
    #    pyBot.send_message(channel, message)
    return HttpResponse(message, 200,)
    #removed {"X-Slack-No-Retry": 1}

# SLACK BOT BELOW

def pre_install(request):
    #"""This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    #return render_template("install.html", client_id=client_id, scope=scope)
    return render(request, 'install.html', {'client_id': client_id, 'scope':scope})

def thanks(request):
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.GET['code']
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render(request, "thanks.html")

@csrf_exempt
def hears(request):
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.body)
    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return HttpResponse(slack_event["challenge"], 200,)
        #removed  {"content_type":"application/json"} from flask response

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        HttpResponse(message, 403,)
        #removed  {"X-Slack-No-Retry": 1}

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
        
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return HttpResponse("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404,)
    #removed  {"X-Slack-No-Retry": 1}

@csrf_exempt
def button(request):    
    response = urllib.unquote(request.body)[8:]    
    json_res = json.loads(response)
    
    sender_id = json_res["user"]["id"]
    channel = json_res["channel"]["id"]
    
    answer = json_res["actions"][0]["value"] 
    adapted_message = pyBot.adapt_message_to_wit(sender_id, answer.encode('utf-8'))
    message = wit.treatment(adapted_message, sender_id)
    print "MESSAGE ICI\n"
    print message
    pyBot.send_message(sender_id, channel, message)
    return HttpResponse("Vous avez choisi "+answer, 200,)
