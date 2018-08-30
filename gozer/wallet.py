# Copyright (C) 2012-2014 The python-gozerlib developers
#
# This file is part of python-gozerlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-gozerlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Wallet-related functionality

Includes things like representing addresses and converting them to/from
scriptPubKeys; currently there is no actual wallet support implemented.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys

_bord = ord
if sys.version > '3':
    _bord = lambda x: x

import gozer
import gozer.base58
import gozer.core
import gozer.core.key
import gozer.core.script as script

class CGozerAddressError(gozer.base58.Base58Error):
    """Raised when an invalid Gozer address is encountered"""

class CGozerAddress(gozer.base58.CBase58Data):
    """A Gozer address"""

    @classmethod
    def from_bytes(cls, data, nVersion):
        self = super(CGozerAddress, cls).from_bytes(data, nVersion)

        if nVersion == gozer.params.BASE58_PREFIXES['SCRIPT_ADDR']:
            self.__class__ = P2SHGozerAddress

        elif nVersion == gozer.params.BASE58_PREFIXES['PUBKEY_ADDR']:
            self.__class__ = P2PKHGozerAddress

        else:
           raise CGozerAddressError('Version %d not a recognized Gozer Address' % nVersion)

        return self

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a CGozerAddress

        Returns a CGozerAddress subclass, either P2SHGozerAddress or
        P2PKHGozerAddress. If the scriptPubKey is not recognized
        CGozerAddressError will be raised.
        """
        try:
            return P2SHGozerAddress.from_scriptPubKey(scriptPubKey)
        except CGozerAddressError:
            pass

        try:
            return P2PKHGozerAddress.from_scriptPubKey(scriptPubKey)
        except CGozerAddressError:
            pass

        raise CGozerAddressError('scriptPubKey not a valid address')

    def to_scriptPubKey(self):
        """Convert an address to a scriptPubKey"""
        raise NotImplementedError

class P2SHGozerAddress(CGozerAddress):
    @classmethod
    def from_bytes(cls, data, nVersion=None):
        if nVersion is None:
            nVersion = gozer.params.BASE58_PREFIXES['SCRIPT_ADDR']

        elif nVersion != gozer.params.BASE58_PREFIXES['SCRIPT_ADDR']:
            raise ValueError('nVersion incorrect for P2SH address: got %d; expected %d' % \
                                (nVersion, gozer.params.BASE58_PREFIXES['SCRIPT_ADDR']))

        return super(P2SHGozerAddress, cls).from_bytes(data, nVersion)

    @classmethod
    def from_redeemScript(cls, redeemScript):
        """Convert a redeemScript to a P2SH address

        Convenience function: equivalent to P2SHGozerAddress.from_scriptPubKey(redeemScript.to_p2sh_scriptPubKey())
        """
        return cls.from_scriptPubKey(redeemScript.to_p2sh_scriptPubKey())

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey):
        """Convert a scriptPubKey to a P2SH address

        Raises CGozerAddressError if the scriptPubKey isn't of the correct
        form.
        """
        if scriptPubKey.is_p2sh():
            return cls.from_bytes(scriptPubKey[2:22], gozer.params.BASE58_PREFIXES['SCRIPT_ADDR'])

        else:
            raise CGozerAddressError('not a P2SH scriptPubKey')

    def to_scriptPubKey(self):
        """Convert an address to a scriptPubKey"""
        assert self.nVersion == gozer.params.BASE58_PREFIXES['SCRIPT_ADDR']
        return script.CScript([script.OP_HASH160, self, script.OP_EQUAL])

class P2PKHGozerAddress(CGozerAddress):
    @classmethod
    def from_bytes(cls, data, nVersion=None):
        if nVersion is None:
            nVersion = gozer.params.BASE58_PREFIXES['PUBKEY_ADDR']

        elif nVersion != gozer.params.BASE58_PREFIXES['PUBKEY_ADDR']:
            raise ValueError('nVersion incorrect for P2PKH address: got %d; expected %d' % \
                                (nVersion, gozer.params.BASE58_PREFIXES['PUBKEY_ADDR']))

        return super(P2PKHGozerAddress, cls).from_bytes(data, nVersion)

    @classmethod
    def from_pubkey(cls, pubkey, accept_invalid=False):
        """Create a P2PKH gozer address from a pubkey

        Raises CGozerAddressError if pubkey is invalid, unless accept_invalid
        is True.

        The pubkey must be a bytes instance; CECKey instances are not accepted.
        """
        if not isinstance(pubkey, bytes):
            raise TypeError('pubkey must be bytes instance; got %r' % pubkey.__class__)

        if not accept_invalid:
            if not isinstance(pubkey, gozer.core.key.CPubKey):
                pubkey = gozer.core.key.CPubKey(pubkey)
            if not pubkey.is_fullyvalid:
                raise CGozerAddressError('invalid pubkey')

        pubkey_hash = gozer.core.Hash160(pubkey)
        return P2PKHGozerAddress.from_bytes(pubkey_hash)

    @classmethod
    def from_scriptPubKey(cls, scriptPubKey, accept_non_canonical_pushdata=True, accept_bare_checksig=True):
        """Convert a scriptPubKey to a P2PKH address

        Raises CGozerAddressError if the scriptPubKey isn't of the correct
        form.

        accept_non_canonical_pushdata - Allow non-canonical pushes (default True)

        accept_bare_checksig          - Treat bare-checksig as P2PKH scriptPubKeys (default True)
        """
        if accept_non_canonical_pushdata:
            # Canonicalize script pushes
            scriptPubKey = script.CScript(scriptPubKey) # in case it's not a CScript instance yet

            try:
                scriptPubKey = script.CScript(tuple(scriptPubKey)) # canonicalize
            except gozer.core.script.CScriptInvalidError:
                raise CGozerAddressError('not a P2PKH scriptPubKey: script is invalid')

        if scriptPubKey.is_witness_v0_keyhash():
            return cls.from_bytes(scriptPubKey[2:22], gozer.params.BASE58_PREFIXES['PUBKEY_ADDR'])
        elif scriptPubKey.is_witness_v0_nested_keyhash():
            return cls.from_bytes(scriptPubKey[3:23], gozer.params.BASE58_PREFIXES['PUBKEY_ADDR'])
        elif (len(scriptPubKey) == 25
                and _bord(scriptPubKey[0])  == script.OP_DUP
                and _bord(scriptPubKey[1])  == script.OP_HASH160
                and _bord(scriptPubKey[2])  == 0x14
                and _bord(scriptPubKey[23]) == script.OP_EQUALVERIFY
                and _bord(scriptPubKey[24]) == script.OP_CHECKSIG):
            return cls.from_bytes(scriptPubKey[3:23], gozer.params.BASE58_PREFIXES['PUBKEY_ADDR'])

        elif accept_bare_checksig:
            pubkey = None

            # We can operate on the raw bytes directly because we've
            # canonicalized everything above.
            if (len(scriptPubKey) == 35 # compressed
                  and _bord(scriptPubKey[0])  == 0x21
                  and _bord(scriptPubKey[34]) == script.OP_CHECKSIG):

                pubkey = scriptPubKey[1:34]

            elif (len(scriptPubKey) == 67 # uncompressed
                    and _bord(scriptPubKey[0]) == 0x41
                    and _bord(scriptPubKey[66]) == script.OP_CHECKSIG):

                pubkey = scriptPubKey[1:65]

            if pubkey is not None:
                return cls.from_pubkey(pubkey, accept_invalid=True)

        raise CGozerAddressError('not a P2PKH scriptPubKey')

    def to_scriptPubKey(self, nested=False):
        """Convert an address to a scriptPubKey"""
        assert self.nVersion == gozer.params.BASE58_PREFIXES['PUBKEY_ADDR']
        return script.CScript([script.OP_DUP, script.OP_HASH160, self, script.OP_EQUALVERIFY, script.OP_CHECKSIG])

class CKey(object):
    """An encapsulated private key

    Attributes:

    pub           - The corresponding CPubKey for this private key

    is_compressed - True if compressed

    """
    def __init__(self, secret, compressed=True):
        self._cec_key = gozer.core.key.CECKey()
        self._cec_key.set_secretbytes(secret)
        self._cec_key.set_compressed(compressed)

        self.pub = gozer.core.key.CPubKey(self._cec_key.get_pubkey(), self._cec_key)

    @property
    def is_compressed(self):
        return self.pub.is_compressed

    def sign(self, hash):
        return self._cec_key.sign(hash)

    def sign_compact(self, hash):
        return self._cec_key.sign_compact(hash)

class CGozerSecretError(gozer.base58.Base58Error):
    pass

class CGozerSecret(gozer.base58.CBase58Data, CKey):
    """A base58-encoded secret key"""

    @classmethod
    def from_secret_bytes(cls, secret, compressed=True):
        """Create a secret key from a 32-byte secret"""
        self = cls.from_bytes(secret + (b'\x01' if compressed else b''),
                              gozer.params.BASE58_PREFIXES['SECRET_KEY'])
        self.__init__(None)
        return self

    def __init__(self, s):
        if self.nVersion != gozer.params.BASE58_PREFIXES['SECRET_KEY']:
            raise CGozerSecretError('Not a base58-encoded secret key: got nVersion=%d; expected nVersion=%d' % \
                                      (self.nVersion, gozer.params.BASE58_PREFIXES['SECRET_KEY']))

        CKey.__init__(self, self[0:32], len(self) > 32 and _bord(self[32]) == 1)


__all__ = (
        'CGozerAddressError',
        'CGozerAddress',
        'P2SHGozerAddress',
        'P2PKHGozerAddress',
        'CKey',
        'CGozerSecretError',
        'CGozerSecret',
)
