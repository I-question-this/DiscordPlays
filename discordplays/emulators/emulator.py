
# -*- coding: utf-8 -*-

"""
Abstract contract of what a controller should do.
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
from abc import ABC, abstractmethod
from PIL import Image
from typing import List
from .action import ButtonPress
from .. import logger

# Exceptions for this class
class AlreadyRunning(Exception):
  """Thrown when a controller is already running an emulator"""
  pass



class ButtonNotRecognized(Exception):
  """Thrown when a button is not recognized"""
  def __init__(self, buttonName: str):
    self.buttonName = buttonName



class NoScreenShotFramesSaved(Exception):
  """Thrown when no screen shot frames are saved but a gif was requested"""
  pass


class NotRunning(Exception):
  """Thrown when a controller is not running an emulator"""
  pass



class ScriptedActionNotRecognized(Exception):
  """Thrown when a button is not recognized"""
  def __init__(self, scriptedActionName: str):
    self.scriptedActionName = scriptedActionName



class Emulator(ABC):
  """Represents how a controller should behave"""
  # Buttons  
  __buttons = {}

  @property
  def buttonNames(self) -> List[str]:
    return [buttonName.lower() for buttonName in self.__buttons.keys()]


  @abstractmethod
  def _abstractPressButton(self, button:ButtonPress) -> None:
    pass


  def _getButton(self, buttonName: str) -> None:
    try:
      return self.__buttons[buttonName.lower()]
    except KeyError:
      logger.critical("{}: Unrecognized button \"{}\"".format(
        self.__class__.__name__,
        buttonName
      ))
      raise ButtonNotReconized(buttonName)


  def pressButton(self, buttonName:str) -> None:
    self.assertIsRunning()
    button = self._getButton(buttonName)

    logger.info("{}: Pressing button {}".format(
      self.__class__.__name__,
      button.name
    ))
    self._abstractPressButton(button)


  def _registerButton(self, button:ButtonPress) -> None:
    self.__buttons[button.name.lower()] = button

  
  # Magic Methods
  def __init__(self, fps:int=60):
    # Save information
    self._fps = fps
    self.__screenShots = [] 


  # Running
  @abstractmethod
  def _runForOneFrame(self) -> None:
    pass


  def runForXFrames(self, numberOfFrames:int) -> None:
    if numberOfFrames < 0:
      raise ValueError("numberOfFrames must 0 or more")

    self.assertIsRunning()

    if numberOfFrames == 0:
      return

    logger.info("{}: Running for {} frames, aka {} seconds".format(
      self.__class__.__name__, 
      numberOfFrames, 
      numberOfFrames / self._fps
    ))

    for _ in range(numberOfFrames):
      self._runForOneFrame()
      self._takeScreenShot()


  def runForXSeconds(self, numberOfSeconds:int) -> None:
    if numberOfSeconds < 0:
      raise ValueError("numberOfSeconds must 0 or more")

    self.assertIsRunning()

    self.runForXFrames(numberOfSeconds * self._fps)


  # Screenshots
  @abstractmethod
  def _abstractTakeScreenShot(self) -> Image:
    pass


  def makeGIF(self, filePath) -> Image:
    self.assertIsRunning()

    if len(self.__screenShots) == 0:
      raise NoScreenShotFramesSaved()

    logger.info("{}: Creating screenshot GIF".format(
      self.__class__.__name__
    ))
    
    self.__screenShots[0].save(
      filePath,
      format='GIF',
      loop=0, save_all=True,
      append_images=self.__screenShots[1:],
      duration=int(round(len(self.__screenShots) / self._fps)))
    
    # Reset values
    self.__screenShots = [] 

    
  def _takeScreenShot(self) -> None:
    self.assertIsRunning()
    self.__screenShots.append(self._abstractTakeScreenShot())



  # Starting
  @abstractmethod
  def _abstractStart(self, gameROMPath:str, bootROMPath:str=None) -> None:
    pass
  

  def start(self, gameROMPath:str, bootROMPath:str=None,
      saveStateFilePath:str=None, numberOfSecondsToRun:int=60) -> None:
    if numberOfSecondsToRun < 0:
      raise ValueError("numberOfSecondsToRun must be 0 or more")

    self.assertNotRunning()

    self._abstractStart(gameROMPath, bootROMPath)

    if saveStateFilePath is not None:
        self.loadState(saveStateFilePath)

    self.runForXSeconds(numberOfSecondsToRun)


  # Stopping 
  @abstractmethod
  def _abstractStop(self):
    pass


  def stop(self, saveStateFilePath:str=None):
    self.assertIsRunning()

    if saveStateFilePath is not None:
        self.saveState(saveStateFilePath)
    self._abstractStop()


  # State Management
  @abstractmethod
  def saveState(self, saveStateFilePath:str) -> None:
      pass


  @abstractmethod
  def loadState(self, saveStateFilePath:str) -> None:
      pass


  # Status
  def assertIsRunning(self) -> None:
    if not self.isRunning:
      logger.critical("{}: Emulator is not running".format(
        self.__class__.__name__
      ))
      raise NotRunning()


  def assertNotRunning(self) -> None:
    if self.isRunning:
      logger.critical("{}: Emulator is already running".format(
        self.__class__.__name__
      ))
      raise AlreadyRunning()


  @property
  @abstractmethod
  def isRunning(self) -> bool:
    pass

