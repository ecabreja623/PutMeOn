"""
This file holds the tests for token.py
"""

import datetime
from unittest import TestCase
import db.usertoken as token
import datetime

FAKE_USER = "Fake user"
FAKE_PLAYLIST = "Fake playlist"

class DBTestCase(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_blank(self):
        """
        make sure a blank token is created as expected
        """
        self.assertEqual({token.ID: "", token.EXP: ""}, token.blank())

    def test_new1(self):
        """
        make sure a new token has a random string of len 25 for ID
        """
        new = token.new()
        self.assertIsInstance(new[token.ID], str)
        self.assertEqual(22, len(new[token.ID]))

    def test_new2(self):
        """
        make sure new token stores expiration date as string
        """
        new = token.new()
        self.assertIsInstance(new[token.EXP], str)

    def test_check1(self):
        """
        make sure authorization fails when token expired
        """
        exp = token.new()
        days = datetime.timedelta(days = 5)
        date = datetime.datetime.fromisoformat(exp[token.EXP])
        exp[token.EXP] = (date - days).isoformat()
        self.assertFalse(token.check(exp))

    def test_check2(self):
        """
        make sure authorization succeeds when token doesn't expire
        """
        new = token.new()
        self.assertTrue(token.check(new))