#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main for Running the Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""

from discordplayspyboy.config import TOKEN
from discordplayspyboy.discordBot import Client

# Set up the client
client = Client()

# Run the client
client.run(TOKEN)
