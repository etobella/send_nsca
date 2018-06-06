import io

import six
from unittest import TestCase

import send_nsca

from .. import util


class TestConfig(TestCase):
    def setUp(self):
        self.sender = send_nsca.nsca.NscaSender(b"test_host", config_path=None)

    def test_ignores_comments(self):
        stream = io.BytesIO()
        stream.write(b"""
password = 1234
# password = 2345
        """)
        self.sender.parse_config(stream)
        self.assertEqual(self.sender.password, b"1234")

    def test_password_limits(self):
        stream = io.BytesIO()
        stream.write(b"password = ")
        stream.write(util.get_chrs(513))
        stream.write(b"\n")
        self.assertRaises(send_nsca.nsca.ConfigParseError, self.sender.parse_config, stream)

    def test_yells_at_random_keys(self):
        stream = io.BytesIO()
        stream.write(b"foo = bar\n")
        self.assertRaises(send_nsca.nsca.ConfigParseError, self.sender.parse_config, stream)

    def test_get_encryption_method(self):
        # map from crypter id to whether or not it should succeed
        crypters = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: False,
            6: False,
            7: False,
            8: True,
            9: False,
            10: False,
            14: True,
            15: True,
            16: True,
            255: False
        }
        for crypter, success in crypters.items():
            stream = io.BytesIO()
            stream.write(
                "encryption_method = {0}\n".format(crypter).encode('UTF-8'),
            )
            if success:
                self.sender.parse_config(stream)
                self.assertEqual(self.sender.encryption_method_i, crypter)
            else:
                self.assertRaises(send_nsca.nsca.ConfigParseError, self.sender.parse_config, stream)
