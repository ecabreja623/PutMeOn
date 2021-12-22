"""
This file holds the tests for data.py
"""

from unittest import TestCase, skip

import data as db
from db.data import USERNAME

FAKE_USER = "Fake user"


class DBTestCase(TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_add_user(self):
        """
        Can we write to the user db?
        """
        db.add_user(FAKE_USER)
        user = db.get_user(FAKE_USER)
        self.assertEqual(user[USERNAME],FAKE_USER)


    def test_get_users(self):
        """
        Can we fetch user db?
        """
        users = db.get_users()
        self.assertIsInstance(users, dict)


    def test_get_user(self):
        """
        Can we fetch a user from the user db?
        """
        db.add_user(FAKE_USER)
        user = db.get_user(FAKE_USER)
        self.assertIsInstance(user, dict)
