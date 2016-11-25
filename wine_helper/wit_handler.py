#!/usr/bin/python
# -*- coding: utf-8 -*-

# Sytem dependencies
import json

# Vendors
from wit import Wit



def wines():
    return [{"appellation":"Pomerol","name":"Chateau Clinet","color":"red","vintage":"2011","price":"79","global_score":"95.14"},{"appellation":"Barsac","name":"Ch\u00e2teau Coutet","color":"white","vintage":"2009","price":"72.9","global_score":"95"},{"appellation":"Pomerol","name":"Petrus","color":"red","vintage":"2015","price":"87.53","global_score":"94.62"},{"appellation":"Languedoc","name":"T\u00eate de b\u00e9lier blanc","color":"white","vintage":"2014","price":"23.5","global_score":"94.2"},{"appellation":"Barsac","name":"Ch\u00e2teau Climens","color":"white","vintage":"2006","price":"78.9","global_score":"94.02"},{"appellation":"Haut-m\u00e9doc","name":"Ch\u00e2teau Bernadette","color":"red","vintage":"2012","price":"16.9","global_score":"93.67"},{"appellation":"Morgon","name":"Morgon","color":"red","vintage":"2015","price":"17","global_score":"93"},{"appellation":"Pomerol","name":"Ch\u00e2teau La Pointe","color":"red","vintage":"2011","price":"34.1","global_score":"90.74"},{"appellation":"Languedoc","name":"Prodige rose","color":"rose","vintage":"2015","price":"12.5","global_score":"90.5"},{"appellation":"C\u00f4tes de Provence","name":"MiP classic","color":"rose","vintage":"2015","price":"9.95","global_score":"90.17"},{"appellation":"Blaye","name":"Ch\u00e2teau La Roche Bazin","color":"red","vintage":"2014","price":"10.5","global_score":"90.15"},{"appellation":"Pomerol","name":"Carillon de Rouget","color":"red","vintage":"2011","price":"23.9","global_score":"89.82"},{"appellation":"Pays d'Oc","name":"Gris blanc","color":"rose","vintage":"2015","price":"8.1","global_score":"89.72"},{"appellation":"Graves","name":"Ch\u00e2teau d'Uza","color":"red","vintage":"2011","price":"12.9","global_score":"88.27"},{"appellation":"C\u00f4tes des Gascogne IGP","name":"Premi\u00e8res Grives","color":"white","vintage":"2015","price":"7.25","global_score":"87.1"},{"appellation":"C\u00f4tes des Gascogne IGP","name":"Colombard-Ugni blanc n\u00b03","color":"white","vintage":"2015","price":"5.5","global_score":"82.64"}]






def send(request, response):
    data = request['context']
    if data.get('missingAdjective') is not None:
        del data['missingAdjective']
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
    if context.get('forecast') is not None:
        del context['forecast']
    if context.get('missingAdjective') is not None:
        del context['missingAdjective']




def getForecast(request):
    context = request['context']
    entities = request['entities']
    print request

    preTreatment(context)

    color = first_entity_value(entities, 'wit_color')
    minprice = first_entity_value(entities, 'wit_minprice')
    maxprice = first_entity_value(entities, 'wit_maxprice')
    currency = first_entity_value(entities, 'wit_currency')

    if entities:
        if 'intent' in entities and entities['intent']:
            if entities['intent'][0]['value'] == "adjective":
                context['missingAdjective'] = True
                if context.get('forecast') is not None:
                    del context['forecast']
            if entities['intent'][0]['value'] == "greetings":
                context['type'] = 'button'
                context['text'] = 'Quel vin souhaitez-vous ?'
                context['options'] = []
                # vin rouge
                rouge = {}
                rouge['text'] = 'Rouge'
                rouge['payload'] = 'Rouge'
                context['options'].append(rouge)
                # vin rose
                rose = {}
                rose['text'] = 'Rose'
                rose['payload'] = 'Rose'
                context['options'].append(rose)
                # vin blanc
                blanc = {}
                blanc['text'] = 'Blanc'
                blanc['payload'] = 'Blanc'
                context['options'].append(blanc)
                if context.get('missingAdjective') is not None:
                    del context['missingAdjective']

        if color:
            context['type'] = 'text'
            context['api_call'] = True
            context['criteria'] = []
            color_criterion = {}
            color_criterion['name'] = 'color.fr'
            color_criterion['value'] = color
            context['criteria'].append(color_criterion)
            if context.get('missingAdjective') is not None:
                del context['missingAdjective']


        #if minprice and maxprice and currency:
            #addToForecast(context,"entre " + minprice + " et " + maxprice + " " + currency)
    else:
       context['type'] = 'text'
       context['text'] = 'Je n\'ai pas compris ce que vous voulez dire'
       context['api_call'] = False
       if context.get('missingAdjective') is not None:
           del context['missingAdjective']
    return context






actions = {
    'send': send,
    'getForecast': getForecast
}





client = Wit(access_token="KUYTEM3SA2QPYI4P6T6JC2QJE7YDQPXC", actions=actions)

def treatment(request):
    session_id = 'my-user-session-42'
    context0 = {}
    context1 = client.run_actions(session_id, request, context0)
    #client.interactive()
    return context1
