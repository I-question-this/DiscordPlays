# -*- coding: utf-8 -*-

"""
Voting Booth for keeping track of votes
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import random

class VotingBox():
  votes = {}
  
  def castVote(self, user, button):
    if self.votes.get(user) is None:
      self.votes[user] = button

  def majorityVote(self):
    # Check that votes were actually cast
    if len(self.votes) == 0:
      return None 
    
    counts = {}
    for button in self.votes.values():
      counts[button] = 1 + counts.get(button, 0)
     
    maxVote = max(counts.values())
    
    return random.choice([k for k,v in counts.items() if v == maxVote])

