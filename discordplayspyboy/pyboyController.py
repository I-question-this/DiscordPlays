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

  def __init__(self, gameROM, bootROM="ROMs/DMG_ROM.bin", tempDir="/tmp/discordPlaysPyBoy"):
    self._pyboy = PyBoy(None, 3, gameROM, bootROM)
    self._pyboy.setEmulationSpeed(False)

    self._tempDir = tempDir
    if not os.path.exists(self._tempDir):
      os.mkdir(self._tempDir)
    
    self._screenShots = []
    self._screenShotGif = "{}/screenshot.gif".format(self._tempDir)
    
    self._fps = 60.0

  def availableButtons(self):
    return self._buttons.keys()

  async def pressButton(self, buttonName, seconds:int=100):
    """Presses button and returns gif of results
    button_name: string of the specified button
    afterTicks: number of ticks to do after the button is pressed
    """
    buttonEvents = self._buttons.get(buttonName)
    if buttonEvents is None:
      logger.critical("PyBoy: Incorrect button selection: {}".format(buttonName))
      return None
    
    self._screenShots = []
    await self._pressButton(buttonEvents)
    await self._tick(int(round(seconds*self._fps)))
    await self._makeGif()
    
    return self._screenShotGif

  def stop(self):
    self._pyboy.stop(save=True)

  async def _pressButton(self, buttonEvents):
    """Presses the specified button
    button_events: tuple(press<button>, release<button>
    """
    logger.info("PyBoy: Pressing button: {}".format(buttonEvents[0]))
    await self._tick(2)
    self._pyboy.sendInput(buttonEvents[0])
    logger.info("PyBoy: Releasing button: {}".format(buttonEvents[1]))
    await self._tick(2)
    self._pyboy.sendInput(buttonEvents[1])
    await self._tick(2)
    return True

  async def _tick(self, numTicks=1):
    logger.info("PyBoy: Moving forward {} ticks".format(numTicks))
    for _ in range(numTicks):
      self._pyboy.tick()
      await self._take_screen_shot()

  async def _makeGif(self):
    logger.info("PyBoy: Creating screenshot GIF")
    self._screenShots[0].save(
      self._screenShotGif,
      format='GIF',
      loop=0, save_all=True,
      append_images=self._screenShots[1:],
      duration=int(round(len(self._screenShotGif) / self._fps)))    

  async def _take_screen_shot(self):
    """Takes screen shot of emulator
    """
    self._screenShots.append(Image.frombytes(self._pyboy.getScreenBufferFormat(), (160, 144), self._pyboy.getScreenBuffer()))

