"""
This file holds the tests for endpoints.py
"""

from unittest import TestCase, skip
from flask_restx import Resource, Api
import random

import API.endpoints as ep
import db.data as db

HUGE_NUM = 1000000000

def new_entity_name(entity_type):
    int_name = random.randint(0,HUGE_NUM)
    return f"new {entity_type}" + str(int_name)


class EndpointTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        hello = ep.HelloWorld(Resource)
        ret = hello.get()
        self.assertIsInstance(ret, dict)
        self.assertIn(ep.HELLO, ret)

    def test_create_user(self):
        """
        Post-condition 1: create user and check if in db
        """
        cu = ep.CreateUser(Resource)
        new_user = new_entity_name("user")
        ret = cu.post(new_user)
        users = db.get_users()
        self.assertIn(new_user, users)


    def test_list_users1(self):
        """
        Post-condition 1: return is a dictionary.
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        self.assertIsInstance(ret, dict)

    def test_list_users2(self):
        """
        Post-condition 2: keys to the dict are strings
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for key in ret:
            self.assertIsInstance(key, str)

    def test_list_users3(self):
        """
        Post-condition 3: the values in the dict are themselves dicts
        """
        lu = ep.ListUsers(Resource)
        ret = lu.get()
        for val in ret.values():
            self.assertIsInstance(val, dict)
