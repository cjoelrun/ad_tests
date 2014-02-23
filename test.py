import yaml
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import Data


class Simple(FunkLoadTestCase):
    """This test use a configuration file Simple.conf."""
    f = open('config.yaml')
    users = yaml.safe_load(f)['users']

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def test_simple(self):
        server_url = self.server_url

        user = random.randint(0, len(users)-1)
        data = '{"auth":{"passwordCredentials": {"username": user, "password": "password"}, "tenantName": "demo"}}'
        self.post(self.server_url + "/v2.0/tokens", params=Data('application/json', data) description="Authenticate with user")

if __name__ in ('main', '__main__'):
    unittest.main()
