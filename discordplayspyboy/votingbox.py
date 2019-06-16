# -*- coding: utf-8 -*-

"""
Voting Booth for keeping track of votes
~~~~~~~~~~~~~~~~~~~
:copyright: (c) 2019 i-question-this
:license: GPL-3.0, see LICENSE for more details.
"""
import random

class VotingBox():
  def __init__(self):
    self._userVotes = {}
    self._voteCounts = {}
  
  def castVote(self, user, vote):
    if self._userVotes.get(user) is None:
      self._userVotes[user] = vote
      self._voteCounts[vote] = 1 + self._voteCounts.get(vote, 0)

  def voteCounts(self):
    return ("{}: {}".format(k,v) for k,v in self._voteCounts.items())

  def majorityVoteResult(self):
    # Check that votes were actually cast
    if len(self._voteCounts) == 0:
      return None 
    
    maxVote = max(self._voteCounts.values())
    majorityVotes = [k for k,v in self._voteCounts.items() if v == maxVote]
    return random.choice(majorityVotes)

