#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main for Running the Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
from discordplays import version_info
from discordplays.config import TOKEN
from discordplays.discordBot import Bot

# Set up the bot
description = "Interface to emulators."
description += "\n Version: {}.{}.{}".format(version_info.major, version_info.minor, version_info.micro)
bot = Bot('.', description=description, case_insensitive=True)

# Run the bot
bot.run(TOKEN)

