#!/usr/bin/env python3

# Copyright (C) 2014 The python-gozerlib developers
#
# This file is part of python-gozerlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-gozerlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

"""Serialize some gozer datastructures and show them in serialized and repr form."""

import sys
if sys.version_info.major < 3:
    sys.stderr.write('Sorry, Python 3.x required by this example.\n')
    sys.exit(1)

from gozer import SelectParams
from gozer.messages import msg_version, msg_tx, msg_block

SelectParams('mainnet')


for c in [msg_version, msg_tx, msg_block]:
    # Instanciate the message with some default values
    msg = c()
    name = c.__name__
    print(name + " repr:")
    print(msg)
    print(name + " serialized:")
    print(msg.to_bytes())
