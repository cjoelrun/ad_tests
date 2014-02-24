import sys
import yaml
import unittest
from random import randint
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import Data


class Authenticate(FunkLoadTestCase):
    """ Authenticates with a random user """
    f = open('config.yaml')
    users = yaml.safe_load(f)['users']

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def test_authenticate(self):
        server_url = self.server_url
        creds = self.users[randint(0, len(self.users)-1)]
        user, password, tenant = creds.split(':')
        data = '{{"auth":{{"passwordCredentials": {{"username": "{user}", "password": "{password}"}}, "tenantName": "{tenant}"}}}}'.format(user=user,
                                                                                                                                           password=password,
                                                                                                                                           tenant=tenant)
        ret = self.post(self.server_url + "/v2.0/tokens", params=Data('application/json', data), description="Authenticate with user")
        self.assert_(ret.code in [200, 203], "expecting 200 or 203")

if __name__ in ('main', '__main__'):
    unittest.main()
