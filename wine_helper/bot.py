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
        #self.last_messages = list()


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
            #self.client = SlackClient(team.bot_access_token)
            self.slacker = Slacker(team.bot_access_token)
            self.id = team.bot_user_id
        except Team.DoesNotExist:
            team = None
        return team

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
                self.handle_error(channel)
    def handle_text(self, s_id, data, channel):
        """
        Handles the sending to messenger of a text message
        """
        self.slacker.chat.post_message(channel, data["text"])


    def handle_error(self, channel):
        """
        Sends an error message to slack
        """
        self.slacker.chat.post_message(channel, "Oups, une erreur est survenue")
       
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
        json_return["text"] = data["text"]
        json_return["fallback"] = "ERREUR"
        json_return["color"] = "#3AA3E3"
        json_return["callback_id"] = "wopr_game"                                
        json_return["attachment_type"] = "default"
        json_return["actions"]=actions
        return json_return