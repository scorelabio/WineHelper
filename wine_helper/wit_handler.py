#!/usr/bin/python
# -*- coding: utf-8 -*-

# System dependencies
import os
import json

# Vendors
from wit import Wit

import json_creator as jc
from django.conf import settings



def treatment(request, sender_id):
    print "wit received message : " + request
    return client.run_actions(sender_id, request.decode('utf-8'))


def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val


def defaultAnswer(request):
    context = request['context']
    context['action'] = 'reask'

    return context

def sayDontUnderstand(request):
    context = request['context']
    if not 'response' in context:
        context['response'] = []
    context['response'].append(jc.create_text_response(settings.DONT_UNDERSTAND))

    return context

def askStoryline(request):
    context = request['context']
    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.INTRO_SENTENCE)
    button_table['options'].append(jc.create_button('Un aperitif', 'aperitif'))
    button_table['options'].append(jc.create_button('Un repas', 'repas'))
    button_table['options'].append(jc.create_button('Un cadeau', 'cadeau'))
    context['response'].append(button_table)

    context['last_step'] = 'storyline'

    return context


def askColor(request):
    context = request['context']
    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.ASK_COLOR)
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe '))
    button_table['options'].append(jc.create_button('Nouvelle recherche', 'Recommencer'))
    context['response'].append(button_table)

    context['last_step'] = 'color'

    return context


def askPrice(request):
    context = request['context']
    entities = request['entities']
    # creation de la reponse de type bouton et ajout des boutons
    if not 'response' in context:
        context['response'] = []
    button_table = jc.create_button_table(settings.ASK_PRICE)
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe '))
    button_table['options'].append(jc.create_button('Nouvelle recherche', 'Recommencer'))
    context['response'].append(button_table)

    context['last_step'] = 'price'

    return context


def askAppelation(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.ASK_APPELATION)
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe '))
    button_table['options'].append(jc.create_button('Nouvelle recherche', 'Recommencer'))
    context['response'].append(button_table)

    context['last_step'] = 'appelation'

    return context


def askVintage(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []
    button_table = jc.create_button_table(settings.ASK_VINTAGE)
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe '))
    button_table['options'].append(jc.create_button('Nouvelle recherche', 'Recommencer'))
    context['response'].append(button_table)

    context['last_step'] = 'vintage'

    return context


def askAdjustment(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.ASK_ADJUSTMENT)
    button_table['options'].append(jc.create_button('Je suis satisfait', 'satisfait'))
    button_table['options'].append(jc.create_button('Reajuster le prix', 'reajuster'))
    context['response'].append(button_table)

    context['last_step'] = 'adjust'

    return context


def askDinerType(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.ASK_DINER_TYPE)
    button_table['options'].append(jc.create_button('Dejeuner', 'dejeuner'))
    button_table['options'].append(jc.create_button('Diner', 'diner'))
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe'))
    context['response'].append(button_table)

    context['last_step'] = 'dinertype'

    return context


def askMealChoice(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []

    button_table = jc.create_button_table(settings.ASK_MEAL_CHOICE)
    button_table['options'].append(jc.create_button('Peu importe', 'peu importe'))
    button_table['options'].append(jc.create_button('Nouvelle recherche', 'Recommencer'))
    context['response'].append(button_table)

    context['last_step'] = 'meal'

    return context


def sayGoodbye(request):
    context = request['context']

    if not 'response' in context:
        context['response'] = []
    context['response'].append(jc.create_text_response(settings.CONCLUSION_SENTENCE))

    return context


def getStorylineAperitif(request):
    context = request['context']

    # ajout du scenario dans le contexte
    context['storyline'] = 'aperitif'
    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('degustation', 'aperitif'))

    return context


def getStorylineGift(request):
    context = request['context']
    context['storyline'] = 'cadeau'
    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('degustation', 'cadeau'))

    return context


def getStorylineRepas(request):
    context = request['context']
    context['storyline'] = 'repas'
    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('degustation', 'dejeuner|diner'))

    return context


def getColor(request):
    context = request['context']
    entities = request['entities']
    print request

    # recuperation de la couleur du vin
    color = first_entity_value(entities, 'wit_color')
    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('color', color))

    return context


def getPrice(request):
    context = request['context']
    print request

    entities = request['entities']
    min = first_entity_value(entities, 'minprice')
    max = first_entity_value(entities, 'maxprice')

    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('priceMin', min))
    context['criteria'].append(jc.create_criterion('priceMax', max))
    # context['criteria'].append(jc.create_criterion('currency', currency))

    return context


def getAppelation(request):
    context = request['context']
    print request

    entities = request['entities']
    appellation = first_entity_value(entities, 'wit_appelation')

    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('appellation', appellation))

    return context


def getVintage(request):
    context = request['context']
    print request

    entities = request['entities']
    vintage = first_entity_value(entities, 'vintage')

    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('vintage', vintage))

    return context


def getDinerType(request):
    context = request['context']
    print request

    entities = request['entities']
    dinertype = first_entity_value(entities, 'wit_typediner')

    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('degustation', dinertype))

    return context


def getMealChoice(request):
    context = request['context']
    print request

    entities = request['entities']
    meal = first_entity_value(entities, 'wit_meal')

    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('food_pairing_french', meal))

    return context


def reset(request):
    print request
    context = request['context']
    context['action'] = 'reset'

    return context


def apiCall(request):
    context = request['context']
    context['action'] = 'api_call'

    return context


def send(request, response):
    print "sending to server..."


actions = {
    'defaultAnswer': defaultAnswer,
    'sayDontUnderstand' : sayDontUnderstand,
    'askStoryline': askStoryline,
    'askColor': askColor,
    'askPrice': askPrice,
    'askAppelation': askAppelation,
    'askVintage': askVintage,
    'askAdjustment': askAdjustment,
    'askDinerType': askDinerType,
    'askMealChoice': askMealChoice,
    'getStorylineAperitif': getStorylineAperitif,
    'getStorylineGift': getStorylineGift,
    'getStorylineRepas': getStorylineRepas,
    'getColor': getColor,
    'getPrice': getPrice,
    'getAppelation': getAppelation,
    'getVintage': getVintage,
    'getDinerType': getDinerType,
    'getMealChoice': getMealChoice,
    'reset': reset,
    'sayGoodbye': sayGoodbye,
    'apiCall': apiCall,
    'send': send
}

client = Wit(access_token=os.getenv('WIT_TOKEN'), actions=actions)
