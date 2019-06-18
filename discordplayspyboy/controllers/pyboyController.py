# -*- coding: utf-8 -*-

"""
Controller Interface For PyBoy
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import os
from PIL import Image
from pyboy import windowevent
from pyboy import PyBoy
from .. import logger
from .action import ButtonPress
from .controller import Controller


class PyBoyController(Controller):
  # Buttons
  def _abstractPressButton(self, button:ButtonPress) -> None:
    """Presses the specified button
    button_events: tuple(press<button>, release<button>
    """
    logger.info("PyBoy: Pressing button: {}".format(button.name))
    self._pyboy.sendInput(button.pressCode)
    self.runForXFrames(int(self._fps / 2))
    logger.info("PyBoy: Releasing button: {}".format(button.name))
    self._pyboy.sendInput(button.releaseCode)
    self.runForXFrames(int(self._fps / 2))
    


  # Magic methods
  def __init__(self, screenWidth:int=160, screenHeight:int=144):
    super().__init__(60)

    self._pyboy = None
    self._screenWidth = 160
    self._screenHeight = 144

    self._registerButton(ButtonPress("A", windowevent.PRESS_BUTTON_A, windowevent.RELEASE_BUTTON_A))
    self._registerButton(ButtonPress("B", windowevent.PRESS_BUTTON_B, windowevent.RELEASE_BUTTON_B))
    self._registerButton(ButtonPress("Select", windowevent.PRESS_BUTTON_SELECT, windowevent.RELEASE_BUTTON_SELECT))
    self._registerButton(ButtonPress("Start", windowevent.PRESS_BUTTON_START, windowevent.RELEASE_BUTTON_START))
    self._registerButton(ButtonPress("Up", windowevent.PRESS_ARROW_UP, windowevent.RELEASE_ARROW_UP))
    self._registerButton(ButtonPress("Down", windowevent.PRESS_ARROW_DOWN, windowevent.RELEASE_ARROW_DOWN))
    self._registerButton(ButtonPress("Left", windowevent.PRESS_ARROW_LEFT, windowevent.RELEASE_ARROW_LEFT))
    self._registerButton(ButtonPress("Right", windowevent.PRESS_ARROW_RIGHT, windowevent.RELEASE_ARROW_RIGHT))

  # Running
  def _runForOneFrame(self) -> None:
    self._pyboy.tick()

  # Screenshots
  def _abstractTakeScreenShot(self) -> Image:
    """Takes screen shot of emulator
    """
    return Image.frombytes(
      self._pyboy.getScreenBufferFormat(),
      (self._screenWidth, self._screenHeight),
      self._pyboy.getScreenBuffer()
    )


  # Starting
  def _abstractStart(self, gameROM, bootROM, saveFilePath:str=None):
    self._pyboy = PyBoy(None, 3, gameROM, bootROM)
    self._pyboy.setEmulationSpeed(False)


  # Stopping
  def _abstractStop(self, saveFilePath:str=None) -> None:
    self._pyboy.stop(save=True)
    self._pyboy = None

  # Status
  @property
  def isRunning(self) -> bool:
    return self._pyboy is not None

