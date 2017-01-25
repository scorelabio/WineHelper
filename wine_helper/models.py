from __future__ import unicode_literals

from django.db import models
from mongoengine import *

class Team(Document):
    name = StringField(max_length=200)
    team_id = StringField(max_length=20)
    bot_user_id = StringField(max_length=20)
    bot_access_token = StringField(max_length=100)

class Criterion(EmbeddedDocument):
    name = StringField()
    value = DynamicField()

class Search(EmbeddedDocument):
    user_storyline = StringField()
    user_last_step = StringField()
    criteria = ListField(EmbeddedDocumentField(Criterion))

class User(Document):
    user_id = StringField()
    current_search = EmbeddedDocumentField(Search)
    searches = ListField(EmbeddedDocumentField(Search))
    meta = {'collection': 'users'}
