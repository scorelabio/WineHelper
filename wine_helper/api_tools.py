# -*- coding: utf-8 -*-

import requests as re
from pprint import pprint
import db_tools as db
import csv_reader as cr

import Wine as W
import Criteria as C

# "Constants" (variables that should not change)
API_BASE_URL = "http://wine-helper-fake-api.herokuapp.com/public/api/wines"


def get_wines_by_criteria(criteria, limit=0):
    """
    Makes an API call with the given criteria and returns a list of wines
    (class Wine)
    """
    url = API_BASE_URL
    # setting limit
    query = "?limit={0}".format(limit)
    # setting criteria
    for criterion in criteria:
        # TODO: remove last &
        value = cr.search_translation("/app/wine_helper/data/translate_file.csv",1,0,str(criterion.get_value())).lower()
        query += "&" + criterion.get_name() + "=" + str(value)
    url += query.replace(" ","%20")
    pprint("[DEBUG] API call url: " + url)

    response = re.get(url)
    data = response.json()
    wine_list = []
    for wine in data:
        wine_object = W.Wine(
            wine['appellation'].encode('utf-8'),
            wine['name'].encode('utf-8'),
            int(wine['vintage']),
            float(wine['price']),
            float(wine['gws']),
            wine['color']
        )
        wine_list.append(wine_object)
    return wine_list

# TODO: review this function
def build_wine_list (data, limit):
    criteria_list = []
    for criterion in data:
        if type(criterion["value"]) == unicode:
            criterion["value"] = criterion["value"].encode('utf-8')
        crit = C.Criteria(criterion["name"].encode('utf-8'), criterion["value"])
        criteria_list.append(crit)
    return get_wines_by_criteria(criteria_list, limit)
