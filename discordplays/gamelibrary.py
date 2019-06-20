# -*- coding: utf-8 -*-

"""
Game library class
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import os
from enum import auto, Enum, unique
from typing import List

class EnumFromString(Enum):
  @classmethod
  def fromString(cls, string_to_convert: str):
      """Turns a string into the corresponding enum value.
      :param string_to_convert: String to turn into an enum value.
      :return: Enum value.
      """
      try:
          return cls.__dict__[string_to_convert.upper()]
      except KeyError:
          raise ValueError("Can not convert \'" + string_to_convert + "\' into type " + cls.__name__)

@unique
class ConsoleType(EnumFromString):
  """Enum describing the directory names of the different console types"""
  GB="gb"
  GBC="gbc"
  NES="nes"



@unique
class FileType(EnumFromString):
  """Enum describing the directory names of the different file types"""
  BOOTS="boots"
  GAMES="games"
  SAVES="saves"



class GameLibrary():
  """Provides easy access to ROM library"""
  # Directories
  def _consoleTypeDir(self, consoleType:ConsoleType) -> str:
    return os.path.join(self._rootDirectory, consoleType.value)


  def _fileTypeDir(self, consoleType:ConsoleType, fileType:FileType) -> str:
    return os.path.join(self._consoleTypeDir(consoleType), fileType.value)


  # Files
  def availableFiles(self, consoleType:ConsoleType, fileType:FileType) -> List[str]:
    filesDir = self._fileTypeDir(consoleType, fileType)
    return [f for f in os.listdir(filesDir) if f != ".gitkeep" and os.path.isfile(os.path.join(filesDir, f))]


  def filePath(self, consoleType:ConsoleType, fileType:FileType, fileName) -> str:
    fPath = os.path.join(self._fileTypeDir(consoleType, fileType), fileName)

    if os.path.isfile(fPath):
      return fPath
    else:
      return None


  # Magic Methods
  def __init__(self, rootDirectory="ROMs"):
    self._rootDirectory = rootDirectory

