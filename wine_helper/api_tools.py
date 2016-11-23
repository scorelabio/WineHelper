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
        wine_object = W.Wine(wine['appellation'],wine['name'],wine['color'],wine['vintage'],
                            wine['price'],wine['global_score'])
        wine_list.append(wine_object)
    return wine_list


criteria = []
criteria.append(C.Criteria("color", "red"))
criteria.append(C.Criteria("priceMin", "50"))

print(get_wines_by_criteria(criteria))
