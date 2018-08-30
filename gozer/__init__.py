# Copyright (C) 2012-2016 The python-gozerlib developers
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

import gozer.core

# Note that setup.py can break if __init__.py imports any external
# dependencies, as these might not be installed when setup.py runs. In this
# case __version__ could be moved to a separate version.py and imported here.
__version__ = '0.7.1-SNAPSHOT'

class MainParams(gozer.core.CoreMainParams):
    MESSAGE_START = b'\xf9\xbe\xb4\xd9'
    DEFAULT_PORT = 8333
    RPC_PORT = 8332
    DNS_SEEDS = (('gozer.sipa.be', 'seed.gozer.sipa.be'),
                 ('bluematt.me', 'dnsseed.bluematt.me'),
                 ('dashjr.org', 'dnsseed.gozer.dashjr.org'),
                 ('gozerstats.com', 'seed.gozerstats.com'),
                 ('xf2.org', 'bitseed.xf2.org'),
                 ('gozer.jonasschnelli.ch', 'seed.gozer.jonasschnelli.ch'))
    BASE58_PREFIXES = {'PUBKEY_ADDR':0,
                       'SCRIPT_ADDR':5,
                       'SECRET_KEY' :128}

class TestNetParams(gozer.core.CoreTestNetParams):
    MESSAGE_START = b'\x0b\x11\x09\x07'
    DEFAULT_PORT = 18333
    RPC_PORT = 18332
    DNS_SEEDS = (('testnetgozer.jonasschnelli.ch', 'testnet-seed.gozer.jonasschnelli.ch'),
                 ('petertodd.org', 'seed.tgzr.petertodd.org'),
                 ('bluematt.me', 'testnet-seed.bluematt.me'),
                 ('gozer.schildbach.de', 'testnet-seed.gozer.schildbach.de'))
    BASE58_PREFIXES = {'PUBKEY_ADDR':111,
                       'SCRIPT_ADDR':196,
                       'SECRET_KEY' :239}

class RegTestParams(gozer.core.CoreRegTestParams):
    MESSAGE_START = b'\xfa\xbf\xb5\xda'
    DEFAULT_PORT = 18444
    RPC_PORT = 18332
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':111,
                       'SCRIPT_ADDR':196,
                       'SECRET_KEY' :239}

"""Master global setting for what chain params we're using.

However, don't set this directly, use SelectParams() instead so as to set the
gozer.core.params correctly too.
"""
#params = gozer.core.coreparams = MainParams()
params = MainParams()

def SelectParams(name):
    """Select the chain parameters to use

    name is one of 'mainnet', 'testnet', or 'regtest'

    Default chain is 'mainnet'
    """
    global params
    gozer.core._SelectCoreParams(name)
    if name == 'mainnet':
        params = gozer.core.coreparams = MainParams()
    elif name == 'testnet':
        params = gozer.core.coreparams = TestNetParams()
    elif name == 'regtest':
        params = gozer.core.coreparams = RegTestParams()
    else:
        raise ValueError('Unknown chain %r' % name)
