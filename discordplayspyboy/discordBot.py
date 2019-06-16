# -*- coding: utf-8 -*-

"""
Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import discord
import discord.ext.commands as commands
import time
from functools import partial
from . import logger
from .config import bootROMByName, gameROMByName, gameROMs
from .pyboyController import PyBoyController
from .votingbox import VotingBox

# Commands
## Checks
async def isControllerRunning(ctx):
  return ctx.bot.controller.isRunning

async def isControllerStopped(ctx):
  return not ctx.bot.controller.isRunning

async def isVotingPeriodCheck(ctx):
  return ctx.bot.isVotingPeriod

## Buttons
async def buttonPush(ctx):
  await ctx.bot.voteForButton(ctx.invoked_with, ctx.message.author, ctx.message.channel)

## Controller
async def listROMs(ctx):
  await ctx.message.channel.send("\n".join((rom.name for rom in gameROMs)))

async def startController(ctx):
  romName = " ".join(ctx.message.content.split()[1:])
  romPath = gameROMByName(romName).path
  if romPath is None:
    await ctx.message.channel.send("No such ROM exists")
  else:
    await ctx.bot.startController(romName, romPath)
    await ctx.bot.sendLastScreenShot(ctx.message.channel)
  
async def stopController(ctx):
  await ctx.bot.stopController()

## Voting
async def setVotingPeriodLength(ctx):
  newLength = " ".join(ctx.message.content.split()[1:])
  try:
    newLength = max(int(newLength), 1)
  except ValueError:
    await ctx.message.channel.send("Can not interpret '{}' as integer".format(newLength))
  
  ctx.bot.votingPeriodLength = newLength
  logger.info("Changed votingPeriodLength to '{}'".format(newLength))
  await ctx.message.channel.send("Set voting period length to '{}'".format(newLength))

## The bot
class Bot(commands.Bot):
  # The controller interface to the player
  controller = PyBoyController()
  # Screenshots
  lastScreenShot = None 
  # Standard messages
  idleActivity = "Nothing.gb"
  # Voting state information
  isVotingPeriod = True
  isFirstVote = True
  votingPeriodLength = 3
  votingBox = VotingBox()

  # Helper methods
  ## Voting
  def castVote(self, author, button):
    logger.info("Bot: '{}' cast vote for '{}'".format(author, button))
    self.votingBox.castVote(author, button)

  async def voteForButton(self, button, author, channel):
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
      # Get the majority vote
      button = self.votingBox.majorityVoteResult()
      if button is not None:
        await self.sendVotingResults(button, channel)
        await self.pushButton(button)
        await self.sendLastScreenShot(channel)
      else:
        logger.critical("Bot: No votes cast...somehow")
      # Reset voting box
      self.votingBox = VotingBox()
      # Reset isFirstVote
      self.isFirstVote = True
      # Turning voting back on
      self.isVotingPeriod = True
      logger.info("Bot: Voting is starting")

  # Controller interaction
  async def pushButton(self, button): 
    logger.info("Bot: Pressing button: {}".format(button))
    self.lastScreenShot = await self.controller.pressButton(button)
  
  async def sendLastScreenShot(self, channel):
    if self.lastScreenShot is None:
      logger.critical("Bot: no screen shot to send")
      return
    logger.info("Bot: Sending screenshot {}".format(self.lastScreenShot))
    await channel.send("", file=discord.File(self.lastScreenShot, "screenshot.gif"))

  async def sendVotingResults(self, chosenButton, channel):
    messageParts = ["Voting Results:"]
    messageParts.extend(self.votingBox.voteCounts())
    messageParts.append("Button Pressed: '{}'".format(chosenButton))
    logger.info("Bot: {}".format(". ".join(messageParts)))
    await channel.send("\n".join(messageParts))

  async def startController(self, gameROMName, gameROMPath):
    self.lastScreenShot = await self.controller.start(gameROMPath, bootROMByName("DMG_ROM").path)
    game = discord.Game(gameROMName)
    await self.change_presence(activity=game)
  
  async def stopController(self):
    self.controller.stop()
    self.lastScreenShot = None
    game = discord.Game(self.idleActivity)
    await self.change_presence(activity=game)

  # Commands
  def addCommands(self):
    # Buttons
    buttonHelpMessage = "Casts vote for button '{}'."
    buttonHelpMessage += "\nOnly usable when a ROM is running"
    for button in self.controller.availableButtons:
      self.add_command(
        commands.Command(
          buttonPush, 
          name=button,
          help=buttonHelpMessage.format(button),
          checks=[
            isControllerRunning,
            isVotingPeriodCheck
          ]
        )
      )

    # ROMs
    self.add_command(
      commands.Command(
        listROMs,
        name="listROMs",
        help="List avialable ROMs"
      )
    )
    self.add_command(
      commands.Command(
        startController,
        name="startROM",
        help="Starts the specified ROM",
        usage="<ROM name>",
        checks=[isControllerStopped]
      )
    )
    self.add_command(
      commands.Command(
        stopController,
        name="stopROM",
        help="Starts the currently running ROM",
        checks=[isControllerRunning]
      )
    )
    # Voting
    self.add_command(
      commands.Command(
        setVotingPeriodLength,
        name="setVotingPeriodLength",
        help="Change the length of seconds for votes.\nMinimum is 1",
        usage="<number of seconds>"
      )
    )
 

  # Discord client event registration
  async def close(self):
    if self.controller.isRunning:
      logger.info("Bot: Shutting down controller")
      await self.stopController()
    game = discord.Game("Down for Server Maintenance")
    await self.change_presence(
      activity=game,
      status=discord.Status.offline
    )

  async def on_ready(self):
    self.addCommands()
    # Set status
    game = discord.Game(self.idleActivity)
    await self.change_presence(activity=game)

