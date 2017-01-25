# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os

from django.conf import settings
from slackclient import SlackClient
from slacker import Slacker
from .models import Team
import db_tools as db
import send_response as sr
import api_tools as api

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
#authed_teams = {}

# "Constants" (variables that should not change)
RESULTS_LIMIT = 3

class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "pythonboardingbot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": settings.SLACK_CLIENT_ID,
                      "client_secret": settings.SLACK_CLIENT_SECRET,
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = settings.SLACK_VERIFICATION_TOKEN

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        self.slacker = Slacker("")
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}
        self.authed_teams = {}
        self.last_message_id = ""


    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        self.authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(self.authed_teams[team_id]["bot_token"])
        self.slacker = Slacker(self.authed_teams[team_id]["bot_token"])
        team = self.find_team(team_id)
        if team is None:
            team = Team(team_id=team_id, 
                name=auth_response["team_name"], 
                bot_user_id=auth_response["bot"]["bot_user_id"],
                bot_access_token=auth_response["bot"]["bot_access_token"])
            team.save()
        
    def find_team(self, team_id):
        try:
            team = Team.objects.get(team_id=team_id)        
            self.client = SlackClient(team.bot_access_token)
            self.slacker = Slacker(team.bot_access_token)
            self.id = team.bot_user_id
        except Team.DoesNotExist:
            team = None
        return team


    def open_dm(self, user_id):
        """
        Open a DM to send a welcome message when a 'team_join' event is
        recieved from Slack.

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the 'team_join' event

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)
        dm_id = new_dm["channel"]["id"]
        return dm_id

    def onboarding_message(self, team_id, user_id):
        """
        Create and send an onboarding welcome message to new users. Save the
        time stamp of this message on the message object for updating in the
        future.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # We've imported a Message class from `message.py` that we can use
        # to create message objects for each onboarding message we send to a
        # user. We can use these objects to keep track of the progress each
        # user on each team has made getting through our onboarding tutorial.

        # First, we'll check to see if there's already messages our bot knows
        # of for the team id we've got.
        if self.messages.get(team_id):
            # Then we'll update the message dictionary with a key for the
            # user id we've recieved and a value of a new message object
            self.messages[team_id].update({user_id: message.Message()})
        else:
            # If there aren't any message for that team, we'll add a dictionary
            # of messages for that team id on our Bot's messages attribute
            # and we'll add the first message object to the dictionary with
            # the user's id as a key for easy access later.
            self.messages[team_id] = {user_id: message.Message()}
        message_obj = self.messages[team_id][user_id]
        # Then we'll set that message object's channel attribute to the DM
        # of the user we'll communicate with
        message_obj.channel = self.open_dm(user_id)
        # We'll use the message object's method to create the attachments that
        # we'll want to add to our Slack message. This method will also save
        # the attachments on the message object which we're accessing in the
        # API call below through the message object's `attachments` attribute.
        message_obj.create_attachments()
        post_message = self.client.api_call("chat.postMessage",
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        timestamp = post_message["ts"]
        # We'll save the timestamp of the message we've just posted on the
        # message object which we'll use to update the message after a user
        # has completed an onboarding task.
        message_obj.timestamp = timestamp

    def update_emoji(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "reaction_added"
        event from Slack. Update timestamp for welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Add an emoji reaction to this "
                                         "message*~ :thinking_face:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.emoji_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_pin(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "pin_added"
        event from Slack. Update timestamp for welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Pin this message*~ "
                                         ":round_pushpin:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.pin_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_share(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "message" event
        with an "is_share" attachment from Slack. Update timestamp for
        welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Share this Message*~ "
                                         ":mailbox_with_mail:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.share_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def send_message(self, s_id, channel, data):
        if 'last_step' in data:
            sr.store_last_step(s_id, data["last_step"])
        if 'storyline' in data:
            sr.store_storyline(s_id,data["storyline"])
        if 'criteria' in data and data["criteria"]:
            sr.store_criteria(s_id, data["criteria"])
        if 'action' in data:
            if data["action"] == 'api_call':
                self.handle_api_call(s_id, channel)
            elif data["action"] == 'reset':
                sr.reset_search(s_id)
        if 'response' in data and data["response"]:
            for item in data["response"]:
                self.handle_response(s_id, item, channel)
        #self.slacker.chat.post_message(channel, message, attachments=attachments)
        #self.client.api_call("chat.postMessage", channel=channel, username=self.name, icon_emoji=self.emoji, text=message,attachments=attachments)
    
    def handle_response(self, s_id, data, channel):    
        """
        TODO: write description
        """
        if 'type' in data:
            if data["type"] == "text":
                self.handle_text(s_id, data, channel)
            elif data["type"] == "button":
                self.handle_button(s_id, data, channel)
            else:
                self.handle_error(s_id)
    def handle_text(self, s_id, data, channel):
        """
        Handles the sending to messenger of a text message
        """
        self.slacker.chat.post_message(channel, data["text"])

       
    def handle_button(self, s_id, data, channel):
        """
        Handles the sending to messenger of a button template of postback buttons
        """
        attachments = [self.json_button_generator(data)]
        self.slacker.chat.post_message(channel, "", attachments=attachments)

    def handle_api_call(self, s_id, channel):
        """
        TODO: write description
        """
        text = ""
        criteria_data = db.get_criteria_data_by_id(s_id)
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

            if not res:
                res = "Aucun vin ne correspond à votre recherche".decode('utf-8')

            text += res
        else:
            text = "Une erreur s'est produite"

        self.slacker.chat.post_message(channel, text)


    def json_button_generator(self, data):
        if not "options" in data:
            print "ERREUR json_button_generator : no options"
        
        options = data["options"]
        actions = list()
        for option in options:
            current = dict()
            current["name"]=option["payload"]
            current["text"]=option["text"]
            current["type"]="button"
            current["value"]=option["payload"]
            actions.append(current)
        json_return = dict()
        #json_return["title"] = "Wine_Helper_Bot"
        json_return["text"] = data["text"]
        json_return["fallback"] = "ERREUR"
        json_return["color"] = "#3AA3E3"
        json_return["callback_id"] = "wopr_game"                                
        json_return["attachment_type"] = "default"
        json_return["actions"]=actions
        return json_return


    def adapt_message_to_wit(self, fbid, message):
        user = db.get_user_by_id(fbid)
        print "TTTT!!!!\n\n"
        storyline = None
        if user is None:
            db.create_user(fbid)
        storyline = db.get_storyline_by_user_id(fbid)
        if storyline is not None:
            new_message = message + "_" + storyline
            return new_message
        else:
            return message

