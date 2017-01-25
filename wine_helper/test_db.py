# coding: utf-8

import unittest

from db_tools import *
from mongoengine import connect






_MONGODB_NAME = 'test_db'
_MONGODB_HOST = 'localhost'
connect(_MONGODB_NAME, host=_MONGODB_HOST)

class Dbtest(unittest.TestCase):

    def test_add_user(self):
        create_user("1")
        create_user("2")
        create_user("3")
        create_user("3")
        users = get_users()
        self.assertEqual(len(users),3)
        self.assertEqual(users[0].user_id,"1")
        self.assertEqual(users[1].user_id,"2")
        self.assertEqual(users[2].user_id,"3")
        self.assertFalse(users[0] is None)
        delete_users()

    def test_get_user(self):
        fbid = "1"
        create_user(fbid)
        user = get_user_by_id(fbid)
        no_user = get_user_by_id(-1)
        self.assertFalse(user is None)
        self.assertTrue(no_user is None)
        delete_users()

    def test_create_criterion(self):
        fbid = "1"
        criterion1 = {"name":"color","value":"rouge"}
        criterion2 = {"name":"price","value":"10"}
        create_user(fbid)
        create_criterion(fbid,criterion1)
        user = get_user_by_id(fbid)
        self.assertTrue(user.current_search.criteria[0]["name"] == "color")
        self.assertTrue(user.current_search.criteria[0]["value"] == "rouge")
        create_criterion(fbid,criterion2)
        user = get_user_by_id(fbid)
        self.assertTrue(user.current_search.criteria[1]["name"] == "price")
        self.assertTrue(user.current_search.criteria[1]["value"] == "10")
        criterion1["value"] = "blanc"
        create_criterion(fbid,criterion1)
        user = get_user_by_id(fbid)
        self.assertTrue(user.current_search.criteria[0]["name"] == "color")
        self.assertTrue(user.current_search.criteria[0]["value"] == "blanc")
        delete_users()

    def test_get_criteria_by_id(self):
        fbid = "1"
        create_user(fbid)
        criterion1 = {"name":"color","value":"rouge"}
        criterion2 = {"name":"price","value":"10"}
        create_criterion(fbid,criterion1)
        create_criterion(fbid,criterion2)
        criterion1 = {"name":"color","value":"blanc"}
        create_criterion(fbid,criterion1)
        criteria = get_criteria_data_by_id(fbid)
        self.assertEqual(len(criteria),2)
        delete_users()

    def test_close_search(self):
        fbid = "1"
        create_user(fbid)
        criterion1 = {"name":"color","value":"rouge"}
        criterion2 = {"name":"price","value":"10"}
        create_criterion(fbid,criterion1)
        create_criterion(fbid,criterion1)
        user = get_user_by_id(fbid)
        old_search = user.current_search
        close_search(fbid)
        user = get_user_by_id(fbid)
        self.assertTrue(user.current_search["criteria"] == [])
        self.assertTrue(user.searches[len(user.searches) - 1] == old_search)

if __name__ == '__main__':
    unittest.main()
