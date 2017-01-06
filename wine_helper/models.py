from __future__ import unicode_literals

from django.db import models
from mongoengine import *

class Criterion(EmbeddedDocument):
    name = StringField()
    value = StringField()

class Search(Document):
    user_id = StringField()
    criteria = ListField(EmbeddedDocumentField(Criterion))
