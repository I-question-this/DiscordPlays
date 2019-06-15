# -*- coding: utf-8 -*-

"""
Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import discord
import time

from . import logger

from .pyboyController import PyBoyController

class Client(discord.Client):
  sleepTimeBeforeScreenShot = 0.5
  channelName = "pyboy"
  controller = PyBoyController("ROMs/Pokemon--Blue_Version.gb")
  basicHelpMessage = "Avaiable Buttons:\n" + "\n".join(controller.availableButtons())
    
  async def on_message(self, message):
    content = message.content.split()
    if message.channel.name == self.channelName:
      if len(content) == 1 and content[0] in self.controller.availableButtons():
        logger.info("Bot: Pressing button: {}".format(content[0]))
        screenShotPath = await self.controller.pressButton(content[0])
        logger.info("Bot: Sending screenshot {}".format(screenShotPath))
        await message.channel.send("Button {} pressed".format(content[0]), file=discord.File(screenShotPath, "screenshot.gif"))

