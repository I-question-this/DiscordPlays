# -*- coding: utf-8 -*-

"""
Configurations for the discord bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import os
from collections import namedtuple

# Discord Bot
TOKEN="IT'S A SECRET!"

# ROMs
ROM = namedtuple("ROM", ["name", "path"])
ROMDir="ROMs"

bootROMs = [
  ROM("DMG_ROM", os.path.join(ROMDir, "DMG_ROM.bin"))
]
def bootROMByName(name):
  matches = [rom for rom in bootROMs if rom.name == name]
  if len(matches) == 0:
    return None
  else:
    return matches[0]

gameROMs = [
  ROM("Example: Standard Version", os.path.join(ROMDir, "Example--Standard_Version.gb"))
]
def gameROMByName(name):
  matches = [rom for rom in gameROMs if rom.name == name]
  if len(matches) == 0:
    return None
  else:
    return matches[0]

