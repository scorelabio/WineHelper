# -*- coding: utf-8 -*-

# System dependencies
from pprint import pprint

from models import Criterion, Search, User


def get_users ():
    """
    TODO: write description
    """
    try:
        users = User.objects.all()
        return users
    except User.DoesNotExist:
        return []


def get_user_by_id(fbid):
    """
    TODO: get description
    """
    try:
        user = User.objects.get(user_id=fbid)
    except User.DoesNotExist:
        user = None
    return user

def delete_users():
    """
    TODO: write description
    """
    User.drop_collection()

def create_user(fbid):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is None:
        user = User(user_id=fbid, current_search=Search(criteria=[],user_storyline=None), searches=[])
        user.save()



def create_storyline(fbid,storyline):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is not None:
        user.current_search.user_storyline = storyline
        user.update(current_search=user.current_search)
        user.save()


def get_storyline_by_user_id(fbid):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is not None:
        return user.current_search.user_storyline
    else:
        return None


def create_last_step(fbid, last_step):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is not None:
        user.current_search.user_last_step = last_step
        user.update(current_search=user.current_search)
        user.save()


def get_last_step_by_user_id(fbid):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is not None:
        return user.current_search.user_last_step
    else:
        return None


def close_search(fbid):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    if user is not None:
        if user.current_search is not None:
            user.searches.append(user.current_search)
            user.current_search = Search(criteria=[],user_storyline=None)
            user.update(current_search=user.current_search)
            user.save()


def create_criterion(fbid, criterion):
    """
    TODO: write description
    """
    user = get_user_by_id(fbid)
    is_created = False
    to_delete_criterion = -1
    if user is not None:
        for i in range(len(user.current_search.criteria)):
            if user.current_search.criteria[i]["name"] == criterion["name"]:
                is_created = True
                if criterion["value"] is None:
                    to_delete_criterion = i
                else:
                    user.current_search.criteria[i]["value"] = criterion["value"]
                    user.update(current_search=user.current_search)
        if (to_delete_criterion != -1):
            del user.current_search.criteria[to_delete_criterion]
            user.update(current_search=user.current_search)
        if not is_created:
            if criterion["value"] is not None:
                cr = Criterion(criterion["name"], criterion["value"])
                user.current_search.criteria.append(cr)
        user.save()


def get_criteria_data_by_id (fbid):
    """
    get current criteria: a list/array of all the criteria of the current search
    """
    user = get_user_by_id (fbid)
    if user is not None:
        return user.current_search.criteria
    else:
        return None
