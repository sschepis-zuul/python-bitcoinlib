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
    MESSAGE_START = b'\xfb\xcd\xbe\xdb'
    DEFAULT_PORT = 8888
    RPC_PORT = 8887
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':38,
                       'SCRIPT_ADDR':16,
                       'SECRET_KEY' :204}

class TestNetParams(gozer.core.CoreTestNetParams):
    MESSAGE_START = b'\xfb\xfa\xdc\xff'
    DEFAULT_PORT = 18888
    RPC_PORT = 18887
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':98,
                       'SCRIPT_ADDR':19,
                       'SECRET_KEY' :239}

class DevNetParams(gozer.core.CoreDevNetParams):
    MESSAGE_START = b'\xfb\xac\xfb\xec'
    DEFAULT_PORT = 18881
    RPC_PORT = 18880
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':98,
                       'SCRIPT_ADDR':19,
                       'SECRET_KEY' :239}

class RegTestParams(gozer.core.CoreRegTestParams):
    MESSAGE_START = b'\xfb\xcf\xbf\xfc'
    DEFAULT_PORT = 18884
    RPC_PORT = 18883
    DNS_SEEDS = ()
    BASE58_PREFIXES = {'PUBKEY_ADDR':98,
                       'SCRIPT_ADDR':19,
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
    elif name == 'devnet':
        params = gozer.core.coreparams = DevNetParams()
    elif name == 'regtest':
        params = gozer.core.coreparams = RegTestParams()
    else:
        raise ValueError('Unknown chain %r' % name)
