#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main for Running the Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
from discordplays.discordBot import bot

# Read the token
with open('token.txt') as f:
  # Strip the newline chracter
  token = f.read().rstrip()

# Run the bot
bot.run(token)

