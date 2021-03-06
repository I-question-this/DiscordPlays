# -*- coding: utf-8 -*-

"""
Discord Controller Settings
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import datetime
import discord
import os
import tempfile
import time
from typing import List
from . import logger
from .emulators.action import Action, ActionNotRecognized
from .emulators.gameBoy import GameBoy
from .gamelibrary import ConsoleType, FileType
from .votingbox import VotingBox

# Exceptions for this class
class ChannelAlreadyRegistered(Exception):
  """Thrown when attempting to register an already registered channel"""
  def __init__(self, channel:discord.abc.Messageable):
    self.channel = channel



class ChannelNotRegistered(Exception):
  """Thrown when attempting to deregister a non registered channel"""
  def __init__(self, channel:discord.abc.Messageable):
    self.channel = channel


class SaveStateFileNotSpecified(Exception):
  """Thrown when attempting to save without a save-state file specified"""


class UnsupportedConsole(Exception):
  """Thrown when attempting to use an unsupported console"""
  def __init__(self, consoleType:ConsoleType):
    self.unsupportedConsole = consoleType



class EmulatorController:
  # Buttons
  @property
  def buttonNames(self):
      if self._emulator is None:
          return []
      else:
          return self._emulator.buttonNames


  @property
  def numberOfSecondsAfterButtonPress(self) -> float:
      self._numberOfSecondsAfterButtonPress


  async def setNumberOfSecondsAfterButtonPress(self, newLength:float) -> None:
    # Check value
    if newLength < 0:
        raise ValueError("numberOfSecondsAfterButtonPress can not be less than 0")
    # Set value
    self._numberOfSecondsAfterButtonPress = newLength
    # Inform users of the change
    await self._sendMessageToRegisteredChannels(
      "Set seconds after button press(s) to '{}'".format(
        newLength
      )
    )


  # Channels
  def deregisterChannel(self, channel:discord.abc.Messageable) -> None:
    if not self._isChannelRegistered:
      raise ChannelNotRegistered(channel)

    self._registeredChannels.remove(channel)


  def isChannelRegistered(self, channel:discord.abc.Messageable) -> bool:
    return channel in self._registeredChannels


  @property
  def numberOfRegisteredChannels(self) -> int:
    return len(self._registeredChannels)


  def registerChannel(self, channel:discord.abc.Messageable) -> None:
    if self._isChannelRegistered:
      raise ChannelAlreadyRegistered(channel)

    self._registeredChannels.append(channel)

  
  def registeredChannels(self) -> List[discord.abc.Messageable]:
    return self._registeredChannels


  # Consoles
  _supportedConsoles = {
    ConsoleType.GB: GameBoy
  }


  @classmethod
  def supportedConsoles(cls) -> List[ConsoleType]:
    return list(cls._supportedConsoles.keys())


  @property
  def consoleType(self) -> ConsoleType:
      return self._consoleType


  # Id Number
  @property
  def idNumber(self):
    return self._idNumber


  # Magic Methods
  def __init__(self, idNumber, firstRegisteredChannel:discord.abc.Messageable):
    # Channels
    self._registeredChannels = [firstRegisteredChannel]

    # Emulaator
    self._emulator = None
    self._saveFilePath = None
    self._consoleType = None
    self._numberOfSecondsAfterButtonPress = 10
    # Id Number
    self._idNumber = idNumber

    # Voting
    self._isVotingPeriod = True
    self._isFirstVote = True
    self._votingPeriodLength = 3
    self._votingBox = VotingBox()


  # Messaging
  async def _sendMessageToRegisteredChannels(self, text, file=None) -> None:
    for channel in self._registeredChannels:
      await channel.send(text, file=file)
 

  async def sendScreenShotGif(self) -> None:
    # Create a unique file name
    filePath = os.path.join(
      tempfile.gettempdir(),
       "{}--screenshot.gif".format(datetime.datetime.now())
    )
    # Save the GIF
    self._emulator.makeGIF(filePath)
    logger.info("{}: Sending screenshot \"{}\"".format(
      self.__class__.__name__,
      filePath
    ))
    # Send the GIF to all regersted channels
    await self._sendMessageToRegisteredChannels(
      "",
      file=discord.File(filePath, "screenshot.gif")
    )
    # Delete the file since we are done with it
    os.remove(filePath)


  # Save action
  def loadState(self):
      self._emulator.assertIsRunning()
      if self.saveStateFilePath is not None:
        self._emulator.loadState(self.saveStateFilePath)
      else:
        raise SaveStateFileNotSpecified()


  def saveState(self):
      self._emulator.assertIsRunning()
      if self.saveStateFilePath is not None:
        self._emulator.saveState(self.saveStateFilePath)
      else:
        raise SaveStateFileNotSpecified()


  # SaveStateFilePath property
  @property
  def saveStateFilePath(self):
      return self._saveStateFilePath


  @saveStateFilePath.setter
  def saveStateFilePath(self, newSaveStateFilePath):
      self._emulator.assertIsRunning()
      self._saveStateFilePath = newSaveStateFilePath


  # Status
  @property
  def isRunning(self):
    if self._emulator is None:
      return False
    else:
      return self._emulator.isRunning


  # Start
  def start(self, consoleType:ConsoleType, gameROMPath:str,
          bootROMPath:str, saveStateFilePath:str=None, newSaveStateFile:bool=False):
    # Confirm there is not an already running emulator 
    if self._emulator is not None:
      self._emulator.assertNotRunning()

    # Confirm we support the choosen console type
    if consoleType in self.supportedConsoles():
      self._emulator = self._supportedConsoles[consoleType]()
      self._consoleType = consoleType
    else:
      raise UnsupportedConsole(consoleType)
 
    # Is save file new?
    loadSaveStateFilePath = None if saveStateFilePath is not None and newSaveStateFile else saveStateFilePath
    # Start the specified game
    self._emulator.start(gameROMPath, bootROMPath, loadSaveStateFilePath)
    # Record saveFilePath
    self.saveStateFilePath = saveStateFilePath


  # Stop
  def stop(self):
    # Confirm there is actually something running
    if self._emulator is not None:
      if self._emulator.isRunning:
        # Stop the emulator
        self._emulator.stop(self.saveStateFilePath)
        # Reset the saveFilePath
        self._saveFilePath = None

 
  # Voting
  def _castVote(self, author:discord.abc.User, button):
    logger.info("{}: '{}' cast vote for '{}'".format(
      self.__class__.__name__,
      author,
      button
    ))
    self._votingBox.castVote(author, button)


  @property
  def isVotingPeriod(self) -> bool:
    return self._isVotingPeriod

  def _restartVoting(self) -> None:
      # Reset voting box
      self._votingBox = VotingBox()
      # Reset isFirstVote
      self._isFirstVote = True
      # Turning voting back on
      self._isVotingPeriod = True
      logger.info("{}: Voting is starting".format(
        self.__class__.__name__
      ))

  async def sendVotingResults(self, chosenButton) -> None:
    messageParts = ["Voting Results:"]
    messageParts.extend(self._votingBox.voteCounts())
    messageParts.append("Button Pressed: '{}'".format(chosenButton))
    logger.info("{}: {}".format(
      self.__class__.__name__,
      ". ".join(messageParts))
    )
    await self._sendMessageToRegisteredChannels("\n".join(messageParts))


  async def setVotingPeriodLength(self, newLength:int) -> None:
    # Check value
    if newLength < 0:
        raise ValueError("votingPeriodLength can not be less than 0")
    # Make change
    self._votingPeriodLength = newLength
    # Inform users of the change
    await self._sendMessageToRegisteredChannels(
      "Set voting period length to '{}'".format(
        newLength
      )
    )


  async def voteForButton(self, vote, author:discord.abc.User) -> None:
    # Quit if votes can not be cast at this time
    if not self._isVotingPeriod:
      return None
    # Vote
    if not self._isFirstVote:
      self._castVote(author, vote)
    else:
      # Turn off isFirstVote
      self.isFirstVote = False
      logger.info("{}: User '{}' started voting period".format(
        self.__class__.__name__,
        author
      ))
      self._castVote(author, vote)
      # Wait for voting period to end
      time.sleep(self._votingPeriodLength)
      self._isVotingPeriod = False
      logger.info("{}: Voting is over".format(
        self.__class__.__name__
      ))
      # Get the majority vote
      resultVote = self._votingBox.majorityVoteResult()
      if resultVote is not None:
        await self.sendVotingResults(resultVote)
        actionType, button, x = resultVote
        # Perform the button action
        if actionType == Action.PRESS: 
            for _ in range(x):
                self._emulator.pressButton(button)
        elif actionType == Action.HOLD:
            self._emulator.holdButton(button, x)
        else:
            self._restartVoting()
            raise ActionNotRecognized(actionType)
        # Run emulator after button press(s)
        self._emulator.runForXSeconds(self._numberOfSecondsAfterButtonPress)
        await self.sendScreenShotGif()
      else:
        logger.critical("{}: No votes cast...somehow".format(
          self.__class__.__name__
        ))
      self._restartVoting()

