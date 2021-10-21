
from unittest import TestCase, skip
from flask_restx import Resource, Api

import API.endpoints as ep

HELLO = 'Hola'
WORLD = 'mundo'

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
