# -*- coding: utf-8 -*-

"""
Actions describing what is being requested of a controller.
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
from abc import ABC, abstractmethod

class Action(ABC):
  """Represents what controllers should respond to"""
  @abstractmethod
  def __init__(self):
    pass


  @property
  def name(self) -> str:
    return self._name




class ButtonPress(Action):
  """The class the represents a button press and realease"""
  def __init__(self, name:str, pressCode: any, releaseCode: any=None):
    self._name = name
    self._pressCode = pressCode
    self._releaseCode = releaseCode


  @property
  def pressCode(self) -> any:
    return self._pressCode


  @property
  def releaseCode(self) -> any:
    return self._releaseCode

