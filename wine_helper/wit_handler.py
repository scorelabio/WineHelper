#!/usr/bin/python
# -*- coding: utf-8 -*-

# System dependencies
import os
import json

# Vendors
from wit import Wit

import json_creator as jc


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
    context['response'] = []
    context['response'].append(jc.create_text_response('Désolé je n\'ai pas compris...'))

    return context


def askStoryline(request):
    context = request['context']
    print request

    context['response'] = []

    button_table = jc.create_button_table('Bonjour, souhaitez vous un vin pour ?')
    button_table['options'].append(jc.create_button('Un aperitif', 'aperitif'))
    button_table['options'].append(jc.create_button('Un repas', 'repas'))
    button_table['options'].append(jc.create_button('Un cadeau', 'cadeau'))
    context['response'].append(button_table)

    context['last_step'] = 'storyline'

    return context


def askColor(request):
    context = request['context']
    print request
    context['response'] = []
    context['response'].append(jc.create_whatever_button('Quel type de vin souhaitez-vous acheter? (rouge, rose, blanc, sucre, petillant)'))

    context['last_step'] = 'color'

    return context


def askPrice(request):
    context = request['context']
    entities = request['entities']
    print request
    #creation de la reponse de type bouton et ajout des boutons
    context['response'] = []
    context['response'].append(jc.create_whatever_button('Quel prix de vin? (exemple : "entre 10 et 20 euros", "moins de 100 euros"...)'))

    context['last_step'] = 'price'

    return context


def askAppelation(request):
    context = request['context']
    print request

    context['response'] = []
    context['response'].append(jc.create_whatever_button('Souhaitez-vous une appelation de vin particulière ? (Bordeaux, Haut medoc, entre deux mers,...)'))

    context['last_step'] = 'appelation'

    return context


def askVintage(request):
    context = request['context']
    print request

    context['response'] = []
    context['response'].append(jc.create_whatever_button('Avez-vous une préférence de millésime (2009, 2013,...) ?'))

    context['last_step'] = 'vintage'

    return context


def askAdjustment(request):
    context = request['context']
    print request

    context['response'] = []

    button_table = jc.create_button_table('Êtes-vous satisfait ou souhaitez-vous réajuster le prix ?')
    button_table['options'].append(jc.create_button('Je suis satisfait', 'satisfait'))
    button_table['options'].append(jc.create_button('Reajuster le prix', 'reajuster'))
    context['response'].append(button_table)

    context['last_step'] = 'adjust'

    return context


def sayGoodbye(request):
    context = request['context']
    print request

    context['response'] = []
    context['response'].append(jc.create_text_response('Merci d\'avoir utilisé mes services, je vais me coucher dis moi bonjour pour me réveiller si tu as besoin de moi !'))

    return context


def getStorylineAperitif(request):
    context = request['context']

    #ajout du scenario dans le contexte
    context['storyline'] = 'aperitif'

    return context


def getStorylineGift(request):
    context = request['context']
    context['storyline'] = 'cadeau'

    return context


def getColor(request):
    context = request['context']
    entities = request['entities']
    print request

    #recuperation de la couleur du vin
    color = first_entity_value(entities, 'wit_color')
    context['criteria'] = []
    context['criteria'].append(jc.create_criterion('color.fr', color))

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
    #context['criteria'].append(jc.create_criterion('currency', currency))

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
    'defaultAnswer' : defaultAnswer,
    'askStoryline' : askStoryline,
    'askColor' : askColor,
    'askPrice' : askPrice,
    'askAppelation' : askAppelation,
    'askVintage' : askVintage,
    'askAdjustment' : askAdjustment,
    'getStorylineAperitif' : getStorylineAperitif,
    'getStorylineGift' : getStorylineGift,
    'getColor' : getColor,
    'getPrice' : getPrice,
    'getAppelation' : getAppelation,
    'getVintage' : getVintage,
    'reset' : reset,
    'sayGoodbye' : sayGoodbye,
    'apiCall' : apiCall,
    'send' : send
}


client = Wit(access_token=os.getenv('WIT_TOKEN'), actions=actions)

#TODO:
#Erreur quand on fait deux fois "peu importe" aux deux questions de la story Apero
#Voir pour obliger l'utilisateur a suivre le scénario et reposer la question s'il n'a pas bien répondu
