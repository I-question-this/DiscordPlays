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
  ## Voting
  def castVote(self, author, button):
    logger.info("Bot: '{}' cast vote for '{}'".format(author, button))
    self.votingBox.castVote(author, button)

  async def voteForButton(self, button, author):
    # Quit if votes can not be cast at this time
    if not self.isVotingPeriod:
      return None
    # Vote
    if not self.isFirstVote:
      self.castVote(author, button)
    else:
      # Turn off isFirstVote
      self.isFirstVote = False
      logger.info("Bot: User '{}' started voting period".format(author))
      self.castVote(author, button)
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
    # Quit if the message did not come from the dedicated channel
    if message.channel.name != self.dedicatedChannelName:
      return None
    # Interpret message 
    args = message.content.lower().split()
    logger.info("Bot: recived message \"{}\"".format(" ".join(args)))
    if args[0] in self.controller.availableButtons():
      await self.voteForButton(args[0], message.author)
    elif args[0] == "setvotingtime":
      try:
        args[1] = int(args[1])
      except ValueError:
        await self.dedicatedChannel.send("{} can not be interpreted as an integer".format(args[1]))
      self.votingPeriodLength = args[1]
      logger.info("Bot: votingPeriodLength changed to {}".format(self.votingPeriodLength))
      await self.dedicatedChannel.send("Voting period length changed to {} seconds".format(self.votingPeriodLength)) 
 
  async def cleanup(self):
    self.controller.stop()

if __name__ == "__main__":
  """Simply runs the client if invoked as a standalone program"""
  from .config import TOKEN
  Client.run(TOKEN)

