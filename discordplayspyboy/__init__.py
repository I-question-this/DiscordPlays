# -*- coding: utf-8 -*-

"""
Init file for discordplayspyboy
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""

__title__ = 'discordplayspyboy'
__author__ = 'i-question-this'
__license__ = 'GPL-3.0'
__copyright__ = 'Copyright 2019 i-question-this'
__version__ = '0.5.0'

from collections import namedtuple

import discord
import logging

VersionInfo = namedtuple('VersionInfo', 'major minor micro')

version_info = VersionInfo(major=0, minor=5, micro=0)

# Set up logging for Discord
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
