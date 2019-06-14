# -*- coding: utf-8 -*-

"""
Controller Interface For PyBoy
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import os
from . import logger
from PIL import Image
from pyboy import windowevent
from pyboy import PyBoy

class PyBoyController():
  _buttons = {
    "up": (windowevent.PRESS_ARROW_UP, windowevent.RELEASE_ARROW_UP),
    "down": (windowevent.PRESS_ARROW_DOWN, windowevent.RELEASE_ARROW_DOWN),
    "left": (windowevent.PRESS_ARROW_LEFT, windowevent.RELEASE_ARROW_LEFT),
    "right": (windowevent.PRESS_ARROW_RIGHT, windowevent.RELEASE_ARROW_RIGHT),
    "start": (windowevent.PRESS_BUTTON_START, windowevent.RELEASE_BUTTON_START),
    "select": (windowevent.PRESS_BUTTON_SELECT, windowevent.RELEASE_BUTTON_SELECT),
    "a": (windowevent.PRESS_BUTTON_A, windowevent.RELEASE_BUTTON_A),
    "b": (windowevent.PRESS_BUTTON_B, windowevent.RELEASE_BUTTON_B),
  }

  def __init__(self, gameROM, bootROM, tempDir="/tmp/discordPlaysPyBoy"):
    self._pyboy = PyBoy('SDL2', 3, gameROM, bootROM)
    self._pyboy.setEmulationSpeed(False)

    self._tempDir = tempDir
    os.mkdir(self._tempDir)
    
    self._screenShots = []
    self._screenShotGif = "{}/screenshot.gif".format(self._tempDir)
    
    self._fps = 60

  async def press_button(self, button_name, afterTicks:int=7):
    """Presses button and returns gif of results
    button_name: string of the specified button
    afterTicks: number of ticks to do after the button is pressed
    """
    button_events = self._buttons.get(button_name)
    if None:
      logger.critical("Incorrect button selection: {}".format(button_name)
      return None
    
    self._screenShots = []
    self._press_button
    for _ in range(afterTicks):
      self._tick()
    self._makeGif()
    
    return self._screenShotGif

  async def _press_button(self, button_events):
    """Presses the specified button
    button_events: tuple(press<button>, release<button>
    """
    self._tick()
    self._pyboy.sendInput(button_events[0])
    self._tick()
    self._pyboy.sendInput(button_events[1])
    return True

  async def _tick(self):
    self._pyboy.tick()
    self._take_screen_shot()

  async def _makeGif(self):
    self._screenShots[0].save(
      self._screenShotGif,
      save_all=True, interlace=False,
      loop=0, optimize=True,
      append_images=self._screenShotGif[1:],
      duration=int(round(1000 / self._fps, -1)))    

  async def _take_screen_shot(self):
    """Takes screen shot of emulator
    """
    self._screenShots.append(Image.frombytes(self._pyboy.getScreenBufferFormat, (160, 144), self._pyboy.getScreenBuffer))

