# -*- coding: utf-8 -*-

"""
Discord Bot
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import discord
import discord.ext.commands as commands
import os
from functools import partial
from . import logger, version_info
from .emulatorController import ChannelAlreadyRegistered, ChannelNotRegistered
from .emulatorControllerGroup import ControllerNotFoundByChannel, ControllerNotFoundByIdNumber, EmulatorControllerGroup
from .gamelibrary import ConsoleType, FileNotFound, FileType, GameLibrary
from .emulators.action import ButtonPress


# Exceptions
class NoPrivateMessages(commands.CheckFailure):
    pass



# bot intialisation
description = "Interface to emulators."
description += "\n Version: {}.{}.{}".format(version_info.major, version_info.minor, version_info.micro)
bot = commands.Bot(
  '.',
  description=description,
  case_insensitive=True
)

# The game library
bot.gameLibrary = GameLibrary()

# The controller of all the emulators
bot.emulatorControllerGroup = EmulatorControllerGroup()

# Setting status messages
#def setStatusMessage() -> None:
#  game = discord.Game("Running {} emulators".format(
#    bot.emulatorControllerGroup.numberOfControllers
#  ))
#  await bot.change_presence(activity=game)

# Global Command Checks
@bot.check
async def globally_block_dms(ctx:commands.Context):
  if ctx.guild is None:
    raise NoPrivateMessages('Hey no DMs!')
  else:
    return True


# Global Error Check
@bot.event
async def on_command_error(context:commands.Context, error:Exception) -> None: 
  # ChannelAlreadyRegistered
  if isinstance(error, ChannelAlreadyRegistered):
    logger.info("{}: User {} attempted to REregister {}:{}".format(
      context.bot.__class__.__name__,
      context.message.author,
      error.channel.guild.name,
      error.channel.name
    ))
  # ChannelNotRegistered
  if isinstance(error, ChannelNotRegistered):
    logger.info("{}: User {} attempted '{}' in a NONregistered channel {}:{}".format(
      context.bot.__class__.__name__,
      context.message.author,
      context.invoked_with,
      error.channel.guild.name,
      error.channel.name
    ))
  # ControllerNotFoundByChannel
  if isinstance(error, ControllerNotFoundByChannel):
    logger.info("{}: No controller found for{}:{}".format(
      context.bot.__class__.__name__,
      error.channel.guild.name,
      error.channel.name
    ))
  # ControllerNotFoundByIdNumber
  if isinstance(error, ControllerNotFoundByIdNumber):
    logger.info("{}: No controller found for id {}".format(
      context.bot.__class__.__name__,
      error.idNumber
    ))
  # FileNotFound
  if isinstance(error, FileNotFound):
    logger.info("{}: File not found: ConsoleType: {}, FileType: {}, FileName: {}".format(
      context.bot.__class__.__name__,
      error.consoleType,
      error.fileType,
      error.fileName
    ))
  # NoPrivateMessagesCheck
  if isinstance(error, NoPrivateMessages):
    logger.info("{}: User {} attempted DM.".format(
      context.bot.__class__.__name__,
      context.message.author
    ))
    await context.send(error)
    return None
  # Unknown error, so print to log
  await commands.Bot.on_command_error(bot, context, error)


# Command Checks
async def isControllerRunning(ctx:commands.Context) -> None:
  return ctx.bot.controller.isRunning


async def isControllerStopped(ctx:commands.Context) -> None:
  return not ctx.bot.controller.isRunning


async def isVotingPeriodCheck(ctx:commands.Context) -> None:
  return ctx.bot.isVotingPeriod


async def isGuildMessageCheck(ctx:commands.Context) -> None:
  return ctx.message.channel.type == discord.ChannelType.text


## Buttons
buttonHelpMessage = "Casts vote for pushing a button (iterations) times."
buttonHelpMessage += "\nOnly usable when a ROM is running"
@bot.command(
  name="push",
  help=buttonHelpMessage
)
async def buttonPush(ctx:commands.Context, buttonName:str,
    iterations:int=1) -> None:
  # Find channel
  controller = ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )
  # Confrim the controller is running
  controller.emulator.assertIsRunning
  # Confirm the button name
  buttonName = buttonName.lower()
  if not buttonName in controller.emulator.buttonNames:
    raise ButtonPress(buttonName)
  # Conform iterations to a level of sanity
  iterations = min(max(abs(int(iterations)), 1), 50)
  await controller.voteForButton((buttonName, iterations),
    ctx.message.author, ctx.message.channel
  )

## Game Library
@bot.command(
  name="listRoms",
  help="List avaialbe ROMs"
)
async def listROMs(ctx:commands.Context, consoleType:ConsoleType=None,
     fileType:FileType=None) -> None:
  if consoleType is None:
    consoleTypeList = ConsoleType
  else:
    consoleTypeList = [consoleType]

  if fileType is None:
    fileTypeList = FileType
  else:
    fileTypeList = [fileType]

  # Send the info
  message = ""
  for consoleType in consoleTypeList:
    message += "{}::\n".format(consoleType.value)
    for fileType in fileTypeList:
      message += "  {}:\n".format(fileType.value)

      files = ctx.bot.gameLibrary.availableFiles(consoleType, fileType)
      message += "\n".join(("    {}".format(f) for f in files))
      message += "\n"

  await ctx.message.channel.send(message)

## Controller
@bot.command(
  name="controllerStatus",
  help="Sends status of control of the channel the message was sent from."
)
async def controllerStatus(ctx:commands.Context) -> None:
  # Find controller
  controller = ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )
  if controller is None:
    # If not connected then send that as the status
    await ctx.send("Not connected to a controller")
    return None

  message = "Status: '{}'\n".format(
    "Running" if controller.isRunning else "Not Running"
  )
  message += "Id Number: {}\n".format(controller.idNumber)
  message += "# Registered Channels: {}".format(
    controller.numberOfRegisteredChannels
  )
  await ctx.send(message)


@bot.command(
  name="createController",
  help="Creates a new controller registered to the message this channel was sent from."
)
async def createNewController(ctx:commands.Context) -> None:
  # determine if this channel is already connected to a controller
  existingController = ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )
  if existingController:
    raise ChannelAlreadyRegistered(ctx.message.channel)

  ctx.bot.emulatorControllerGroup.createController(ctx.message.channel)
    
@bot.command(
  name="startROM",
  help="Starts a ROM on the conroller of the channel the message was sent to"
)
async def startROM(ctx:commands.Context, consoleType:ConsoleType,
    gameROM: str, bootROM: str) -> None:
  # Find controller
  controller = ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )
  # If no controller then error out
  if controller is None:
    raise ChannelNotRegistered(ctx.message.channel)

  # Construct file paths, errors if path not correct
  gameROMPath = ctx.bot.gameLibrary.filePath(consoleType, FileType.GAMES, gameROM)
  bootROMPath = ctx.bot.gameLibrary.filePath(consoleType, FileType.BOOTS, bootROM)
  # Specification correct, start the game 
  game = discord.Game("{}: {}".format(consoleType.value, parameters[1]))
  await ctx.bot.change_presence(activity=game)
  controller.start(consoleType, gameROMPath, bootROMPath)
  # Send first screen shot
  await ctx.bot.sendScreenShotGif(ctx.message.channel)
  

@bot.command(
  name="stopROM",
  help="Stops the ROM on the conroller of the channel the message was sent to"
)
async def stopROM(ctx:commands.Context) -> None:
  # Find controller
  controller = ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )
  # If no controller then error out
  if controller is None:
    raise ChannelNotRegistered(ctx.message.channel)
  # Stop emulator
  controller.stop()

 
@bot.command(
  name="setVotingPeriodLength",
  help="Change the length of seconds for votes.\nMinimum is 1"
)
async def setVotingPeriodLength(ctx:commands.Context, length:int) -> None:
  # Find controller
  controller = ctx.bot.emulatorcontrollergroup.findControllerByChannel(
    ctx.message.channel
  )
  # If no controller then error out
  if controller is None:
    raise ChannelNotRegistered(ctx.message.channel)
  # Sanatize the number
  length = max(length)
  controller.setVotingPeriodLength()

    
@bot.event
async def close() -> None:
  bot.emulatorControllerGroup.stopAll()


@bot.event
async def on_ready() -> None:
  # Set status
  #setStatusMessage()
  pass

