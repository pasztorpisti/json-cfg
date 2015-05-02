"""
These tests contain real-life-ish code snippets with different
problematic input configs that should cause the expected errors.
"""

from unittest import TestCase
from jsoncfg import loads_config, expect_object, expect_array, JSONConfigNodeTypeError


class ServerConfigLoader(object):
    """
    This is the workhorse that we will use with different
    input configs for testing.
    """
    def __init__(self, json_string):
        self.logs = []
        self.cfg = loads_config(json_string)

    def __call__(self):
        self._load_servers(expect_array(self.cfg.servers))
        self._load_users(expect_object(self.cfg.users))
        return self.logs

    def _log(self, msg):
        self.logs.append(msg)

    def _load_servers(self, servers_cfg):
        for server_cfg in servers_cfg:
            expect_object(server_cfg)
            self._log('%s|%s|%s' % (server_cfg.ip_address(), server_cfg.port(8000),
                                    server_cfg.wwwroot()))

    def _load_users(self, users_cfg):
        for username, user_cfg in users_cfg:
            expect_object(user_cfg)
            self._log('%s|%s|%s' % (username, user_cfg.password(), user_cfg.is_admin(False)))


class TestServerConfigExample(TestCase):
    def test_successful_loading(self):
        cfg = """
            {
                servers: [
                    {
                        ip_address: "127.0.0.1",
                        // The port is optional and defaults to 8000
                        //port: 8080,
                        wwwroot: "/home/tron/www/root0",
                    },
                    {
                        ip_address: "127.0.0.1",
                        port: 8081,
                        wwwroot: "/home/tron/www/root1",
                    }
                ],
                users: {
                    tron: {
                        password: "trons_hashed_pwd",
                        is_admin: true,
                    },
                    tom: {
                        password: "toms_hashed_pwd",
                        // is_admin is optional, the config loader uses a default of false
                        // is_admin: false,
                    },
                    "jerry the mouse": {
                        password: "jerrys_hashed_pwd",
                        is_admin: false,
                    },
                },
            }"""

        logs = ServerConfigLoader(cfg)()
        self.assertSetEqual(set(logs), {
            '127.0.0.1|8000|/home/tron/www/root0',
            '127.0.0.1|8081|/home/tron/www/root1',
            'tron|trons_hashed_pwd|True',
            'tom|toms_hashed_pwd|False',
            'jerry the mouse|jerrys_hashed_pwd|False',
        })

    def test_servers_is_not_list(self):
        cfg = '{servers: {}, users: {}}'
        self.assertRaises(JSONConfigNodeTypeError, ServerConfigLoader(cfg))

    def test_users_is_not_dict(self):
        cfg = '{servers: [], users: []}'
        self.assertRaises(JSONConfigNodeTypeError, ServerConfigLoader(cfg))
