
from unittest import TestCase, skip
from flask_restx import Resource, Api
import random

import API.endpoints as ep
import db.db as db

HELLO = 'Hola'
WORLD = 'mundo'

HUGE_NUM = 1000000000
def random_username():
    random_num = random.randint(0,HUGE_NUM)
    return "User" + str(random_num)


class EndpointTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_hello(self):
        hello = ep.HelloWorld(Resource)
        ret = hello.get()
        self.assertIsInstance(ret, dict)
        self.assertIn(HELLO, ret)

    def test_create_user(self):
        """
        Post-condition 1: create user and check if in db
        """
        cu = ep.CreateUser(Resource)
        new_user = random_username()
        ret = cu.post(new_user)
        users = db.get_users()
        self.assertIn(new_user, users)


