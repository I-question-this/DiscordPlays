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
from .emulators.emulator import ButtonNotRecognized


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
async def setStatusMessage() -> None:
 game = discord.Game("Running {} emulators".format(
   bot.emulatorControllerGroup.numberOfRunningEmulators
 ))
 await bot.change_presence(activity=game)

## Context Helper Methods
def getControllerForMessageContext(ctx:commands.Context):
  return ctx.bot.emulatorControllerGroup.findControllerByChannel(
    ctx.message.channel
  )

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
async def isConnectedToController(ctx:commands.Context) -> None:
  return getControllerForMessageContext(ctx) is not None

async def isEmulatorRunning(ctx:commands.Context) -> None:
  controller = getControllerForMessageContext(ctx)
  return controller.isRunning if controller is not None else False


async def isVotingPeriod(ctx:commands.Context) -> None:
  controller = getControllerForMessageContext(ctx)
  return controller.isVotingPeriod if controller is not None else False


## Buttons
buttonHelpMessage = "Casts vote for pushing a button (iterations) times."
buttonHelpMessage += "\nOnly usable when a ROM is running"
@bot.command(
  name="push",
  help=buttonHelpMessage
)
@commands.check(isVotingPeriod)
async def buttonPush(ctx:commands.Context, buttonName:str,
    iterations:int=1) -> None:
  # Find channel
  controller = getControllerForMessageContext(ctx) 
  # Confirm the button name
  buttonName = buttonName.lower()
  if not buttonName in controller.buttonNames:
    raise ButtonNotRecognized(buttonName)
  # Conform iterations to a level of sanity
  iterations = min(max(abs(int(iterations)), 1), 50)
  await controller.voteForButton(
          (buttonName, iterations),
          ctx.message.author
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
def craftControllerStatus(controller):
  message = "Status: '{}'\n".format(
    "Running" if controller.isRunning else "Not Running"
  )
  message += "Id Number: {}\n".format(controller.idNumber)
  message += "# Registered Channels: {}".format(
    controller.numberOfRegisteredChannels
  )
  return message


@bot.command(
  name="controllerStatus",
  help="Sends status of control of the channel the message was sent from."
)
async def controllerStatus(ctx:commands.Context) -> None:
  # Find controller
  controller = getControllerForMessageContext(ctx) 
  # Send status
  await ctx.send(craftControllerStatus(controller) if controller is not None else "Not connected to a controller")


@bot.command(
  name="createController",
  help="Creates a new controller registered to the message this channel was sent from."
)
async def createNewController(ctx:commands.Context) -> None:
  # determine if this channel is already connected to a controller
  existingController = getControllerForMessageContext(ctx)
  if existingController is not None:
    ctx.send("This channel is already registered to a controller")
    raise ChannelAlreadyRegistered(ctx.message.channel)

  # Create the new controller
  ctx.bot.emulatorControllerGroup.createController(ctx.message.channel)
  # Find new controller
  controller = getControllerForMessageContext(ctx)
  if controller is None:
      ctx.send("Failed to create controller")
  else:
      await ctx.send(craftControllerStatus(controller))
    
@bot.command(
  name="startROM",
  help="Starts a ROM on the conroller of the channel the message was sent to"
)
@commands.check(isConnectedToController)
async def startROM(ctx:commands.Context, consoleType:ConsoleType,
        gameROM: str, bootROM: str, saveFileName:str=None) -> None:
  # Find controller
  controller = getControllerForMessageContext(ctx)

  # Construct file paths, errors if path not correct
  gameROMPath = ctx.bot.gameLibrary.filePath(consoleType, FileType.GAMES, gameROM)
  bootROMPath = ctx.bot.gameLibrary.filePath(consoleType, FileType.BOOTS, bootROM)
  if saveFileName is not None:
    try:
      saveFilePath = ctx.bot.gameLibrary.filePath(consoleType, FileType.SAVES, saveFileName)
      newSaveFile = False
    except FileNotFound:
        saveFilePath = ctx.bot.gameLibrary.filePath(consoleType, FileType.SAVES, saveFileName, True)
        newSaveFile = True
  else:
    saveFilePath = None
    newSaveFile = False
  # Specification correct, start the game 
  await setStatusMessage()
  controller.start(consoleType, gameROMPath, bootROMPath, saveFilePath, newSaveFile)
  # Send first screen shot
  await controller.sendScreenShotGif()
  

@bot.command(
  name="stopROM",
  help="Stops the ROM on the conroller of the channel the message was sent to"
)
@commands.check(isEmulatorRunning)
async def stopROM(ctx:commands.Context) -> None:
  # Find controller
  controller = getControllerForMessageContext(ctx)
  # Stop emulator
  controller.stop()
  await setStatusMessage()

@bot.command(
  name="saveState",
  help="Saves the state to name given or the previously specified name."
)
@commands.check(isEmulatorRunning)
async def saveState(ctx:commands.Context, saveStateName:str=None) -> None:
  # Find controller
  controller = getControllerForMessageContext(ctx)
  # Stop emulator
  if saveStateName is not None:
      controller.saveStateFilePath = ctx.bot.gameLibrary.filePath(controller.consoleType, FileType.SAVES, saveStateName, True)

  if controller.saveStateFilePath is None:
      await ctx.send("No prioer save state file name specified, can not save with implicit name")

  controller.saveState()
  await ctx.send("State saved to: {}".format(controller.saveStateFilePath))

 
@bot.command(
  name="setVotingPeriodLength",
  help="Change the length of seconds for votes.\nMinimum is 1"
)
@commands.check(isConnectedToController)
async def setVotingPeriodLength(ctx:commands.Context, length:int) -> None:
  # Find controller
  controller = getControllerForMessageContext(ctx)
  # Sanatize the number
  length = max(length)
  controller.setVotingPeriodLength()

    
@bot.event
async def close() -> None:
  bot.emulatorControllerGroup.stopAll()


@bot.event
async def on_ready() -> None:
  # Set status
  await setStatusMessage()

