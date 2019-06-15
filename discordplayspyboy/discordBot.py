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
from .votingbox import VotingBox

class Client(discord.Client):
  # The controller interface to the player
  controller = PyBoyController("ROMs/Pokemon--Blue_Version.gb")
  # Name of the only channel this bot will respond to
  dedicatedChannelName = "pyboy"
  dedicatedChannel = None
  # Booleans keeping track of proper message response behavior states
  isVotingPeriod = True
  isFirstVote = True
  votingPeriodLength = 10
  votingBox = VotingBox()

  # Helper methods
  def castVote(self, author, button):
    logger.info("Bot: '{}' cast vote for '{}'".format(author, button))
    self.votingBox.castVote(author, button)

  async def ourChannel(self):
    for channel in self.get_all_channels():
      if channel.name == self.dedicatedChannelName:
        return channel
    logger.critical("Unable to find dedicated channel: {}".format(dedicatedChannelName))
    return None

  async def pushButton(self, button): 
    logger.info("Bot: Pressing button: {}".format(button))
    screenShotPath = await self.controller.pressButton(button)
    logger.info("Bot: Sending screenshot {}".format(screenShotPath))
    if self.dedicatedChannel is not None:
      await self.dedicatedChannel.send("Button {} pressed".format(button), file=discord.File(screenShotPath, "screenshot.gif"))

  # Event registration
  async def on_ready(self):
    self.dedicatedChannel = await self.ourChannel()
    logger.info("Sending starting messages")
    if self.dedicatedChannel is not None:
      screenShotPath = await self.controller.pressButton("a")
      logger.info("Bot: Sending screenshot {}".format(screenShotPath))
      await self.dedicatedChannel.send("", file=discord.File(screenShotPath, "screenshot.gif"))

  async def on_message(self, message):
    # Quit if votes can not be cast at this time
    if not self.isVotingPeriod:
      return
    # Quit if the message did not come from the dedicated channel
    if message.channel.name != self.dedicatedChannelName:
      return
    # Remove case senstivity
    button = message.content.lower()
    # Check if an actual button
    if button in self.controller.availableButtons():
      if not self.isFirstVote:
        self.castVote(message.author, button)
      else:
        # Turn off isFirstVote
        self.isFirstVote = False
        logger.info("Bot: User '{}' started voting period".format(message.author))
        self.castVote(message.author, button)
        # Wait for voting period to end
        time.sleep(self.votingPeriodLength)
        self.isVotingPeriod = False
        logger.info("Bot: Voting is over")
        # Rest isFirstVote
        self.isFirstVote = True
        # Get the majority vote
        button = self.votingBox.majorityVote()
        # Reset voting box
        self.votingBox = VotingBox()
        if button is not None:
          await self.pushButton(button)
        else:
          logger.critical("Bot: No votes cast...somehow")
        # Turning voting back on
        self.isVotingPeriod = True
        logger.info("Bot: Voting is starting")

  async def cleanup(self):
    self.controller.stop()

if __name__ == "__main__":
  """Simply runs the client if invoked as a standalone program"""
  from .config import TOKEN
  Client.run(TOKEN)

