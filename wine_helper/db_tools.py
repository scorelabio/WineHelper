from models import Criterion, Search, User
from pprint import pprint



def get_user_by_id(fbid):
    try:
        user = User.objects.get(user_id=fbid)
    except User.DoesNotExist:
        user = None
    return user


def create_user(fbid):
    user = get_user_by_id(fbid)
    if user is None:
        pprint("[DEBUG][db_tools.py][create_user] user is None")
        user = User(user_id=fbid, current_search=Search(criteria=[]), searches=[])
        user.save()
    else:
        pprint("[DEBUG] create user else")


def close_search(fbid):
    user = get_user_by_id(fbid)
    if user is not None:
        if user.current_search is not None:
            user.searches.append(current_search)
            user.current_search = Search(criteria=[])
            user.modify()
            user.save()


def create_criterion(fbid, criterion):
    user = get_user_by_id(fbid)
    is_created = False
    if user is not None:
        current_search = user.current_search
        pprint("[DEBUG][db_tools.py][create_criterion] current_search")
        pprint(current_search.criteria)
        for c in current_search.criteria:
            if c['name'] == criterion['name']:
                is_created = True
                c['value'] = criterion['value']
                user.modify()
        if not is_created:
            cr = Criterion(criterion["name"], criterion["value"])
            user.current_search.criteria.append(cr)
        user.save()
