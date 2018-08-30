# Copyright (C) 2013-2015 The python-gozerlib developers
#
# This file is part of python-gozerlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-gozerlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from gozer.wallet import CGozerSecret
from gozer.signmessage import GozerMessage, VerifyMessage, SignMessage
import sys
import os
import json

_bchr = chr
_bord = ord
if sys.version > '3':
    long = int
    _bchr = lambda x: bytes([x])
    _bord = lambda x: x

def load_test_vectors(name):
    with open(os.path.dirname(__file__) + '/data/' + name, 'r') as fd:
        return json.load(fd)


class Test_SignVerifyMessage(unittest.TestCase):
    def test_verify_message_simple(self):
        address = "1F26pNMrywyZJdr22jErtKcjF8R3Ttt55G"
        message = address
        signature = "H85WKpqtNZDrajOnYDgUY+abh0KCAcOsAIOQwx2PftAbLEPRA7mzXA/CjXRxzz0MC225pR/hx02Vf2Ag2x33kU4="

        message = GozerMessage(message)

        self.assertTrue(VerifyMessage(address, message, signature))

    def test_verify_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            message = GozerMessage(vector['address'])
            self.assertTrue(VerifyMessage(vector['address'], message, vector['signature']))

    def test_sign_message_simple(self):
        key = CGozerSecret("L4vB5fomsK8L95wQ7GFzvErYGht49JsCPJyJMHpB4xGM6xgi2jvG")
        address = "1F26pNMrywyZJdr22jErtKcjF8R3Ttt55G"
        message = address

        message = GozerMessage(message)
        signature = SignMessage(key, message)

        self.assertTrue(signature)
        self.assertTrue(VerifyMessage(address, message, signature))

    def test_sign_message_vectors(self):
        for vector in load_test_vectors('signmessage.json'):
            key = CGozerSecret(vector['wif'])
            message = GozerMessage(vector['address'])

            signature = SignMessage(key, message)

            self.assertTrue(signature, "Failed to sign for [%s]" % vector['address'])
            self.assertTrue(VerifyMessage(vector['address'], message, vector['signature']), "Failed to verify signature for [%s]" % vector['address'])


if __name__ == "__main__":
    unittest.main()
