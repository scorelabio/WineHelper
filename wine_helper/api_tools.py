#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests as re
import Wine as W
import Criteria as C

# "Constants" (variables that should not change)
API_BASE_URL = "http://wine-helper-fake-api.herokuapp.com/public/api/wines"

# Warning: takes only color in French
def get_wines_by_criteria(criteria):
    """
    Makes an API call with the given criteria and returns a list of wines
    (class Wine)
    """
    url = API_BASE_URL
    query = ""
    if criteria:
        query += "?"
    for criterion in criteria:
        # TODO: remove last &
        query += criterion.get_name() + "=" + criterion.get_value() + "&"
    url += query

    response = re.get(url)
    data = response.json()
    wine_list = []
    for wine in data:
        wine_object = W.Wine(
            wine['appellation'].encode('utf-8'),
            wine['name'].encode('utf-8'),
            wine['color']['fr'].encode('utf-8'), # TODO: handle English case too
            wine['vintage'],
            wine['price'],
            wine['globalScore']
        )
        wine_list.append(wine_object)
    return wine_list
