#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sytem dependencies
import os
import json

# Vendors
from wit import Wit
from pprint import pprint

# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
# TODO: clean file (remove unused code, add comments, etc.)
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\


def send(request, response):
    data = request['context']
    json_data = json.dumps(data)
    print('Sending to server...', json_data)





def first_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]['value']
    if not val:
        return None
    return val['value'] if isinstance(val, dict) else val




def preTreatment(context):
    if context.get('answer') is not None:
        del context['answer']




def getAnswer(request):
    context = request['context']
    entities = request['entities']
    print request

    preTreatment(context)

    context['answer'] = ''

    # Unused variables
    color = first_entity_value(entities, 'wit_color')
    pprint("[DEBUG] wit color")
    pprint(color)
    minprice = first_entity_value(entities, 'wit_minprice')
    maxprice = first_entity_value(entities, 'wit_maxprice')
    currency = first_entity_value(entities, 'wit_currency')

    if entities:
        if 'wit_color' in entities and entities['wit_color']:
            pprint("[DEBUG] color ok")
            context['type'] = 'text'
            context['api_call'] = True
            context['criteria'] = []
            color_criterion = {}
            color_criterion['name'] = 'color.fr'
            color_criterion['value'] = entities['wit_color'][0]['value']
            context['criteria'].append(color_criterion)
        elif 'intent' in entities and entities['intent']:
            if entities['intent'][0]['value'] == "adjective":
                if context.get('answer') is not None:
                    del context['answer']
            elif entities['intent'][0]['value'] == "greetings":
                context['type'] = 'button'
                context['text'] = 'Quel vin souhaitez-vous ?'
                context['options'] = []
                # vin rouge
                rouge = {}
                rouge['text'] = "rouge"
                rouge['payload'] = "rouge"
                context['options'].append(rouge)
                # vin rose
                rose = {}
                rose['text'] = "rosé"
                rose['payload'] = "rosé"
                context['options'].append(rose)
                # vin blanc
                blanc = {}
                blanc['text'] = "blanc"
                blanc['payload'] = "blanc"
                context['options'].append(blanc)
            else:
               context['type'] = 'text'
               context['text'] = 'Je n\'ai pas compris ce que vous voulez dire'
               context['api_call'] = False
        else:
           context['type'] = 'text'
           context['text'] = 'Je n\'ai pas compris ce que vous voulez dire'
           context['api_call'] = False

        #if minprice and maxprice and currency:
            #addToanswer(context,"entre " + minprice + " et " + maxprice + " " + currency)
    else:
       context['type'] = 'text'
       context['text'] = 'Je n\'ai pas compris ce que vous voulez dire'
       context['api_call'] = False
    return context






actions = {
    'send': send,
    'getAnswer': getAnswer
}





client = Wit(access_token=os.getenv('WIT_TOKEN'), actions=actions)

def treatment(request):
    session_id = 'my-user-session-42'
    context0 = {}
    pprint("[DEBUG] wit request")
    pprint(request)
    context1 = client.run_actions(session_id, request, context0)
    #client.interactive()
    return context1
