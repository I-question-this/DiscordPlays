# -*- coding: utf-8 -*-

"""
Emulator Controller Group
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import discord
from . import logger
from .emulatorController import ChannelAlreadyRegistered, ChannelNotRegistered, EmulatorController, UnsupportedConsole
from .gamelibrary import ConsoleType

# Exceptions for this class
class ControllerNotFoundByChannel(Exception):
  """Thrown when a controller is not found by channel"""
  def __init__(self, channel:discord.abc.Messageable):
    self.channel = channel



class ControllerNotFoundByIdNumber(Exception):
  """Thrown when a controller is not found by id number"""
  def __init__(self, idNumber:int):
    self.idNumber = idNumber



class EmulatorControllerGroup:
  # Channels
  def _isChannelRegistered(self, channel:discord.abc.Messageable) -> bool:
    for controller in self._emulatorControllers:
      if controller.isChannelRegistered(channel):
        return True
    # If not found
    return False


  # Controllers
  def createController(self, channel:discord.abc.Messageable) -> None:
    if self._isChannelRegistered(channel):
      raise ChannelAlreadyRegistered(channel.guild.name, channel.name)

    # Start controller
    newController = EmulatorController(
      self._uniqueIdNumber(),
      channel
    )
    self._emulatorControllers.append(newController)
    logger.info("{}: Created controller ID#{}".format(
      self.__class__.__name__,
      newController.idNumber
    ))


  def deleteController(self, idNumber:int) -> None:
    controller = find(lambda controller: controller.idNumber == idNumber,
                      self._emulatorControllers
                     )
    if controller is not None:
      if controller.emulator.isRunning:
        controller.emulator.stop()
        self._emulatorControllers.remove(controller)
        logger.info("{}: Deleted controller ID#{}".format(
          self.__class__.__name__,
          idNumber
        ))
    else:
      raise ControllerNotFoundByIdNumber(idNumber)


  def findControllerByChannel(self, channel:discord.abc.Messageable) -> None:
    for controller in self._emulatorControllers:
      if controller.isChannelRegistered(channel):
        return controller
    return None

  def findControllerById(self, idNumber:int) -> None:
    for controller in self._emulatorControllers:
      if controller.idNumber == idNumber:
        return controller
    return None

  @property
  def numberOfControllers(self) -> int:
    return len(self._emulatorControllers)


  def stopAll(self) -> None:
    for controller in self._emulatorControllers:
      if controller.isRunning():
        controller.stop()


  # Id Number
  def _uniqueIdNumber(self) -> int:
    self.__previousIdNumber += 1
    return self.__previousIdNumber


  # Magic Methods
  def __init__(self):
    self._emulatorControllers = []
    self.__previousIdNumber = -1

