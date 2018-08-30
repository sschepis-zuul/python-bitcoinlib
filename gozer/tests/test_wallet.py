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

from gozer.core import b2x, x
from gozer.core.script import CScript, IsLowDERSignature
from gozer.core.key import CPubKey
from gozer.wallet import *

class Test_CGozerAddress(unittest.TestCase):
    def test_create_from_string(self):
        """Create CGozerAddress's from strings"""

        def T(str_addr, expected_bytes, expected_nVersion, expected_class):
            addr = CGozerAddress(str_addr)
            self.assertEqual(addr.to_bytes(), expected_bytes)
            self.assertEqual(addr.nVersion, expected_nVersion)
            self.assertEqual(addr.__class__, expected_class)

        T('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
          x('62e907b15cbf27d5425399ebf6f0fb50ebb88f18'), 0,
          P2PKHGozerAddress)

        T('37k7toV1Nv4DfmQbmZ8KuZDQCYK9x5KpzP',
          x('4266fc6f2c2861d7fe229b279a79803afca7ba34'), 5,
          P2SHGozerAddress)

    def test_wrong_nVersion(self):
        """Creating a CGozerAddress from a unknown nVersion fails"""

        # tests run in mainnet, so both of the following should fail
        with self.assertRaises(CGozerAddressError):
            CGozerAddress('mpXwg4jMtRhuSpVq4xS3HFHmCmWp9NyGKt')

        with self.assertRaises(CGozerAddressError):
            CGozerAddress('2MyJKxYR2zNZZsZ39SgkCXWCfQtXKhnWSWq')

    def test_from_scriptPubKey(self):
        def T(hex_scriptpubkey, expected_str_address, expected_class):
            scriptPubKey = CScript(x(hex_scriptpubkey))
            addr = CGozerAddress.from_scriptPubKey(scriptPubKey)
            self.assertEqual(str(addr), expected_str_address)
            self.assertEqual(addr.__class__, expected_class)

        T('a914000000000000000000000000000000000000000087', '31h1vYVSYuKP6AhS86fbRdMw9XHieotbST',
          P2SHGozerAddress)
        T('76a914000000000000000000000000000000000000000088ac', '1111111111111111111114oLvT2',
          P2PKHGozerAddress)

    def test_from_nonstd_scriptPubKey(self):
        """CGozerAddress.from_scriptPubKey() with non-standard scriptPubKeys"""

        # Bad P2SH scriptPubKeys

        # non-canonical pushdata
        scriptPubKey = CScript(x('a94c14000000000000000000000000000000000000000087'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

        # Bad P2PKH scriptPubKeys

        # Missing a byte
        scriptPubKey = CScript(x('76a914000000000000000000000000000000000000000088'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

        # One extra byte
        scriptPubKey = CScript(x('76a914000000000000000000000000000000000000000088acac'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

        # One byte changed
        scriptPubKey = CScript(x('76a914000000000000000000000000000000000000000088ad'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

    def test_from_invalid_scriptPubKey(self):
        """CGozerAddress.from_scriptPubKey() with invalid scriptPubKeys"""

        # We should raise a CGozerAddressError, not any other type of error

        # Truncated P2SH
        scriptPubKey = CScript(x('a91400000000000000000000000000000000000000'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

        # Truncated P2PKH
        scriptPubKey = CScript(x('76a91400000000000000000000000000000000000000'))
        with self.assertRaises(CGozerAddressError):
            CGozerAddress.from_scriptPubKey(scriptPubKey)

    def test_to_scriptPubKey(self):
        """CGozerAddress.to_scriptPubKey() works"""
        def T(str_addr, expected_scriptPubKey_hexbytes):
            addr = CGozerAddress(str_addr)

            actual_scriptPubKey = addr.to_scriptPubKey()
            self.assertEqual(b2x(actual_scriptPubKey), expected_scriptPubKey_hexbytes)

        T('31h1vYVSYuKP6AhS86fbRdMw9XHieotbST',
          'a914000000000000000000000000000000000000000087')

        T('1111111111111111111114oLvT2',
          '76a914000000000000000000000000000000000000000088ac')

class Test_P2SHGozerAddress(unittest.TestCase):
    def test_from_redeemScript(self):
        addr = P2SHGozerAddress.from_redeemScript(CScript())
        self.assertEqual(str(addr), '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy')

class Test_P2PKHGozerAddress(unittest.TestCase):
    def test_from_non_canonical_scriptPubKey(self):
        def T(hex_scriptpubkey, expected_str_address):
            scriptPubKey = CScript(x(hex_scriptpubkey))
            addr = P2PKHGozerAddress.from_scriptPubKey(scriptPubKey)
            self.assertEqual(str(addr), expected_str_address)

            # now test that CGozerAddressError is raised with accept_non_canonical_pushdata=False
            with self.assertRaises(CGozerAddressError):
                P2PKHGozerAddress.from_scriptPubKey(scriptPubKey, accept_non_canonical_pushdata=False)

        T('76a94c14000000000000000000000000000000000000000088ac', '1111111111111111111114oLvT2')
        T('76a94d1400000000000000000000000000000000000000000088ac', '1111111111111111111114oLvT2'),
        T('76a94e14000000000000000000000000000000000000000000000088ac', '1111111111111111111114oLvT2')

        # make sure invalid scripts raise CGozerAddressError
        with self.assertRaises(CGozerAddressError):
            P2PKHGozerAddress.from_scriptPubKey(x('76a94c14'))

    def test_from_bare_checksig_scriptPubKey(self):
        def T(hex_scriptpubkey, expected_str_address):
            scriptPubKey = CScript(x(hex_scriptpubkey))
            addr = P2PKHGozerAddress.from_scriptPubKey(scriptPubKey)
            self.assertEqual(str(addr), expected_str_address)

            # now test that CGozerAddressError is raised with accept_non_canonical_pushdata=False
            with self.assertRaises(CGozerAddressError):
                P2PKHGozerAddress.from_scriptPubKey(scriptPubKey, accept_bare_checksig=False)

        # compressed
        T('21000000000000000000000000000000000000000000000000000000000000000000ac', '14p5cGy5DZmtNMQwTQiytBvxMVuTmFMSyU')

        # uncompressed
        T('410000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ac', '1QLFaVVt99p1y18zWSZnespzhkFxjwBbdP')

        # non-canonical encoding
        T('4c21000000000000000000000000000000000000000000000000000000000000000000ac', '14p5cGy5DZmtNMQwTQiytBvxMVuTmFMSyU')

        # odd-lengths are *not* accepted
        with self.assertRaises(CGozerAddressError):
            P2PKHGozerAddress.from_scriptPubKey(x('2200000000000000000000000000000000000000000000000000000000000000000000ac'))

    def test_from_valid_pubkey(self):
        """Create P2PKHGozerAddress's from valid pubkeys"""

        def T(pubkey, expected_str_addr):
            addr = P2PKHGozerAddress.from_pubkey(pubkey)
            self.assertEqual(str(addr), expected_str_addr)

        T(x('0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71'),
          '1C7zdTfnkzmr13HfA2vNm5SJYRK6nEKyq8')
        T(x('0478d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71a1518063243acd4dfe96b66e3f2ec8013c8e072cd09b3834a19f81f659cc3455'),
          '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T')

        T(CPubKey(x('0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71')),
          '1C7zdTfnkzmr13HfA2vNm5SJYRK6nEKyq8')
        T(CPubKey(x('0478d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71a1518063243acd4dfe96b66e3f2ec8013c8e072cd09b3834a19f81f659cc3455')),
          '1JwSSubhmg6iPtRjtyqhUYYH7bZg3Lfy1T')

    def test_from_invalid_pubkeys(self):
        """Create P2PKHGozerAddress's from invalid pubkeys"""

        # first test with accept_invalid=True
        def T(invalid_pubkey, expected_str_addr):
            addr = P2PKHGozerAddress.from_pubkey(invalid_pubkey, accept_invalid=True)
            self.assertEqual(str(addr), expected_str_addr)

        T(x(''),
          '1HT7xU2Ngenf7D4yocz2SAcnNLW7rK8d4E')
        T(x('0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c72'),
          '1L9V4NXbNtZsLjrD3nkU7gtEYLWRBWXLiZ')

        # With accept_invalid=False we should get CGozerAddressError's
        with self.assertRaises(CGozerAddressError):
            P2PKHGozerAddress.from_pubkey(x(''))
        with self.assertRaises(CGozerAddressError):
            P2PKHGozerAddress.from_pubkey(x('0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c72'))
        with self.assertRaises(CGozerAddressError):
            P2PKHGozerAddress.from_pubkey(CPubKey(x('0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c72')))

class Test_CGozerSecret(unittest.TestCase):
    def test(self):
        def T(base58_privkey, expected_hex_pubkey, expected_is_compressed_value):
            key = CGozerSecret(base58_privkey)
            self.assertEqual(b2x(key.pub), expected_hex_pubkey)
            self.assertEqual(key.is_compressed, expected_is_compressed_value)

        T('5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS',
          '0478d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71a1518063243acd4dfe96b66e3f2ec8013c8e072cd09b3834a19f81f659cc3455',
          False)
        T('L3p8oAcQTtuokSCRHQ7i4MhjWc9zornvpJLfmg62sYpLRJF9woSu',
          '0378d430274f8c5ec1321338151e9f27f4c676a008bdf8638d07c0b6be9ab35c71',
          True)

    def test_sign(self):
        key = CGozerSecret('5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS')
        hash = b'\x00' * 32
        sig = key.sign(hash)

        # Check a valid signature
        self.assertTrue(key.pub.verify(hash, sig))
        self.assertTrue(IsLowDERSignature(sig))

        # Check that invalid hash returns false
        self.assertFalse(key.pub.verify(b'\xFF'*32, sig))

        # Check that invalid signature returns false.
        #
        # Note the one-in-four-billion chance of a false positive :)
        self.assertFalse(key.pub.verify(hash, sig[0:-4] + b'\x00\x00\x00\x00'))

    def test_sign_invalid_hash(self):
        key = CGozerSecret('5KJvsngHeMpm884wtkJNzQGaCErckhHJBGFsvd3VyK5qMZXj3hS')
        with self.assertRaises(TypeError):
          sig = key.sign('0' * 32)

        hash = b'\x00' * 32
        with self.assertRaises(ValueError):
          sig = key.sign(hash[0:-2])
