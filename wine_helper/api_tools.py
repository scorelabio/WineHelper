# coding: utf8
from __future__ import unicode_literals

import requests as re
import Wine as W
import Criteria as C

def get_api_base_url ():
    return "http://hiti.ifenua.net/api/wines"


def get_wines_by_criteria(criteria):
    url = get_api_base_url()
    query = ""
    if criteria:
        query += "?"
    for criterion in criteria:
        query += criterion.get_name() + "=" + criterion.get_value() + "&"
    url += query
    response = re.get(url)
    data = response.json()
    wine_list = []
    for wine in data:
        wine_object = W.Wine(wine['appellation'].encode("ascii","ignore"),wine['name'].encode("ascii","ignore"),wine['color'],wine['vintage'],
                            wine['price'],wine['global_score'])
        wine_list.append(wine_object)
    return wine_list


criteria = []
criteria.append(C.Criteria("color", "rouge"))

print(get_wines_by_criteria(criteria))
