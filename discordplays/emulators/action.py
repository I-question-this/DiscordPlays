# -*- coding: utf-8 -*-

"""
Actions describing what is being requested of a controller.
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
from enum import Enum, unique


@unique
class Action(Enum):
  """Represents what controllers should respond to"""
  PRESS = "press"
  HOLD = "hold"



class ActionNotRecognized(Exception):
  """Thrown when a voted upon action was not recognized"""
  def __init__(self, action:Action):
      self.action = action
