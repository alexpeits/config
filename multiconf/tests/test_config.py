import unittest

from multiconf.main import Config


test_conf = """
[main]
database=postgres
scheme=testing
debug=True

[testing]
username=user_testing
password=pw_testing
path=${main:database}://${username}:${password}

[production]
username=user_prod
password=pw_prod
path=${main:database}://${username}:${password}
"""


class TestConfig(unittest.TestCase):
    def test_all(self):
        conf = Config(test_conf)
        self.assertEqual(conf('database'), 'postgres')
        self.assertEqual(conf('scheme'), 'testing')
        self.assertEqual(conf('path'), 'postgres://user_testing:pw_testing')
        self.assertEqual(conf('password', section='production'), 'pw_prod')
        self.assertTrue(conf('debug', section='main'))
